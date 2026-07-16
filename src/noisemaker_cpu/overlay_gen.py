"""Procedural worm/fiber/scratch overlay generator.

Port of noisemaker-cpu ``src/effects/cpu/worm-overlay.js``. filter/fibers,
filter/scratches and filter/strayHair declare an ``overlayTex`` texture that no
pass produces; the reference engine generates it once on the CPU and binds it.

Fidelity notes:
- SeededRng multiplies with plain JS ``*`` on products up to ~2^61, which is
  LOSSY in float64 (it is NOT Math.imul). We replicate that by doing the
  multiply in Python float (float64) and truncating: ``int(float(a) * b) & M``.
- Grid/field/surface storage is Float32Array; reads are promoted to float64 for
  arithmetic (explicit float()), writes round to float32.
- Final surface is quantized to 8-bit (round(x*255)/255) like the reference.
"""

from __future__ import annotations

import math

import numpy as np

from .surface import Surface

F32 = np.float32
_TAU = math.pi * 2.0
_M = 0xFFFFFFFF


class SeededRng:
    def __init__(self, seed):
        state = int(seed) & _M
        # constructor already advances once (matches JS)
        self.state = int(float(state) * 747796405.0 + 2891336453.0) & _M

    def next(self):
        self.state = int(float(self.state) * 747796405.0 + 2891336453.0) & _M
        word = int(float((self.state >> ((self.state >> 28) + 4)) ^ self.state) * 277803737.0) & _M
        return ((word >> 22) ^ word) & _M

    def float(self):
        return self.next() / 4294967295.0

    def normal(self, mean=0.0, deviation=1.0):
        u1 = max(self.float(), 1e-10)
        u2 = self.float()
        return mean + deviation * math.sqrt(-2.0 * math.log(u1)) * math.cos(_TAU * u2)


def _value_noise_field(width, height, frequency, rng):
    grid_w = math.ceil(frequency) + 2
    grid_h = math.ceil(frequency) + 2
    grid = np.array([F32(rng.float()) for _ in range(grid_w * grid_h)], dtype=F32)
    field = np.zeros(width * height, dtype=F32)
    for y in range(height):
        for x in range(width):
            fx = x / width * frequency
            fy = y / height * frequency
            ix = math.floor(fx)
            iy = math.floor(fy)
            dx = fx - ix
            dy = fy - iy
            sx = dx * dx * (3 - 2 * dx)
            sy = dy * dy * (3 - 2 * dy)
            tl = float(grid[iy * grid_w + ix])
            tr = float(grid[iy * grid_w + ix + 1])
            bl = float(grid[(iy + 1) * grid_w + ix])
            br = float(grid[(iy + 1) * grid_w + ix + 1])
            field[y * width + x] = (tl * (1 - sx) + tr * sx) * (1 - sy) + (bl * (1 - sx) + br * sx) * sy
    return field


def _draw_segment(surface, x0, y0, x1, y1, line_width, color, alpha):
    if alpha <= 0:
        return
    radius = line_width * 0.5
    min_x = max(0, math.floor(min(x0, x1) - radius - 1))
    max_x = min(surface.width - 1, math.ceil(max(x0, x1) + radius + 1))
    min_y = max(0, math.floor(min(y0, y1) - radius - 1))
    max_y = min(surface.height - 1, math.ceil(max(y0, y1) + radius + 1))
    dx = x1 - x0
    dy = y1 - y0
    len_sq = dx * dx + dy * dy
    data = surface.data
    w = surface.width
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            px = x + 0.5
            py = y + 0.5
            amount = min(max(((px - x0) * dx + (py - y0) * dy) / len_sq, 0), 1) if len_sq > 0 else 0
            near_x = x0 + dx * amount
            near_y = y0 + dy * amount
            distance = math.hypot(px - near_x, py - near_y)
            coverage = min(max(radius + 0.5 - distance, 0), 1)
            src_a = alpha * coverage
            if src_a <= 0:
                continue
            off = (y * w + x) * 4
            dst_a = float(data[off + 3])
            out_a = src_a + dst_a * (1 - src_a)
            for c in range(3):
                data[off + c] = (color[c] * src_a + float(data[off + c]) * dst_a * (1 - src_a)) / out_a if out_a > 0 else 0
            data[off + 3] = out_a


