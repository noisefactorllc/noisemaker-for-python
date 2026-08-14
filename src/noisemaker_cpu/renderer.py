"""Render a bundled effect: load metadata + transpiled kernel, run the pass(es).

P0 supports single-pass generators (solid) and single-input filters (invert).
The multi-pass render graph (named attachments, half-float quantization, blend,
drawMode) is P1.
"""

from __future__ import annotations

import json
import math
import os
import time as _clock

import numpy as np

from .adapters import get_adapter
from .adapters._palette_data import PALETTE_DATA
from .draw_ops import get_draw_op
from .dsl import compile_dsl
from .frame_export import CpuFrameExportAdapter, FrameExportQueue
from .iteration import compute_iteration_groups, is_particle_state_name, iteration_schedule
from .kernel_loader import KernelCache
from .overlay_gen import OVERLAY_EFFECTS, render_worm_overlay
from .pass_runner import Ctx, run_pass, run_pass_deriv, run_pass_mrt
from .runtime import F32, Runtime, f32
from .sink import SinkManager
from .surface import Surface
from .texture_format import quantize_texture

_META = None
_CACHE = KernelCache()
_PARTICLE_STATE_FALLBACK_SIZE = 256
_PARTICLE_STATE_FORMATS = {
    "global_xyz": "rgba32f",
    "global_vel": "rgba32f",
    "global_rgba": "rgba8",
    "global_life_data": "rgba16f",
}


def _is_chain_bundle(value):
    return isinstance(value, dict) and "image" in value


def _chain_bundle(value):
    if _is_chain_bundle(value):
        return value
    return {"image": value, "volume": None, "geometry": None, "volumeSize": None}


def _bundle_output(name, input_surface, resources):
    if not name or name in {"inputTex", "inputTex3d", "inputGeo"}:
        return input_surface
    return resources.get(name)


def _inherit_volume_size(effect, params, bundle):
    volume = bundle["volume"]
    if volume is None or "volumeSize" not in effect.get("params", {}):
        return params
    if effect.get("domain") not in {"volume-generator", "volume-filter", "volume-renderer"}:
        return params
    expected_height = volume.width**2
    if volume.height != expected_height:
        raise ValueError(
            f"input volume atlas expected {volume.width}x{expected_height}, received {volume.width}x{volume.height}"
        )
    inherited = dict(params)
    inherited["volumeSize"] = volume.width
    return inherited


def bundle_dir() -> str:
    return os.environ.get("NOISEMAKER_BUNDLE") or os.path.join(os.path.dirname(__file__), "bundle")


def _meta() -> dict:
    global _META
    if _META is None:
        with open(os.path.join(bundle_dir(), "metadata.json"), encoding="utf-8") as f:
            _META = json.load(f)
    return _META


def _kernel_for(key: str):
    def factory():
        fname = key.replace("/", "__").replace(":", "__") + ".py"
        with open(os.path.join(bundle_dir(), "kernels", "python", fname), encoding="utf-8") as f:
            return f.read()

    return _CACHE.get(key, factory)


def _parse_hex(s: str):
    s = s.lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    r = int(s[0:2], 16) / 255.0
    g = int(s[2:4], 16) / 255.0
    b = int(s[4:6], 16) / 255.0
    if len(s) >= 8:
        a = int(s[6:8], 16) / 255.0
        return [r, g, b, a]
    return [r, g, b]


def _coerce(spec: dict, value):
    t = spec["type"]
    if value is None:
        value = spec.get("default")
    if t == "color":
        if isinstance(value, str):
            value = _parse_hex(value)
        return np.array(value, dtype=F32)
    if t in ("vec2", "vec3", "vec4", "mat3"):
        if isinstance(value, str):  # CLI --param: "0.1,0.2,0.3"
            value = [float(x) for x in value.split(",")]
        return np.array(value, dtype=F32)
    if t == "float":
        return f32(float(value))
    if t in ("int", "enum", "member"):
        if isinstance(value, str):
            choices = spec.get("choices") or {}
            key = value.split(".")[-1]  # "oscType.sine" -> "sine"
            if value in choices:
                return int(choices[value])
            if key in choices:
                return int(choices[key])
            try:
                return int(float(value))
            except ValueError:
                return 0  # CDN member with no inline choices: defaults are the 0th member
        return int(value)
    if t in ("bool", "boolean"):
        if isinstance(value, str):
            return value.strip().lower() in ("1", "true", "yes", "on")
        return bool(value)
    return value


