"""Port of the CPU fractal adapter, including its float32 Julia and color paths."""

from __future__ import annotations

import math

import numpy as np

from ..js_trig import js_cos, js_sin
from . import register

F32 = np.float32

_PI = 3.14159265359
_TAU = 6.28318530718
_PI_METAL = 3.1415929794311523


def _f32(x) -> float:
    return float(F32(x))


def _map(value, in_min, in_max, out_min, out_max):
    return out_min + (out_max - out_min) * (value - in_min) / (in_max - in_min)


def _map_f32(value, in_min, in_max, out_min, out_max):
    return _f32(out_min + _f32(out_max - out_min) * ((value - in_min) * _f32(1 / _f32(in_max - in_min))))


def _mix_f32(a, b, amount):
    return _f32(_f32(a * _f32(1 - amount)) + _f32(b * amount))


def _rotate_f32(x, y, rotation, aspect):
    angle = _f32(_map_f32(rotation, 0, 360, 0, 2) * _f32(_PI_METAL))
    px = _f32(x - _f32(0.5 * aspect))
    py = _f32(y - 0.5)
    cs = _f32(js_cos(angle))
    sn = _f32(js_sin(angle))
    return [_f32(sn * py + _f32(cs * px)), _f32(cs * py + _f32(-sn * px))]


def _fract_f32(value):
    return _f32(value - math.floor(value))


def _mod_f32(value, divisor):
    base = _f32(value)
    return _f32(base - _f32(divisor * math.floor(_f32(base / divisor))))


def _hsv_to_rgb_f32(h, s, v, out):
    h = _fract_f32(h)
    c = _f32(v * s)
    x = _f32(c * _f32(1 - abs(_mod_f32(_f32(h * 6), 2) - 1)))
    m = _f32(v - c)
    if h < 1 / 6:
        out[:] = [_f32(c + m), _f32(x + m), _f32(m)]
    elif h < 2 / 6:
        out[:] = [_f32(x + m), _f32(c + m), _f32(m)]
    elif h < 3 / 6:
        out[:] = [_f32(m), _f32(c + m), _f32(x + m)]
    elif h < 4 / 6:
        out[:] = [_f32(m), _f32(x + m), _f32(c + m)]
    elif h < 5 / 6:
        out[:] = [_f32(x + m), _f32(m), _f32(c + m)]
    else:
        out[:] = [_f32(c + m), _f32(m), _f32(x + m)]


def _palette_f32(t, b, out):
    for channel in range(3):
        inner = _f32(b["paletteFreq"][channel] * t + b["palettePhase"][channel])
        cosine = _f32(js_cos(_f32(inner * _f32(6.28318))))
        out[channel] = _f32(b["paletteAmp"][channel] * cosine + b["paletteOffset"][channel])
    if b["paletteMode"] == 1:
        _hsv_to_rgb_f32(float(out[0]), float(out[1]), float(out[2]), out)
    elif b["paletteMode"] == 2:
        _palette(t, b, out)


def _fract(value):
    return value - math.floor(value)


def _mod(value, divisor):
    return value - divisor * math.floor(value / divisor)


def _mix(a, b, amount):
    return a * (1 - amount) + b * amount


def _rotate(x, y, rotation, aspect):
    angle = _map(rotation, 0, 360, 0, 2) * _PI
    px = x - 0.5 * aspect
    py = y - 0.5
    cs = js_cos(angle)
    sn = js_sin(angle)
    return [cs * px + sn * py + 0.5 * aspect, -sn * px + cs * py + 0.5]


def _hypot(x, y):
    # V8's Math.hypot: scale by the larger magnitude before squaring.
    m = max(abs(x), abs(y))
    if m == 0:
        return 0.0
    sx = x / m
    sy = y / m
    return m * math.sqrt(sx * sx + sy * sy)


def _hsv_to_rgb(h, s, v, out):
    h = _fract(h)
    c = v * s
    x = c * (1 - abs(_mod(h * 6, 2) - 1))
    m = v - c
    if h < 1 / 6:
        out[:] = [c + m, x + m, m]
    elif h < 2 / 6:
        out[:] = [x + m, c + m, m]
    elif h < 3 / 6:
        out[:] = [m, c + m, x + m]
    elif h < 4 / 6:
        out[:] = [m, x + m, c + m]
    elif h < 5 / 6:
        out[:] = [x + m, m, c + m]
    else:
        out[:] = [c + m, m, x + m]


def _linear_to_srgb(value):
    if value <= 0.0031308:
        return value * 12.92
    return 1.055 * math.pow(value, 1 / 2.4) - 0.055


