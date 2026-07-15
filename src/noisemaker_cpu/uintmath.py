"""GPU-accurate uint32 and half-float integer primitives.

Faithful, bit-exact port of the integer/bitwise helpers in noisemaker-cpu
`src/csl/glsl-runtime.js`: `uint32`, `pcg3d`, `hashUint32`, `floatBitsToUint`,
`packHalf2x16`/`unpackHalf2x16`, and `glslMod`, plus the uint32 bitwise and
arithmetic primitives (`+`, `-`, `*`, `<<`, `>>>`, `&`, `|`, `^`) that back
GLSL `uint` operators in transpiled kernels. This module is self-contained:
stdlib + numpy only, no dependency on the rest of the package.

Python `int` is arbitrary-precision, so every uint32 result here is masked
with `& 0xFFFFFFFF` to emulate JS `>>> 0` / GLSL `uint` wraparound.

`Math.imul` (a 32-bit wrapping *signed* multiply) is reproduced in `umul`
as a plain unsigned-masked multiply. This is exact, not an approximation:
for any integers a, b, `(a * b) mod 2**32` is identical whether a and b are
first reduced to their signed (`ToInt32`) or unsigned (`ToUint32`) residues,
because multiplication mod a fixed power of two is invariant to which
representative of a residue class you pick. So
`((a & 0xFFFFFFFF) * (b & 0xFFFFFFFF)) & 0xFFFFFFFF` reproduces
`Math.imul(a, b) >>> 0` exactly — confirmed against
`umul(0xffffffff, 374761393) == 3920205903`, the golden vector in
`tests/test_uintmath.py` (no signedness adjustment was needed).

Float32 bit-reinterpretation (`float_bits_to_uint`/`uint_bits_to_float`) and
the float16 codec (`pack_half_2x16`/`unpack_half_2x16`) use `numpy.float32`/
`numpy.uint32` views to get exact IEEE-754 rounding and bit layout, matching
JS's shared-`ArrayBuffer` `Float32Array`/`Uint32Array` reinterpretation
(`this.bitsFloat` / `this.bitsUint` in `GlslCpuRuntime`).
"""

from __future__ import annotations

import math

import numpy as np

_MASK32 = 0xFFFFFFFF


def _int_operand(x) -> int:
    """Coerce a Python/numpy scalar to a plain int for bitwise work.

    Floats truncate toward zero, matching JS `ToInt32`/`ToUint32` (which
    truncate, not round); NaN/Infinity coerce to 0, also matching JS
    (`Number.NaN >>> 0 === 0`, `Infinity >>> 0 === 0`).
    """
    if isinstance(x, (float, np.floating)):
        xf = float(x)
        if not math.isfinite(xf):
            return 0
        return math.trunc(xf)
    return int(x)


def u32(x) -> int:
    """JS `value >>> 0` — coerce to an unsigned 32-bit integer with wraparound."""
    return _int_operand(x) & _MASK32


def umul(a, b) -> int:
    """JS `Math.imul(a, b) >>> 0` — 32-bit wrapping multiply, unsigned result."""
    return (u32(a) * u32(b)) & _MASK32


def uadd(a, b) -> int:
    """JS `(a + b) >>> 0` — 32-bit wrapping unsigned add."""
    return (u32(a) + u32(b)) & _MASK32


def usub(a, b) -> int:
    """JS `(a - b) >>> 0` — 32-bit wrapping unsigned subtract."""
    return (u32(a) - u32(b)) & _MASK32


def ushl(a, b) -> int:
    """JS `(a << b) >>> 0` — left shift; shift count masked to 0-31 (JS `& 0x1F`)."""
    return (u32(a) << (u32(b) & 0x1F)) & _MASK32


def ushr(a, b) -> int:
    """JS `a >>> b` — logical (zero-fill) right shift for uint; shift count masked to 0-31."""
    return (u32(a) >> (u32(b) & 0x1F)) & _MASK32


def uand(a, b) -> int:
    """JS `(a & b) >>> 0`."""
    return u32(a) & u32(b)


def uor(a, b) -> int:
    """JS `(a | b) >>> 0`."""
    return u32(a) | u32(b)


def uxor(a, b) -> int:
    """JS `(a ^ b) >>> 0`."""
    return u32(a) ^ u32(b)


def glsl_mod(x, y):
    """Floored modulo — GLSL/JS `x - y * floor(x / y)` (NOT Python's `%`).

    Uses `numpy.floor` (rather than `math.floor`) so a non-finite
    `x / y` (e.g. from `y == 0`) propagates Infinity/NaN like JS instead of
    raising `OverflowError`/`ValueError`.
    """
    return x - y * np.floor(x / y)


