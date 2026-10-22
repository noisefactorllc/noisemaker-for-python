import pytest

from noisemaker_cpu.iteration import (
    ITERATION_DELTA_TIME,
    compute_iteration_groups,
    is_particle_state_name,
    iteration_schedule,
)


def _effect(effect_id):
    return {"kind": "effect", "effect_id": effect_id}


def test_particle_state_name_is_narrow():
    assert is_particle_state_name("global_xyz")
    assert is_particle_state_name("global_life_data")
    assert is_particle_state_name("global_points_trail")
    # Upstream's expander scopes each behavior base_color memory into the
    # particle pipeline; a merely global_-prefixed scratch texture stays outside.
    assert is_particle_state_name("global_dla_base_color")
    assert is_particle_state_name("global_flock_base_color")
    assert not is_particle_state_name("global_rd_state")


def test_particle_chain_forms_one_iterated_group():
    effects = {
        "render/pointsEmit": {
            "iterated": True,
            "textures": {"global_xyz": {}},
            "passes": [],
        },
        "points/flow": {
            "iterated": True,
            "textures": {},
            "passes": [{"inputs": {"xyzTex": "global_xyz"}}],
        },
        "render/pointsRender": {
            "iterated": True,
            "textures": {},
            "passes": [{"inputs": {"xyzTex": "global_xyz"}, "outputs": {"fragColor": "global_points_trail"}}],
        },
        "filter/invert": {"passes": [], "textures": {}},
    }
    steps = [
        _effect("render/pointsEmit"),
        _effect("points/flow"),
        _effect("render/pointsRender"),
        _effect("filter/invert"),
    ]

    groups = compute_iteration_groups(steps, effects)

    assert groups == [
        {"steps": steps[:3], "iterated": True},
        {"steps": steps[3:], "iterated": False},
    ]


def test_read_and_write_steps_break_particle_groups():
    effects = {
        "render/pointsEmit": {"iterated": True, "textures": {"global_xyz": {}}, "passes": []},
    }
    read = {"kind": "read", "surface": "o0"}
    write = {"kind": "write", "surface": "o1"}
    steps = [_effect("render/pointsEmit"), write, read]

    groups = compute_iteration_groups(steps, effects)

    assert groups == [
        {"steps": steps[:1], "iterated": True},
        {"steps": [write], "iterated": False},
        {"steps": [read], "iterated": False},
    ]


def test_iteration_schedule_anchors_last_tick_to_requested_time():
    assert iteration_schedule(0.25, 3) == [
        {"frame": 0, "delta_time": ITERATION_DELTA_TIME, "time": pytest.approx(0.25 - 2 * ITERATION_DELTA_TIME)},
        {"frame": 1, "delta_time": ITERATION_DELTA_TIME, "time": pytest.approx(0.25 - ITERATION_DELTA_TIME)},
        {"frame": 2, "delta_time": ITERATION_DELTA_TIME, "time": pytest.approx(0.25)},
    ]


def test_iteration_schedule_wraps_time_and_allows_zero_iterations():
    assert iteration_schedule(0.0, 0) == []
    assert iteration_schedule(0.0, 2)[0]["time"] == pytest.approx(1.0 - ITERATION_DELTA_TIME)


def test_balanced_loop_region_forms_one_iteration_group():
    effects = {
        "synth/solid": {"passes": [], "textures": {}},
        "render/loopBegin": {
            "iterated": True,
            "loopRole": "begin",
            "passes": [],
            "textures": {},
        },
        "filter/blur": {"passes": [], "textures": {}},
        "render/loopEnd": {"loopRole": "end", "passes": [], "textures": {}},
        "filter/invert": {"passes": [], "textures": {}},
    }
    steps = [
        _effect("synth/solid"),
        _effect("render/loopBegin"),
        _effect("filter/blur"),
        _effect("render/loopEnd"),
        _effect("filter/invert"),
    ]

    groups = compute_iteration_groups(steps, effects)

    assert groups == [
        {"steps": [steps[0]], "iterated": False},
        {"steps": steps[1:4], "iterated": True, "loop": True},
        {"steps": [steps[4]], "iterated": False},
    ]


def test_flow3d_absorbs_the_preceding_animated_noise3d_group():
    # The authority re-runs animated noise3d before every flow3d tick: a
    # single-step synth3d/noise3d group immediately before a positive-iteration
    # flow3d joins flow3d's iterated group. A static noise3d (speed 0) and a
    # zero-iteration flow3d both keep the chains independent.
    effects = {
        "synth3d/noise3d": {"passes": [], "textures": {}},
        "filter3d/flow3d": {"iterated": True, "passes": [], "textures": {}},
    }

    def noise(speed):
        step = _effect("synth3d/noise3d")
        step["params"] = {"speed": speed}
        return step

    def flow(iteration_count):
        step = _effect("filter3d/flow3d")
        step["params"] = {"iterationCount": iteration_count}
        return step

    animated, flow_step = noise(1), flow(2)
    assert compute_iteration_groups([animated, flow_step], effects) == [
        {"steps": [animated, flow_step], "iterated": True},
    ]

    static, slow_flow = noise(0), flow(2)
    assert compute_iteration_groups([static, slow_flow], effects) == [
        {"steps": [static], "iterated": False},
        {"steps": [slow_flow], "iterated": True},
    ]

    zero_flow = flow(0)
    static_case = _effect("synth3d/noise3d")
    static_case["params"] = {"speed": 1}
    assert compute_iteration_groups([static_case, zero_flow], effects) == [
        {"steps": [static_case], "iterated": False},
        {"steps": [zero_flow], "iterated": True},
    ]


@pytest.mark.parametrize(("speed", "count", "joins"), [(1, 3, True), (0, 3, False), (1, 0, False)])
def test_cpu_sync_particle_owner_repeats_animated_input_only_when_needed(speed, count, joins):
    effects = {
        "synth/noise": {
            "kind": "generator",
            "domain": "image",
            "passes": [],
            "textures": {},
            "params": {"speed": {"default": 1}},
        },
        "render/pointsEmit": {"iterated": True, "textures": {"global_xyz": {}}, "passes": []},
    }
    image = {**_effect("synth/noise"), "params": {"speed": speed}}
    owner = {**_effect("render/pointsEmit"), "params": {"iterationCount": count}}
    groups = compute_iteration_groups([image, owner], effects)
    assert [group["steps"] for group in groups] == ([[image, owner]] if joins else [[image], [owner]])
