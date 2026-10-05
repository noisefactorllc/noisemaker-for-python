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
from .automation import is_automation_value as _is_automation_value
from .automation import is_finite_number as _is_finite_number
from .automation import resolve_automation_uniform as _resolve_automation_uniform
from .draw_ops import get_draw_op
from .dsl import compile_dsl
from .external_textures import external_data_surface
from .frame_export import CpuFrameExportAdapter, FrameExportQueue
from .iteration import compute_iteration_groups, is_particle_state_name, iteration_schedule
from .kernel_loader import KernelCache
from .mesh_render import get_mesh_op
from .overlay_gen import OVERLAY_EFFECTS, render_worm_overlay
from .pass_runner import Ctx, run_pass, run_pass_deriv, run_pass_mrt
from .runtime import F32, Runtime, f32, _oracle_pass_repeat_clamp
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


def _automation_param_spec(param):
    """The consumer-range spec upstream's expander builds for automation scaling
    (shaders/src/runtime/expander.js uniformSpecs): a float/int parameter without
    choices scales the 0..1 automation output into its declared min..max (0..100
    when undeclared); an int parameter with choices (a conditional selector) is
    only rounded to the selected integer, scaled into its declared range when it
    declares one. Everything else gets no spec, so an automation value resolves
    unscaled."""
    if not param:
        return None
    param_type = param.get("type")
    if param_type in ("float", "int") and not param.get("choices"):
        param_min = param.get("min")
        param_max = param.get("max")
        return {"min": 0 if param_min is None else param_min, "max": 100 if param_max is None else param_max}
    if param_type == "int" and param.get("choices"):
        spec = {"type": "int"}
        param_min = param.get("min")
        param_max = param.get("max")
        if _is_finite_number(param_min) and _is_finite_number(param_max):
            spec["min"] = param_min
            spec["max"] = param_max
        return spec
    return None


def _resolve_effect_automation(effect, params, time):
    """Resolves `osc(...)` automation values in a step's params to concrete numbers
    for this render, using `time` (the normalized 0..1 loop time the canonical
    kernels receive). Returns the params object unchanged when no param carries
    automation, so every pre-existing program keeps its exact identity and
    byte-identical render path. Only float/int params resolve (the JS engine
    accepts automation on those types alone); other types keep the raw value so
    coercion rejects the program."""
    has_automation = any(_is_automation_value(value) for value in params.values())
    if not has_automation:
        return params
    effect_params = (effect or {}).get("params", {})
    resolved = {}
    for name, value in params.items():
        spec = effect_params.get(name) or {}
        resolved[name] = (
            _resolve_automation_uniform(value, time, _automation_param_spec(spec))
            if spec.get("type") in ("float", "int")
            else value
        )
    return resolved


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


class ParameterRangeError(ValueError):
    """A numeric parameter value falls outside its declared min/max range.

    Mirrors the pinned oracle's src/effects/definition.js, which raises
    `RangeError('Parameter "<name>" must be at most <max>')` after coercing
    every numeric parameter value (GAP-007).
    """


def _bound_text(bound) -> str:
    """Render a declared range bound the way JS Number -> String does: the
    metadata declares some maxima as integral floats (1000.0) but the reference
    diagnostic prints `1000`."""
    if isinstance(bound, float) and bound.is_integer():
        return str(int(bound))
    return str(bound)


def _check_param_range(spec: dict, name: str | None, value) -> None:
    """Enforce a numeric parameter's declared min/max range. `name=None` skips
    the check: the unvalidated call paths are the DSL renderer's implicit
    render-seed threading (runtime/renderer.js spreads the render seed into step
    params without a range check, while explicit DSL assignments go through
    coerceWithRange) and per-render resolved `osc()` automation values (the JS
    engine validates the automation object at normalization, never the number
    resolved from it at render time)."""
    if (
        name is None
        or isinstance(value, bool)
        or not isinstance(value, (int, float, np.integer, np.floating))
    ):
        return
    number = value.item() if isinstance(value, (np.integer, np.floating)) else value
    declared_min, declared_max = spec.get("min"), spec.get("max")
    if declared_min is not None and number < declared_min:
        raise ParameterRangeError(f'Parameter "{name}" must be at least {_bound_text(declared_min)}')
    if declared_max is not None and number > declared_max:
        raise ParameterRangeError(f'Parameter "{name}" must be at most {_bound_text(declared_max)}')


