"""Stable list, partial and saved-element behavior from the pinned CPU compiler."""

import pytest

from noisemaker_cpu.dsl import DslError, compile_dsl, tokenize_dsl
from noisemaker_cpu.renderer import _meta, render_dsl

HEADER = "search synth, synth3d, filter, mixer, render\n"


def compile_body(body, effects=None):
    return compile_dsl(HEADER + body, _meta()["effects"] if effects is None else effects)


@pytest.mark.parametrize("literal", ["[1, .25, .5, /*end*/]", "vec3(1, .25, .5,)"])
@pytest.mark.parametrize("keyword", ["", "color: "])
def test_trailing_commas_preserve_components_and_arguments(literal, keyword):
    source = f"search synth; solid({keyword}{literal},).write(o0); render(o0);"
    assert render_dsl(source, width=1, height=1).to_rgba8() == bytes([255, 64, 128, 255])


@pytest.mark.parametrize(("namespace", "call", "name", "components"), [
    ("synth", "media(imageSize: vec2(32, 24,))", "imageSize", [32, 24]),
    ("classicNoisedeck", "noise(paletteOffset: vec3(.1, .2, .3,))", "paletteOffset", [.1, .2, .3]),
    ("synth", "solid(color: vec4(.1, .2, .3, .4,))", "color", [.1, .2, .3, .4]),
    ("synth", "remap(zone0_bounds: vec4(0, 0.2, 0.5, 1,))", "zone0_bounds", [0, 0.2, 0.5, 1]),
])
def test_vector_calls_retain_every_authored_component(namespace, call, name, components):
    plan = compile_dsl(f"search {namespace}\n{call}.write(o0)\nrender(o0)", _meta()["effects"])
    assert plan["chains"][0]["steps"][0]["params"][name] == components


def test_remap_positional_arguments_reach_the_next_zone_after_32_vertex_pairs():
    pairs = ["[0, 0, 1, 0]"] * 32
    args = ", ".join(["2", "#123", ".25", ".04", "read(o1)", "4", ".75", "[0, 0, 1, 1]", *pairs, "read(o2)"])
    step = compile_body(f"remap({args}).write(o0)")["chains"][0]["steps"][0]
    assert step["surfaces"] == {"zone0_tex": ("surface", "o1"), "zone1_tex": ("surface", "o2")}
    assert step["params"]["zone0_count"] == 4
    assert step["params"]["zone0_alpha"] == .75
    assert step["params"]["zone0_v31"] == [0, 0, 1, 0]


@pytest.mark.parametrize("args", ["[,1]", "[1,,]", "[1,,0]", ",", "1,,", "color: ,"])
def test_trailing_commas_still_reject_missing_values(args):
    with pytest.raises(DslError, match="Expected DSL value"):
        compile_body(f"solid({args}).write(o0)")


@pytest.mark.parametrize(("binding", "call", "params"), [
    ("let t = noise(seed: 7)", "t(3, 4)", {"type": 3, "octaves": 4, "seed": 7}),
    ("let t = noise(3, 4)", "t(seed: 7)", {"type": 3, "octaves": 4, "seed": 7}),
    ("let t = noise(type: 11)", "t(unregistered(), 4)", {"type": 11, "octaves": 4}),
    ("let t = noise(unregistered(), 4)", "t(type: 11)", {"type": 11, "octaves": 4}),
    ("let t = noise(seed: 7); let alias = t", "alias(3, 4)", {"type": 3, "octaves": 4, "seed": 7}),
    ("let n = noise; let t = n(3, 4)", "t(seed: 7)", {"type": 3, "octaves": 4, "seed": 7}),
])
def test_partial_merges_by_parameter_index_before_values_resolve(binding, call, params):
    step = compile_body(f"{binding}; {call}.write(o0)")["chains"][0]["steps"][0]
    assert step["params"] == params
    assert "inlineChains" not in step


@pytest.mark.parametrize("source", [
    "solid(#f00, 1, unregistered())",
    "let red = solid(#f00); red(1, noise())",
])
def test_excess_arguments_warn_once_and_are_never_evaluated(source, capsys):
    step = compile_body(source + ".write(o0)")["chains"][0]["steps"][0]
    assert step["params"] == {"color": [1, 0, 0], "alpha": 1}
    assert "inlineChains" not in step
    assert capsys.readouterr().err.splitlines() == ["Too many positional arguments for solid(): 'solid' takes 2"]


def test_single_quoted_strings_keep_escapes_and_source_locations():
    tokens = tokenize_dsl(r"""'a\'b"c\n' next""")
    assert tokens[0]["value"] == "a'b\"c\n"
    assert tokens[1]["column"] == 12
    with pytest.raises(DslError, match="Unterminated string"):
        tokenize_dsl("'unfinished\\")


def test_saved_ids_stay_on_effects_inline_chains_subchains_and_io():
    plan = compile_body("""
let base = noise(_id: "base_2", seed: 1)
base().subchain(id: "block") { .invert(_id: 'flip') }.write(o1, _id: "w")
read(o1, _id: "r").blendMode(tex: base(_id: "over")).write(o0)
read(_id: "again", surface: o1).write(o2)
noise3d().write3d(vol0, geo0, _id: "w3")
read3d(vol0, geo0, _id: "r3").render3d().write(o3)
read3d(_id: "named3", _skip: true, tex3d: vol0, geo: geo0).render3d().write(o4)
base().write(o5)
""")
    chains = [chain["steps"] for chain in plan["chains"]]
    assert [[step.get("_id") for step in steps] for steps in chains] == [
        ["base_2", "flip", "w"], ["r", None, None], ["again", None], [None, "w3"],
        ["r3", None, None], ["named3", None, None], ["base_2", None],
    ]
    assert chains[5][0]["_skip"] is True
    assert (chains[5][0]["volume"], chains[5][0]["geometry"]) == ("vol0", "geo0")
    inner = chains[1][1]["inlineChains"][0]["chain"]["steps"][0]
    assert inner["_id"] == "over"
    assert all("_id" not in step.get("params", {}) for steps in [*chains, [inner]] for step in steps)


