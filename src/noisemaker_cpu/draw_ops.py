"""CPU-only draw operations for passes the GPU expresses with non-fragment draw
modes (e.g. point-scatter). Dispatched by render_effect for passes flagged
``drawMode`` that have no transpiled fragment kernel.

Port of noisemaker-cpu ``src/effects/cpu/wormhole.js`` (runWormholeDeposit).
"""

from __future__ import annotations

import math

import numpy as np

from .sampler import sample_bilinear, sample_nearest_bottom_left
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
            odata[do] = _float16_truncate(
                np.array([_add(float(odata[do]), _mul(float(idata[so]), weight))], dtype=F32)
            )[0]
            odata[do + 1] = _float16_truncate(
                np.array([_add(float(odata[do + 1]), _mul(float(idata[so + 1]), weight))], dtype=F32)
            )[0]
            odata[do + 2] = _float16_truncate(
                np.array([_add(float(odata[do + 2]), _mul(float(idata[so + 2]), weight))], dtype=F32)
            )[0]


GOLDEN_RATIO_CONJUGATE = 0.618033988749895
_TAU_APPROX = 6.283185
_QUAD_CORNERS = ((-1, -1), (1, -1), (-1, 1), (1, 1))


def _fract(value):
    return value - math.floor(value)


def texel_fetch_agent(surface, sx, sy):
    x = min(max(sx, 0), surface.width - 1)
    shader_y = min(max(sy, 0), surface.height - 1)
    row = surface.height - 1 - shader_y
    offset = (row * surface.width + x) * 4
    return [float(value) for value in surface.data[offset : offset + 4]]


def scatter_point_pixel(clip_x, clip_y, clip_w, dest_width, dest_height):
    if not clip_w > 0:
        return None
    pixel_x = (clip_x / clip_w * 0.5 + 0.5) * dest_width
    pixel_y = (clip_y / clip_w * 0.5 + 0.5) * dest_height
    if not math.isfinite(pixel_x) or not math.isfinite(pixel_y):
        return None
    gl_col = math.floor(pixel_x)
    gl_row = math.floor(pixel_y)
    if gl_col < 0 or gl_col >= dest_width or gl_row < 0 or gl_row >= dest_height:
        return None
    storage_row = dest_height - 1 - gl_row
    return (storage_row * dest_width + gl_col) * 4


def _compute_clip_center(x, y, z, uniforms):
    if int(uniforms["viewMode"]) == 0:
        return x * 2 - 1, y * 2 - 1
    is_2d = abs(z) < 1 and 0 <= x <= 1 and 0 <= y <= 1
    px, py, pz = (x - 0.5, y - 0.5, 0.0) if is_2d else (x, y, z)
    cos_x = math.cos(uniforms["rotateX"])
    sin_x = math.sin(uniforms["rotateX"])
    x1 = px
    y1 = py * cos_x - pz * sin_x
    z1 = py * sin_x + pz * cos_x
    cos_y = math.cos(uniforms["rotateY"])
    sin_y = math.sin(uniforms["rotateY"])
    x2 = x1 * cos_y + z1 * sin_y
    y2 = y1
    cos_z = math.cos(uniforms["rotateZ"])
    sin_z = math.sin(uniforms["rotateZ"])
    fx = x2 * cos_z - y2 * sin_z + uniforms["posX"]
    fy = x2 * sin_z + y2 * cos_z + uniforms["posY"]
    if is_2d:
        return fx * 3.5 * uniforms["viewScale"], fy * 3.5 * uniforms["viewScale"]
    return fx / 40 * uniforms["viewScale"], fy / 40 * uniforms["viewScale"]