def _coerce(spec: dict, value, name: str | None = None):
    t = spec["type"]
    if value is None:
        value = spec.get("default")
    if _is_automation_value(value):
        # An `osc(...)` automation value (numeric params only, matching the JS
        # EffectDefinition.normalizeValue contract) is kept as-is here and
        # resolved to a concrete number per render in _render_effect_once;
        # other types keep rejecting it.
        if t in ("float", "int"):
            return value
        raise TypeError(f'Parameter "{name}" does not accept an osc() automation value')
    if t == "color":
        if isinstance(value, str):
            value = _parse_hex(value)
        return np.array(value, dtype=F32)
    if t in ("vec2", "vec3", "vec4", "mat3"):
        if isinstance(value, str):  # CLI --param: "0.1,0.2,0.3"
            value = [float(x) for x in value.split(",")]
        return np.array(value, dtype=F32)
    if t == "float":
        number = float(value)
        _check_param_range(spec, name, number)
        return f32(number)
    if t in ("int", "enum", "member"):
        if isinstance(value, str):
            choices = spec.get("choices") or {}
            key = value.split(".")[-1]  # "oscType.sine" -> "sine"
            if value in choices:
                number = int(choices[value])
            elif key in choices:
                number = int(choices[key])
            else:
                try:
                    number = int(float(value))
                except ValueError:
                    return 0  # CDN member with no inline choices: defaults are the 0th member
        else:
            number = int(value)
        _check_param_range(spec, name, number)
        return number
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


_REMAP_BOUNDS_SLOT = 267


def _remap_uniform_data(u, width, height):
    """Pack synth/remap's std140 `data[275]` block from the bound uniforms —
    port of noisemaker-cpu renderer.js remapUniformData. At the default
    zoneCount=0 this yields the background color for every pixel."""

    def g(name, default):
        v = u.get(name)
        return default if v is None else v

    data = [np.zeros(4, dtype=F32) for _ in range(275)]
    bg = np.asarray(g("bgColor", [0, 0, 0]), dtype=F32)
    data[0] = np.array([bg[0], bg[1], bg[2], g("bgAlpha", 1)], dtype=F32)
    data[1] = np.array([g("zoneCount", 0), g("smoothEdge", 0.04), 0, g("time", 0)], dtype=F32)
    for zone in range(8):
        data[2 + zone] = np.array(
            [g(f"zone{zone}_count", 0), g(f"zone{zone}_active", 0), 0, g(f"zone{zone}_alpha", 1)], dtype=F32
        )
        for pair in range(32):
            data[10 + zone * 32 + pair] = np.asarray(g(f"zone{zone}_v{pair}", [0, 0, 0, 0]), dtype=F32)
        data[_REMAP_BOUNDS_SLOT + zone] = np.asarray(g(f"zone{zone}_bounds", [0, 0, 1, 1]), dtype=F32)
    data[266] = np.array([width, height, 0, 0], dtype=F32)
    return data


# Reactive (MIDI/audio) uniform defaults and mesh/external data-texture bindings.
# Port of noisemaker-cpu renderer.js bindExternalInputs (GAP-003 reactive/mesh
# import): mirrors the upstream pipeline's global-uniform stage
# (updateGlobalUniforms) — the 128-float audio arrays and the MIDI clock counter
# are bound only for the effects whose kernels declare them, zero-initialized
# when no external state is supplied, and the packed note grid uploads as a
# 128x16 RGBA data texture. Mesh textures (`global_mesh0_*`) bind from
# `external_inputs["meshData"]` — the same packed RGBA arrays the upstream
# `uploadMeshData` path feeds.
_REACTIVE_EFFECT_IDS = frozenset({"synth/roll", "synth/scope", "synth/spectrum"})
_MESH_TEX_WIDTH = 256
_MESH_TEX_HEIGHT = 256


