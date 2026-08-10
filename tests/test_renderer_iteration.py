import numpy as np
import pytest

from noisemaker_cpu import renderer


def _install_effect(monkeypatch, effect, kernel):
    monkeypatch.setattr(renderer, "_meta", lambda: {"effects": {"filter/test": effect}})
    monkeypatch.setattr(renderer, "_kernel_for", lambda _key: kernel)


def test_iterated_effect_persists_self_texture_and_iteration_uniforms(monkeypatch):
    effect = {
        "namespace": "filter",
        "kind": "filter",
        "iterated": True,
        "params": {"iterationCount": {"type": "int", "default": 60, "cpuOnly": True}},
        "textures": {},
        "passes": [
            {
                "name": "step",
                "program": "step",
                "key": "filter/test:step",
                "inputs": {"previous": "selfTex"},
                "outputs": {"fragColor": "outputTex"},
            }
        ],
    }
    seen = []

    def kernel(ctx, out):
        seen.append((ctx.uniforms["frame"], ctx.uniforms["deltaTime"], ctx.uniforms["time"]))
        out[:] = [float(ctx.textures["previous"].data[0]) + 1.0, 0.0, 0.0, 1.0]

    _install_effect(monkeypatch, effect, kernel)

    surface = renderer.render_effect("filter/test", {"iterationCount": 3}, width=1, height=1, time=0.25)

    assert surface.data[0] == 3.0
    assert [entry[0] for entry in seen] == [0, 1, 2]
    assert [entry[1] for entry in seen] == pytest.approx([1 / 600, 1 / 600, 1 / 600])
    assert seen[-1][2] == 0.25


def test_parameter_named_repeat_reuses_previous_attachment(monkeypatch):
    effect = {
        "namespace": "filter",
        "kind": "filter",
        "params": {"iterations": {"type": "int", "default": 3, "uniform": "iterations"}},
        "textures": {"state": {"format": "rgba32f"}},
        "passes": [
            {
                "name": "pressure",
                "program": "pressure",
                "key": "filter/test:pressure",
                "inputs": {"previous": "state"},
                "outputs": {"fragColor": "state"},
                "repeat": "iterations",
            }
        ],
    }

    def kernel(ctx, out):
        out[:] = [float(ctx.textures["previous"].data[0]) + 1.0, 0.0, 0.0, 1.0]

    _install_effect(monkeypatch, effect, kernel)

    surface = renderer.render_effect("filter/test", width=1, height=1)

    assert np.array_equal(surface.data, np.array([3.0, 0.0, 0.0, 1.0], dtype=np.float32))


def test_particle_chain_iterates_as_one_group_with_shared_state(monkeypatch):
    effects = {
        "render/emit": {
            "namespace": "render",
            "kind": "filter",
            "iterated": True,
            "params": {
                "iterationCount": {"type": "int", "default": 60, "cpuOnly": True},
                "stateSize": {"type": "int", "default": 256, "uniform": "stateSize"},
            },
            "textures": {
                "global_xyz": {
                    "format": "rgba32f",
                    "width": {"param": "stateSize"},
                    "height": {"param": "stateSize"},
                }
            },
            "passes": [
                {
                    "name": "emit",
                    "program": "emit",
                    "key": "render/emit:emit",
                    "inputs": {},
                    "outputs": {"fragColor": "global_xyz"},
                }
            ],
        },
        "points/move": {
            "namespace": "points",
            "kind": "filter",
            "iterated": True,
            "params": {
                "iterationCount": {"type": "int", "default": 60, "cpuOnly": True},
                "stateSize": {"type": "int", "default": 256, "uniform": "stateSize"},
            },
            "textures": {},
            "passes": [
                {
                    "name": "move",
                    "program": "move",
                    "key": "points/move:move",
                    "inputs": {"state": "global_xyz"},
                    "outputs": {"fragColor": "global_xyz"},
                }
            ],
        },
    }
    plan = {
        "chains": [
            {
                "steps": [
                    {
                        "kind": "effect",
                        "effect_id": "render/emit",
                        "params": {"iterationCount": 2, "stateSize": 2},
                        "surfaces": {},
                    },
                    {"kind": "effect", "effect_id": "points/move", "params": {}, "surfaces": {}},
                    {"kind": "write", "surface": "o0"},
                ]
            }
        ],
        "render_surface": "o0",
    }
    seen_state_sizes = []

    def emit_kernel(ctx, out):
        out[:] = [float(ctx.uniforms["frame"] + 1), 0.0, 0.0, 1.0]

    def move_kernel(ctx, out):
        seen_state_sizes.append(ctx.uniforms["stateSize"])
        out[:] = [float(ctx.textures["state"].data[0]) + 1.0, 0.0, 0.0, 1.0]

    kernels = {"render/emit:emit": emit_kernel, "points/move:move": move_kernel}
    monkeypatch.setattr(renderer, "_meta", lambda: {"effects": effects})
    monkeypatch.setattr(renderer, "compile_dsl", lambda _source, _effects: plan)
    monkeypatch.setattr(renderer, "_kernel_for", kernels.__getitem__)

    surface = renderer.render_dsl("ignored", width=1, height=1)

    assert (surface.width, surface.height) == (2, 2)
    assert np.all(surface.data.reshape(-1, 4)[:, 0] == 3.0)
    assert seen_state_sizes == [2] * 8