def dla_deposit_grid(inputs, destination, uniforms, _render_pass):
    xyz_tex = inputs["xyzTex"]
    vel_tex = inputs["velTex"]
    rgba_tex = inputs["rgbaTex"]
    energy = uniforms["deposit"] * 0.1
    for vertex in range(xyz_tex.width * xyz_tex.height):
        sx = vertex % xyz_tex.width
        sy = vertex // xyz_tex.width
        if texel_fetch_agent(vel_tex, sx, sy)[1] < 0.5:
            continue
        xyz = texel_fetch_agent(xyz_tex, sx, sy)
        offset = scatter_point_pixel(
            xyz[0] * 2 - 1,
            xyz[1] * 2 - 1,
            1,
            destination.width,
            destination.height,
        )
        if offset is None:
            continue
        rgba = texel_fetch_agent(rgba_tex, sx, sy)
        destination.data[offset : offset + 3] += np.asarray(rgba[:3], dtype=F32) * energy
        destination.data[offset + 3] += energy


def lenia_deposit(inputs, destination, uniforms, _render_pass):
    xyz_tex = inputs["xyzTex"]
    for vertex in range(xyz_tex.width * xyz_tex.height):
        sx = vertex % xyz_tex.width
        sy = vertex // xyz_tex.width
        xyz = texel_fetch_agent(xyz_tex, sx, sy)
        if xyz[3] < 0.5:
            continue
        offset = scatter_point_pixel(
            xyz[0] * 2 - 1,
            xyz[1] * 2 - 1,
            1,
            destination.width,
            destination.height,
        )
        if offset is None:
            continue
        destination.data[offset] += uniforms["depositAmount"]
        destination.data[offset + 3] += 1


def physarum_deposit(inputs, destination, uniforms, _render_pass):
    xyz_tex = inputs["xyzTex"]
    rgba_tex = inputs["rgbaTex"]
    for vertex in range(xyz_tex.width * xyz_tex.height):
        sx = vertex % xyz_tex.width
        sy = vertex // xyz_tex.width
        xyz = texel_fetch_agent(xyz_tex, sx, sy)
        if xyz[3] < 0.5:
            continue
        offset = scatter_point_pixel(
            xyz[0] * 2 - 1,
            xyz[1] * 2 - 1,
            1,
            destination.width,
            destination.height,
        )
        if offset is None:
            continue
        rgba = np.asarray(texel_fetch_agent(rgba_tex, sx, sy), dtype=F32)
        destination.data[offset : offset + 4] += rgba * uniforms["deposit"]


def points_render_deposit(inputs, destination, uniforms, _render_pass):
    xyz_tex = inputs["xyzTex"]
    rgba_tex = inputs["rgbaTex"]
    threshold = uniforms["density"] / 100
    for vertex in range(xyz_tex.width * xyz_tex.height):
        if _fract(vertex * GOLDEN_RATIO_CONJUGATE) > threshold:
            continue
        sx = vertex % xyz_tex.width
        sy = vertex // xyz_tex.width
        xyz = texel_fetch_agent(xyz_tex, sx, sy)
        if xyz[3] < 0.5:
            continue
        clip_x, clip_y = _compute_clip_center(xyz[0], xyz[1], xyz[2], uniforms)
        offset = scatter_point_pixel(clip_x, clip_y, 1, destination.width, destination.height)
        if offset is None:
            continue
        destination.data[offset : offset + 4] += np.asarray(texel_fetch_agent(rgba_tex, sx, sy), dtype=F32)


def flow3d_deposit(inputs, destination, uniforms, render_pass):
    state1 = inputs["stateTex1"]
    state2 = inputs["stateTex2"]
    capacity = state1.width * state1.height
    max_agents = math.trunc(max(state1.width, state1.height) * uniforms["density"] * 0.2)
    draw_count = render_pass.get("count", capacity)
    count = max(0, min(int(draw_count), capacity, max_agents))
    volume_size = int(uniforms["volumeSize"])
    atlas_height = volume_size * volume_size
    for agent_index in range(count):
        state_x = agent_index % state1.width
        state_y = agent_index // state1.width
        position = texel_fetch_agent(state1, state_x, state_y)
        color = texel_fetch_agent(state2, state_x, state_y)
        atlas_x = position[0]
        atlas_y = position[1] + math.floor(position[2]) * volume_size
        offset = scatter_point_pixel(
            atlas_x / volume_size * 2 - 1,
            atlas_y / atlas_height * 2 - 1,
            1,
            destination.width,
            destination.height,
        )
        if offset is None:
            continue
        destination.data[offset : offset + 3] += np.asarray(color[:3], dtype=F32)
        destination.data[offset + 3] += 1


