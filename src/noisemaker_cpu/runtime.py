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

from . import uintmath

F32 = np.float32
_U32 = 0xFFFFFFFF


def f32(x) -> float:
    """Round a Python/np scalar to float32 (matches JS Math.fround)."""
    return float(np.float32(x))


def _s32(x) -> int:
    """Wrap a Python int to signed 32-bit (GLSL int overflow semantics)."""
    return ((int(x) + 0x80000000) & _U32) - 0x80000000


_SWIZZLE = {"x": 0, "y": 1, "z": 2, "w": 3, "r": 0, "g": 1, "b": 2, "a": 3, "s": 0, "t": 1, "p": 2, "q": 3}


def _is_scalar(v) -> bool:
    return isinstance(v, (int, float, np.floating, np.integer, bool))


class Runtime:
    def __init__(self):
        self._ctx = None
        self._deriv_mode = None      # None | "record" | "replay"
        self._deriv_log = []         # record: list of (op, value)
        self._deriv_diffs = None     # replay: precomputed diff per call index
        self._deriv_i = 0

    def begin_pixel(self, ctx=None):
        self._ctx = ctx

    # ---- screen-space derivatives (2x2-quad record/replay) ----
    def deriv_reset(self, mode, diffs=None):
        self._deriv_mode = mode
        self._deriv_i = 0
        self._deriv_log = []
        self._deriv_diffs = diffs

    def _deriv(self, op, v):
        if self._deriv_mode == "record":
            self._deriv_log.append((op, float(v) if _is_scalar(v) else np.array(v, dtype=F32)))
            self._deriv_i += 1
            return 0.0 if _is_scalar(v) else np.zeros(np.asarray(v).shape[0], dtype=F32)
        if self._deriv_mode == "replay":
            d = self._deriv_diffs[self._deriv_i] if self._deriv_i < len(self._deriv_diffs) else (0.0 if _is_scalar(v) else np.zeros(np.asarray(v).shape[0], dtype=F32))
            self._deriv_i += 1
            return d
        return 0.0 if _is_scalar(v) else np.zeros(np.asarray(v).shape[0], dtype=F32)

    def dFdx(self, v):
        return self._deriv("dFdx", v)

    def dFdy(self, v):
        return self._deriv("dFdy", v)

    def fwidth(self, v):
        return self._deriv("fwidth", v)

    def deriv_compute(self, recs):
        tl, tr, bl = recs[0], recs[1], recs[2]

        def val(rec, i):
            return rec[i][1] if i < len(rec) else tl[i][1]

        diffs = []
        for i in range(len(tl)):
            op = tl[i][0]
            a = np.asarray(tl[i][1], dtype=np.float64)
            dx = np.asarray(val(tr, i), dtype=np.float64) - a
            dy = np.asarray(val(bl, i), dtype=np.float64) - a
            if op == "dFdx":
                r = dx
            elif op == "dFdy":
                r = dy
            else:  # fwidth
                r = np.abs(dx) + np.abs(dy)
            diffs.append(f32(float(r)) if r.ndim == 0 else np.asarray(r, dtype=F32))
        return diffs

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
    def construct(self, width: int, *comps, base="float"):
        """Build a vecN (width>1) or scalar (width==1) from scalars/vectors.

        One scalar arg splats. Otherwise components are flattened in order and
        truncated/consumed to exactly `width` components. `base` int/uint builds
        an integer array (values kept exact, not float32-rounded).
        """
        supplied = [c for c in comps if c is not None]
        if base in ("int", "uint"):
            if len(supplied) == 1 and _is_scalar(supplied[0]) and width > 1:
                iv = int(supplied[0])
                iv = (iv & _U32) if base == "uint" else _s32(iv)
                return np.full(width, iv, dtype=np.int64)
            ivals = []
            for c in supplied:
                if _is_scalar(c):
                    ivals.append(int(c))
                else:
                    ivals.extend(int(x) for x in np.asarray(c).ravel())
            ivals = [(v & _U32) if base == "uint" else _s32(v) for v in ivals]
            return ivals[0] if width == 1 else np.array(ivals[:width], dtype=np.int64)
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
        v = np.asarray(vec)  # preserve dtype (int vectors must stay integer)
        if len(idx) == 1:
            return int(v[idx[0]]) if np.issubdtype(v.dtype, np.integer) else float(v[idx[0]])
        return v[idx]

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
    def binary(self, op, a, b, width=None, base="float"):
        if op in ("==", "!=", "<", ">", "<=", ">=", "&&", "||"):
            return self._logical(op, a, b)
        if base in ("int", "uint") or op in ("&", "|", "^", "<<", ">>"):
            return self._int_binary(op, a, b, "uint" if base == "uint" else "int")
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
        elif op == "%":
            r = np.fmod(av, bv)
        else:
            raise ValueError(f"unsupported binary op {op!r}")
        if _is_scalar(av) and _is_scalar(bv):
            return f32(r)
        return np.asarray(r, dtype=F32)

    def _int_binary(self, op, a, b, base):
        if _is_scalar(a) and _is_scalar(b):
            return _int_scalar(op, int(a), int(b), base)
        # element-wise: uint uses uint64 (mul wraps mod 2^64 -> mask mod 2^32)
        dt = np.uint64 if base == "uint" else np.int64
        av = (np.asarray(a).astype(np.int64) & _U32).astype(dt) if base == "uint" else np.asarray(a).astype(np.int64)
        bv = (np.asarray(b).astype(np.int64) & _U32).astype(dt) if base == "uint" else np.asarray(b).astype(np.int64)
        r = _int_vec(op, av, bv, base)
        return np.asarray(r, dtype=np.int64)

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
        if name == "atan" and len(args) == 2:  # atan(y, x) -> atan2
            r = np.arctan2(np.asarray(args[0], dtype=np.float64), np.asarray(args[1], dtype=np.float64))
            return f32(float(r)) if all(_is_scalar(a) for a in args) else np.asarray(r, dtype=F32)
        if name in _RELATIONAL:  # lessThan/equal/... -> bvec
            return _RELATIONAL[name](np.asarray(args[0], dtype=F32), np.asarray(args[1], dtype=F32))
        if name == "any":
            return bool(np.any(np.asarray(args[0])))
        if name == "all":
            return bool(np.all(np.asarray(args[0])))
        if name == "not":
            return np.logical_not(np.asarray(args[0]))
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

    def texel_fetch(self, sampler, coord, lod=0):
        w, h = sampler.width, sampler.height
        x = min(max(int(coord[0]), 0), w - 1)
        # GL bottom-left origin -> top-down storage row flip (integer texel).
        ty = min(max(h - 1 - int(coord[1]), 0), h - 1)
        i = (ty * w + x) * 4
        d = sampler.data
        return np.array([d[i], d[i + 1], d[i + 2], d[i + 3]], dtype=F32)

    # ---- uint32 / half-float primitives (delegate to bit-exact uintmath) ----
    def pcg3d(self, v):
        arr = np.asarray(v).astype(np.int64)
        r = uintmath.pcg3d([int(arr[0]) & _U32, int(arr[1]) & _U32, int(arr[2]) & _U32])
        return np.asarray(r, dtype=np.int64)

    def hash_uint(self, x):
        return uintmath.hash_uint32(int(x) & _U32)

    def float_bits_to_uint(self, f):
        return uintmath.float_bits_to_uint(float(f))

    def uint_bits_to_float(self, u):
        return f32(uintmath.uint_bits_to_float(int(u) & _U32))

    def pack_half_2x16(self, v):
        return uintmath.pack_half_2x16([float(v[0]), float(v[1])])

    def unpack_half_2x16(self, u):
        return np.asarray(uintmath.unpack_half_2x16(int(u) & _U32), dtype=F32)

    def to_int(self, x):
        if _is_scalar(x):
            return _s32(int(x))  # GLSL int(float) truncates toward zero, then wraps
        return np.asarray(x).astype(np.int64)

    def to_uint(self, x):
        if _is_scalar(x):
            return int(x) & _U32
        return np.asarray(x).astype(np.int64) & _U32

    # ---- vector geometry (accumulate float64, round to float32 once) ----
    def dot(self, a, b, width=None):
        return f32(float(np.dot(np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64))))

    def length(self, a, width=None):
        v = np.asarray(a, dtype=np.float64)
        return f32(float(np.sqrt(np.dot(v, v))))

    def distance(self, a, b, width=None):
        d = np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)
        return f32(float(np.sqrt(np.dot(d, d))))

    def normalize(self, a, width=None):
        v = np.asarray(a, dtype=np.float64)
        mag = np.sqrt(np.dot(v, v))
        if mag == 0.0:
            return np.zeros(v.shape[0], dtype=F32)
        return (v / mag).astype(F32)

    def cross(self, a, b):
        return np.cross(np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)).astype(F32)

    def reflect(self, i, n):
        iv = np.asarray(i, dtype=np.float64)
        nv = np.asarray(n, dtype=np.float64)
        return (iv - 2.0 * np.dot(nv, iv) * nv).astype(F32)

    def refract(self, i, n, eta):
        iv = np.asarray(i, dtype=np.float64)
        nv = np.asarray(n, dtype=np.float64)
        e = float(eta)
        d = np.dot(nv, iv)
        k = 1.0 - e * e * (1.0 - d * d)
        if k < 0.0:
            return np.zeros(iv.shape[0], dtype=F32)
        return (e * iv - (e * d + np.sqrt(k)) * nv).astype(F32)

    # ---- matrices (flat, column-major: element [col*N + row]) ----
    def matrix_mult(self, a, b, dim):
        n = int(dim)
        av = np.asarray(a, dtype=np.float64)
        bv = np.asarray(b, dtype=np.float64)
        a_mat = av.size == n * n
        b_mat = bv.size == n * n
        if a_mat and b_mat:  # GLSL A*B, both column-major -> (Bcm @ Acm)
            r = (bv.reshape(n, n) @ av.reshape(n, n)).ravel()
        elif a_mat:  # mat * vec
            r = bv @ av.reshape(n, n)
        else:  # vec * mat
            r = bv.reshape(n, n) @ av
        return np.asarray(r, dtype=F32)

    def mat_col(self, mat, i, dim):
        n = int(dim)
        c = int(i)
        return np.asarray(mat, dtype=F32)[c * n:(c + 1) * n].astype(F32)

    # ---- arrays (GLSL fixed-size arrays -> Python lists) ----
    @staticmethod
    def new_array(n, width=1):
        n = int(n)
        if width <= 1:
            return [0.0] * n
        return [np.zeros(int(width), dtype=F32) for _ in range(n)]

    @staticmethod
    def array(elems):
        return list(elems)

    def bit_not(self, x):
        if _is_scalar(x):
            return _s32(~int(x))
        return (~np.asarray(x).astype(np.int64))


