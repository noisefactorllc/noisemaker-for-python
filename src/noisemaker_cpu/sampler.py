"""Texture samplers — nearest, bottom-left-flipped nearest, and bilinear.

Faithful port of noisemaker-cpu `src/runtime/sampler.js`. Every sampler
clamps to the edge texel for out-of-range `u`/`v` (no wraparound).

GLSL samplers address rows from the bottom, but `Surface` storage stays
top-down (for fast Canvas/ImageData and PNG handoff). `sample_nearest`
addresses storage rows directly (no flip). `sample_nearest_bottom_left`
flips the *integer texel row* (`y = height - 1 - shader_y`) rather than the
normalized coordinate (`1 - v`) — `1 - v` is wrong exactly on texel
boundaries. `sample_bilinear` does not flip at all; it addresses storage
directly, same as `sample_nearest`.

`sample_bilinear` mirrors the JS precision behavior: the four taps are read
at full (float64) precision and blended, and only the final per-channel
result is rounded to float32 (`Math.fround` <-> `numpy.float32`), matching
JS's implicit float64 widening of Float32Array reads.
"""

from __future__ import annotations

import math

import numpy as np


def _clamp(value, lo, hi):
    if value < lo:
        return lo
    if value > hi:
        return hi
    return value


def sample_nearest(surface, u: float, v: float) -> np.ndarray:
    """Nearest-neighbor sample, addressing storage rows top-down (no flip)."""
    width = surface.width
    height = surface.height
    x = _clamp(math.floor(u * width), 0, width - 1)
    y = _clamp(math.floor(v * height), 0, height - 1)
    source = (y * width + x) * 4
    return surface.data[source:source + 4].astype(np.float32)


def sample_nearest_bottom_left(surface, u: float, v: float) -> np.ndarray:
    """Nearest-neighbor sample with GLSL bottom-left row addressing.

    Flips the integer texel row (`height - 1 - shader_y`), not the
    normalized `v` coordinate, so results stay correct exactly on texel
    boundaries.
    """
    width = surface.width
    height = surface.height
    x = _clamp(math.floor(u * width), 0, width - 1)
    shader_y = _clamp(math.floor(v * height), 0, height - 1)
    y = height - 1 - shader_y
    source = (y * width + x) * 4
    return surface.data[source:source + 4].astype(np.float32)


def sample_bilinear(surface, u: float, v: float) -> np.ndarray:
    """Bilinear sample, half-texel-centered, clamped to edge, no row flip."""
    width = surface.width
    height = surface.height
    data = surface.data

    px = _clamp(u * width - 0.5, 0, width - 1)
    py = _clamp(v * height - 0.5, 0, height - 1)
    x0 = math.floor(px)
    y0 = math.floor(py)
    x1 = min(x0 + 1, width - 1)
    y1 = min(y0 + 1, height - 1)
    tx = px - x0
    ty = py - y0

    row0 = y0 * width * 4
    row1 = y1 * width * 4
    p00 = row0 + x0 * 4
    p10 = row0 + x1 * 4
    p01 = row1 + x0 * 4
    p11 = row1 + x1 * 4

    # Widen to float64 first, matching JS's implicit widening of
    # Float32Array reads to double before arithmetic.
    c00 = data[p00:p00 + 4].astype(np.float64)
    c10 = data[p10:p10 + 4].astype(np.float64)
    c01 = data[p01:p01 + 4].astype(np.float64)
    c11 = data[p11:p11 + 4].astype(np.float64)

    top = c00 + (c10 - c00) * tx
    bottom = c01 + (c11 - c01) * tx
    # Math.fround happens once, at the very end, in the JS source.
    return (top + (bottom - top) * ty).astype(np.float32)
