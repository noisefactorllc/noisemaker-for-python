"""Render a bundled effect: load metadata + transpiled kernel, run the pass(es).

P0 supports single-pass generators (solid) and single-input filters (invert).
The multi-pass render graph (named attachments, half-float quantization, blend,
drawMode) is P1.
"""

from __future__ import annotations

import json
import os

import numpy as np

from .kernel_loader import KernelCache
from .pass_runner import Ctx, run_pass, run_pass_deriv
from .runtime import F32, Runtime, f32
from .adapters import get_adapter
from .adapters._palette_data import PALETTE_DATA
from .draw_ops import get_draw_op
from .overlay_gen import OVERLAY_EFFECTS, render_worm_overlay
from .surface import Surface
from .texture_format import quantize_texture

_META = None
_CACHE = KernelCache()


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
    if t in ("vec2", "vec3", "vec4"):
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


def _canonical_uniforms(width, height, time, seed, effect_uniforms):
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
    u.update({  # canonical values always win
        "resolution": res,
        "fullResolution": res,
        "tileOffset": np.zeros(2, dtype=F32),
        "aspectRatio": aspect,
        "aspect": aspect,
        "time": f32(time),
        "globalTime": f32(time),
        "deltaTime": 0,
    })
    return u


def render_effect(effect_id, params=None, inputs=None, width=256, height=256, seed=1, time=0.0) -> Surface:
    params = params or {}
    inputs = inputs or {}
    eff = _meta()["effects"][effect_id]

    effect_uniforms = {}
    surface_params = {}  # sampler-name -> provided Surface (or None)
    for pname, spec in eff["params"].items():
        if spec.get("type") == "surface":
            sampler = spec.get("uniform") or spec.get("texture") or pname
            surface_params[sampler] = inputs.get(sampler) or inputs.get(pname)
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
        if spec.get("uniform") is not None:
            effect_uniforms[spec["uniform"]] = val
        if spec.get("define") is not None:
            effect_uniforms[spec["define"]] = val

    # classicNoisedeck palette presets: a `palette`-type param > 0 selects
    # cosine-palette coefficients from the shared table, overriding the
    # paletteAmp/Freq/Offset/Phase/Mode uniforms (reference renderer.js).
    if eff.get("namespace") == "classicNoisedeck":
        pal = next((pn for pn, sp in eff["params"].items()
                    if isinstance(sp, dict) and sp.get("type") == "palette"), None)
        if pal is not None:
            idx = _coerce(eff["params"][pal], params.get(pal))
            if isinstance(idx, int) and 0 < idx <= len(PALETTE_DATA):
                e = PALETTE_DATA[idx - 1]
                effect_uniforms["paletteAmp"] = np.array(e[0:3], dtype=F32)
                effect_uniforms["paletteFreq"] = np.array(e[4:7], dtype=F32)
                effect_uniforms["paletteOffset"] = np.array(e[8:11], dtype=F32)
                effect_uniforms["palettePhase"] = np.array(e[12:15], dtype=F32)
                effect_uniforms["paletteMode"] = 3 if e[3] == 0 else int(e[3])

    uniforms = _canonical_uniforms(width, height, time, seed, effect_uniforms)
    blank = Surface(1, 1)

    rt = Runtime()
    result = None
    attachments = {}  # attach-name -> Surface produced by an earlier pass this render

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
                        gen[pn] = _coerce(gp, seed) if pn == "seed" and "seed" not in params else _coerce(gp, params.get(pn))
                attachments[tname] = render_worm_overlay(effect_id, width, height, gen)

    for p in eff["passes"]:
        textures = _DefaultTex(blank)
        for sampler, surf in surface_params.items():
            if surf is not None:
                surf.filter = "linear"
                textures[sampler] = surf
        for sampler_name, source in (p.get("inputs") or {}).items():
            # An earlier pass's named attachment wins over a same-named external
            # input (e.g. `inputTex` reused as an intermediate attach name).
            surf = attachments.get(source) or inputs.get(source) or inputs.get(sampler_name) or result
            if surf is not None:
                surf.filter = "linear"
                textures[sampler_name] = surf
        # Pass-level uniform aliases: the definition may expose a param under one
        # name (e.g. `color`) while this pass's GLSL declares another (`splatColor`).
        pass_uniforms = dict(uniforms)
        for glsl_name, param_name in (p.get("uniforms") or {}).items():
            if param_name in effect_uniforms:
                pass_uniforms[glsl_name] = effect_uniforms[param_name]
            elif param_name in uniforms:
                pass_uniforms[glsl_name] = uniforms[param_name]
        out_names = list((p.get("outputs") or {}).values())
        fmt = eff.get("textures", {}).get(out_names[0], {}).get("format", "rgba16f") if out_names else "rgba16f"
        draw_op = get_draw_op(effect_id, p["program"]) if p.get("drawMode") else None
        if draw_op is not None:
            # CPU-only draw op (e.g. point-scatter). A fresh destination seeds
            # from the prior same-name attachment (accumulator) or clears, then
            # the op writes into it.
            src = textures.get(list((p.get("inputs") or {}).values() or ["inputTex"])[0]) or textures["inputTex"]
            result = Surface(width, height)
            prev = attachments.get(out_names[0]) if out_names else None
            if prev is not None and prev.data.shape == result.data.shape:
                result.data[:] = prev.data
            draw_op(src, result, pass_uniforms)
        else:
            ctx = Ctx(
                rt,
                uniforms=pass_uniforms,
                textures=textures,
                resolution=np.array([float(width), float(height)], dtype=F32),
                time=time,
                seed=seed,
            )
            kernel = _kernel_for(p["key"])
            adapter = get_adapter(effect_id, p["program"])
            if adapter is not None:
                kernel = adapter(rt, kernel)
            runner = run_pass_deriv if getattr(kernel, "uses_derivatives", False) else run_pass
            result = runner(kernel, ctx, width, height)
        # Quantize the pass output to its declared texture format (rgba16f half
        # by default), matching the reference engine's per-pass FBO storage.
        quantize_texture(result, fmt)
        for attach_name in out_names:
            attachments[attach_name] = result
    return result
