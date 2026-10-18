"""Direct float32 port of noisemaker-for-cpu's handwritten Metal CRT adapter."""

from __future__ import annotations

import math
import struct

import numpy as np

from . import register


def _f(value):
    return float(np.float32(value))


def _floor(value):
    # JavaScript Math.floor carries NaN/infinity and preserves signed zero.
    return math.floor(value) if math.isfinite(value) and value != 0 else value


def _trunc(value):
    return math.trunc(value) if math.isfinite(value) and value != 0 else value


def _to_int32(value):
    # Bitwise operators and the source fetch's Int32Array use ToInt32.
    if not math.isfinite(value) or value == 0:
        return 0
    bits = math.trunc(float(value)) % (1 << 32)
    return bits - (1 << 32) if bits >= (1 << 31) else bits


def _minimum(*values):
    if any(math.isnan(value) for value in values):
        return math.nan
    result = min(values)
    if result == 0 and any(math.copysign(1, value) < 0 for value in values if value == 0):
        return -0.0
    return result


def _maximum(*values):
    if any(math.isnan(value) for value in values):
        return math.nan
    result = max(values)
    if result == 0 and any(math.copysign(1, value) > 0 for value in values if value == 0):
        return 0.0
    return result


def fma32(a, b, c):
    """Round the exact float32 product and sum once, including midpoint ties."""
    product = a * b
    total = product + c
    back = total - product
    error = (product - (total - back)) + (c - back)
    rounded = _f(total)
    if error == 0 or rounded == total:
        return rounded
    toward_sum = 1 if total > rounded else -1
    if rounded == 0:
        neighbor = toward_sum * struct.unpack("<f", struct.pack("<I", 1))[0]
    else:
        bits = struct.unpack("<I", struct.pack("<f", rounded))[0]
        bits += 1 if (rounded > 0) == (toward_sum > 0) else -1
        neighbor = struct.unpack("<f", struct.pack("<I", bits))[0]
    if (rounded + neighbor) / 2 != total:
        return rounded
    return _maximum(rounded, neighbor) if error > 0 else _minimum(rounded, neighbor)


def _add(a, b):
    return _f(a + b)


def _sub(a, b):
    return _f(a - b)


def _mul(a, b):
    return _f(a * b)


def _div(a, b):
    # CRT's M2 compile multiplies by the rounded reciprocal.
    with np.errstate(divide="ignore", invalid="ignore"):
        return _f(a * _f(np.divide(1.0, b)))


def _fract(value):
    return _f(value - _floor(value))


def _clamp(value, low, high):
    return _minimum(_maximum(value, low), high)


def _clamp01(value):
    return _clamp(value, 0, 1)


def _sqrt(value):
    return _f(math.sqrt(value))


def _mix(a, b, t):
    return fma32(t, _sub(b, a), a)


def _length2(x, y):
    return _sqrt(fma32(y, y, _mul(x, x)))


def _dot3(ax, ay, az, bx, by, bz):
    return fma32(az, bz, fma32(ay, by, _mul(ax, bx)))


_INV_TAU = _f(1 / (2 * math.pi))
_INV_THREE = _f(1 / 3)
_HASH = _f(43758.5453123)
_HASH3 = _f(43758.5453)


def _quadrant_sine(r):
    n = _floor(r)
    fraction = r - n
    y = 1 - fraction if _to_int32(n) & 1 else fraction
    if y == 0:
        return -0.0 if n >= 2 else 0.0
    z = 2 * y * y - 1
    quotient = math.sin(y * math.pi / 2) / y
    p = _f(quotient - 2**-23 * (0.783734 + 0.010102 * z + 0.052674 * (2 * z * z - 1)))
    value = _f(y * p)
    return -value if n >= 2 else value


def _quadrant_of_turns(turns):
    return _f(4 * (turns - _floor(turns)))


def _sin(x):
    return _quadrant_sine(_quadrant_of_turns(_f(x * _INV_TAU)))


def _sin_turns(turns):
    return _quadrant_sine(_quadrant_of_turns(turns))


def _cos_turns(turns):
    return _quadrant_sine(_quadrant_of_turns(_add(turns, 0.25)))


def _cos_half_turns(turns):
    return _quadrant_sine(_quadrant_of_turns(fma32(turns, 0.5, 0.25)))


