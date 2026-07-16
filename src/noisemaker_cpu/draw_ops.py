"""CPU-only draw operations for passes the GPU expresses with non-fragment draw
modes (e.g. point-scatter). Dispatched by render_effect for passes flagged
``drawMode`` that have no transpiled fragment kernel.

Port of noisemaker-cpu ``src/effects/cpu/wormhole.js`` (runWormholeDeposit).
"""

from __future__ import annotations

import math

import numpy as np

from .texture_format import _float16_truncate

F32 = np.float32
_TAU = 6.28318530717959


def _f32(x):
    return float(F32(x))


def _add(a, b):
    return _f32(a + b)


def _mul(a, b):
    return _f32(a * b)


def _div(a, b):
    return _f32(a / b)


def _oklab_lightness(red, green, blue):
    r = min(max(red, 0.0), 1.0)
    g = min(max(green, 0.0), 1.0)
    b = min(max(blue, 0.0), 1.0)
    l = _add(_add(_mul(_f32(0.4122214708), r), _mul(_f32(0.5363325363), g)), _mul(_f32(0.0514459929), b))
    m = _add(_add(_mul(_f32(0.2119034982), r), _mul(_f32(0.6806995451), g)), _mul(_f32(0.1073969566), b))
    s = _add(_add(_mul(_f32(0.0883024619), r), _mul(_f32(0.2817188376), g)), _mul(_f32(0.6299787005), b))
    exponent = _div(1.0, 3.0)
    lr = _f32(math.pow(max(l, 0.0), exponent))
    mr = _f32(math.pow(max(m, 0.0), exponent))
    sr = _f32(math.pow(max(s, 0.0), exponent))
    return _add(_add(_mul(_f32(0.2104542553), lr), _mul(_f32(0.793617785), mr)), _mul(_f32(-0.0040720468), sr))


def _wrap_repeat(value, size):
    return ((value % size) + size) % size


def _wrap_mirror(value, size):
    doubled = size * 2
    mirrored = _wrap_repeat(value, doubled)
    return size - 1 - abs(mirrored - size + 1)


def wormhole_deposit(input_surf, dest_surf, uniforms):
    """Scatter each source pixel into a lightness-driven offset destination,
    accumulating weighted color with float16 truncation (matches the GPU
    rgba16f attachment)."""
    width, height = input_surf.width, input_surf.height
    if input_surf.width != dest_surf.width or input_surf.height != dest_surf.height:
        raise ValueError("wormhole deposit requires matching source/destination dimensions")
    idata = input_surf.data
    odata = dest_surf.data
    kink = float(uniforms["kink"])
    pixel_stride = 1024 * float(uniforms["stride"])
    rotation = _div(_mul(_f32(uniforms["rotation"]), _f32(math.pi)), 180.0)
    wrap = int(uniforms["wrap"])
    for source_y in range(height):
        for source_x in range(width):
            source_row = height - 1 - source_y
            so = (source_row * width + source_x) * 4
            lightness = _oklab_lightness(float(idata[so]), float(idata[so + 1]), float(idata[so + 2]))
            angle = _add(_mul(_mul(lightness, _f32(_TAU)), _f32(kink)), rotation)
            offset_x = _mul(_add(_f32(math.cos(angle)), 1.0), _f32(pixel_stride))
            offset_y = _mul(_add(_f32(math.sin(angle)), 1.0), _f32(pixel_stride))
            dest_x = math.floor(_add(source_x, offset_x))
            dest_y = math.floor(_add(source_y, offset_y))
            if wrap == 0:
                dest_x = _wrap_mirror(dest_x, width)
                dest_y = _wrap_mirror(dest_y, height)
            elif wrap == 2:
                dest_x = min(max(dest_x, 0), width - 1)
                dest_y = min(max(dest_y, 0), height - 1)
            else:
                dest_x = _wrap_repeat(dest_x, width)
                dest_y = _wrap_repeat(dest_y, height)
            dest_row = height - 1 - dest_y
            do = (dest_row * width + dest_x) * 4
            weight = _mul(lightness, lightness)
            odata[do] = _float16_truncate(np.array([_add(float(odata[do]), _mul(float(idata[so]), weight))], dtype=F32))[0]
            odata[do + 1] = _float16_truncate(np.array([_add(float(odata[do + 1]), _mul(float(idata[so + 1]), weight))], dtype=F32))[0]
            odata[do + 2] = _float16_truncate(np.array([_add(float(odata[do + 2]), _mul(float(idata[so + 2]), weight))], dtype=F32))[0]


POINT_DRAW_OPS = {
    "filter/wormhole:deposit": wormhole_deposit,
}


def get_draw_op(effect_id, program):
    return POINT_DRAW_OPS.get(f"{effect_id}:{program}")