def _trace(surface, opts):
    rng = SeededRng(opts["seed"])
    min_dim = min(surface.width, surface.height)
    max_dim = max(surface.width, surface.height)
    stride_scale = max_dim / 1024
    flow = _value_noise_field(surface.width, surface.height, opts["flowFrequency"], SeededRng(opts["seed"] * 31337))
    count = max(1, math.floor(max_dim * opts["density"]))
    shared_rotation = rng.float() * _TAU
    worms = []
    for index in range(count):
        worms.append({
            "x": rng.float() * surface.width,
            "y": rng.float() * surface.height,
            "stride": rng.normal(opts["stride"], opts["strideDeviation"]) * stride_scale,
            "rotation": shared_rotation if opts["behavior"] == "obedient" else rng.float() * _TAU,
            "color": opts["color"](rng, index),
        })
    iterations = max(1, math.floor(math.sqrt(min_dim) * opts["duration"]))
    for worm in worms:
        x = worm["x"]
        y = worm["y"]
        for iteration in range(iterations):
            lifetime = iteration / (iterations - 1) if iterations > 1 else 1
            exposure = 1 - abs(1 - lifetime * 2)
            flow_x = math.floor(((x % surface.width) + surface.width) % surface.width)
            flow_y = math.floor(((y % surface.height) + surface.height) % surface.height)
            angle = float(flow[flow_y * surface.width + flow_x]) * _TAU * opts["kink"]
            angle += shared_rotation if opts["behavior"] == "obedient" else worm["rotation"]
            next_x = x + math.sin(angle) * worm["stride"]
            next_y = y + math.cos(angle) * worm["stride"]
            _draw_segment(surface, x, y, next_x, next_y, opts["lineWidth"], worm["color"], opts["alpha"] * exposure)
            x = next_x
            y = next_y


def render_worm_overlay(effect_id, width, height, params):
    surface = Surface(width, height)
    seed = params.get("seed") or 1
    density = params["density"]
    if effect_id == "filter/fibers":
        base_density = 0.5 + density * 2
        for layer in range(4):
            layer_seed = seed * 1000 + layer * 137
            _trace(surface, {
                "seed": layer_seed, "density": base_density, "kink": 5 + layer_seed % 5,
                "stride": 0.75, "strideDeviation": 0.125, "duration": 1, "behavior": "chaotic",
                "flowFrequency": 4, "lineWidth": max(1.5, width / 384),
                "color": lambda rng, i=0: [math.floor(rng.float() * 200 + 55) / 255,
                                           math.floor(rng.float() * 200 + 55) / 255,
                                           math.floor(rng.float() * 200 + 55) / 255],
                "alpha": 0.5,
            })
    elif effect_id == "filter/scratches":
        for layer in range(4):
            layer_seed = seed * 1000 + layer * 251
            _trace(surface, {
                "seed": layer_seed, "density": 0.1 + density * 0.4, "kink": 0.125 + layer_seed % 50 / 400,
                "stride": 0.75, "strideDeviation": 0.5, "duration": 2 + layer_seed % 3,
                "behavior": "obedient" if layer_seed % 2 == 0 else "unruly",
                "flowFrequency": 2 + layer_seed % 3, "lineWidth": max(0.5, width / 1024),
                "color": lambda rng, i=0: [1.0, 1.0, 1.0], "alpha": 1,
            })
    elif effect_id == "filter/strayHair":
        layer_seed = seed * 1000 + 42
        _trace(surface, {
            "seed": layer_seed, "density": 0.001 + density * 0.004, "kink": 5 + layer_seed % 45,
            "stride": 0.5, "strideDeviation": 0.25, "duration": 8 + layer_seed % 8, "behavior": "unruly",
            "flowFrequency": 4, "lineWidth": max(1, width / 400),
            "color": lambda rng, i=0: [math.floor(rng.float() * 30) / 255,
                                       math.floor(rng.float() * 30) / 255,
                                       math.floor(rng.float() * 30) / 255],
            "alpha": 0.666,
        })
    else:
        raise ValueError(f"Unsupported canonical CPU overlay {effect_id}")
    d = surface.data
    d[:] = np.round(np.clip(d, 0.0, 1.0) * 255.0) / 255.0
    return surface


OVERLAY_EFFECTS = ("filter/fibers", "filter/scratches", "filter/strayHair")