class _DefaultTex(dict):
    """Texture map where an unbound sampler reads as a 1x1 black surface (WebGL
    zero-initializes unbound samplers)."""

    def __init__(self, default):
        super().__init__()
        self._default = default

    def __missing__(self, key):
        return self._default


def _remap_uniform_data(u, width, height):
    """Pack synth/remap's std140 `data[267]` block from the bound uniforms —
    port of noisemaker-cpu renderer.js remapUniformData. At the default
    zoneCount=0 this yields the background color for every pixel."""

    def g(name, default):
        v = u.get(name)
        return default if v is None else v

    data = [np.zeros(4, dtype=F32) for _ in range(267)]
    bg = np.asarray(g("bgColor", [0, 0, 0]), dtype=F32)
    data[0] = np.array([bg[0], bg[1], bg[2], g("bgAlpha", 1)], dtype=F32)
    data[1] = np.array([g("zoneCount", 0), g("smoothEdge", 0.04), 0, g("time", 0)], dtype=F32)
    for zone in range(8):
        data[2 + zone] = np.array(
            [g(f"zone{zone}_count", 0), g(f"zone{zone}_active", 0), 0, g(f"zone{zone}_alpha", 1)], dtype=F32
        )
        for pair in range(32):
            data[10 + zone * 32 + pair] = np.asarray(g(f"zone{zone}_v{pair}", [0, 0, 0, 0]), dtype=F32)
    data[266] = np.array([width, height, 0, 0], dtype=F32)
    return data


def _size_component(spec, params, full_size, resources=None, axis="width"):
    if spec is None or (isinstance(spec, str) and spec in {"input", "screen", "resolution", "100%"}):
        return full_size
    if isinstance(spec, (int, float)):
        return max(1, int(spec))
    if isinstance(spec, str) and spec.endswith("%"):
        return max(1, round(full_size * float(spec[:-1]) / 100))
    if isinstance(spec, dict):
        input_override = spec.get("inputOverride")
        if input_override and resources and resources.get(input_override) is not None:
            surface = resources[input_override]
            return surface.width if axis == "width" else surface.height
        if "param" in spec:
            value = params.get(spec["param"], spec.get("paramDefault", spec.get("default", full_size)))
            if "power" in spec:
                value **= spec["power"]
            return max(1, round(value))
        if "screenDivide" in spec:
            divisor = max(1, float(params.get(spec["screenDivide"], spec.get("default", 1))))
            return max(1, math.ceil(full_size / divisor))
    return full_size


def _texture_dimensions(texture_spec, params, width, height, resources=None):
    texture_spec = texture_spec or {}
    return (
        _size_component(texture_spec.get("width"), params, width, resources, "width"),
        _size_component(texture_spec.get("height"), params, height, resources, "height"),
    )


def _particle_state_dimensions(params):
    size = max(1, int(params.get("stateSize", _PARTICLE_STATE_FALLBACK_SIZE)))
    return size, size


def _texture_format(effect, name):
    declared = (effect.get("textures") or {}).get(name, {})
    if "format" in declared:
        return declared["format"]
    if is_particle_state_name(name):
        return _PARTICLE_STATE_FORMATS.get(name, "rgba16f")
    return "rgba16f"


def _pass_enabled(render_pass, uniforms):
    conditions = render_pass.get("conditions") or {}
    for condition in conditions.get("runIf", []):
        if uniforms.get(condition["uniform"]) != condition.get("equals"):
            return False
    for condition in conditions.get("skipIf", []):
        if uniforms.get(condition["uniform"]) == condition.get("equals"):
            return False
    return True