def test_read_skip_and_id_still_sample_the_requested_surface():
    source = HEADER + "solid(color: #36a).write(o1); read(_id: 'r', _skip: true, tex: o1).write(o0)"
    assert render_dsl(source, width=1, height=1).to_rgba8() == bytes([0x33, 0x66, 0xaa, 255])
    plan = compile_body("noise().blendMode(tex: read(_skip: true, _id: 'r', tex: o1)).write(o0)")
    step = plan["chains"][0]["steps"][1]
    assert step["surfaces"]["tex"] == ("surface", "o1")


@pytest.mark.parametrize("value", ["5", '""', '"9a"', '"a-b"', '"_a"', "alias", "unregistered()"])
def test_invalid_id_overrides_prior_id_without_evaluating_or_warning(value, capsys):
    source = f'let alias = "valid"; let base = solid(_id: "id"); base(_id: {value}).write(o0, _id: {value})'
    assert all("_id" not in step for step in compile_body(source)["chains"][0]["steps"])
    assert not capsys.readouterr().err


@pytest.mark.parametrize("source", [
    'solid(1, _id: "s").write(o0)', 'solid(_id: "s", 1).write(o0)', "noise({seed: 1}).write(o0)",
    "solid().write(o0,)", 'solid().write(surface: o0, _id: "w")', 'solid().write(o0, _id: "w",)',
    'solid().write(o0, other: "w")', 'read(o0, other: "r").write(o1)',
    'noise3d().write3d(vol0, geo0, other: "w")', 'read3d(vol0, geo0, other: "r").render3d().write(o0)',
])
def test_io_metadata_exception_keeps_stable_call_syntax(source):
    with pytest.raises(DslError):
        compile_body(source)


@pytest.fixture
def rgb_effects():
    return {**_meta()["effects"], "filter/rgbProbe": {
        "kind": "filter", "params": {k: {"type": "float", "default": 1} for k in "rgbax"}, "passes": [{}],
    }}


@pytest.mark.parametrize(("binding", "call", "params"), [
    ("", "rgbProbe(#f80)", {"r": 1, "g": 136 / 255, "b": 0}),
    ("let color = #f00", "rgbProbe(color, .5, .6, .7)", {"r": 1, "g": 0, "b": 0, "a": .7}),
    ("let t = rgbProbe(#f00)", "t(_skip: false)", {"r": 1, "g": 0, "b": 0}),
    ("let t = rgbProbe(#f00); let u = t(g: .25)", 'u(_id: "u")', {"r": 1, "g": .25, "b": 0}),
    ('let t = rgbProbe(_id: "t")', "t(#f00)", {"r": 1, "g": 0, "b": 0}),
    ("let t = rgbProbe(r: .25); let u = t(#f00, .6)", 'u(_id: "u")', {"r": .25, "g": .6}),
    ("let c = #f00; let t = rgbProbe(c); let c = #0f0", "t()", {"r": 1, "g": 0, "b": 0}),
    ("let c = #f00; let a = c; let c = #0f0", "rgbProbe(a)", {"r": 1, "g": 0, "b": 0}),
])
def test_hex_colors_fill_rgb_slots_at_declaration(binding, call, params, rgb_effects):
    step = compile_body(f"{binding}; solid().{call}.write(o0)", rgb_effects)["chains"][0]["steps"][1]
    assert step["params"] == params


def test_array_literals_cannot_fill_scalar_rgb_arguments(rgb_effects):
    with pytest.raises(DslError, match='Parameter "r" must be a finite number'):
        compile_body("solid().rgbProbe([1, 0, 0]).write(o0)", rgb_effects)


def test_inline_chain_in_partial_captures_its_hex_color_before_rebinding():
    source = "let c = #f00; let t = blendMode(tex: solid(color: c).invert()); let c = #0f0; noise().t().write(o0)"
    mix = compile_body(source)["chains"][0]["steps"][1]
    assert mix["inlineChains"][0]["chain"]["steps"][0]["params"]["color"] == [1, 0, 0]


@pytest.mark.parametrize(("prefix", "chain", "suffix"), [
    ("solid().blendMode(tex: ", "read(o1).invert()", ").write(o0)"),
    ("solid().blendMode(", "read(o1).invert()", ").write(o0)"),
    ("solid().blendMode(tex: ", 'noise().subchain("s") { .invert() }', ").write(o0)"),
    ("let mix = blendMode(tex: ", "read(o1).invert()", "); solid().mix().write(o0)"),
    ("solid().blendMode(tex: ", "read3d(vol0, geo0).render3d()", ").write(o0)"),
    ("let layer = ", "read(o1).invert()", "; let alias = layer; solid().blendMode(tex: alias).write(o0)"),
])
def test_invalid_chain_argument_reports_s001_at_its_first_element(prefix, chain, suffix):
    message = r"Chain for argument 'tex' in blendMode\(\) may contain only effect calls"
    with pytest.raises(DslError, match=message) as exc:
        compile_body(prefix + chain + suffix)
    assert (exc.value.code, exc.value.line, exc.value.column) == ("S001", 2, len(prefix) + 1)
