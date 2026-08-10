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
