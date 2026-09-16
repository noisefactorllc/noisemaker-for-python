import numpy as np

from noisemaker_cpu.draw_ops import (
    dla_deposit_grid,
    flow3d_deposit,
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
        ("filter3d/flow3d", "deposit"),
        ("points/dla", "depositGrid"),
        ("points/lenia", "deposit"),
        ("points/physarum", "deposit"),
        ("render/pointsRender", "deposit"),
        ("render/pointsBillboardRender", "deposit"),
    ):
        assert get_draw_op(*key) is not None


def test_flow3d_deposit_flattens_voxel_z_into_volume_atlas():
    inputs = {
        "stateTex1": _surface(1, 1, [[1.0, 2.0, 3.0, 1.0]]),
        "stateTex2": _surface(1, 1, [[0.25, 0.5, 0.75, 1.0]]),
    }
    destination = Surface(4, 16)

    flow3d_deposit(inputs, destination, {"density": 100.0, "volumeSize": 4}, {"count": 1})

    shader_y = 2 + 3 * 4
    storage_y = destination.height - 1 - shader_y
    offset = (storage_y * destination.width + 1) * 4
    assert np.array_equal(destination.data[offset : offset + 4], np.array([0.25, 0.5, 0.75, 1.0], dtype=np.float32))


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


def _billboard_base_uniforms(**overrides):
    uniforms = {
        "density": 100.0,
        "shapeMode": 1,
        "depositOpacity": 100.0,
        "pointSize": 4.0,
        "sizeVariation": 0.0,
        "rotationVar": 0.0,
        "seed": 0,
        "viewMode": 1,
        "rotateX": 0.0,
        "rotateY": 0.0,
        "rotateZ": 0.0,
        "viewScale": 1.0,
        "posX": 0.0,
        "posY": 0.0,
        "posZ": 0.0,
        "fieldOfView": 60.0,
        "sizeDistance": 0.0,
        "brightnessDistance": 0.0,
        "aperture": 0.0,
        "focalDistance": 80.0,
        "blendMode": 0,
        "blurLayer": 0,
        "resolution": np.array([16.0, 16.0], dtype=np.float32),
    }
    uniforms.update(overrides)
    return uniforms


def test_billboard_perspective_mode_draws_a_finite_footprint():
    destination = Surface(16, 16)
    inputs = {
        "xyzTex": _surface(1, 1, [[2.0, 1.0, 0.0, 1.0]]),
        "rgbaTex": _surface(1, 1, [[1.0, 0.5, 0.25, 1.0]]),
        "spriteTex": Surface(1, 1),
    }
    uniforms = _billboard_base_uniforms(viewMode=2)

    points_billboard_render_deposit(inputs, destination, uniforms, {"blend": True})

    assert np.count_nonzero(destination.data) > 0
    assert np.isfinite(destination.data).all()


def test_billboard_perspective_mode_culls_agent_behind_near_plane():
    destination = Surface(8, 8)
    inputs = {
        "xyzTex": _surface(1, 1, [[0.0, 0.0, 100.0, 1.0]]),
        "rgbaTex": _surface(1, 1, [[1.0, 1.0, 1.0, 1.0]]),
        "spriteTex": Surface(1, 1),
    }
    uniforms = _billboard_base_uniforms(viewMode=2)

    points_billboard_render_deposit(inputs, destination, uniforms, {"blend": True})

    assert np.count_nonzero(destination.data) == 0


def test_billboard_depth_sort_reindexes_through_order_tex():
    destination = Surface(8, 8)
    inputs = {
        "xyzTex": _surface(2, 1, [[0.5, 0.5, 0.0, 1.0], [0.5, 0.5, 0.0, 1.0]]),
        "rgbaTex": _surface(2, 1, [[1.0, 0.0, 0.0, 1.0], [0.0, 1.0, 0.0, 1.0]]),
        "spriteTex": Surface(1, 1),
        # g channel (index 1) holds the ORIGINAL agent index each output slot should draw.
        "orderTex": _surface(2, 1, [[0.0, 1.0, 0.0, 1.0], [0.0, 0.0, 0.0, 1.0]]),
    }
    uniforms = _billboard_base_uniforms(blendMode=1, pointSize=2.0)

    points_billboard_render_deposit(inputs, destination, uniforms, {"blend": ["ONE", "ONE_MINUS_SRC_ALPHA"]})

    assert np.count_nonzero(destination.data) > 0


def test_billboard_blur_layer_gate_skips_whole_draw():
    destination = Surface(8, 8)
    inputs = {
        "xyzTex": _surface(1, 1, [[0.5, 0.5, 0.0, 1.0]]),
        "rgbaTex": _surface(1, 1, [[1.0, 1.0, 1.0, 1.0]]),
        "spriteTex": Surface(1, 1),
    }

    aperture_zero = Surface(8, 8)
    points_billboard_render_deposit(
        inputs, aperture_zero, _billboard_base_uniforms(blurLayer=1, aperture=0.0, blendMode=0), {"blend": True}
    )
    assert np.count_nonzero(aperture_zero.data) == 0

    alpha_blend = Surface(8, 8)
    points_billboard_render_deposit(
        inputs, alpha_blend, _billboard_base_uniforms(blurLayer=1, aperture=5.0, blendMode=1), {"blend": True}
    )
    assert np.count_nonzero(alpha_blend.data) == 0


def test_billboard_aperture_defocus_samples_sprite_mean_and_stays_finite():
    destination = Surface(16, 16)
    sprite_mean = Surface(5, 5)
    sprite_mean.data[:] = 0.2
    inputs = {
        "xyzTex": _surface(1, 1, [[0.5, 0.5, 40.0, 1.0]]),
        "rgbaTex": _surface(1, 1, [[1.0, 1.0, 1.0, 1.0]]),
        "spriteTex": Surface(1, 1),
        "spriteMeanTex": sprite_mean,
    }
    # blurLayer=1: a strongly defocused additive footprint's lowWeight saturates toward 1, so its
    # whole contribution routes to this (defocus-accumulation) clone.
    uniforms = _billboard_base_uniforms(blurLayer=1, pointSize=2.0, shapeMode=0, aperture=10.0, focalDistance=80.0)

    points_billboard_render_deposit(inputs, destination, uniforms, {"blend": True})

    assert np.count_nonzero(destination.data) > 0
    assert np.isfinite(destination.data).all()
    assert (destination.data >= 0).all()
