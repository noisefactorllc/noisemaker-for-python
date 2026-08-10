import numpy as np

from noisemaker_cpu.draw_ops import (
    dla_deposit_grid,
    get_draw_op,
    lenia_deposit,
    points_billboard_render_deposit,
    points_render_deposit,
    scatter_point_pixel,
    texel_fetch_agent,
)
from noisemaker_cpu.surface import Surface


def _surface(width, height, pixels):
    return Surface(width, height, np.array(pixels, dtype=np.float32).reshape(-1))


def test_texel_fetch_agent_flips_gl_row_to_top_down_storage():
    surface = _surface(1, 2, [[1, 0, 0, 1], [0, 1, 0, 1]])

    assert texel_fetch_agent(surface, 0, 0) == [0, 1, 0, 1]
    assert texel_fetch_agent(surface, 0, 1) == [1, 0, 0, 1]


def test_scatter_point_pixel_maps_clip_center_and_discards_invalid_points():
    assert scatter_point_pixel(0.0, 0.0, 1.0, 3, 3) == (1 * 3 + 1) * 4
    assert scatter_point_pixel(2.0, 0.0, 1.0, 3, 3) is None
    assert scatter_point_pixel(float("nan"), 0.0, 1.0, 3, 3) is None
    assert scatter_point_pixel(0.0, 0.0, 0.0, 3, 3) is None


def test_dla_deposit_grid_adds_stuck_agent_color_and_energy():
    inputs = {
        "xyzTex": _surface(1, 1, [[0.5, 0.5, 0.0, 1.0]]),
        "velTex": _surface(1, 1, [[0.0, 1.0, 0.0, 0.0]]),
        "rgbaTex": _surface(1, 1, [[0.25, 0.5, 0.75, 1.0]]),
    }
    destination = Surface(1, 1)

    dla_deposit_grid(inputs, destination, {"deposit": 10.0}, {})

    assert np.array_equal(destination.data, np.array([0.25, 0.5, 0.75, 1.0], dtype=np.float32))


def test_lenia_and_points_render_deposit_alive_agents():
    xyz = _surface(1, 1, [[0.5, 0.5, 0.0, 1.0]])
    rgba = _surface(1, 1, [[0.2, 0.4, 0.6, 0.8]])
    lenia_destination = Surface(1, 1)
    points_destination = Surface(1, 1)

    lenia_deposit({"xyzTex": xyz}, lenia_destination, {"depositAmount": 2.0}, {})
    points_render_deposit(
        {"xyzTex": xyz, "rgbaTex": rgba},
        points_destination,
        {
            "density": 100.0,
            "viewMode": 0,
            "rotateX": 0.0,
            "rotateY": 0.0,
            "rotateZ": 0.0,
            "viewScale": 1.0,
            "posX": 0.0,
            "posY": 0.0,
        },
        {},
    )

    assert np.array_equal(lenia_destination.data, np.array([2.0, 0.0, 0.0, 1.0], dtype=np.float32))
    assert np.allclose(points_destination.data, rgba.data)


def test_catalog_scatter_programs_are_registered():
    for key in (
        ("filter/wormhole", "deposit"),
        ("points/dla", "depositGrid"),
        ("points/lenia", "deposit"),
        ("points/physarum", "deposit"),
        ("render/pointsRender", "deposit"),
        ("render/pointsBillboardRender", "deposit"),
    ):
        assert get_draw_op(*key) is not None


def test_billboard_additive_pass_rasterizes_procedural_shape():
    destination = Surface(3, 3)
    inputs = {
        "xyzTex": _surface(1, 1, [[0.5, 0.5, 0.0, 1.0]]),
        "rgbaTex": _surface(1, 1, [[1.0, 0.5, 0.25, 1.0]]),
        "spriteTex": Surface(1, 1),
    }
    uniforms = {
        "density": 100.0,
        "shapeMode": 1,
        "depositOpacity": 100.0,
        "pointSize": 1.0,
        "sizeVariation": 0.0,
        "rotationVar": 0.0,
        "seed": 1,
        "viewMode": 0,
        "rotateX": 0.0,
        "rotateY": 0.0,
        "rotateZ": 0.0,
        "viewScale": 1.0,
        "posX": 0.0,
        "posY": 0.0,
    }

    points_billboard_render_deposit(inputs, destination, uniforms, {"blend": True})

    assert destination.data.reshape(3, 3, 4)[1, 1, 3] > 0