def _periodic_value(time, value):
    return fma32(_sin_turns(_sub(time, value)), 0.5, 0.5)


_C289 = _f(1 / 289)
_TAYLOR_A = _f(1.79284291400159)
_TAYLOR_B = _f(0.85373472095314)
_C_X = _f(1 / 6)
_C_Y = _f(1 / 3)
_N = _f(0.14285714285714285)
_NS_X = _mul(_N, 2)
_NS_Y = _sub(_mul(_N, 0.5), 1)
_M0 = _f(0.6)


def _mod289(x):
    return _sub(x, _mul(_floor(_mul(x, _C289)), 289))


def _permute(x):
    return _mod289(_mul(fma32(x, 34, 1), x))


def _simplex_noise(vx, vy, vz):
    dv = _dot3(vx, vy, vz, _C_Y, _C_Y, _C_Y)
    i0x, i0y, i0z = (_floor(_add(v, dv)) for v in (vx, vy, vz))
    di = _dot3(i0x, i0y, i0z, _C_X, _C_X, _C_X)
    x0x, x0y, x0z = (_add(_sub(v, i), di) for v, i in ((vx, i0x), (vy, i0y), (vz, i0z)))
    s1x = 0 if x0x < x0y else 1
    s1y = 0 if x0y < x0z else 1
    s1z = 0 if x0z < x0x else 1
    lx, ly, lz = 1 - s1z, 1 - s1x, 1 - s1y
    i1x, i1y, i1z = _minimum(s1x, lx), _minimum(s1y, ly), _minimum(s1z, lz)
    i2x, i2y, i2z = _maximum(s1x, lx), _maximum(s1y, ly), _maximum(s1z, lz)
    corners = [
        x0x,
        x0y,
        x0z,
        _add(_sub(x0x, i1x), _C_X),
        _add(_sub(x0y, i1y), _C_X),
        _add(_sub(x0z, i1z), _C_X),
        _add(_sub(x0x, i2x), _C_Y),
        _add(_sub(x0y, i2y), _C_Y),
        _add(_sub(x0z, i2z), _C_Y),
        _sub(x0x, 0.5),
        _sub(x0y, 0.5),
        _sub(x0z, 0.5),
    ]
    ix, iy, iz = (_mod289(i) for i in (i0x, i0y, i0z))
    offsets_x, offsets_y, offsets_z = [0, i1x, i2x, 1], [0, i1y, i2y, 1], [0, i1z, i2z, 1]
    p = []
    for k in range(4):
        pz = _permute(_add(iz, offsets_z[k]))
        py = _permute(_add(_add(pz, iy), offsets_y[k]))
        p.append(_permute(_add(_add(py, ix), offsets_x[k])))
    x, y, h = [], [], []
    for k in range(4):
        j = _sub(p[k], _mul(49, _floor(_mul(_mul(p[k], _N), _N))))
        xi = _floor(_mul(j, _N))
        yi = _floor(_sub(j, _mul(7, xi)))
        x.append(fma32(xi, _NS_X, _NS_Y))
        y.append(fma32(yi, _NS_X, _NS_Y))
        h.append(_sub(_sub(1, abs(x[k])), abs(y[k])))
    b0, b1 = [x[0], x[1], y[0], y[1]], [x[2], x[3], y[2], y[3]]
    s0 = [_add(_mul(_floor(v), 2), 1) for v in b0]
    s1 = [_add(_mul(_floor(v), 2), 1) for v in b1]
    sh = [0 if v > 0 else -1 for v in h]
    gradient = [
        fma32(s0[0], sh[0], b0[0]),
        fma32(s0[2], sh[0], b0[2]),
        h[0],
        fma32(s0[1], sh[1], b0[1]),
        fma32(s0[3], sh[1], b0[3]),
        h[1],
        fma32(s1[0], sh[2], b1[0]),
        fma32(s1[2], sh[2], b1[2]),
        h[2],
        fma32(s1[1], sh[3], b1[1]),
        fma32(s1[3], sh[3], b1[3]),
        h[3],
    ]
    total = 0
    for k in range(4):
        g = k * 3
        gx, gy, gz = gradient[g : g + 3]
        norm = fma32(-_TAYLOR_B, _dot3(gx, gy, gz, gx, gy, gz), _TAYLOR_A)
        cx, cy, cz = corners[g : g + 3]
        m = _maximum(_sub(_M0, _dot3(cx, cy, cz, cx, cy, cz)), 0)
        msq = _mul(m, m)
        term = _dot3(_mul(gx, norm), _mul(gy, norm), _mul(gz, norm), cx, cy, cz)
        total = _mul(_mul(msq, msq), term) if k == 0 else fma32(_mul(msq, msq), term, total)
    return _mul(42, total)


