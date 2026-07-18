"""Unit tests for the Polymorphic DSL front-end and graph evaluator (no oracle).

These exercise tokenize -> parse -> compile -> render_dsl end to end, plus the
diagnostic errors, mirroring noisemaker-cpu test/dsl.test.js against the real
catalog bundle.
"""

import numpy as np
import pytest

from noisemaker_cpu.dsl import DslError, compile_dsl, parse_dsl, tokenize_dsl
from noisemaker_cpu.renderer import _meta, render_dsl, render_effect


def _effects():
    return _meta()["effects"]


def _rgba8(surface):
    return np.frombuffer(surface.to_rgba8(), dtype=np.uint8)


def test_tokenize_classifies_lexemes():
    types = [t["type"] for t in tokenize_dsl("search synth\nnoise(scaleX: 8).write(o0)")]
    assert "keyword" in types  # search
    assert "surface" in types  # o0
    assert types[-1] == "eof"
    color = tokenize_dsl("#3af")[0]
    assert color["type"] == "color" and color["lexeme"] == "#3af"


def test_parse_program_shape():
    ast = parse_dsl("search synth, filter\nsolid(color: #336699).invert().write(o0)\nrender(o0)")
    assert ast["search"] == ["synth", "filter"]
    assert len(ast["chains"]) == 1
    assert [call["name"] for call in ast["chains"][0]["calls"]] == ["solid", "invert", "write"]
    assert ast["render"]["name"] == "o0"


def test_compile_resolves_effect_and_splits_surface_params():
    plan = compile_dsl("search synth, mixer\nnoise().cellSplit(tex: o1).write(o0)\nrender(o0)", _effects())
    effect_step = plan["chains"][0]["steps"][1]
    assert effect_step["effect_id"] == "mixer/cellSplit"
    assert effect_step["surfaces"]["tex"] == ("surface", "o1")


def test_compile_render_surface_defaults_to_last_write():
    plan = compile_dsl("search synth\nsolid().write(o3)", _effects())
    assert plan["render_surface"] == "o3"


def test_render_solid_exact_color():
    surface = render_dsl("search synth\nsolid(color: #336699).write(o0)\nrender(o0)", width=4, height=4)
    assert list(_rgba8(surface)[:4]) == [0x33, 0x66, 0x99, 0xFF]


def test_render_generator_filter_chain_runs():
    surface = render_dsl(
        "search synth, filter\nnoise(seed: 3, scaleX: 8, scaleY: 8).vignette().write(o0)\nrender(o0)",
        width=8,
        height=8,
        seed=3,
    )
    assert (surface.width, surface.height) == (8, 8)


def test_render_let_value_and_partial_bindings():
    program = (
        "search synth, filter\n"
        "let amt = 3\n"
        "let base = noise(scaleX: 7, scaleY: 7)\n"
        "base(seed: 11).posterize(levels: amt).write(o0)\n"
        "render(o0)\n"
    )
    surface = render_dsl(program, width=8, height=8, seed=1)
    assert (surface.width, surface.height) == (8, 8)


def test_render_cross_chain_read_into_mixer():
    program = (
        "search synth, mixer\n"
        "solid(color: #f80).write(o0)\n"
        "noise(seed: 2).cellSplit(tex: read(o0)).write(o1)\n"
        "render(o1)\n"
    )
    surface = render_dsl(program, width=8, height=8, seed=2)
    assert (surface.width, surface.height) == (8, 8)


def test_arithmetic_and_array_values_render():
    surface = render_dsl("search synth\nsolid(color: [0.2, 0.4, 0.6]).write(o0)\nrender(o0)", width=2, height=2)
    assert list(_rgba8(surface)[:3]) == [51, 102, 153]  # 0.2/0.4/0.6 * 255
    # arithmetic in a scalar param compiles and renders
    render_dsl("search synth\nnoise(scaleX: 4 * 2, scaleY: 16 / 2, seed: 3).write(o0)\nrender(o0)", width=4, height=4)


def test_missing_search_directive():
    with pytest.raises(DslError, match="Missing required search directive"):
        compile_dsl("solid().write(o0)\nrender(o0)", _effects())


def test_unknown_effect():
    with pytest.raises(DslError, match='Unknown effect "wat" in search namespaces synth'):
        compile_dsl("search synth\nwat().write(o0)\nrender(o0)", _effects())


def test_unknown_parameter_lists_accepted():
    with pytest.raises(DslError, match='Unknown parameter "bogus" for synth/noise'):
        compile_dsl("search synth\nnoise(bogus: 1).write(o0)\nrender(o0)", _effects())


def test_generator_chain_must_end_with_write():
    with pytest.raises(DslError, match="Generator chain must end with write"):
        compile_dsl("search synth\nnoise()\nrender(o0)", _effects())


def test_cannot_mix_positional_and_named_arguments():
    with pytest.raises(DslError, match="Cannot mix positional and named arguments"):
        parse_dsl("search synth\nnoise(4, seed: 2).write(o0)")


def test_surface_reference_out_of_range():
    with pytest.raises(DslError, match="Surface reference must be o0 through o7"):
        parse_dsl("search synth\nnoise().write(o9)")


def test_read_unwritten_surface_raises():
    with pytest.raises(ValueError, match="Surface o5 has not been written"):
        render_dsl("search synth, filter\nread(o5).invert().write(o0)\nrender(o0)", width=4, height=4)


def test_malformed_numeric_literal_is_a_dsl_error():
    # A truncated exponent must surface as a located DslError, not a bare ValueError.
    with pytest.raises(DslError, match="Invalid numeric literal"):
        tokenize_dsl("noise(scaleX: 1e)")


def test_render_effect_samples_pooled_inputs_nearest():
    # The JS oracle binds ONLY the declared externalTexture as 'linear'; every pooled
    # surface stays 'nearest'. Forcing pooled inputs to linear diverges from node for
    # warp effects that sample at fractional coordinates. A regression here would
    # silently reintroduce that (identity/solid sampling can't detect it).
    src = render_effect("synth/noise", {"seed": 3, "ridges": True}, width=8, height=8, seed=3)
    render_effect("filter/octaveWarp", {}, {"inputTex": src}, width=8, height=8, seed=3)
    assert src.filter == "nearest"


def test_render_effect_binds_external_texture_linear():
    # filter/text declares externalTexture=textTex: that sampler must be 'linear',
    # while the pooled inputTex stays 'nearest' — mirroring JS buildBindings.
    assert _meta()["effects"]["filter/text"].get("externalTexture") == "textTex"
    src = render_effect("synth/noise", {"seed": 1}, width=8, height=8, seed=1)
    tex = render_effect("synth/noise", {"seed": 2}, width=8, height=8, seed=2)
    render_effect("filter/text", {}, {"inputTex": src, "textTex": tex}, width=8, height=8, seed=1)
    assert tex.filter == "linear"
    assert src.filter == "nearest"
