"""Port of the CPU remap adapter's polygon coverage and premultiplied compositing."""

from __future__ import annotations

import math

from . import register


def _zones(ctx, width, height, feather):
    """Resolve active polygons and their feathered rejection bounds once per pass."""
    uniforms = ctx.uniforms
    zones = []
    for index in reversed(range(min(int(uniforms.get("zoneCount", 0)), 8))):
        zone = f"zone{index}"
        count = min(int(uniforms.get(f"{zone}_count", 0)), 64)
        if count < 3 or uniforms.get(f"{zone}_active", 0) < 0.5:
            continue
        vertices = []
        for vertex in range(count):
            pair = uniforms.get(f"{zone}_v{vertex // 2}", (0, 0, 0, 0))
            offset = (vertex % 2) * 2
            vertices.append((float(pair[offset]) * width, float(pair[offset + 1]) * height))
        edges = []
        bx, by = vertices[-1]
        for ax, ay in vertices:
            ex, ey = bx - ax, by - ay
            edges.append((ax, ay, by, ex, ey, max(ex * ex + ey * ey, 1e-6)))
            bx, by = ax, ay
        x0, y0, x1, y1 = uniforms.get(f"{zone}_bounds", (0, 0, 1, 1))
        bounds = (x0 - feather / width, y0 - feather / height, x1 + feather / width, y1 + feather / height)
        zones.append((bounds, edges, ctx.textures[f"{zone}_tex"], uniforms.get(f"{zone}_alpha", 1)))
    return zones


def _coverage(edges, qx, qy, feather):
    inside = False
    distance_squared = 1e30
    for ax, ay, by, ex, ey, length_squared in edges:
        wx, wy = qx - ax, qy - ay
        if (qy >= ay) == (qy < by) == (ex * wy > ey * wx):
            inside = not inside
        if feather:
            s = min(max((wx * ex + wy * ey) / length_squared, 0.0), 1.0)
            rx, ry = wx - ex * s, wy - ey * s
            distance_squared = min(distance_squared, rx * rx + ry * ry)
    if inside:
        return 1.0
    if not feather:
        return 0.0
    t = min(math.sqrt(distance_squared) / feather, 1.0)
    return 1.0 - t * t * (3.0 - 2.0 * t)


@register("synth/remap:remap")
def remap_factory(rt, _base_kernel):
    zones = None

    def kernel(ctx, out):
        nonlocal zones
        rt.begin_pixel(ctx)
        uniforms = ctx.uniforms
        width, height = map(float, uniforms["fullResolution"])
        feather = max(uniforms.get("smoothEdge", 0), 0) * 0.05 * min(width, height)
        if zones is None:
            zones = _zones(ctx, width, height, feather)
        frag_x, frag_y = map(float, ctx.frag_coord[:2])
        tile_x, tile_y = uniforms.get("tileOffset", (0, 0))
        qx, qy = frag_x + float(tile_x), height - (frag_y + float(tile_y))
        px, py = qx / width, qy / height
        resolution_x, resolution_y = map(float, uniforms["resolution"])
        sample_uv = (frag_x / resolution_x, frag_y / resolution_y)
        color = [0.0, 0.0, 0.0, 0.0]
        for (x0, y0, x1, y1), edges, texture, alpha in zones:
            if px < x0 or py < y0 or px > x1 or py > y1:
                continue
            coverage = _coverage(edges, qx, qy, feather)
            if coverage <= 0:
                continue
            weight = coverage * alpha
            remaining = 1.0 - color[3]
            for channel, value in enumerate(rt.texture(texture, sample_uv)):
                color[channel] += float(value) * weight * remaining
            if color[3] >= 0.999:
                break
        remaining = 1.0 - color[3]
        bg_alpha = uniforms.get("bgAlpha", 1)
        for channel, value in enumerate(uniforms.get("bgColor", (0, 0, 0))[:3]):
            color[channel] += float(value) * bg_alpha * remaining
        color[3] += bg_alpha * remaining
        out[:] = color

    return kernel