def _wrap_float(value, limit):
    if limit <= 0:
        return 0
    result = fma32(-_floor(_div(value, limit)), limit, value)
    return _add(result, limit) if result < 0 else result


def _freq_for_shape(base_freq, width, height):
    freq, width, height = _maximum(base_freq, 1), _maximum(width, 1), _maximum(height, 1)
    if abs(_sub(width, height)) < _f(1e-5):
        return freq, freq
    if height < width:
        return freq, _maximum(_floor(_div(_mul(freq, width), height)), 1)
    return _maximum(_floor(_div(_mul(freq, height), width)), 1), freq


def _value_noise_hash(cx, cy, cz, seed):
    value = fma32(seed, _f(0.001), _dot3(cx, cy, cz, _f(12.9898), _f(78.233), _f(37.719)))
    return _fract(_mul(_sin(value), _HASH3))


def _fade(value):
    return _mul(_mul(value, value), fma32(-2, value, 3))


def _lerp(a, b, t):
    return fma32(_sub(b, a), t, a)


def _value_noise_3d(x, y, z, seed):
    cx, cy, cz = _floor(x), _floor(y), _floor(z)
    tx, ty, tz = _fade(_sub(x, cx)), _fade(_sub(y, cy)), _fade(_sub(z, cz))

    def h(dx, dy, dz):
        return _value_noise_hash(cx + dx, cy + dy, cz + dz, seed)

    x00 = _lerp(h(0, 0, 0), h(1, 0, 0), tx)
    x10 = _lerp(h(0, 1, 0), h(1, 1, 0), tx)
    x01 = _lerp(h(0, 0, 1), h(1, 0, 1), tx)
    x11 = _lerp(h(0, 1, 1), h(1, 1, 1), tx)
    return _lerp(_lerp(x00, x10, ty), _lerp(x01, x11, ty), tz)


def _wrap_unit(value):
    wrapped = _sub(value, _floor(value))
    return _add(wrapped, 1) if wrapped < 0 else wrapped


def _rgb_to_hsv(r, g, b):
    cmax, cmin = _maximum(_maximum(r, g), b), _minimum(_minimum(r, g), b)
    delta, hue = _sub(cmax, cmin), 0
    if delta > 0:
        if cmax == r:
            hue = _div(_sub(g, b), delta)
            if hue < 0:
                hue = _add(hue, 6)
        elif cmax == g:
            hue = _add(_div(_sub(b, r), delta), 2)
        else:
            hue = _add(_div(_sub(r, g), delta), 4)
        hue = _wrap_unit(_div(hue, 6))
    return hue, _div(delta, cmax) if cmax != 0 else 0, cmax


def _hsv_to_rgb(h, s, v):
    dh, one_minus_s = _mul(h, 6), _sub(1, s)
    return [
        _clamp01(_mul(fma32(s, _clamp01(_sub(abs(_sub(dh, 3)), 1)), one_minus_s), v)),
        _clamp01(_mul(fma32(s, _clamp01(_add(-abs(_sub(dh, 2)), 2)), one_minus_s), v)),
        _clamp01(_mul(fma32(s, _clamp01(_add(-abs(_sub(dh, 4)), 2)), one_minus_s), v)),
    ]


def _adjust_hue(r, g, b, amount):
    h, s, v = _rgb_to_hsv(r, g, b)
    return _hsv_to_rgb(_wrap_unit(_add(h, amount)), _clamp01(s), _clamp01(v))


def _adjust_saturation(r, g, b, amount):
    h, s, v = _rgb_to_hsv(r, g, b)
    return _hsv_to_rgb(h, _clamp01(_mul(s, amount)), _clamp01(v))