def _s32arr(x):
    return (((x.astype(np.int64) + 0x80000000) & _U32) - 0x80000000).astype(np.int64)


def _int_scalar(op, a, b, base):
    if base == "uint":
        a &= _U32
        b &= _U32
        table = {
            "+": uintmath.uadd, "-": uintmath.usub, "*": uintmath.umul,
            "&": uintmath.uand, "|": uintmath.uor, "^": uintmath.uxor,
            "<<": uintmath.ushl, ">>": uintmath.ushr,
            "/": lambda x, y: (x // y) if y else 0,
            "%": lambda x, y: (x % y) if y else 0,
        }
        return table[op](a, b)
    if op == "+":
        return _s32(a + b)
    if op == "-":
        return _s32(a - b)
    if op == "*":
        return _s32(a * b)
    if op == "&":
        return _s32(a & b)
    if op == "|":
        return _s32(a | b)
    if op == "^":
        return _s32(a ^ b)
    if op == "<<":
        return _s32(a << (b & 31))
    if op == ">>":
        return a >> (b & 31)
    if op == "/":
        return _s32(int(a / b)) if b else 0
    if op == "%":
        return _s32(a - b * int(a / b)) if b else 0
    raise ValueError(f"unsupported int op {op!r}")


def _int_vec(op, av, bv, base):
    if base == "uint":
        m = np.uint64(_U32)
        if op == "+":
            return (av + bv) & m
        if op == "-":
            return (av - bv) & m
        if op == "*":
            return (av * bv) & m
        if op == "&":
            return av & bv
        if op == "|":
            return av | bv
        if op == "^":
            return av ^ bv
        if op == "<<":
            return (av << (bv & np.uint64(31))) & m
        if op == ">>":
            return av >> (bv & np.uint64(31))
        if op == "/":
            return np.where(bv == 0, 0, av // np.maximum(bv, np.uint64(1)))
        if op == "%":
            return np.where(bv == 0, 0, av % np.maximum(bv, np.uint64(1)))
        raise ValueError(f"unsupported uint op {op!r}")
    if op == "+":
        return _s32arr(av + bv)
    if op == "-":
        return _s32arr(av - bv)
    if op == "*":
        return _s32arr(av * bv)
    if op == "&":
        return av & bv
    if op == "|":
        return av | bv
    if op == "^":
        return av ^ bv
    if op == "<<":
        return _s32arr(av << (bv & 31))
    if op == ">>":
        return av >> (bv & 31)
    if op in ("/", "%"):
        safe = np.where(bv == 0, 1, bv)
        q = np.trunc(av / safe).astype(np.int64)
        return np.where(bv == 0, 0, q if op == "/" else av - bv * q)
    raise ValueError(f"unsupported int op {op!r}")


def _clamp(x, lo, hi):
    return np.minimum(np.maximum(x, lo), hi)


def _mix(a, b, t):
    return a * (1.0 - t) + b * t


def _smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


_PI = 3.141592653589793

_RELATIONAL = {
    "lessThan": np.less,
    "lessThanEqual": np.less_equal,
    "greaterThan": np.greater,
    "greaterThanEqual": np.greater_equal,
    "equal": np.equal,
    "notEqual": np.not_equal,
}

_COMPONENT = {
    "abs": np.abs,
    "floor": np.floor,
    "ceil": np.ceil,
    "fract": lambda x: x - np.floor(x),
    "sign": np.sign,
    "sqrt": np.sqrt,
    "inversesqrt": lambda x: 1.0 / np.sqrt(x),
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "asin": np.arcsin,
    "acos": np.arccos,
    "atan": np.arctan,
    "sinh": np.sinh,
    "cosh": np.cosh,
    "tanh": np.tanh,
    "exp": np.exp,
    "log": np.log,
    "exp2": np.exp2,
    "log2": np.log2,
    "radians": lambda x: x * (_PI / 180.0),
    "degrees": lambda x: x * (180.0 / _PI),
    "min": np.minimum,
    "max": np.maximum,
    "pow": np.power,
    "clamp": _clamp,
    "mix": _mix,
    "step": lambda edge, x: np.where(x < edge, 0.0, 1.0),
    "smoothstep": _smoothstep,
    "mod": lambda x, y: x - y * np.floor(x / y),
    "trunc": np.trunc,
    "round": lambda x: np.floor(x + 0.5),
}