def _palette(t, b, out):
    for channel in range(3):
        out[channel] = _f32(
            b["paletteOffset"][channel]
            + b["paletteAmp"][channel] * js_cos(
                6.28318 * (b["paletteFreq"][channel] * t + b["palettePhase"][channel])
            )
        )
    if b["paletteMode"] == 1:
        _hsv_to_rgb(out[0], out[1], out[2], out)
    elif b["paletteMode"] == 2:
        big_l = out[0]
        a = out[1] * -0.509 + 0.276
        big_b = out[2] * -0.509 + 0.198
        l1 = big_l + 0.3963377774 * a + 0.2158037573 * big_b
        m1 = big_l - 0.1055613458 * a - 0.0638541728 * big_b
        s1 = big_l - 0.0894841775 * a - 1.291485548 * big_b
        l = l1 * l1 * l1
        m = m1 * m1 * m1
        s = s1 * s1 * s1
        out[0] = _f32(_linear_to_srgb(4.0767245293 * l - 3.3072168827 * m + 0.2307590544 * s))
        out[1] = _f32(_linear_to_srgb(-1.2681437731 * l + 2.6093323231 * m - 0.341134429 * s))
        out[2] = _f32(_linear_to_srgb(-0.0041119885 * l - 0.7034763098 * m + 1.7068625689 * s))


def _julia(x, y, b, aspect):
    x, y, aspect = _f32(x), _f32(y), _f32(aspect)
    time = _f32(b["time"])
    zoom = _map_f32(b["zoomAmt"], 0, 100, 2, 0.5)
    speedy = _map_f32(b["speed"], 0, 100, 0, 1)
    speed = _mix_f32(_f32(speedy * 0.05), _f32(speedy * 0.125), speedy)
    cx = _f32(js_sin(_f32(time * _f32(_TAU))) * speed + _map_f32(b["offsetX"], -100, 100, -0.5, 0.5))
    cy = _f32(js_cos(_f32(time * _f32(_TAU))) * speed + _map_f32(b["offsetY"], -100, 100, -1, 1))
    x, y = _rotate_f32(x, y, _f32(b["rotation"]), aspect)
    x = _f32(x * zoom + _map_f32(b["centerX"], -100, 100, 1, -1))
    y = _f32(y * zoom + _map_f32(b["centerY"], -100, 100, 1, -1))
    count = int(b["iterations"]) * 2
    iteration = 0
    for index in range(count):
        iteration = index
        next_x = _f32(_f32(x * x + cx) - y * y)
        next_y = _f32(y * x + x * y + cy)
        if _f32(next_x * next_x + next_y * next_y) > 4:
            break
        x = next_x
        y = next_y
    if count - iteration < int(b["cutoff"]):
        return 1
    if b["mode"] == 0:
        return _f32(iteration / count)
    return _f32(math.sqrt(_f32(x * x + y * y)))


def _newton(x, y, b, aspect):
    x, y = _rotate(x, y, b["rotation"] + 90, aspect)
    x = (x - 0.5 * aspect) * _map(b["zoomAmt"], 0, 130, 1, 0.01) + b["centerY"] * 0.01
    y = (y - 0.5) * _map(b["zoomAmt"], 0, 130, 1, 0.01) + b["centerX"] * 0.01
    speed = _map(b["speed"], 0, 100, 0, 1)
    offset_x = _map(b["offsetX"], -100, 100, -0.25, 0.25)
    offset_y = _map(b["offsetY"], -100, 100, -0.25, 0.25)
    iteration = 0
    for _ in range(int(b["iterations"])):
        fx = x * x * x - 3 * x * y * y - 1
        fy = 3 * x * x * y - y * y * y
        fpx = 3 * x * x - 3 * y * y
        fpy = 6 * x * y
        denominator = fpx * fpx + fpy * fpy
        tx = (fx * fpx + fy * fpy) / denominator
        ty = (fy * fpx - fx * fpy) / denominator
        tx += js_sin(b["time"] * _TAU) * 0.1 * speed + offset_x
        ty += js_cos(b["time"] * _TAU) * 0.1 * speed + offset_y
        if _hypot(tx, ty) < 0.001:
            break
        x -= tx
        y -= ty
        iteration += 1
    if b["mode"] == 0:
        return iteration / int(b["iterations"])
    return _hypot(x, y)


def _mandelbrot(x, y, b, aspect):
    zoom = _map(b["zoomAmt"], 0, 100, 2, 0.5)
    speedy = _map(b["speed"], 0, 100, 0, 1)
    speed = _mix(speedy * 0.05, speedy * 0.125, speedy)
    x, y = _rotate(x, y, b["rotation"], aspect)
    y = y * 2 - 1
    x = x * 2 - aspect
    cx = zoom * x - (b["centerX"] + 50) * 0.01
    cy = zoom * y - b["centerY"] * 0.01
    x = js_sin(b["time"] * _TAU) * speed
    y = js_cos(b["time"] * _TAU) * speed
    iteration = 0
    while iteration < int(b["iterations"]):
        next_x = x * x - y * y + cx
        next_y = 2 * x * y + cy
        x = next_x
        y = next_y
        if x * x + y * y > 16:
            break
        iteration += 1
    if iteration == int(b["iterations"]):
        return 1
    if b["mode"] == 0:
        return iteration / int(b["iterations"])
    return _hypot(x, y) / int(b["iterations"])