def _repeat_count(render_pass, uniforms):
    repeat = render_pass.get("repeat", 1)
    if isinstance(repeat, str):
        repeat = uniforms.get(repeat, 1)
    return max(0, int(repeat))


def _canonical_uniforms(width, height, time, seed, effect_uniforms, frame=0, delta_time=0):
    """Match noisemaker-cpu src/csl/glsl-kernel.js createCanonicalBindings."""
    res = np.array([float(width), float(height)], dtype=F32)
    aspect = f32(width / height)
    u = {
        "renderScale": f32(1.0),
        "speed": 0,
        "seed": f32(seed),
        "centerLoX": 0,
        "centerLoY": 0,
        "size": np.zeros(4, dtype=F32),
        "motion": np.zeros(4, dtype=F32),
    }
    u.update(effect_uniforms)  # effect params override base defaults
    u.update(
        {  # canonical values always win
            "resolution": res,
            "fullResolution": res,
            "tileOffset": np.zeros(2, dtype=F32),
            "aspectRatio": aspect,
            "aspect": aspect,
            "time": f32(time),
            "globalTime": f32(time),
            "frame": int(frame),
            "deltaTime": f32(delta_time),
        }
    )
    return u


def _render_effect_once(
    effect_id,
    params=None,
    inputs=None,
    width=256,
    height=256,
    seed=1,
    time=0.0,
    *,
    attachments=None,
    previous_output=None,
    frame=0,
    delta_time=0,
) -> Surface:
    params = params or {}
    inputs = inputs or {}
    eff = _meta()["effects"][effect_id]
    domain = eff.get("domain", "image")
    input_bundle = {
        "image": inputs.get("inputTex"),
        "volume": inputs.get("inputTex3d"),
        "geometry": inputs.get("inputGeo"),
        "volumeSize": inputs.get("inputTex3d").width if inputs.get("inputTex3d") is not None else None,
    }
    input_was_bundle = input_bundle["volume"] is not None or input_bundle["geometry"] is not None

    effect_uniforms = {}
    param_values = {}
    surface_params = {}  # sampler-name -> provided Surface (or None)
    for pname, spec in eff["params"].items():
        if spec.get("type") == "surface":
            sampler = spec.get("uniform") or spec.get("texture") or pname
            surf = inputs.get(sampler) or inputs.get(pname)
            surface_params[sampler] = surf
            # colorModeUniform (e.g. mashup's layerN_active): 1 when the surface
            # is wired, 0 when unbound, so the kernel can fall back per band.
            if spec.get("colorModeUniform"):
                effect_uniforms[spec["colorModeUniform"]] = 1 if surf is not None else 0
            continue
        if pname == "seed" and "seed" not in params:
            # Match noisemaker-cpu bin/noisemaker-cpu.js `effect` command: an
            # effect's own `seed` param shares the GLSL uniform name with the
            # canonical render seed. When the caller doesn't explicitly set the
            # param, the CLI threads the render `seed` into it instead of
            # falling back to the param's own (possibly different) metadata
            # default, so `seed=` actually changes the generator's look.
            val = _coerce(spec, seed)
        else:
            val = _coerce(spec, params.get(pname))
        param_values[pname] = val
        if spec.get("uniform") is not None:
            effect_uniforms[spec["uniform"]] = val
        if spec.get("define") is not None:
            effect_uniforms[spec["define"]] = val

    # classicNoisedeck palette presets: a `palette`-type param > 0 selects
    # cosine-palette coefficients from the shared table, overriding the
    # paletteAmp/Freq/Offset/Phase/Mode uniforms (reference renderer.js).
    if eff.get("namespace") == "classicNoisedeck":
        pal = next(
            (pn for pn, sp in eff["params"].items() if isinstance(sp, dict) and sp.get("type") == "palette"), None
        )
        if pal is not None:
            idx = _coerce(eff["params"][pal], params.get(pal))
            if isinstance(idx, int) and 0 < idx <= len(PALETTE_DATA):
                e = PALETTE_DATA[idx - 1]
                effect_uniforms["paletteAmp"] = np.array(e[0:3], dtype=F32)
                effect_uniforms["paletteFreq"] = np.array(e[4:7], dtype=F32)
                effect_uniforms["paletteOffset"] = np.array(e[8:11], dtype=F32)
                effect_uniforms["palettePhase"] = np.array(e[12:15], dtype=F32)
                effect_uniforms["paletteMode"] = 3 if e[3] == 0 else int(e[3])

    uniforms = _canonical_uniforms(width, height, time, seed, effect_uniforms, frame=frame, delta_time=delta_time)
    # synth/remap's std140 `data` block is packed from the bound uniforms.
    if effect_id == "synth/remap":
        uniforms["data"] = _remap_uniform_data(uniforms, width, height)
    blank = Surface(1, 1)

    rt = Runtime()
    result = None
    output_result = None
    if attachments is None:
        attachments = {}

    for pname, spec in eff["params"].items():
        param_type = spec.get("type")
        if param_type not in {"volume", "geometry"}:
            continue
        typed_input = input_bundle["volume" if param_type == "volume" else "geometry"]
        if typed_input is not None:
            attachments[pname] = typed_input
            continue
        output_name = eff.get("outputTex3d" if param_type == "volume" else "outputGeo")
        output_spec = (eff.get("textures") or {}).get(output_name)
        if output_spec is None:
            raise ValueError(f'{effect_id} parameter "{pname}" requires a {param_type} input')
        typed_width, typed_height = _texture_dimensions(
            output_spec,
            param_values,
            width,
            height,
            {**inputs, **attachments},
        )
        attachments[pname] = Surface(typed_width, typed_height)

    # One-shot CPU-generated textures declared but not produced by any pass
    # (fibers/scratches/strayHair overlayTex): generate and bind before the loop.
    if effect_id in OVERLAY_EFFECTS:
        produced = {an for pp in eff["passes"] for an in (pp.get("outputs") or {}).values()}
        for tname in eff.get("textures", {}):
            if tname == "overlayTex" and tname not in produced and tname not in surface_params:
                gen = {}
                for pn in ("seed", "density"):
                    if pn in eff["params"]:
                        gp = eff["params"][pn]
                        gen[pn] = (
                            _coerce(gp, seed) if pn == "seed" and "seed" not in params else _coerce(gp, params.get(pn))
                        )
                attachments[tname] = render_worm_overlay(effect_id, width, height, gen)

    for texture_name, texture_spec in (eff.get("textures") or {}).items():
        if texture_name not in attachments:
            texture_width, texture_height = _texture_dimensions(
                texture_spec,
                param_values,
                width,
                height,
                {**inputs, **attachments},
            )
            attachments[texture_name] = Surface(texture_width, texture_height)

    # Texture filtering must match the JS oracle: it sets filter='linear' ONLY on
    # the declared external texture (renderer.js buildBindings); every pooled
    # surface (inputTex, heightMap, mixer surface params) has no filter set, so
    # `surface.filter === 'linear'` is false and the JS sampler uses NEAREST. The
    # difference is invisible at texel-center (identity) sampling but decisive for
    # warp/displacement/refraction effects that sample at fractional coordinates.
    external_tex = eff.get("externalTexture")

    for p in eff["passes"]:
        # Pass-level uniform aliases: the definition may expose a param under one
        # name (e.g. `color`) while this pass's GLSL declares another (`splatColor`).
        pass_uniforms = dict(uniforms)
        for glsl_name, param_name in (p.get("uniforms") or {}).items():
            if param_name in effect_uniforms:
                pass_uniforms[glsl_name] = effect_uniforms[param_name]
            elif param_name in uniforms:
                pass_uniforms[glsl_name] = uniforms[param_name]
        if not _pass_enabled(p, pass_uniforms):
            continue
        for _ in range(_repeat_count(p, pass_uniforms)):
            textures = _DefaultTex(blank)
            for sampler, surf in surface_params.items():
                if surf is not None:
                    surf.filter = "linear" if sampler == external_tex else "nearest"
                    textures[sampler] = surf
            for sampler_name, source in (p.get("inputs") or {}).items():
                if source in {"selfTex", "feedback"}:
                    surf = previous_output
                elif source == "inputTex" and inputs.get("inputTex") is not None:
                    surf = inputs["inputTex"]
                else:
                    surf = attachments.get(source) or inputs.get(source) or inputs.get(sampler_name) or result
                if surf is None and is_particle_state_name(source):
                    particle_width, particle_height = _particle_state_dimensions(param_values)
                    surf = Surface(particle_width, particle_height)
                    attachments[source] = surf
                if surf is not None:
                    surf.filter = "linear" if sampler_name == external_tex else "nearest"
                    textures[sampler_name] = surf

            outputs = p.get("outputs") or {}
            out_names = list(outputs.values())
            texture_spec = (eff.get("textures") or {}).get(out_names[0], {}) if out_names else {}
            dimension_spec = p.get("viewport") or texture_spec
            prior_output = attachments.get(out_names[0]) if out_names else None
            if prior_output is not None and out_names[0] not in (eff.get("textures") or {}):
                pass_width, pass_height = prior_output.width, prior_output.height
            elif out_names and is_particle_state_name(out_names[0]) and out_names[0] not in (eff.get("textures") or {}):
                pass_width, pass_height = _particle_state_dimensions(param_values)
            else:
                pass_width, pass_height = _texture_dimensions(
                    dimension_spec,
                    param_values,
                    width,
                    height,
                    {**inputs, **attachments},
                )
            pass_resolution = np.array([float(pass_width), float(pass_height)], dtype=F32)
            pass_aspect = f32(pass_width / pass_height)
            pass_uniforms.update(
                {
                    "resolution": pass_resolution,
                    "aspectRatio": pass_aspect,
                    "aspect": pass_aspect,
                }
            )
            draw_op = get_draw_op(effect_id, p["program"]) if p.get("drawMode") else None
            produced = []
            if draw_op is not None:
                destination = Surface(pass_width, pass_height)
                prior = attachments.get(out_names[0]) if out_names else None
                if prior is not None and prior.data.shape == destination.data.shape:
                    destination.data[:] = prior.data
                draw_op(textures, destination, pass_uniforms, p)
                produced = [destination]
            else:
                ctx = Ctx(
                    rt,
                    uniforms=pass_uniforms,
                    textures=textures,
                    resolution=np.array([float(pass_width), float(pass_height)], dtype=F32),
                    time=time,
                    seed=seed,
                )
                kernel = _kernel_for(p["key"])
                adapter = get_adapter(effect_id, p["program"])
                if adapter is not None:
                    kernel = adapter(rt, kernel)
                if len(out_names) > 1:
                    produced = run_pass_mrt(kernel, ctx, pass_width, pass_height)
                else:
                    runner = run_pass_deriv if getattr(kernel, "uses_derivatives", False) else run_pass
                    produced = [runner(kernel, ctx, pass_width, pass_height)]
            for attach_name, surface in zip(out_names, produced, strict=True):
                quantize_texture(surface, _texture_format(eff, attach_name))
                attachments[attach_name] = surface
                if attach_name == "outputTex":
                    output_result = surface
            if produced:
                result = produced[0]
    is_volume_domain = domain in {"volume-generator", "volume-filter", "volume-renderer"}
    image = (
        _bundle_output(eff.get("outputTex"), input_bundle["image"], attachments)
        if eff.get("outputTex")
        else (attachments.get("outputTex") or (input_bundle["image"] if is_volume_domain else result))
    )
    volume = _bundle_output(eff.get("outputTex3d"), input_bundle["volume"], attachments)
    geometry = _bundle_output(eff.get("outputGeo"), input_bundle["geometry"], attachments)
    volume_size = (
        param_values.get("volumeSize", volume.width if volume is not None else None)
        if domain == "volume-generator"
        else (
            input_bundle["volumeSize"]
            or param_values.get("volumeSize")
            or (volume.width if volume is not None else None)
        )
    )
    if is_volume_domain and volume is None and domain != "volume-renderer":
        raise ValueError(f"{effect_id} did not produce outputTex3d")
    if volume is not None and domain in {"volume-generator", "volume-filter"}:
        expected_width = volume_size
        expected_height = volume_size**2
        if volume.width != expected_width or volume.height != expected_height:
            raise ValueError(
                f"{effect_id} volume atlas expected {expected_width}x{expected_height}, "
                f"received {volume.width}x{volume.height}"
            )
    if image is None and domain not in {"volume-generator", "volume-filter"}:
        raise ValueError(f"{effect_id} did not produce outputTex")
    if input_was_bundle or is_volume_domain:
        return {"image": image, "volume": volume, "geometry": geometry, "volumeSize": volume_size}
    return output_result if output_result is not None else image