@register("filter/crt:crt")
def crt_factory(rt, base_kernel):
    def kernel(ctx, out):
        rt.begin_pixel(ctx)
        uniforms = ctx.uniforms
        resolution = uniforms.get("resolution", ctx.resolution)
        tile_offset = uniforms.get("tileOffset", (0, 0))
        render_scale = float(uniforms.get("renderScale", 1))
        alpha = _clamp01(float(uniforms.get("alpha", 0)))
        rs = _maximum(render_scale, 1)
        full_res = uniforms.get("fullResolution", (0, 0))
        if full_res[0] <= 0:
            full_res = resolution
        width = _maximum(_div(float(full_res[0]), rs), 1)
        height = _maximum(_div(float(full_res[1]), rs), 1)
        time = float(uniforms.get("time", ctx.time))
        speed = float(uniforms.get("speed", 1))
        seed = float(uniforms.get("seed", ctx.seed))
        gx, gy = _to_int32(ctx.frag_coord[0]), _to_int32(ctx.frag_coord[1])

        def fetch(x, y):
            return rt.texel_fetch(ctx.textures["inputTex"], [_to_int32(x), _to_int32(y)])

        base_sample = fetch(gx, gy)
        base_r, base_g, base_b, base_a = map(float, base_sample)
        if alpha == 0:
            out[:] = [base_r, base_g, base_b, base_a]
            return

        freq = _freq_for_shape(2, width, height)
        freq_x, freq_y = _maximum(freq[1], 1), _maximum(freq[0], 1)
        z_base = _mul(_cos_turns(time), speed)
        s = _mul(seed, 73)
        base_seed_x, base_seed_y, base_seed_z = _add(17, s), fma32(s, _f(1.1), 29), fma32(s, _f(0.7), 47)
        time_seed_x, time_seed_y, time_seed_z = _add(base_seed_x, 54), _add(base_seed_y, 82), _add(base_seed_z, 124)

        def animated_simplex_value(u, v):
            base_noise = _simplex_noise(_add(u, base_seed_x), _add(v, base_seed_y), _add(z_base, base_seed_z))
            value = _clamp01(fma32(base_noise, 0.5, 0.5))
            if speed != 0 and time != 0:
                time_noise = _simplex_noise(_add(u, time_seed_x), _add(v, time_seed_y), time_seed_z)
                time_value = _clamp01(fma32(time_noise, 0.5, 0.5))
                value = _clamp01(_periodic_value(_mul(_periodic_value(time, time_value), speed), value))
            return _clamp01(value)

        aspect = _div(width, height)
        max_radius = _length2(_mul(aspect, 0.5), 0.5)

        def lens_offsets(sample_x, sample_y):
            wx, wy = _wrap_float(sample_x, width), _wrap_float(sample_y, height)
            noise = animated_simplex_value(_mul(_div(wx, width), freq_x), _mul(_div(wy, height), freq_y))
            dx = abs(_sub(_div(_add(wx, 0.5), width), 0.5))
            dy = abs(_sub(_div(_add(wy, 0.5), height), 0.5))
            mask = 0
            if max_radius > 0:
                normalized = _clamp01(_div(_length2(_mul(dx, aspect), dy), max_radius))
                masked = _sqrt(normalized)
                squared = _mul(masked, masked)
                mask = _mul(_mul(squared, squared), masked)
            distortion = _mul(fma32(noise, 2, -1), mask)
            return _mul(_mul(_cos_turns(distortion), 0.0625), width), _mul(_mul(_sin_turns(distortion), 0.0625), height)

        time_scaled = _mul(_mul(time, speed), _f(0.1))
        noise_seed = fma32(seed, 31, _f(19.37))
        scan_base0 = _value_noise_3d(0, 0, time_scaled, noise_seed)
        scan_base1 = _value_noise_3d(1, 0, time_scaled, noise_seed)

        def scan_row(row):
            return scan_base0 if _trunc(_floor(_div(row, 2.5))) % 2 == 0 else scan_base1

        def sample_scanline(sample_x, sample_y):
            wx = fma32(-_floor(_div(sample_x, width)), width, sample_x)
            wy = fma32(-_floor(_div(sample_y, height)), height, sample_y)
            if wx < 0:
                wx = _add(wx, width)
            if wy < 0:
                wy = _add(wy, height)
            wx, wy = _clamp(wx, 0, _sub(width, 1)), _clamp(wy, 0, _sub(height, 1))
            y0 = _floor(wy)
            y1 = _minimum(_add(y0, 1), _sub(height, 1))
            xf, yf = _clamp01(_sub(wx, _floor(wx))), _clamp01(_sub(wy, y0))
            top, bottom = scan_row(y0), scan_row(y1)
            return _mix(_mix(top, top, xf), _mix(bottom, bottom, xf), yf)

        def seed_hash(offset):
            turns = fma32(seed, _f(73 * _INV_TAU), _f(_f(17 + _f(offset)) * _INV_TAU))
            return _fract(_mul(_quadrant_sine(_quadrant_of_turns(turns)), _HASH))

        displacement_base = fma32(seed_hash(0.37), _f(0.00625), _f(0.0125))
        displacement_pixels = _mul(_mul(displacement_base, width), seed_hash(0.73))
        hue_shift = fma32(seed_hash(1.91), 0.25, -0.125)
        vignette_alpha = _mul(seed_hash(3.17), _f(0.175))

        def blend_cosine(a, b, value):
            c = _cos_half_turns(_clamp01(value))
            weight = _mul(_sub(1, c), 0.5)
            return fma32(b, weight, _mul(a, fma32(0.5, c, 0.5)))

        def blend_scan(value, scan):
            return _mix(value, _mul(_add(value, scan), scan), 0.5)

        x, y = _div(_add(gx, float(tile_offset[0])), rs), _div(_add(gy, float(tile_offset[1])), rs)
        ox, oy = lens_offsets(x, y)
        scan_value = sample_scanline(_add(x, ox), _add(y, oy))
        green = [_clamp01(blend_scan(v, scan_value)) for v in (base_r, base_g, base_b)]
        dx, dy = _div(_sub(x, _mul(width, 0.5)), width), _div(_sub(y, _mul(height, 0.5)), height)
        singularity = _length2(dx, dy)
        aber_mask = _mul(_mul(singularity, singularity), singularity)
        gradient_x = _clamp01(_div(x, _sub(width, 1)))
        red_x = _mix(_minimum(_add(x, displacement_pixels), _sub(width, 1)), x, gradient_x)
        red_sample_x = blend_cosine(x, red_x, aber_mask)
        red_fetch_x = _trunc(_sub(_mul(red_sample_x, render_scale), float(tile_offset[0])))
        red_sample = list(map(float, fetch(red_fetch_x, gy)))
        ox, oy = lens_offsets(red_sample_x, y)
        red_scan = sample_scanline(_add(red_sample_x, ox), _add(y, oy))
        blue_x = _mix(x, _maximum(_sub(x, displacement_pixels), 0), gradient_x)
        blue_sample_x = blend_cosine(x, blue_x, aber_mask)
        blue_fetch_x = _trunc(_sub(_mul(blue_sample_x, render_scale), float(tile_offset[0])))
        blue_sample = list(map(float, fetch(blue_fetch_x, gy)))
        ox, oy = lens_offsets(blue_sample_x, y)
        blue_scan = sample_scanline(_add(blue_sample_x, ox), _add(y, oy))
        red = _adjust_hue(*(blend_scan(v, red_scan) for v in red_sample[:3]), hue_shift)
        green = _adjust_hue(*green, hue_shift)
        blue = _adjust_hue(*(blend_scan(v, blue_scan) for v in blue_sample[:3]), hue_shift)
        color = _adjust_hue(red[0], green[1], blue[2], -hue_shift)
        color = _adjust_saturation(*color, 1.125)
        color = [_mix(v, _mix(v, 0, singularity), _clamp01(vignette_alpha)) for v in color]
        local_mean = _mul(_add(_add(color[0], color[1]), color[2]), _INV_THREE)
        for channel, base in enumerate((base_r, base_g, base_b)):
            normalized = _clamp01(fma32(_sub(color[channel], local_mean), 1.25, local_mean))
            quantized = _div(_floor(fma32(_clamp01(normalized), 255, 0.5)), 255)
            out[channel] = _mix(base, quantized, alpha)
        out[3] = base_a

    kernel.uses_derivatives = False
    return kernel