def _bind_external_inputs(effect_id, eff, uniforms, attachments, external_inputs):
    external_inputs = external_inputs or {}
    pass_input_names = set()
    for render_pass in eff.get("passes") or []:
        for resource_name in (render_pass.get("inputs") or {}).values():
            pass_input_names.add(resource_name)
    if effect_id in _REACTIVE_EFFECT_IDS:
        midi_state = external_inputs.get("midiState")
        audio_state = external_inputs.get("audioState")
        uniforms["midiClockCount"] = midi_state.clock_count if midi_state else 0
        # GLSL uniform arrays are zero-initialized when the upstream pipeline has
        # no external state; the CPU kernels index them unconditionally, so
        # always bind 128-float arrays (zeros when no audio state is supplied).
        uniforms["audioWaveform"] = (
            audio_state.waveform if audio_state else np.zeros(128, dtype=np.float32)
        )
        uniforms["audioSpectrum"] = (
            audio_state.spectrum if audio_state else np.zeros(128, dtype=np.float32)
        )
        if "midiNoteGrid" in pass_input_names:
            grid = midi_state.note_grid if midi_state else np.zeros(128 * 16 * 4, dtype=np.float32)
            attachments["midiNoteGrid"] = external_data_surface(grid, 128, 16)
    mesh_names = [name for name in pass_input_names if name.startswith("global_mesh0_")]
    if mesh_names:
        mesh_data = external_inputs.get("meshData")
        if not mesh_data:
            raise ValueError(f"{effect_id} requires external mesh data (external_inputs['meshData'])")
        tex_width = mesh_data.get("texWidth") or _MESH_TEX_WIDTH
        tex_height = mesh_data.get("texHeight") or _MESH_TEX_HEIGHT
        if "global_mesh0_positions" in mesh_names:
            attachments["global_mesh0_positions"] = external_data_surface(mesh_data["positionData"], tex_width, tex_height)
        if "global_mesh0_normals" in mesh_names:
            attachments["global_mesh0_normals"] = external_data_surface(mesh_data["normalData"], tex_width, tex_height)
        if "global_mesh0_uvs" in mesh_names:
            attachments["global_mesh0_uvs"] = external_data_surface(mesh_data["uvData"], tex_width, tex_height)


def _round_half_up(value) -> int:
    # JS Math.round: half away from zero, not Python banker's rounding
    # (round(0.5) == 0 in Python but 1 in JS). Dimension specs must resolve
    # identically to the -cpu engine.
    return math.floor(value + 0.5)


def _size_component(spec, params, full_size, resources=None, axis="width"):
    if spec is None or (
        isinstance(spec, str) and spec in {"input", "screen", "auto", "resolution", "100%"}
    ):
        return full_size
    if isinstance(spec, (int, float)):
        return max(1, _round_half_up(spec))
    if isinstance(spec, str) and spec.endswith("%"):
        return max(1, _round_half_up(full_size * float(spec[:-1]) / 100))
    if isinstance(spec, dict):
        input_override = spec.get("inputOverride")
        if input_override and resources and resources.get(input_override) is not None:
            surface = resources[input_override]
            return surface.width if axis == "width" else surface.height
        if "param" in spec:
            # Mirrors noisemaker-for-cpu textureDimension's `{ param }` form:
            # multiply/power transforms apply to the param value (or its
            # paramDefault/default fallback, which bottoms out at 64); when a
            # transform is present and the param is absent, an explicit
            # `default` is used verbatim instead of the transformed value.
            has_transform = "power" in spec or "multiply" in spec
            param_default = spec.get("paramDefault", spec.get("default", 64))
            value = params.get(spec["param"], param_default)
            if "multiply" in spec:
                value *= spec["multiply"]
            if "power" in spec:
                value = float(value) ** spec["power"]
            if has_transform and spec["param"] not in params and "default" in spec:
                value = spec["default"]
            return max(1, _round_half_up(value))
        if "screenDivide" in spec:
            divisor = max(1, float(params.get(spec["screenDivide"], spec.get("default", 1))))
            return max(1, math.ceil(full_size / divisor))
        if "scale" in spec:
            computed = math.floor(full_size * spec["scale"])
            clamp = spec.get("clamp")
            if clamp:
                if "min" in clamp:
                    computed = max(clamp["min"], computed)
                if "max" in clamp:
                    computed = min(clamp["max"], computed)
            return max(1, computed)
    return full_size