def _uniform(u, name, default):
    value = u.get(name, default)
    if isinstance(value, (list, tuple, np.ndarray)):
        return [float(v) for v in value]
    return float(value)


@register("classicNoisedeck/fractal:fractal")
def fractal_factory(rt, base_kernel):
    color = np.zeros(3, dtype=F32)

    def kernel(ctx, out):
        rt.begin_pixel(ctx)
        u = ctx.uniforms
        b = {
            "time": ctx.time if u.get("time") is None else float(u["time"]),
            "type": int(_uniform(u, "type", 0)),
            "symmetry": int(_uniform(u, "symmetry", 0)),
            "offsetX": _uniform(u, "offsetX", 0.0),
            "offsetY": _uniform(u, "offsetY", 0.0),
            "centerX": _uniform(u, "centerX", 0.0),
            "centerY": _uniform(u, "centerY", 0.0),
            "zoomAmt": _uniform(u, "zoomAmt", 0.0),
            "speed": _uniform(u, "speed", 0.0),
            "rotation": _uniform(u, "rotation", 0.0),
            "iterations": int(_uniform(u, "iterations", 0)),
            "mode": int(_uniform(u, "mode", 0)),
            "colorMode": int(_uniform(u, "colorMode", 0)),
            "paletteMode": int(_uniform(u, "paletteMode", 0)),
            "paletteOffset": _uniform(u, "paletteOffset", [0.0, 0.0, 0.0]),
            "paletteAmp": _uniform(u, "paletteAmp", [0.0, 0.0, 0.0]),
            "paletteFreq": _uniform(u, "paletteFreq", [0.0, 0.0, 0.0]),
            "palettePhase": _uniform(u, "palettePhase", [0.0, 0.0, 0.0]),
            "cyclePalette": int(_uniform(u, "cyclePalette", 0)),
            "rotatePalette": _uniform(u, "rotatePalette", 0.0),
            "repeatPalette": _uniform(u, "repeatPalette", 0.0),
            "hueRange": _uniform(u, "hueRange", 0.0),
            "levels": _uniform(u, "levels", 0.0),
            "bgColor": _uniform(u, "bgColor", [0.0, 0.0, 0.0]),
            "bgAlpha": _uniform(u, "bgAlpha", 0.0),
            "cutoff": _uniform(u, "cutoff", 0.0),
        }
        tile_offset = _uniform(u, "tileOffset", [0.0, 0.0])
        full_resolution = _uniform(u, "fullResolution", [0.0, 0.0])
        aspect = full_resolution[0] / full_resolution[1]
        global_x = float(ctx.frag_coord[0]) + tile_offset[0]
        global_y = float(ctx.frag_coord[1]) + tile_offset[1]
        x = global_x / full_resolution[1]
        y = global_y / full_resolution[1]
        if b["type"] == 0:
            distance = _julia(x, y, b, aspect)
        elif b["type"] == 1:
            distance = _newton(x, y, b, aspect)
        else:
            distance = _mandelbrot(x, y, b, aspect)
        if distance == 1:
            out[0] = b["bgColor"][0]
            out[1] = b["bgColor"][1]
            out[2] = b["bgColor"][2]
            out[3] = _f32(_f32(b["bgAlpha"]) * _f32(0.01))
            return
        if b["cyclePalette"] == -1:
            distance = _f32(distance - b["time"])
        elif b["cyclePalette"] == 1:
            distance = _f32(distance + b["time"])
        distance = _fract_f32(_f32(distance * _f32(b["repeatPalette"]) + _f32(_f32(b["rotatePalette"]) * _f32(0.01))))
        if b["levels"] > 0:
            levels = _f32(_f32(b["levels"]) + 1)
            distance = _f32(math.floor(_f32(distance * levels)) / levels)
        if b["colorMode"] == 0:
            value = _fract_f32(distance)
            color[:] = [value, value, value]
        elif b["colorMode"] == 4:
            _palette_f32(distance, b, color)
        elif b["colorMode"] == 6:
            _hsv_to_rgb_f32(_f32(distance * _f32(_f32(b["hueRange"]) * _f32(0.01))), 1, 1, color)
        else:
            color[:] = [0.0, 0.0, 1.0]
        out[0] = _f32(color[0])
        out[1] = _f32(color[1])
        out[2] = _f32(color[2])
        out[3] = 1

    kernel.uses_derivatives = False
    return kernel