def test_ungrouped_particle_state_uses_state_size_fallback(monkeypatch):
    effect = {
        "namespace": "points",
        "kind": "filter",
        "iterated": True,
        "params": {
            "iterationCount": {"type": "int", "default": 1, "cpuOnly": True},
            "stateSize": {"type": "int", "default": 3, "uniform": "stateSize"},
        },
        "textures": {},
        "passes": [
            {
                "name": "move",
                "program": "move",
                "key": "points/test:move",
                "inputs": {"state": "global_xyz"},
                "outputs": {"fragColor": "global_xyz"},
            }
        ],
    }
    seen_input_sizes = []

    def kernel(ctx, out):
        seen_input_sizes.append((ctx.textures["state"].width, ctx.textures["state"].height))
        out[:] = [0.0, 0.0, 0.0, 1.0]

    _install_effect(monkeypatch, effect, kernel)

    surface = renderer.render_effect("filter/test", width=1, height=1)

    assert (surface.width, surface.height) == (3, 3)
    assert seen_input_sizes == [(3, 3)] * 9


def test_pass_resolution_uses_destination_size_and_preserves_full_resolution(monkeypatch):
    effect = {
        "namespace": "filter",
        "kind": "filter",
        "params": {},
        "textures": {"state": {"width": "50%", "height": "25%", "format": "rgba32f"}},
        "passes": [
            {
                "name": "step",
                "program": "step",
                "key": "filter/test:step",
                "inputs": {},
                "outputs": {"fragColor": "state"},
            }
        ],
    }
    seen = []

    def kernel(ctx, out):
        seen.append((tuple(ctx.uniforms["resolution"]), tuple(ctx.uniforms["fullResolution"])))
        out[:] = [0.0, 0.0, 0.0, 1.0]

    _install_effect(monkeypatch, effect, kernel)

    renderer.render_effect("filter/test", width=8, height=8)

    assert seen == [((4.0, 2.0), (8.0, 8.0))] * 8


def test_multi_pass_effect_returns_output_texture_instead_of_last_scratch(monkeypatch):
    effect = {
        "namespace": "filter",
        "kind": "filter",
        "params": {},
        "textures": {"history": {"format": "rgba32f"}},
        "passes": [
            {
                "name": "main",
                "program": "main",
                "key": "filter/test:main",
                "inputs": {},
                "outputs": {"fragColor": "outputTex"},
            },
            {
                "name": "history",
                "program": "history",
                "key": "filter/test:history",
                "inputs": {},
                "outputs": {"fragColor": "history"},
            },
        ],
    }

    def kernel_for(key):
        value = 1.0 if key.endswith(":main") else 2.0

        def kernel(_ctx, out):
            out[:] = [value, 0.0, 0.0, 1.0]

        return kernel

    monkeypatch.setattr(renderer, "_meta", lambda: {"effects": {"filter/test": effect}})
    monkeypatch.setattr(renderer, "_kernel_for", kernel_for)

    surface = renderer.render_effect("filter/test", width=1, height=1)

    assert surface.data[0] == 1.0