def render_effect(effect_id, params=None, inputs=None, width=256, height=256, seed=1, time=0.0):
    params = params or {}
    inputs = inputs or {}
    effect = _meta()["effects"][effect_id]
    input_bundle = {
        "image": inputs.get("inputTex"),
        "volume": inputs.get("inputTex3d"),
        "geometry": inputs.get("inputGeo"),
        "volumeSize": inputs.get("inputTex3d").width if inputs.get("inputTex3d") is not None else None,
    }
    params = _inherit_volume_size(effect, params, input_bundle)
    if not effect.get("iterated"):
        return _render_effect_once(effect_id, params, inputs, width, height, seed, time)

    iteration_spec = effect["params"]["iterationCount"]
    iteration_count = _coerce(iteration_spec, params.get("iterationCount"))
    if iteration_count <= 0:
        if input_bundle["volume"] is not None or input_bundle["geometry"] is not None:
            return {
                "image": input_bundle["image"].clone() if input_bundle["image"] is not None else None,
                "volume": input_bundle["volume"].clone() if input_bundle["volume"] is not None else None,
                "geometry": input_bundle["geometry"].clone() if input_bundle["geometry"] is not None else None,
                "volumeSize": input_bundle["volumeSize"],
            }
        source = input_bundle["image"]
        if source is not None:
            return source.clone()
        if effect.get("domain") == "volume-generator":
            param_values = {name: _coerce(spec, params.get(name)) for name, spec in effect["params"].items()}
            output_name = effect.get("outputTex3d")
            output_spec = (effect.get("textures") or {}).get(output_name, {})
            volume_width, volume_height = _texture_dimensions(output_spec, param_values, width, height)
            geometry = None
            geometry_name = effect.get("outputGeo")
            if geometry_name and geometry_name != "inputGeo":
                geometry_spec = (effect.get("textures") or {}).get(geometry_name, {})
                geometry_width, geometry_height = _texture_dimensions(geometry_spec, param_values, width, height)
                geometry = Surface(geometry_width, geometry_height)
            return {
                "image": None,
                "volume": Surface(volume_width, volume_height),
                "geometry": geometry,
                "volumeSize": param_values.get("volumeSize", volume_width),
            }
        return Surface(width, height)
    attachments = {}
    previous_output = None
    result = None
    for tick in iteration_schedule(time, iteration_count):
        result = _render_effect_once(
            effect_id,
            params,
            inputs,
            width,
            height,
            seed,
            tick["time"],
            attachments=attachments,
            previous_output=previous_output,
            frame=tick["frame"],
            delta_time=tick["delta_time"],
        )
        previous_output = _chain_bundle(result)["image"]
    return result


