import numpy as np
import pytest

from noisemaker_cpu import renderer
from noisemaker_cpu.external_input import pack_mesh_data_for_textures

_BACKDROP = [0.25, 0.5, 1.0, 0.75]
_SOURCE = [0.5, 0.25, 0.75, 0.5]


def _color_pass(color, *, blend=None, target="outputTex"):
    return {
        "program": "color", "key": "color", "uniforms": {"color": color},
        "outputs": {"fragColor": target}, "blend": blend,
    }


def _render_blend(monkeypatch, passes, iterated=False, kernels=None):
    def color(ctx, out):
        out[:] = ctx.uniforms["color"]

    effect = {
        "namespace": "synth", "kind": "generator", "iterated": iterated,
        "params": {"iterationCount": {"type": "int", "default": 1}}, "passes": passes,
    }
    monkeypatch.setattr(renderer, "_meta", lambda: {"effects": {"synth/blendProbe": effect}})
    monkeypatch.setattr(renderer, "_kernel_for", {"color": color, **(kernels or {})}.__getitem__)
    return renderer.render_dsl("search synth\nblendProbe().write(o0)\nrender(o0)", width=1, height=1)


@pytest.mark.parametrize(("blend", "expected"), [
    (["ONE", "ZERO"], _SOURCE),
    ([0, 1], _BACKDROP),
    (["SRC_COLOR", "zero"], [0.25, 0.0625, 0.5625, 0.25]),
    (["dst", "ZERO"], [0.125, 0.125, 0.75, 0.375]),
    (["ONE_MINUS_SRC_COLOR", "zero"], [0.25, 0.1875, 0.1875, 0.25]),
    ([0x0307, "ZERO"], [0.375, 0.125, 0.0, 0.125]),
    (["zero", "src"], [0.125, 0.125, 0.75, 0.375]),
    (["zero", "one-minus-dst"], [0.1875, 0.25, 0.0, 0.1875]),
    (["zero", "one-minus-src"], [0.125, 0.375, 0.25, 0.375]),
    (["SRC_ALPHA", "ONE_MINUS_SRC_ALPHA"], [0.375, 0.375, 0.875, 0.625]),
    ([0x0304, 0x0305], [0.4375, 0.3125, 0.8125, 0.5625]),
    (True, [0.75, 0.75, 1.75, 1.25]),
])
def test_canonical_pass_blend_factors(monkeypatch, blend, expected):
    result = _render_blend(monkeypatch, [_color_pass(_BACKDROP), _color_pass(_SOURCE, blend=blend)])
    np.testing.assert_array_equal(result.data, expected)


def test_first_attachment_write_blends_against_transparent_black(monkeypatch):
    result = _render_blend(monkeypatch, [_color_pass(_SOURCE, blend=["DST_COLOR", "ONE"])])
    np.testing.assert_array_equal(result.data, [0, 0, 0, 0])


@pytest.mark.parametrize("iterated", [False, True])
def test_each_draw_buffer_blends_against_its_own_previous_color(monkeypatch, iterated):
    def split(ctx, outputs):
        outputs[0][:] = _SOURCE
        outputs[1][:] = _SOURCE

    split.output_names = ("a", "b")

    def combine(ctx, out):
        out[:] = [*ctx.textures["left"].data[:2], *ctx.textures["right"].data[2:]]

    passes = [
        _color_pass(_BACKDROP, target="_left"),
        _color_pass([0.0, 1.0, 0.25, 0.5], target="_right"),
        {"program": "split", "key": "split", "drawBuffers": 2,
         "outputs": {"a": "_left", "b": "_right"}, "blend": ["DST_COLOR", "ZERO"]},
        {"program": "combine", "key": "combine", "inputs": {"left": "_left", "right": "_right"},
         "outputs": {"fragColor": "outputTex"}},
        _color_pass(_SOURCE, blend=["zero", "one"]),
    ]
    result = _render_blend(monkeypatch, passes, iterated, {"split": split, "combine": combine})
    np.testing.assert_array_equal(result.data, [0.125, 0.125, 0.1875, 0.25])


def _render_mesh(monkeypatch, count, uniform, *, default_extent=False):
    width, height = (256, 256) if default_extent else (3, 2)
    mesh_data = pack_mesh_data_for_textures(
        [-1, -1, 0, 0, -1, 0, -1, 1, 0, 0, -1, 0, 1, -1, 0, 0, 1, 0],
        [0, 0, 1] * 6, [0, 0] * 6, width, height,
    )
    if not default_extent:
        mesh_data.update(texWidth=width, texHeight=height)
    mesh = renderer._meta()["effects"]["render/meshRender"]
    render_pass = next(p for p in mesh["passes"] if p.get("drawMode") == "triangles")
    monkeypatch.setitem(render_pass, "count", count)
    monkeypatch.setitem(render_pass, "countUniform", "vertices")
    monkeypatch.setitem(render_pass["uniforms"], "vertices", uniform)
    return renderer.render_dsl(
        "search render\nmeshLoader().meshRender(bgAlpha: 0).write(o0)\nrender(o0)",
        width=8, height=8, external_inputs={"meshData": mesh_data},
    )


@pytest.mark.parametrize(("count", "uniform", "right_alpha"), [
    ("screen", 3, 0), (3, None, 0), (None, None, 0), (3, 6, 1),
    ("screen", 0, 1), ("screen", -1, 1), ("screen", "invalid", 1),
    ("screen", None, 1), ("auto", 0, 1), ("input", 0, 1), (1000, None, 1),
])
def test_mesh_draw_count_uses_uniform_then_pass_count_or_mesh_extent(monkeypatch, count, uniform, right_alpha):
    result = _render_mesh(monkeypatch, count, uniform)
    alpha = result.data.reshape(8, 8, 4)[5, :, 3]
    assert alpha[1] == 1
    assert alpha[5] == right_alpha


def test_mesh_draw_accepts_packed_arrays_with_default_texture_extent(monkeypatch):
    result = _render_mesh(monkeypatch, "screen", 3, default_extent=True)
    alpha = result.data.reshape(8, 8, 4)[5, :, 3]
    np.testing.assert_array_equal(alpha[[1, 5]], [1, 0])
