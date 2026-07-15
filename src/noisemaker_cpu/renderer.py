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
from .pass_runner import Ctx, run_pass
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


def render_effect(effect_id, params=None, inputs=None, width=256, height=256, seed=1, time=0.0) -> Surface:
    params = params or {}
    inputs = inputs or {}
    eff = _meta()["effects"][effect_id]

    uniforms = {}
    for pname, spec in eff["params"].items():
        uni = spec.get("uniform")
        if uni is not None:
            uniforms[uni] = _coerce(spec, params.get(pname))
    # Common bindings used by canonical shaders (harmless if the shader ignores them).
    uniforms.setdefault("time", f32(time))
    uniforms.setdefault("seed", int(seed))
    uniforms.setdefault("resolution", np.array([float(width), float(height)], dtype=F32))

    rt = Runtime()
    result = None
    for p in eff["passes"]:
        textures = {}
        for uni_name, source in (p.get("inputs") or {}).items():
            surf = inputs.get(source) or inputs.get(uni_name) or result
            if surf is not None:
                surf.filter = "linear"  # external image inputs sample linear
                textures[uni_name] = surf
        ctx = Ctx(
            rt,
            uniforms=dict(uniforms),
            textures=textures,
            resolution=np.array([float(width), float(height)], dtype=F32),
            time=time,
            seed=seed,
        )
        kernel = _kernel_for(p["key"])
        result = run_pass(kernel, ctx, width, height)
    return result