def _resolve_surface_marker(marker, current, surfaces):
    """Turn a compiled surface binding into a Surface (or None for unbound)."""
    if marker == "@current":
        return _chain_bundle(current)["image"]
    _, name = marker
    surf = surfaces.get(name)
    if surf is None:
        raise ValueError(f"Surface {name} has not been written")
    return surf


def _effect_step_inputs(step, current, surfaces, external_textures):
    # Mirror the JS renderer's per-step binding: the chain's current image is the
    # effect's inputTex; each surface param is bound by param name (the path
    # render_effect resolves), and external textures (imageTex/textTex/named) pass
    # straight through. Explicit surface args and inputTex-defaults win over them.
    inputs = dict(external_textures or {})
    bundle = _chain_bundle(current)
    if bundle["image"] is not None:
        inputs["inputTex"] = bundle["image"]
    if bundle["volume"] is not None:
        inputs["inputTex3d"] = bundle["volume"]
    if bundle["geometry"] is not None:
        inputs["inputGeo"] = bundle["geometry"]
    for pname, marker in step["surfaces"].items():
        surf = _resolve_surface_marker(marker, current, surfaces)
        if surf is not None:
            inputs[pname] = surf
    return inputs


def _run_effect_step(step, current, surfaces, external_textures, width, height, seed, time):
    inputs = _effect_step_inputs(step, current, surfaces, external_textures)
    effect = _meta()["effects"][step["effect_id"]]
    params = _inherit_volume_size(effect, step["params"], _chain_bundle(current))
    return render_effect(step["effect_id"], params, inputs, width=width, height=height, seed=seed, time=time)