def _hash_uint32(seed):
    state = ((seed & 0xFFFFFFFF) * 747796405 + 2891336453) & 0xFFFFFFFF
    word = ((((state >> ((state >> 28) + 4)) ^ state) & 0xFFFFFFFF) * 277803737) & 0xFFFFFFFF
    return ((word >> 22) ^ word) & 0xFFFFFFFF


def _hash(value, seed):
    bits = int(np.asarray([F32(value + seed)], dtype=F32).view(np.uint32)[0])
    return _hash_uint32(bits) / 4294967295


def _sign(value):
    return -1 if value < 0 else 1 if value > 0 else 0


def _clamp(value, low, high):
    return min(max(value, low), high)


def _smoothstep(edge0, edge1, value):
    amount = _clamp((value - edge0) / (edge1 - edge0), 0, 1)
    return amount * amount * (3 - 2 * amount)


def _shape_distance(shape_mode, px, py):
    if shape_mode == 1:
        return math.hypot(px, py) - 0.45
    if shape_mode == 2:
        return abs(math.hypot(px, py) - 0.35) - 0.08
    if shape_mode == 3:
        return max(abs(px), abs(py)) - 0.4
    if shape_mode == 4:
        return abs(px) + abs(py) - 0.45
    if shape_mode == 5:
        radius = 0.25
        root_three = 1.732050808
        tx = abs(px) - radius
        ty = py - 0.04 + radius / root_three
        if tx + root_three * ty > 0:
            tx, ty = (tx - root_three * ty) / 2, (-root_three * tx - ty) / 2
        tx -= _clamp(tx, -2 * radius, 0)
        return -math.hypot(tx, ty) * _sign(ty)
    radius = 0.35
    radius_factor = 0.4
    k1x, k1y = 0.809016994375, -0.587785252292
    k2x, k2y = -k1x, k1y
    sx, sy = abs(px), py
    projection = max(k1x * sx + k1y * sy, 0)
    sx -= 2 * projection * k1x
    sy -= 2 * projection * k1y
    projection = max(k2x * sx + k2y * sy, 0)
    sx = abs(sx - 2 * projection * k2x)
    sy = sy - 2 * projection * k2y - radius
    bax, bay = radius_factor * -k1y, radius_factor * k1x - 1
    amount = _clamp((sx * bax + sy * bay) / (bax * bax + bay * bay), 0, radius)
    return math.hypot(sx - bax * amount, sy - bay * amount) * _sign(sy * bax - sx * bay)


def _billboard_fragment(shape_mode, sprite, u, v, color, opacity):
    if shape_mode == 0:
        sample = (
            sample_bilinear(sprite, u, v) if sprite.filter == "linear" else sample_nearest_bottom_left(sprite, u, v)
        )
        return np.asarray(sample, dtype=F32) * np.asarray(color, dtype=F32) * opacity
    px, py = u - 0.5, v - 0.5
    if 1 <= shape_mode <= 6:
        alpha = 1 - _smoothstep(-0.02, 0.02, _shape_distance(shape_mode, px, py))
    else:
        alpha = math.exp(-(px * px + py * py) * 8)
    return np.asarray([color[0] * alpha, color[1] * alpha, color[2] * alpha, alpha * color[3]], dtype=F32) * opacity


