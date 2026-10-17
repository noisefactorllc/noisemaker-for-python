"""Direct scalar path for the billboard depth-merge fullscreen pass."""

from __future__ import annotations

import numpy as np

from . import register


@register("render/pointsBillboardRender:depthMerge")
def depth_merge_adapter(_rt, _base):
    def kernel(ctx, out):
        source = ctx.textures["orderTex"]
        data = source.data
        width, height = source.width, source.height
        count = width * height
        x = int(ctx.frag_coord[0])
        y = int(ctx.frag_coord[1])
        index = y * width + x
        run_length = int(ctx.uniforms["runLength"])

        def key_at(position):
            sx, sy = position % width, position // width
            offset = ((height - 1 - sy) * width + sx) * 4
            return float(data[offset]), float(data[offset + 1])

        if run_length >= count:
            offset = ((height - 1 - y) * width + x) * 4
            out[:] = data[offset : offset + 4]
            return

        def before(a, b):
            return a[0] < b[0] or (a[0] == b[0] and a[1] <= b[1])

        start = index // (2 * run_length) * (2 * run_length)
        length_a = min(run_length, count - start)
        length_b = min(run_length, count - start - length_a)
        diagonal = index - start
        low = max(0, diagonal - length_b)
        high = min(diagonal, length_a)
        for _ in range(22):
            if low >= high:
                break
            mid = (low + high) // 2
            other = diagonal - mid
            if mid < length_a and other > 0 and before(
                key_at(start + mid), key_at(start + length_a + other - 1)
            ):
                low = mid + 1
            else:
                high = mid
        other = diagonal - low
        maximum = float(np.finfo(np.float32).max)
        a = key_at(start + low) if low < length_a else (maximum, maximum)
        b = key_at(start + length_a + other) if other < length_b else (maximum, maximum)
        winner = a if before(a, b) else b
        out[:] = (winner[0], winner[1], 0.0, 1.0)

    kernel.output_names = ("fragColor",)
    return kernel
