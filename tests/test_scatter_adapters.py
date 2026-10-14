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


def test_dla_deposit_grid_accumulates_in_float64_and_rounds_once():
    # The sibling adds rgba * energy to a Float32Array slot in float64, with
    # energy = deposit * 0.1 unrounded, and rounds once on store. Expected
    # values are noisemaker-for-cpu's dlaDepositGridAdapter on these inputs;
    # float32 arithmetic gives 1.2001065015792847.
    inputs = {
        "xyzTex": _surface(1, 1, [[0.5, 0.5, 0.0, 1.0]]),
        "velTex": _surface(1, 1, [[0.0, 1.0, 0.0, 0.0]]),
        "rgbaTex": _surface(1, 1, [[0.9956448078155518, 0.0, 0.0, 1.0]]),
    }
    destination = _surface(1, 1, [[0.23433096706867218, 0.0, 0.0, 0.0]])

    dla_deposit_grid(inputs, destination, {"deposit": 9.7}, {})

    assert [float(c) for c in destination.data] == [1.2001063823699951, 0.0, 0.0, 0.9700000286102295]


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


def test_points_render_density_cull_rounds_cull_value_to_f32_at_65536_agents():
    # The sibling's pointsRenderDepositAdapter frounds the golden-ratio cull
    # product to f32 (highp float) before the fract (points-deposit.js, M4
    # parity); expected values are noisemaker-for-cpu's scatter-adapters.test.js
    # on the same inputs. float64 arithmetic culls only 65 of the 65536 agents.
    xyz = _surface(256, 256, [[0.5, 0.5, 0.0, 1.0]] * (256 * 256))
    rgba = _surface(256, 256, [[1.0, 0.0, 0.0, 1.0]] * (256 * 256))
    destination = Surface(8, 8)

    points_render_deposit(
        {"xyzTex": xyz, "rgbaTex": rgba},
        destination,
        {
            "density": 0.1,
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

    offset = (3 * 8 + 4) * 4
    assert [float(c) for c in destination.data[offset:offset + 4]] == [142.0, 0.0, 0.0, 142.0]
    assert float(destination.data.sum()) == 284.0


def test_lenia_deposit_rounds_each_additive_blend_into_an_rgba16f_target():
    # The sibling's leniaDepositAdapter rounds every additive write back into
    # an rgba16f attachment (truncation to half after each point); expected
    # values are noisemaker-for-cpu's scatter-adapters.test.js on the same
    # inputs. r grows by one half-ULP per deposit until 4096, where a 3.6
    # addend truncates away; alpha stops at 2048 the same way.
    xyz = _surface(64, 64, [[0.5, 0.5, 0.0, 1.0]] * (64 * 64))
    destination = Surface(4, 4)
    destination.format = "rgba16f"

    lenia_deposit({"xyzTex": xyz}, destination, {"depositAmount": 3.6}, {})

    offset = (1 * 4 + 2) * 4
    assert [float(c) for c in destination.data[offset:offset + 4]] == [4096.0, 0.0, 0.0, 2048.0]


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

    # M4/Metal rasterization (GAP-003 alignment): atlasY = 2 + 3*4 = 14.
    # The 1/256 subpixel snap assigns an integer boundary to the LOWER GL
    # pixel, so an exact boundary lands at gl_row 13 / gl_col 0 — storage row
    # 16-1-13 = 2, col 0. (The pre-alignment floor mapping placed it at row 1,
    # col 1; the sibling's own updated fixture asserts the new placement.)
    storage_y = 2
    offset = (storage_y * destination.width + 0) * 4
    assert np.array_equal(destination.data[offset : offset + 4], np.array([0.25, 0.5, 0.75, 1.0], dtype=np.float32))
    # The pre-alignment location must stay untouched.
    assert np.count_nonzero(destination.data[0 * destination.width * 4 : (storage_y) * destination.width * 4]) == 0


def _flow3d_poke(surface, sx, sy, rgba):
    row = surface.height - 1 - sy
    offset = (row * surface.width + sx) * 4
    surface.data[offset : offset + 4] = np.array(rgba, dtype=np.float32)


def _flow3d_pixel(surface, row, col):
    offset = (row * surface.width + col) * 4
    return [float(value) for value in surface.data[offset : offset + 4]]


def test_flow3d_deposit_places_integer_atlas_boundaries_in_the_lower_gl_pixel():
    # The M4/Metal point rasterizer snaps window positions to 1/256 pixel and
    # assigns an integer boundary to the lower GL pixel. Mirrors the sibling's
    # scatter-adapters coverage of the GAP-003 rasterization alignment.
    state1 = _surface(2, 1, [[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]])
    state2 = _surface(2, 1, [[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]])
    _flow3d_poke(state1, 0, 0, [20, 1.9599609375, 5.7421875, 0])
    _flow3d_poke(state1, 1, 0, [20.71875, 17, 29.671875, 0])
    _flow3d_poke(state2, 0, 0, [0.5, 0, 0, 1])
    _flow3d_poke(state2, 1, 0, [0.25, 0, 0, 1])
    destination = Surface(32, 1024)

    flow3d_deposit(
        {"stateTex1": state1, "stateTex2": state2},
        destination,
        {"density": 100.0, "volumeSize": 32},
        {"count": 2},
    )

    assert _flow3d_pixel(destination, 862, 19) == [0.5, 0.0, 0.0, 1.0]
    assert _flow3d_pixel(destination, 862, 20) == [0.0, 0.0, 0.0, 0.0]
    assert _flow3d_pixel(destination, 79, 20) == [0.25, 0.0, 0.0, 1.0]
    assert _flow3d_pixel(destination, 78, 20) == [0.0, 0.0, 0.0, 0.0]


def test_flow3d_deposit_rounds_atlas_addition_as_gsl_float_before_raster():
    # atlasY is rounded through Math.fround (f32) BEFORE raster placement:
    # 0.0001220703125 + 4032 must round to exactly 4032 in f32, placing the
    # deposit at GL row 4031 (storage row 64), not row 4032 (storage row 63).
    state1 = _surface(1, 1, [[1.25, 0.0001220703125, 63, 0]])
    state2 = _surface(1, 1, [[0.5, 0, 0, 1]])
    destination = Surface(64, 4096)

    flow3d_deposit(
        {"stateTex1": state1, "stateTex2": state2},
        destination,
        {"density": 100.0, "volumeSize": 64},
        {"count": 1},
    )

    assert _flow3d_pixel(destination, 64, 1) == [0.5, 0.0, 0.0, 1.0]
    assert _flow3d_pixel(destination, 63, 1) == [0.0, 0.0, 0.0, 0.0]


def test_flow3d_deposit_culls_points_inside_the_m4_viewport_subpixel_edge():
    # A center within half a subpixel step of the left or bottom edge produces
    # no fragment under the M4 rasterization model.
    for volume_size, position in (
        (32, [0.00032138824462890625, 22.546875, 13.6015625, 0]),
        (32, [1 / 512, 22.546875, 13.6015625, 0]),
        (64, [1.25, 0.00006103515625, 0, 0]),
        (64, [1.25, 1 / 512, 0, 0]),
    ):
        state1 = _surface(1, 1, [position])
        state2 = _surface(1, 1, [[0.5, 0, 0, 1]])
        destination = Surface(volume_size, volume_size**2)

        flow3d_deposit(
            {"stateTex1": state1, "stateTex2": state2},
            destination,
            {"density": 100.0, "volumeSize": volume_size},
            {"count": 1},
        )

        assert np.count_nonzero(destination.data) == 0, (volume_size, position)


def test_flow3d_deposit_snaps_half_subpixel_inputs_with_js_round_ties():
    # A position exactly half a subpixel step past an integer must round UP
    # like JS Math.round (ties toward +infinity), not like Python round()'s
    # ties-to-even: x*256 = 512.5 rounds to 512 under banker's rounding but
    # 513 under Math.round. input 2.001953125 (f32-exact) * 256 = 512.5.
    state1 = _surface(1, 1, [[2.001953125, 1.25, 0, 0]])
    state2 = _surface(1, 1, [[0.5, 0, 0, 1]])
    destination = Surface(32, 1024)

    flow3d_deposit(
        {"stateTex1": state1, "stateTex2": state2},
        destination,
        {"density": 100.0, "volumeSize": 32},
        {"count": 1},
    )

    # Math.round(512.5)=513 -> ceil(513/256)-1 = 2. Banker's rounding would
    # give ceil(512/256)-1 = 1. atlasY = 1.25 -> gl_row 1 -> storage row 1022.
    assert _flow3d_pixel(destination, 1022, 2) == [0.5, 0.0, 0.0, 1.0]
    assert _flow3d_pixel(destination, 1022, 1) == [0.0, 0.0, 0.0, 0.0]


def test_flow3d_deposit_snaps_near_integer_atlas_positions_to_the_subpixel_grid():
    state1 = _surface(2, 1, [[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]])
    state2 = _surface(2, 1, [[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]])
    _flow3d_poke(state1, 0, 0, [1.0009765625, 0.25, 1.1, 0])
    _flow3d_poke(state1, 1, 0, [2.25, 1.0009765625, 1.1, 0])
    _flow3d_poke(state2, 0, 0, [0.5, 0, 0, 1])
    _flow3d_poke(state2, 1, 0, [0.25, 0, 0, 1])
    destination = Surface(32, 1024)

    flow3d_deposit(
        {"stateTex1": state1, "stateTex2": state2},
        destination,
        {"density": 100.0, "volumeSize": 32},
        {"count": 2},
    )

    assert _flow3d_pixel(destination, 991, 0) == [0.5, 0.0, 0.0, 1.0]
    assert _flow3d_pixel(destination, 991, 1) == [0.0, 0.0, 0.0, 0.0]
    assert _flow3d_pixel(destination, 991, 2) == [0.25, 0.0, 0.0, 1.0]
    assert _flow3d_pixel(destination, 990, 2) == [0.0, 0.0, 0.0, 0.0]


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