def _texture_dimensions(texture_spec, params, width, height, resources=None):
    texture_spec = texture_spec or {}
    # `w`/`h` are aliases of `width`/`height` (noisemaker-for-cpu canonicalDestination).
    return (
        _size_component(texture_spec.get("w", texture_spec.get("width")), params, width, resources, "width"),
        _size_component(texture_spec.get("h", texture_spec.get("height")), params, height, resources, "height"),
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
    external_inputs=None,
    validate_implicit_seed=True,
) -> Surface:
    params = params or {}
    inputs = inputs or {}
    eff = _meta()["effects"][effect_id]
    domain = eff.get("domain", "image")
    # `osc()` automation values resolve to concrete numbers against this render's
    # normalized time (renderer.js effectParams); raw_params keeps the pre-resolution
    # view so coercion knows which params bypass the declared-range check.
    raw_params = params
    params = _resolve_effect_automation(eff, raw_params, time)
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
            # The CLI/effect-command path validates the threaded seed against
            # the declared range; the DSL's implicit threading (validate_implicit_seed
            # False) matches runtime/renderer.js, which spreads the render seed
            # into step params without a range check.
            val = _coerce(spec, seed, pname if validate_implicit_seed else None)
        else:
            val = _coerce(
                spec,
                params.get(pname),
                None if _is_automation_value(raw_params.get(pname)) else pname,
            )
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
            idx = _coerce(eff["params"][pal], params.get(pal), pal)
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
                            _coerce(gp, seed, pn if validate_implicit_seed else None)
                            if pn == "seed" and "seed" not in params
                            else _coerce(
                                gp,
                                params.get(pn),
                                None if _is_automation_value(raw_params.get(pn)) else pn,
                            )
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

    # Reactive uniform defaults and mesh/note-grid data-texture bindings (see
    # _bind_external_inputs). Bound like the JS buildBindings externalInputs stage,
    # after canonical resources initialize and before any pass runs.
    _bind_external_inputs(effect_id, eff, uniforms, attachments, external_inputs)

    for p in eff["passes"]:
        # Pass-level uniform aliases: the definition may expose a param under one
        # name (e.g. `color`) while this pass's GLSL declares another (`splatColor`).
        pass_uniforms = dict(uniforms)
        for glsl_name, param_name in (p.get("uniforms") or {}).items():
            if not isinstance(param_name, str):
                # A literal pass-level uniform override (e.g. depthMerge's per-clone
                # `runLength`, pointsBillboardRender deposit's `blurLayer`) -- not a
                # reference to another param name, use the value as-is.
                pass_uniforms[glsl_name] = param_name
            elif param_name in effect_uniforms:
                pass_uniforms[glsl_name] = effect_uniforms[param_name]
            elif param_name in uniforms:
                pass_uniforms[glsl_name] = uniforms[param_name]
        # Pass-level defines (e.g. VIEW_MODE/BLEND_MODE/BLUR_LAYER on a
        # `.flatMap()`-cloned pass): bind this clone's literal value as if it
        # were an ordinary uniform, matching how build.py's runtime_defines
        # lowered the identifier to a `uniform int NAME` runtime branch.
        pass_uniforms.update(p.get("defines") or {})
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
            mesh_op = get_mesh_op(effect_id, p["program"]) if p.get("drawMode") == "triangles" else None
            draw_op = mesh_op or (get_draw_op(effect_id, p["program"]) if p.get("drawMode") else None)
            produced = []
            if mesh_op is not None:
                destination = Surface(pass_width, pass_height)
                prior = attachments.get(out_names[0]) if out_names else None
                if prior is not None and prior.data.shape == destination.data.shape:
                    destination.data[:] = prior.data
                mesh_op(textures, destination, pass_uniforms, p, external_inputs=external_inputs)
                produced = [destination]
            elif draw_op is not None:
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