def _run_iterated_group(group, current, surfaces, external_textures, effects, width, height, seed, time):
    first_step = group["steps"][0]
    first_effect = effects[first_step["effect_id"]]
    iteration_spec = first_effect["params"]["iterationCount"]
    iteration_count = _coerce(iteration_spec, first_step["params"].get("iterationCount"))
    if iteration_count <= 0:
        if _is_chain_bundle(current):
            return {
                "image": current["image"].clone() if current["image"] is not None else None,
                "volume": current["volume"].clone() if current["volume"] is not None else None,
                "geometry": current["geometry"].clone() if current["geometry"] is not None else None,
                "volumeSize": current["volumeSize"],
            }
        return current.clone() if current is not None else Surface(width, height)

    state_size = None
    if "stateSize" in first_effect["params"]:
        state_size = _coerce(first_effect["params"]["stateSize"], first_step["params"].get("stateSize"))

    group_input = current
    group_attachments = {}
    step_attachments = [{} for _ in group["steps"]]
    previous_outputs = [None] * len(group["steps"])
    for tick in iteration_schedule(time, iteration_count):
        iteration_current = group_input
        for index, step in enumerate(group["steps"]):
            effect = effects[step["effect_id"]]
            params = _inherit_volume_size(effect, dict(step["params"]), _chain_bundle(iteration_current))
            if state_size is not None and "stateSize" in effect["params"]:
                params["stateSize"] = state_size
            inputs = _effect_step_inputs(step, iteration_current, surfaces, external_textures)
            attachments = {**step_attachments[index], **group_attachments}
            iteration_current = _render_effect_once(
                step["effect_id"],
                params,
                inputs,
                width,
                height,
                seed,
                tick["time"],
                attachments=attachments,
                previous_output=previous_outputs[index],
                frame=tick["frame"],
                delta_time=tick["delta_time"],
            )
            step_attachments[index] = {
                name: surface
                for name, surface in attachments.items()
                if name != "global_accum" and not is_particle_state_name(name)
            }
            group_attachments.update(
                {
                    name: surface
                    for name, surface in attachments.items()
                    if name == "global_accum" or is_particle_state_name(name)
                }
            )
            previous_outputs[index] = _chain_bundle(iteration_current)["image"]
        current = iteration_current
    return current


