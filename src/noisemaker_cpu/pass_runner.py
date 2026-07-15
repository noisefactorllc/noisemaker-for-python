"""Per-pixel pass runner — turns a compiled kernel into filled Surface data.

Faithful port of noisemaker-cpu `src/runtime/pass-runner.js`. GLSL uses a
**bottom-left** origin with pixel centers at (x+0.5, y+0.5); surface storage is
**top-down**. So for top-down row ``y`` we feed the kernel ``fy = height-y-0.5``
(bottom-left) and ``uv = fragCoord / resolution``. The kernel writes 4 floats
into ``out``; we store them into the top-down row.
"""

from __future__ import annotations

import numpy as np

from .surface import Surface

F32 = np.float32


class Ctx:
    """Per-render context handed to each kernel invocation.

    ``rt``/``uniforms``/``textures``/``resolution``/``time``/``seed`` are set once
    per pass; ``frag_coord``/``uv`` are updated per pixel.
    """

    def __init__(self, rt, uniforms=None, textures=None, resolution=None, time=0.0, seed=1):
        self.rt = rt
        self.uniforms = uniforms or {}
        self.textures = textures or {}
        self.resolution = resolution
        self.time = f32_or(time)
        self.seed = seed
        self.frag_coord = None
        self.uv = None


def f32_or(x):
    return float(np.float32(x))


def run_pass(kernel, ctx: Ctx, width: int, height: int) -> Surface:
    surf = Surface(width, height)
    data = surf.data
    out = [0.0, 0.0, 0.0, 0.0]
    fw = float(width)
    fh = float(height)
    if ctx.resolution is None:
        ctx.resolution = np.array([fw, fh], dtype=F32)
    for y in range(height):
        fy = height - y - 0.5
        base = y * width * 4
        for x in range(width):
            fx = x + 0.5
            ctx.frag_coord = np.array([fx, fy, 0.0, 1.0], dtype=F32)
            ctx.uv = np.array([fx / fw, fy / fh], dtype=F32)
            kernel(ctx, out)
            i = base + x * 4
            data[i] = out[0]
            data[i + 1] = out[1]
            data[i + 2] = out[2]
            data[i + 3] = out[3]
    return surf
