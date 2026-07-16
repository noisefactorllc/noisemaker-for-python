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
        # Preserve a passed-in mapping even when it is empty/falsy: renderer hands
        # us a _DefaultTex (a dict subclass whose __missing__ returns a blank
        # surface for unbound samplers). An empty _DefaultTex is falsy, so
        # `textures or {}` would drop the __missing__ override and re-raise KeyError.
        self.uniforms = uniforms if uniforms is not None else {}
        self.textures = textures if textures is not None else {}
        self.resolution = resolution
        self.time = f32_or(time)
        self.seed = seed
        self.frag_coord = None
        self.uv = None


def f32_or(x):
    return float(np.float32(x))


def run_pass_deriv(kernel, ctx: Ctx, width: int, height: int) -> Surface:
    """Pass runner for kernels using dFdx/dFdy/fwidth: process 2x2 quads,
    running each kernel in 'record' mode on the (clamped) quad corners to capture
    derivative arguments, computing per-call differences, then 'replay' on the
    real pixels."""
    surf = Surface(width, height)
    data = surf.data
    rt = ctx.rt
    fw, fh = float(width), float(height)

    def set_px(x, y):
        fx = x + 0.5
        fy = height - y - 0.5
        ctx.frag_coord = np.array([fx, fy, 0.0, 1.0], dtype=F32)
        ctx.uv = np.array([fx / fw, fy / fh], dtype=F32)

    if ctx.resolution is None:
        ctx.resolution = np.array([fw, fh], dtype=F32)
    scratch = [0.0, 0.0, 0.0, 0.0]
    for qy in range(0, height, 2):
        for qx in range(0, width, 2):
            x1 = min(qx + 1, width - 1)
            y1 = min(qy + 1, height - 1)
            recs = []
            for (px, py) in ((qx, qy), (x1, qy), (qx, y1), (x1, y1)):  # TL, TR, BL, BR
                set_px(px, py)
                rt.deriv_reset("record")
                kernel(ctx, scratch)
                recs.append(rt._deriv_log)
            diffs = rt.deriv_compute(recs)
            for py in range(qy, min(qy + 2, height)):
                for px in range(qx, min(qx + 2, width)):
                    set_px(px, py)
                    rt.deriv_reset("replay", diffs)
                    out = [0.0, 0.0, 0.0, 0.0]
                    kernel(ctx, out)
                    i = (py * width + px) * 4
                    data[i] = out[0]
                    data[i + 1] = out[1]
                    data[i + 2] = out[2]
                    data[i + 3] = out[3]
    rt.deriv_reset(None)
    return surf


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