def points_billboard_render_deposit(inputs, destination, uniforms, render_pass):
    xyz_tex = inputs["xyzTex"]
    rgba_tex = inputs["rgbaTex"]
    sprite_tex = inputs["spriteTex"]
    threshold = uniforms["density"] / 100
    shape_mode = int(uniforms["shapeMode"])
    opacity = uniforms["depositOpacity"] / 100
    size_variation = uniforms["sizeVariation"] / 100
    rotation_variation = uniforms["rotationVar"] / 100
    blend = render_pass.get("blend")
    premultiplied = isinstance(blend, list) and [str(value).upper() for value in blend] == [
        "ONE",
        "ONE_MINUS_SRC_ALPHA",
    ]
    for vertex in range(xyz_tex.width * xyz_tex.height):
        if _fract(vertex * GOLDEN_RATIO_CONJUGATE) > threshold:
            continue
        sx = vertex % xyz_tex.width
        sy = vertex // xyz_tex.width
        xyz = texel_fetch_agent(xyz_tex, sx, sy)
        if xyz[3] < 0.5:
            continue
        color = texel_fetch_agent(rgba_tex, sx, sy)
        center_x, center_y = _compute_clip_center(xyz[0], xyz[1], xyz[2], uniforms)
        final_size = uniforms["pointSize"] * (1 - size_variation * (_hash(vertex, uniforms["seed"]) - 0.5))
        if not final_size > 0:
            continue
        rotation = rotation_variation * _hash(vertex + 1234.5, uniforms["seed"]) * _TAU_APPROX
        cos_rotation, sin_rotation = math.cos(rotation), math.sin(rotation)
        size_clip_x = final_size / destination.width
        size_clip_y = final_size / destination.height
        corners = []
        for ox, oy in _QUAD_CORNERS:
            rotated_x = ox * cos_rotation - oy * sin_rotation
            rotated_y = ox * sin_rotation + oy * cos_rotation
            corners.append(
                (
                    (center_x + rotated_x * size_clip_x) * 0.5 * destination.width + destination.width * 0.5,
                    (center_y + rotated_y * size_clip_y) * 0.5 * destination.height + destination.height * 0.5,
                )
            )
        col_start = max(0, math.floor(min(point[0] for point in corners)))
        col_end = min(destination.width - 1, math.ceil(max(point[0] for point in corners)))
        row_start = max(0, math.floor(min(point[1] for point in corners)))
        row_end = min(destination.height - 1, math.ceil(max(point[1] for point in corners)))
        for gl_row in range(row_start, row_end + 1):
            b = ((((gl_row + 0.5) / destination.height) * 2 - 1) - center_y) / size_clip_y
            storage_row = destination.height - 1 - gl_row
            for column in range(col_start, col_end + 1):
                a = ((((column + 0.5) / destination.width) * 2 - 1) - center_x) / size_clip_x
                offset_x = a * cos_rotation + b * sin_rotation
                offset_y = -a * sin_rotation + b * cos_rotation
                if offset_x < -1 or offset_x > 1 or offset_y < -1 or offset_y > 1:
                    continue
                source = _billboard_fragment(
                    shape_mode,
                    sprite_tex,
                    offset_x * 0.5 + 0.5,
                    offset_y * 0.5 + 0.5,
                    color,
                    opacity,
                )
                dest_offset = (storage_row * destination.width + column) * 4
                if premultiplied:
                    destination.data[dest_offset : dest_offset + 4] = source + destination.data[
                        dest_offset : dest_offset + 4
                    ] * (1 - source[3])
                else:
                    destination.data[dest_offset : dest_offset + 4] += source


def _wormhole_draw(inputs, destination, uniforms, _render_pass):
    wormhole_deposit(inputs["inputTex"], destination, uniforms)


POINT_DRAW_OPS = {
    "filter/wormhole:deposit": _wormhole_draw,
    "filter3d/flow3d:deposit": flow3d_deposit,
    "points/dla:depositGrid": dla_deposit_grid,
    "points/lenia:deposit": lenia_deposit,
    "points/physarum:deposit": physarum_deposit,
    "render/pointsRender:deposit": points_render_deposit,
    "render/pointsBillboardRender:deposit": points_billboard_render_deposit,
}


def get_draw_op(effect_id, program):
    return POINT_DRAW_OPS.get(f"{effect_id}:{program}")
