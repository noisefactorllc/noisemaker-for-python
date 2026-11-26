"""Small remap renders checked against the pinned CPU renderer."""

from noisemaker_cpu.renderer import render_dsl


def _remap(args, width, height):
    return render_dsl(
        "search synth\nsolid(color: #ff8040).write(o1)\n"
        f"remap(bgColor: #0000ff, zoneCount: 1, smoothEdge: 0, zone0_tex: read(o1){args}).write(o0)\nrender(o0)",
        width=width,
        height=height,
    ).to_rgba8()


def test_remap_clips_and_composites_a_custom_polygon():
    pixels = _remap(
        ", zone0_count: 4, zone0_alpha: 0.5, zone0_bounds: vec4(0, 0, 0.6, 1,), "
        "zone0_v0: [0.35, 0.2, 0.9, 0.3], zone0_v1: [0.8, 0.9, 0.35, 0.8]",
        6,
        4,
    )
    blue = bytes([0, 0, 255, 255])
    overlay = bytes([128, 64, 159, 255])
    middle_row = blue * 2 + overlay * 2 + blue * 2
    assert pixels == blue * 6 + middle_row * 2 + blue * 6


def test_remap_bounds_preserve_coordinates_either_side_of_a_pixel_center():
    pixels = _remap(
        ", zone0_count: 4, zone0_bounds: vec4(0.375000000001, 0, 1, 1,), "
        "zone0_v0: [0, 0, 1, 0], zone0_v1: [1, 1, 0, 1]",
        4,
        2,
    )
    assert pixels == (bytes([0, 0, 255, 255]) * 2 + bytes([255, 128, 64, 255]) * 2) * 2


def test_remap_bound_texture_without_polygon_uses_background():
    assert _remap("", 3, 2) == bytes([0, 0, 255, 255]) * 6
