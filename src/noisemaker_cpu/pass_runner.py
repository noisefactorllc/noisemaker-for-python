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


def _blend_weight(factor, src, dst):
    if isinstance(factor, str):
        factor = factor.lower().replace("_", "-")
    if isinstance(factor, bool):
        return 1.0
    match factor:
        case 0 | "zero":
            return 0.0
        case 0x0300 | "src-color" | "src":
            return src
        case 0x0301 | "one-minus-src-color" | "one-minus-src":
            return 1.0 - src
        case 0x0302 | "src-alpha":
            return src[:, 3:4]
        case 0x0303 | "one-minus-src-alpha":
            return 1.0 - src[:, 3:4]
        case 0x0304 | "dst-alpha":
            return dst[:, 3:4]
        case 0x0305 | "one-minus-dst-alpha":
            return 1.0 - dst[:, 3:4]
        case 0x0306 | "dst-color" | "dst":
            return dst
        case 0x0307 | "one-minus-dst-color" | "one-minus-dst":
            return 1.0 - dst
        case _:
            return 1.0


def blend_pass_output(blend, destination: Surface, previous: Surface | None):
    """Combine the fragment output with the previous attachment before format quantization."""
    factors = iter(blend) if isinstance(blend, (list, tuple)) else iter(())
    src_factor = next(factors, None)
    dst_factor = next(factors, None)
    rows = destination.data.reshape(destination.height, destination.width, 4)
    backdrop = None
    if previous is not None and (previous.width, previous.height) == (destination.width, destination.height):
        backdrop = previous.data.reshape(rows.shape)
    transparent = np.zeros((1, 4), dtype=np.float64)
    for y, row in enumerate(rows):
        # Match JS scalar arithmetic, rounding once on float32 storage. Widen a row at a time.
        src = row.astype(np.float64)
        dst = backdrop[y].astype(np.float64) if backdrop is not None else transparent
        row[:] = src * _blend_weight(src_factor, src, dst) + dst * _blend_weight(dst_factor, src, dst)


def run_pass_deriv(kernel, ctx: Ctx, width: int, height: int) -> Surface:
    """Pass runner for kernels using dFdx/dFdy/fwidth. Mirrors the reference
    engine's wrapDerivatives: derivatives are computed in bottom-left pixel space
    over 2x2 quads. Each quad's 4 corners are probed in 'record' mode (arguments
    captured, no edge clamping — probes may fall outside the image like the GPU);
    each real pixel then replays with FINE derivatives selected by its parity."""
    surf = Surface(width, height)
    data = surf.data
    rt = ctx.rt
    fw, fh = float(width), float(height)
    if ctx.resolution is None:
        ctx.resolution = np.array([fw, fh], dtype=F32)

    def set_frag(fx, fy):
        ctx.frag_coord = np.array([fx, fy, 0.0, 1.0], dtype=F32)
        ctx.uv = np.array([fx / fw, fy / fh], dtype=F32)

    def probe(fx, fy):
        set_frag(fx, fy)
        rt.deriv_reset("record")
        kernel(ctx, [0.0, 0.0, 0.0, 0.0])
        return rt._deriv_log

    lane_cache = {}  # (quadX, quadY) -> [LL, LR, UL, UR] logs
    diff_cache = {}  # (quadX, quadY, xParity, yParity) -> fine diffs
    for y in range(height):
        fy = height - y - 0.5
        for x in range(width):
            fx = x + 0.5
            pixel_x = x
            pixel_y = height - 1 - y  # bottom-left pixel row
            quad_x, quad_y = pixel_x >> 1, pixel_y >> 1
            lanes = lane_cache.get((quad_x, quad_y))
            if lanes is None:
                x0, y0 = quad_x * 2 + 0.5, quad_y * 2 + 0.5
                lanes = [probe(x0, y0), probe(x0 + 1, y0), probe(x0, y0 + 1), probe(x0 + 1, y0 + 1)]
                lane_cache[(quad_x, quad_y)] = lanes
            xp, yp = pixel_x & 1, pixel_y & 1
            dkey = (quad_x, quad_y, xp, yp)
            diffs = diff_cache.get(dkey)
            if diffs is None:
                diffs = rt.deriv_fine(lanes, xp, yp)
                diff_cache[dkey] = diffs
            set_frag(fx, fy)
            rt.deriv_reset("replay", diffs)
            out = [0.0, 0.0, 0.0, 0.0]
            kernel(ctx, out)
            i = (y * width + x) * 4
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


def run_pass_mrt(kernel, ctx: Ctx, width: int, height: int) -> list[Surface]:
    """Run a kernel with multiple ``out vec4`` declarations into one surface
    per declared output, preserving declaration/location order."""
    output_names = getattr(kernel, "output_names", ())
    if len(output_names) < 2:
        raise ValueError("run_pass_mrt requires a kernel with at least two outputs")
    surfaces = [Surface(width, height) for _ in output_names]
    outputs = [[0.0, 0.0, 0.0, 0.0] for _ in output_names]
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
            kernel(ctx, outputs)
            offset = base + x * 4
            for surface, output in zip(surfaces, outputs, strict=True):
                surface.data[offset : offset + 4] = output
    return surfaces
