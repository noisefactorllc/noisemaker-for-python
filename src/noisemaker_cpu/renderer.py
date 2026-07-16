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
from .surface import Surface

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
    if t in ("int", "enum"):
        if isinstance(value, str):
            choices = spec.get("choices") or {}
            if value in choices:
                return int(choices[value])
            return int(float(value))
        return int(value)
    if t == "bool":
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
        val = _coerce(spec, params.get(pname))
        if spec.get("uniform") is not None:
            effect_uniforms[spec["uniform"]] = val
        if spec.get("define") is not None:
            effect_uniforms[spec["define"]] = val

    uniforms = _canonical_uniforms(width, height, time, seed, effect_uniforms)
    blank = Surface(1, 1)

    rt = Runtime()
    result = None
    for p in eff["passes"]:
        textures = _DefaultTex(blank)
        for sampler, surf in surface_params.items():
            if surf is not None:
                surf.filter = "linear"
                textures[sampler] = surf
        for sampler_name, source in (p.get("inputs") or {}).items():
            surf = inputs.get(source) or inputs.get(sampler_name) or result
            if surf is not None:
                surf.filter = "linear"
                textures[sampler_name] = surf
        ctx = Ctx(
            rt,
            uniforms=dict(uniforms),
            textures=textures,
            resolution=np.array([float(width), float(height)], dtype=F32),
            time=time,
            seed=seed,
        )
        kernel = _kernel_for(p["key"])
        runner = run_pass_deriv if getattr(kernel, "uses_derivatives", False) else run_pass
        result = runner(kernel, ctx, width, height)
    return result