def render_effect(
    effect_id, params=None, inputs=None, width=256, height=256, seed=1, time=0.0, external_inputs=None,
    *, validate_implicit_seed=True,
):
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
        return _render_effect_once(
            effect_id, params, inputs, width, height, seed, time, external_inputs=external_inputs,
            validate_implicit_seed=validate_implicit_seed,
        )

    # Pass-repeat rule (see _run_iterated_group): when any pass of the definition
    # carries a `repeat`, the iteration loop is inert above 0 and the per-frame
    # multiplier is the pass repeat resolved from its uniform.
    # JS derives the group's iteration count (and the zero-iteration sizing below)
    # from the init-time effectParams resolution at the render's normalized time;
    # per-iteration re-resolution happens inside _render_effect_once against each
    # tick's own rewound time.
    init_params = _resolve_effect_automation(effect, params, time)
    iteration_spec = effect["params"]["iterationCount"]
    iteration_count = _coerce(
        iteration_spec,
        init_params.get("iterationCount"),
        None if _is_automation_value(params.get("iterationCount")) else "iterationCount",
    )
    if _oracle_pass_repeat_clamp() and any(p.get("repeat") for p in effect.get("passes", [])):
        iteration_count = min(iteration_count, 1)
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
            param_values = {
                name: _coerce(
                    spec,
                    init_params.get(name),
                    None if _is_automation_value(params.get(name)) else name,
                )
                for name, spec in effect["params"].items()
            }
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
            validate_implicit_seed=validate_implicit_seed,
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


def _run_effect_step(step, current, surfaces, external_textures, width, height, seed, time, external_inputs=None):
    inputs = _effect_step_inputs(step, current, surfaces, external_textures)
    effect = _meta()["effects"][step["effect_id"]]
    params = _inherit_volume_size(effect, step["params"], _chain_bundle(current))
    # The DSL's implicit render-seed threading is unvalidated, matching
    # runtime/renderer.js (explicit DSL assignments still go through the range
    # check inside render_effect).
    return render_effect(
        step["effect_id"], params, inputs, width=width, height=height, seed=seed, time=time,
        external_inputs=external_inputs, validate_implicit_seed=False,
    )


def _run_iterated_group(group, current, surfaces, external_textures, effects, width, height, seed, time, external_inputs=None):
    first_step = group["steps"][0]
    first_effect = effects[first_step["effect_id"]]
    # Upstream (shaders/src/runtime/pipeline.js render()) executes each pass exactly
    # resolveRepeatCount(pass) times per frame — there is no group-level multiplier.
    # For effects whose passes carry a `repeat` (synth/reactionDiffusion,
    # synth/navierStokes, synth3d/reactionDiffusion3d) the pass repeat IS the
    # per-frame iteration count, so the group loop must not multiply it again; the
    # documented iterationCount:0 bypass (zero passes run) is still honored. All
    # other iterated effects keep the established `iterationCount` group loop
    # (filter/temporalAberration requires N=60).
    # JS derives the group's iteration count and owner stateSize from the owner
    # step's init-time effectParams resolution (render-level time); per-iteration
    # re-resolution happens inside _render_effect_once against each tick's time.
    first_init_params = _resolve_effect_automation(first_effect, first_step["params"], time)
    iteration_spec = first_effect["params"]["iterationCount"]
    iteration_count = _coerce(
        iteration_spec,
        first_init_params.get("iterationCount"),
        None if _is_automation_value(first_step["params"].get("iterationCount")) else "iterationCount",
    )
    if _oracle_pass_repeat_clamp() and any(p.get("repeat") for p in first_effect.get("passes", [])):
        iteration_count = min(iteration_count, 1)
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
        state_size = _coerce(
            first_effect["params"]["stateSize"],
            first_init_params.get("stateSize"),
            None if _is_automation_value(first_step["params"].get("stateSize")) else "stateSize",
        )

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
                validate_implicit_seed=False,
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


def render_dsl(source, width=512, height=512, seed=1, time=0.0, external_textures=None, seed_surfaces=None, external_inputs=None) -> Surface:
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
                    external_inputs,
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
                    current = _run_effect_step(step, current, surfaces, external_textures, width, height, seed, time, external_inputs)
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

    def should_defer_render(self) -> bool:
        return self.sink_manager.should_defer_render()

    shouldDeferRender = should_defer_render

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
        external_inputs=None,
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
            external_inputs=external_inputs,
        )
        timestamp = presentation_timestamp if presentation_timestamp is not None else _clock.perf_counter() * 1000
        self.sink_manager.submit(result, timestamp)
        return result

    def dispose(self) -> None:
        self.sink_manager.close()
