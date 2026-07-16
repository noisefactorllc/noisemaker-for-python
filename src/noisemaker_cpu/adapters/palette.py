"""filter/palette:palette adapter — port of noisemaker-cpu
src/effects/adapters/palette.js (`paletteFactory`).

The reference engine renders filter/palette through this hand-written CPU
adapter instead of the transpiled GLSL kernel, so we ignore `base_kernel` and
reimplement the whole per-pixel algorithm: sample the input texel, turn its
luminance into a phase `t`, evaluate a per-channel cosine palette
(`offset + amp*cos(TAU*(freq*t+phase))`) looked up from a 55-entry
coefficient table, optionally reinterpret the raw triple as HSV or OKLAB, and
alpha-blend the result back over the input.

Float model (matches palette.js exactly — see that file for the original):
  - JS `color` is a `Float32Array(3)`, so every `color[channel] = ...` write
    rounds to float32 *immediately*, before hsvToRgb/oklabToRgb ever reads it
    back. We mirror that with an explicit ``f32()`` round at each assignment
    into `color`.
  - Everything else — `t`, `lum`, the cosine-palette arithmetic, and the
    local variables inside hsvToRgb/oklabToRgb — is plain JS number math,
    i.e. float64 (Python `float`), with no intermediate rounding. This
    matches `Math.cos`/`Math.pow` (double precision) and raw `*`/`+`/`-`/`/`
    on scalars.
  - The final blend applies `Math.fround` to the blended R/G/B (reproduced
    with `f32()`); alpha is copied through from the input unrounded by
    `fround` in the JS source, though it is already float32-exact since it
    came straight from a texture read.
"""

from __future__ import annotations

import math

import numpy as np

from . import register
from ._palette_data import PALETTE_DATA
from ..sampler import sample_bilinear, sample_nearest_bottom_left

F32 = np.float32
_TAU = 6.283185307179586


def f32(x) -> float:
    return float(F32(x))


def _to_int32(x) -> int:
    """JS `x | 0`: ToInt32 — truncate toward zero, then wrap to signed 32-bit."""
    n = int(math.trunc(float(x))) & 0xFFFFFFFF
    return n - 0x100000000 if n >= 0x80000000 else n


def _clamp01(value: float) -> float:
    return min(max(value, 0.0), 1.0)


def _mix(a: float, b: float, amount: float) -> float:
    return a * (1.0 - amount) + b * amount


def _hsv_to_rgb(h: float, s: float, v: float):
    c = v * s
    hp = h * 6.0
    x = c * (1.0 - abs((hp - 2.0 * math.floor(hp / 2.0)) - 1.0))
    m = v - c
    if hp < 1.0:
        r, g, b = c + m, x + m, m
    elif hp < 2.0:
        r, g, b = x + m, c + m, m
    elif hp < 3.0:
        r, g, b = m, c + m, x + m
    elif hp < 4.0:
        r, g, b = m, x + m, c + m
    elif hp < 5.0:
        r, g, b = x + m, m, c + m
    else:
        r, g, b = c + m, m, x + m
    return f32(r), f32(g), f32(b)


def _linear_to_srgb(value: float) -> float:
    if value <= 0.0031308:
        return value * 12.92
    return 1.055 * math.pow(value, 1.0 / 2.4) - 0.055


def _oklab_to_rgb(lab_l: float, lab_a: float, lab_b: float):
    L = lab_l
    a = lab_a * -0.509 + 0.276
    b = lab_b * -0.509 + 0.198
    l1 = L + 0.3963377774 * a + 0.2158037573 * b
    m1 = L - 0.1055613458 * a - 0.0638541728 * b
    s1 = L - 0.0894841775 * a - 1.291485548 * b
    l = l1 * l1 * l1
    m = m1 * m1 * m1
    s = s1 * s1 * s1
    r = _clamp01(_linear_to_srgb(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s))
    g = _clamp01(_linear_to_srgb(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s))
    b_out = _clamp01(_linear_to_srgb(-0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s))
    return f32(r), f32(g), f32(b_out)


def _sample_input(surface, fx: float, fy: float):
    """Mirror glsl-runtime.js `GlslCpuRuntime#texture`: uv is computed against
    the *input texture's own* width/height (not the output resolution — this
    only matters when they differ), then sampled bilinear when
    `surface.filter == 'linear'` — flipping v (`1 - v`) because
    `sampleBilinear` addresses storage top-down directly — else
    nearest-bottom-left, which flips the integer texel row itself so v is
    passed through unflipped.
    """
    u = fx / surface.width
    v = fy / surface.height
    if getattr(surface, "filter", "nearest") == "linear":
        return sample_bilinear(surface, u, 1.0 - v)
    return sample_nearest_bottom_left(surface, u, v)


@register("filter/palette:palette")
def palette_factory(rt, base_kernel):
    def kernel(ctx, out):
        rt.begin_pixel(ctx)
        surface = ctx.textures["inputTex"]
        inp = _sample_input(surface, float(ctx.frag_coord[0]), float(ctx.frag_coord[1]))

        palette_index = _to_int32(ctx.uniforms.get("paletteIndex", 0))
        if palette_index <= 0 or palette_index > len(PALETTE_DATA):
            out[0] = f32(inp[0])
            out[1] = f32(inp[1])
            out[2] = f32(inp[2])
            out[3] = f32(inp[3])
            return

        entry = PALETTE_DATA[palette_index - 1]
        lum = float(inp[0]) * 0.299 + float(inp[1]) * 0.587 + float(inp[2]) * 0.114
        repeat = ctx.uniforms.get("repeat", 0)
        offset = ctx.uniforms.get("offset", 0.0)
        rotation = ctx.uniforms.get("rotation", 0)
        time = ctx.uniforms.get("time", ctx.time)
        t = lum * repeat + offset * 0.01
        if rotation == -1:
            t += time
        elif rotation == 1:
            t -= time

        color = [0.0, 0.0, 0.0]
        for channel in range(3):
            raw = entry[8 + channel] + entry[channel] * math.cos(
                _TAU * (entry[4 + channel] * t + entry[12 + channel])
            )
            color[channel] = f32(_clamp01(raw))

        mode = _to_int32(entry[3])
        if mode == 1:
            color[0], color[1], color[2] = _hsv_to_rgb(color[0], color[1], color[2])
        elif mode == 2:
            color[0], color[1], color[2] = _oklab_to_rgb(color[0], color[1], color[2])

        alpha = ctx.uniforms.get("alpha", 0.0)
        out[0] = f32(_mix(float(inp[0]), color[0], alpha))
        out[1] = f32(_mix(float(inp[1]), color[1], alpha))
        out[2] = f32(_mix(float(inp[2]), color[2], alpha))
        out[3] = f32(inp[3])

    kernel.uses_derivatives = False
    return kernel
