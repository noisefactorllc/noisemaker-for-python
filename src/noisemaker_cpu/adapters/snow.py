"""filter/snow:snow adapter — port of noisemaker-cpu src/effects/adapters/snow.js.

The reference engine renders `filter/snow` entirely through this hand-written
CPU adapter instead of the transpiled GLSL kernel (`filter__snow__snow.py`), so
this is a **full reimplementation**: `base_kernel` is ignored and every pixel
is computed here, mirroring snow.js's helper functions verbatim — including
the exact points where it rounds to float32 (``Math.fround``) versus where it
leaves an expression as raw float64 (plain JS ``+ - * /``).

Two deliberate deviations from the transpiled GLSL kernel, both inherited from
snow.js itself (not bugs to "fix"):
  * `snowHash`'s internal dot-product-like sum is NOT computed with the CPU
    runtime's `dot()` (accumulate in float64, round once); it's a hand-unrolled
    sum with float32 rounding applied only at specific sub-expressions — see
    `_snow_hash` below for the exact grouping.
  * the coordinates fed to the noise are the raw `fragCoord.xy` — unlike the
    transpiled kernel, this adapter never adds `tileOffset`.
"""

from __future__ import annotations

import math

import numpy as np

from . import register

F32 = np.float32


def _f32(x) -> float:
    return float(F32(x))


_TAU = _f32(6.283185307179586)
_INV_TAU = _f32(1.0 / 6.283185307179586)
_TIME_SEED_OFFSETS = (_f32(97.0), _f32(57.0), _f32(131.0))
_STATIC_SEED = (_f32(37.0), _f32(17.0), _f32(53.0))
_LIMITER_SEED = (_f32(113.0), _f32(71.0), _f32(193.0))


def _add(a, b):
    return _f32(a + b)


def _sub(a, b):
    return _f32(a - b)


def _mul(a, b):
    return _f32(a * b)


def _div(a, b):
    return _f32(a / b)


def _fract(value):
    return _f32(value - math.floor(value))


def _clamp01(value):
    if value <= 0:
        return 0.0
    if value >= 1:
        return 1.0
    return value


def _sine(value):
    turns = _f32(value * _INV_TAU)
    phase = turns - math.floor(turns)
    return _f32(math.sin(phase * _TAU))


def _cosine(value):
    return _f32(math.cos(value))


def _periodic_value(time, value):
    return _mul(_add(_sine(_mul(_sub(time, value), _TAU)), 1.0), 0.5)


def _snow_hash(x, y, z):
    sx = _fract(_mul(x, _f32(0.1031)))
    sy = _fract(_mul(y, _f32(0.1031)))
    sz = _fract(_mul(z, _f32(0.1031)))
    # dot = F32(F32(sx*add(sy,33.33) + mul(sy,add(sz,33.33))) + sz*add(sx,33.33))
    # NB: `sx * add(...)` and `sz * add(...)` are raw (unrounded) float64
    # products in the JS source; only `mul(...)` and the two outer `F32(...)`
    # wraps actually round to float32. Preserve that grouping exactly.
    inner = _f32(sx * _add(sy, _f32(33.33)) + _mul(sy, _add(sz, _f32(33.33))))
    dot = _f32(inner + sz * _add(sx, _f32(33.33)))
    shifted_xy = _f32(sx + sy + _f32(2.0 * dot))
    return _clamp01(_fract(_f32(shifted_xy * _add(sz, dot))))


def _snow_noise(x, y, time, speed, seed):
    angle = _mul(time, _TAU)
    cosine_value = _cosine(angle)
    z_base = 0.0 if abs(cosine_value) < _f32(0.0000001) else _mul(cosine_value, speed)
    base_value = _snow_hash(_add(x, seed[0]), _add(y, seed[1]), _add(z_base, seed[2]))
    if speed == 0 or time == 0:
        return base_value

    time_seed_x = _add(seed[0], _TIME_SEED_OFFSETS[0])
    time_seed_y = _add(seed[1], _TIME_SEED_OFFSETS[1])
    time_seed_z = _add(seed[2], _TIME_SEED_OFFSETS[2])
    time_value = _snow_hash(_add(x, time_seed_x), _add(y, time_seed_y), _add(1.0, time_seed_z))
    scaled_time = _mul(_periodic_value(time, time_value), speed)
    return _clamp01(_periodic_value(scaled_time, base_value))


@register("filter/snow:snow")
def snow_factory(rt, base_kernel):
    def kernel(ctx, out):
        rt.begin_pixel(ctx)
        x = float(ctx.frag_coord[0])
        y = float(ctx.frag_coord[1])
        source = rt.texel_fetch(ctx.textures["inputTex"], [x, y])
        alpha = _clamp01(ctx.uniforms.get("alpha", 0.0))
        if alpha == 0:
            out[0] = float(source[0])
            out[1] = float(source[1])
            out[2] = float(source[2])
            out[3] = float(source[3])
            return

        pause = ctx.uniforms.get("pause", False)
        time = 0.0 if pause > 0.5 else ctx.uniforms.get("time", ctx.time)
        speed = _f32(100.0)
        static_value = _snow_noise(x, y, time, speed, _STATIC_SEED)
        limiter_value = _snow_noise(x, y, time, speed, _LIMITER_SEED)
        density = max(_mul(ctx.uniforms.get("density", 0.0), _f32(0.01)), _f32(0.0001))
        exponent = _div(_sub(1.0, density), density)
        limiter_mask = _mul(_f32(math.pow(min(limiter_value, _f32(0.99)), exponent)), alpha)
        inverse_mask = _sub(1.0, limiter_mask)
        out[0] = _f32(float(source[0]) * inverse_mask + static_value * limiter_mask)
        out[1] = _f32(float(source[1]) * inverse_mask + static_value * limiter_mask)
        out[2] = _f32(float(source[2]) * inverse_mask + static_value * limiter_mask)
        out[3] = float(source[3])

    kernel.uses_derivatives = False
    return kernel