def pcg3d(v3):
    """3-lane PCG hash (uvec3 -> uvec3). Faithful port of `pcg3d` in
    glsl-runtime.js — including its sequential, in-place lane updates: in
    the two mixing blocks below, later lanes read the *already-updated*
    value of earlier lanes (e.g. `y`'s update uses the new `x`), exactly
    matching the JS `out[1] = ... out[0] ...` statement order. Computing
    all three lanes from pre-block values (a naive "parallel" translation)
    gives the wrong answer.
    """
    x = u32(v3[0])
    y = u32(v3[1])
    z = u32(v3[2])

    x = uadd(umul(x, 1664525), 1013904223)
    y = uadd(umul(y, 1664525), 1013904223)
    z = uadd(umul(z, 1664525), 1013904223)

    x = uadd(x, umul(y, z))
    y = uadd(y, umul(z, x))
    z = uadd(z, umul(x, y))

    x = uxor(x, ushr(x, 16))
    y = uxor(y, ushr(y, 16))
    z = uxor(z, ushr(z, 16))

    x = uadd(x, umul(y, z))
    y = uadd(y, umul(z, x))
    z = uadd(z, umul(x, y))

    return [x, y, z]


def hash_uint32(x) -> int:
    """Murmur-style uint32 finalizer. Faithful port of `hashUint32` in
    glsl-runtime.js.
    """
    result = u32(x)
    result = uxor(result, ushr(result, 16))
    result = umul(result, 0x7FEB352D)
    result = uxor(result, ushr(result, 15))
    result = umul(result, 0x846CA68B)
    result = uxor(result, ushr(result, 16))
    return result


# `stdlib.hashUint` in glsl-runtime.js is a bare alias for `hashUint32`
# (`hashUint: hashUint32`) — kept here under both names for parity.
hash_uint = hash_uint32


def float_bits_to_uint(f) -> int:
    """Reinterpret a float32's bits as a uint32 (GLSL `floatBitsToUint`).

    `f` is first rounded to float32 (matching JS's `Float32Array[0] = f`,
    an implicit double -> single rounding), then its 4 bytes are
    reinterpreted as a uint32.
    """
    return int(np.float32(f).view(np.uint32))


def uint_bits_to_float(u) -> float:
    """Reinterpret a uint32's bits as a float32 — the inverse of
    `float_bits_to_uint` (GLSL `uintBitsToFloat`).

    Not a separately named export in glsl-runtime.js (the JS runtime only
    reaches this direction implicitly, via its internal shared
    `ArrayBuffer`); included here for API completeness/symmetry.
    """
    return float(np.uint32(u32(u)).view(np.float32))


def _half_to_float(bits) -> float:
    """Decode one IEEE-754 binary16 value to a Python float. Faithful port
    of `halfToFloat` in glsl-runtime.js.
    """
    bits &= 0xFFFF
    sign = -1 if (bits & 0x8000) else 1
    exponent = (bits >> 10) & 0x1F
    fraction = bits & 0x3FF
    if exponent == 0:
        return sign * math.pow(2, -14) * (fraction / 1024)
    if exponent == 0x1F:
        return math.nan if fraction else sign * math.inf
    return sign * math.pow(2, exponent - 15) * (1 + fraction / 1024)


def _float_to_half(value) -> int:
    """Encode a Python float to one IEEE-754 binary16 value (round-to-nearest,
    denormals handled, overflow saturated to +-Infinity). Faithful port of
    `floatToHalf` in glsl-runtime.js.
    """
    if math.isnan(value):
        return 0x7E00
    if value == math.inf:
        return 0x7C00
    if value == -math.inf:
        return 0xFC00
    bits = int(np.float32(value).view(np.uint32))
    sign = (bits >> 16) & 0x8000
    exponent = ((bits >> 23) & 0xFF) - 127 + 15
    fraction = bits & 0x7FFFFF
    if exponent <= 0:
        if exponent < -10:
            return sign
        fraction = (fraction | 0x800000) >> (1 - exponent)
        return sign | ((fraction + 0x1000) >> 13)
    if exponent >= 31:
        return sign | 0x7C00
    fraction += 0x1000
    if fraction & 0x800000:
        fraction = 0
        exponent += 1
        if exponent >= 31:
            return sign | 0x7C00
    return sign | (exponent << 10) | (fraction >> 13)


def pack_half_2x16(v2) -> int:
    """Pack two floats into a uint32 as two binary16 halves (GLSL
    `packHalf2x16`): `v2[0]` occupies the low 16 bits, `v2[1]` the high 16.
    """
    lo = _float_to_half(v2[0])
    hi = _float_to_half(v2[1])
    return u32(lo | (hi << 16))


def unpack_half_2x16(u):
    """Unpack a uint32 into two floats from two binary16 halves (GLSL
    `unpackHalf2x16`) — the inverse of `pack_half_2x16`.
    """
    uu = u32(u)
    return [_half_to_float(uu & 0xFFFF), _half_to_float((uu >> 16) & 0xFFFF)]