def render_dsl(source, width=512, height=512, seed=1, time=0.0, external_textures=None, seed_surfaces=None) -> Surface:
    """Render a Polymorphic DSL program on the CPU — the Python counterpart of
    noisemaker-cpu's CpuRenderer.render(). Compiles the program to a plan, then
    threads each chain's `current` surface through read/write/effect steps over a
    named-surface map (o0..o7). Stateful and particle chains execute as iteration
    groups so their attachments persist across frames and joining effects."""
    effects = _meta()["effects"]
    plan = compile_dsl(source, effects)
    surfaces = dict(seed_surfaces or {})
    for chain in plan["chains"]:
        current = None
        for group in compute_iteration_groups(chain["steps"], effects):
            if group["iterated"]:
                current = _run_iterated_group(
                    group,
                    current,
                    surfaces,
                    external_textures,
                    effects,
                    width,
                    height,
                    seed,
                    time,
                )
                continue
            for step in group["steps"]:
                kind = step["kind"]
                if kind == "read":
                    current = surfaces.get(step["surface"])
                    if current is None:
                        raise ValueError(f"Surface {step['surface']} has not been written")
                elif kind == "write":
                    surfaces[step["surface"]] = _chain_bundle(current)["image"]
                else:
                    current = _run_effect_step(step, current, surfaces, external_textures, width, height, seed, time)
    rendered = surfaces.get(plan["render_surface"])
    if rendered is None:
        raise ValueError(f"Surface {plan['render_surface']} has not been written")
    return rendered


