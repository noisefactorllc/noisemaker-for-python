"""Texture samplers — nearest, bottom-left-flipped nearest, and bilinear.

Faithful port of noisemaker-cpu `src/runtime/sampler.js`. Every sampler
clamps to the edge texel for out-of-range `u`/`v` (no wraparound).

GLSL samplers address rows from the bottom, but `Surface` storage stays
top-down (for fast Canvas/ImageData and PNG handoff). `sample_nearest`
addresses storage rows directly (no flip). `sample_nearest_bottom_left` and
`sample_bilinear` flip the *integer texel row* (`y = height - 1 - shader_y`)
rather than the normalized coordinate (`1 - v`) — `1 - v` is wrong exactly on
texel boundaries. The flip is only observable on a non-uniform texture (a solid
input renders identically either way), which is why it must match the GL
bottom-left convention that texelFetch uses.

`sample_bilinear` mirrors the JS precision behavior: the four taps are read
at full (float64) precision and blended, and only the final per-channel
result is rounded to float32 (`Math.fround` <-> `numpy.float32`), matching
JS's implicit float64 widening of Float32Array reads.
"""

from __future__ import annotations

import math

import numpy as np

_F32 = np.float32


def _clamp(value, lo, hi):
    # JS `clamp` is a ternary, not a min/max pair: a NaN compares false on
    # both sides and passes through unchanged (Math.min/max would too).
    if value < lo:
        return lo
    if value > hi:
        return hi
    return value


def _floor(value):
    """JS ``Math.floor`` over a float: NaN/Infinity stay floats (Python's
    ``math.floor`` raises on them). The caller clamps afterwards, so +/-
    Infinity land on the edge texel exactly like the oracle's sampler, while
    a NaN coordinate stays NaN and reads the undefined texel (NaN channels)."""
    return float(np.floor(value))


def _undefined_texel() -> np.ndarray:
    """A NaN uv reads `data[NaN]` in the oracle: every channel is `undefined`,
    which a Float32Array assignment coerces to NaN."""
    return np.array([np.nan, np.nan, np.nan, np.nan], dtype=_F32)


def sample_nearest(surface, u: float, v: float) -> np.ndarray:
    """Nearest-neighbor sample, addressing storage rows top-down (no flip)."""
    width = surface.width
    height = surface.height
    x = _clamp(_floor(u * width), 0, width - 1)
    y = _clamp(_floor(v * height), 0, height - 1)
    if not (math.isfinite(x) and math.isfinite(y)):
        return _undefined_texel()
    source = (int(y) * width + int(x)) * 4
    return surface.data[source : source + 4].astype(np.float32)


def sample_nearest_bottom_left(surface, u: float, v: float) -> np.ndarray:
    """Nearest-neighbor sample with GLSL bottom-left row addressing.

    Flips the integer texel row (`height - 1 - shader_y`), not the
    normalized `v` coordinate, so results stay correct exactly on texel
    boundaries.
    """
    width = surface.width
    height = surface.height
    x = _clamp(_floor(u * width), 0, width - 1)
    shader_y = _clamp(_floor(v * height), 0, height - 1)
    if not (math.isfinite(x) and math.isfinite(shader_y)):
        return _undefined_texel()
    y = height - 1 - int(shader_y)
    source = (y * width + int(x)) * 4
    return surface.data[source : source + 4].astype(np.float32)


def sample_bilinear(surface, u: float, v: float) -> np.ndarray:
    """Bilinear sample, half-texel-centered, clamped to edge, GL bottom-left row
    addressing (flips the integer texel row, like sample_nearest_bottom_left)."""
    width = surface.width
    height = surface.height
    data = surface.data

    px = _clamp(u * width - 0.5, 0, width - 1)
    py = _clamp(v * height - 0.5, 0, height - 1)
    if not (math.isfinite(px) and math.isfinite(py)):
        # A NaN uv reads undefined taps on both engines (the clamp above
        # passes NaN through; +/-Infinity clamps to the edge before this).
        return _undefined_texel()
    x0 = int(_floor(px))
    y0 = int(_floor(py))
    x1 = min(x0 + 1, width - 1)
    y1 = min(y0 + 1, height - 1)
    tx = px - x0
    ty = py - y0

    row0 = (height - 1 - y0) * width * 4
    row1 = (height - 1 - y1) * width * 4
    p00 = row0 + x0 * 4
    p10 = row0 + x1 * 4
    p01 = row1 + x0 * 4
    p11 = row1 + x1 * 4

    # Widen to float64 first, matching JS's implicit widening of
    # Float32Array reads to double before arithmetic.
    c00 = data[p00 : p00 + 4].astype(np.float64)
    c10 = data[p10 : p10 + 4].astype(np.float64)
    c01 = data[p01 : p01 + 4].astype(np.float64)
    c11 = data[p11 : p11 + 4].astype(np.float64)

    top = c00 + (c10 - c00) * tx
    bottom = c01 + (c11 - c01) * tx
    # Math.fround happens once, at the very end, in the JS source.
    return (top + (bottom - top) * ty).astype(np.float32)
