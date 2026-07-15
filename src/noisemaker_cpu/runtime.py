"""CSL/GLSL CPU runtime — the vector-math core that transpiled kernels call.

Faithful port of the semantics in noisemaker-cpu `src/csl/runtime.js` /
`glsl-runtime.js`: scalars are Python floats (float32-rounded), vectors are
1-D ``numpy.float32`` arrays, and every arithmetic result is re-rounded to
float32 to emulate GPU register precision (JS ``Math.fround``).

The emitted kernel accesses this instance as ``ctx.rt``. This module implements
the subset needed by the P0 effects (solid, invert) plus the structural hooks
(``binary``/``unary``/``component_wise``) that later effects extend.
"""

from __future__ import annotations

import numpy as np

F32 = np.float32


def f32(x) -> float:
    """Round a Python/np scalar to float32 (matches JS Math.fround)."""
    return float(np.float32(x))


_SWIZZLE = {"x": 0, "y": 1, "z": 2, "w": 3, "r": 0, "g": 1, "b": 2, "a": 3, "s": 0, "t": 1, "p": 2, "q": 3}


def _is_scalar(v) -> bool:
    return isinstance(v, (int, float, np.floating, np.integer, bool))


class Runtime:
    def __init__(self):
        self._ctx = None

    def begin_pixel(self, ctx=None):
        self._ctx = ctx

    @staticmethod
    def f32(x) -> float:
        return f32(x)

    # ---- literals ----
    @staticmethod
    def f(x) -> float:  # float literal
        return f32(x)

    @staticmethod
    def i(x) -> int:  # int literal
        return int(x)

    # ---- construction ----
    def construct(self, width: int, *comps):
        """Build a vecN (width>1) or scalar (width==1) from scalars/vectors.

        One scalar arg splats. Otherwise components are flattened in order and
        truncated/consumed to exactly `width` components.
        """
        supplied = [c for c in comps if c is not None]
        if width == 1:
            c = supplied[0]
            return f32(c if _is_scalar(c) else np.asarray(c, dtype=F32).ravel()[0])
        if len(supplied) == 1 and _is_scalar(supplied[0]):
            return np.full(width, F32(supplied[0]), dtype=F32)
        vals: list = []
        for c in supplied:
            if _is_scalar(c):
                vals.append(F32(c))
            else:
                vals.extend(np.asarray(c, dtype=F32).ravel().tolist())
        arr = np.array(vals[:width], dtype=F32)
        if arr.shape[0] < width:  # pad by repeating last (defensive; valid GLSL won't hit this)
            arr = np.concatenate([arr, np.full(width - arr.shape[0], arr[-1], dtype=F32)])
        return arr

    def copy(self, vec, width=None):
        if _is_scalar(vec):
            return f32(vec)
        return np.array(vec, dtype=F32)

    # ---- swizzles ----
    def swizzle(self, vec, sw: str):
        idx = [_SWIZZLE[c] for c in sw]
        v = np.asarray(vec, dtype=F32)
        if len(idx) == 1:
            return float(v[idx[0]])
        return v[idx].astype(F32)

    def assign_swizzle(self, vec, sw: str, value):
        idx = [_SWIZZLE[c] for c in sw]
        v = np.asarray(vec, dtype=F32)
        if _is_scalar(value):
            for j in idx:
                v[j] = F32(value)
        else:
            val = np.asarray(value, dtype=F32).ravel()
            for k, j in enumerate(idx):
                v[j] = F32(val[k])
        return vec

    # ---- operators ----
    def binary(self, op, a, b, width=None):
        if op in ("==", "!=", "<", ">", "<=", ">=", "&&", "||"):
            return self._logical(op, a, b)
        av = a if _is_scalar(a) else np.asarray(a, dtype=F32)
        bv = b if _is_scalar(b) else np.asarray(b, dtype=F32)
        if op == "+":
            r = np.add(av, bv)
        elif op == "-":
            r = np.subtract(av, bv)
        elif op == "*":
            r = np.multiply(av, bv)
        elif op == "/":
            r = np.divide(av, bv)
        else:
            raise ValueError(f"unsupported binary op {op!r}")
        if _is_scalar(av) and _is_scalar(bv):
            return f32(r)
        return np.asarray(r, dtype=F32)

    @staticmethod
    def _logical(op, a, b):
        av = float(a) if _is_scalar(a) else np.asarray(a)
        bv = float(b) if _is_scalar(b) else np.asarray(b)
        if op == "==":
            return bool(np.all(av == bv))
        if op == "!=":
            return bool(np.any(av != bv))
        if op == "<":
            return bool(av < bv)
        if op == ">":
            return bool(av > bv)
        if op == "<=":
            return bool(av <= bv)
        if op == ">=":
            return bool(av >= bv)
        if op == "&&":
            return bool(av) and bool(bv)
        if op == "||":
            return bool(av) or bool(bv)
        raise ValueError(op)

    def unary(self, op, a, width=None):
        if op == "-":
            return f32(-a) if _is_scalar(a) else np.asarray(-np.asarray(a, dtype=F32), dtype=F32)
        if op == "!":
            return not bool(a)
        if op == "+":
            return a
        raise ValueError(f"unsupported unary op {op!r}")

    # ---- component-wise builtins ----
    def component_wise(self, name, *args, width=None):
        arrs = [a if _is_scalar(a) else np.asarray(a, dtype=F32) for a in args]
        fn = _COMPONENT.get(name)
        if fn is None:
            raise ValueError(f"unsupported builtin {name!r}")
        r = fn(*arrs)
        if all(_is_scalar(a) for a in args):
            return f32(r)
        return np.asarray(r, dtype=F32)

    # ---- texture ----
    def texture(self, sampler, uv):
        from .sampler import sample_bilinear, sample_nearest_bottom_left

        u = float(uv[0])
        v = float(uv[1])
        if getattr(sampler, "filter", "nearest") == "linear":
            return sample_bilinear(sampler, u, v)
        return sample_nearest_bottom_left(sampler, u, v)

    def texture_size(self, sampler):
        return np.array([sampler.width, sampler.height], dtype=F32)


def _clamp(x, lo, hi):
    return np.minimum(np.maximum(x, lo), hi)


def _mix(a, b, t):
    return a * (1.0 - t) + b * t


_COMPONENT = {
    "abs": np.abs,
    "floor": np.floor,
    "ceil": np.ceil,
    "fract": lambda x: x - np.floor(x),
    "sign": np.sign,
    "sqrt": np.sqrt,
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "exp": np.exp,
    "log": np.log,
    "min": np.minimum,
    "max": np.maximum,
    "pow": np.power,
    "clamp": _clamp,
    "mix": _mix,
    "step": lambda edge, x: np.where(x < edge, 0.0, 1.0),
    "mod": lambda x, y: x - y * np.floor(x / y),
}