class CpuRenderer:
    """Stateful renderer facade that owns output sinks and export queues."""

    def __init__(self, *, on_sink_error=None):
        self.sink_manager = SinkManager(on_error=on_sink_error)
        self._sink_descriptor = {
            "width": 0,
            "height": 0,
            "format": "rgba8unorm",
            "colorSpace": "srgb",
            "alphaMode": "straight",
            "fps": 60,
        }
        self._sinks_configured = False

    def add_sink(self, sink):
        return self.sink_manager.add(sink)

    @staticmethod
    def create_frame_export_queue(*, slots=3, on_error=None):
        return FrameExportQueue(CpuFrameExportAdapter(), slots=slots, on_error=on_error)

    def _configure_sinks(self, width, height) -> None:
        extent_unchanged = self._sink_descriptor["width"] == width and self._sink_descriptor["height"] == height
        if self._sinks_configured and extent_unchanged:
            return
        self._sink_descriptor["width"] = width
        self._sink_descriptor["height"] = height
        self._sinks_configured = True
        self.sink_manager.configure(self._sink_descriptor)

    @staticmethod
    def _validate_options(width, height, seed, time) -> None:
        if not isinstance(width, int) or isinstance(width, bool) or width <= 0:
            raise ValueError("width must be a positive integer")
        if not isinstance(height, int) or isinstance(height, bool) or height <= 0:
            raise ValueError("height must be a positive integer")
        valid_time_type = isinstance(time, (int, float, np.integer, np.floating)) and not isinstance(time, bool)
        if not valid_time_type or not math.isfinite(time):
            raise TypeError("time must be finite")
        if not isinstance(seed, (int, np.integer)) or isinstance(seed, bool):
            raise TypeError("seed must be an integer")

    def render(
        self,
        source,
        *,
        width=512,
        height=512,
        seed=1,
        time=0.0,
        external_textures=None,
        seed_surfaces=None,
        presentation_timestamp=None,
    ) -> Surface:
        self._validate_options(width, height, seed, time)
        self._configure_sinks(width, height)
        result = render_dsl(
            source,
            width=width,
            height=height,
            seed=seed,
            time=time,
            external_textures=external_textures,
            seed_surfaces=seed_surfaces,
        )
        timestamp = presentation_timestamp if presentation_timestamp is not None else _clock.perf_counter() * 1000
        self.sink_manager.submit(result, timestamp)
        return result

    def dispose(self) -> None:
        self.sink_manager.close()
