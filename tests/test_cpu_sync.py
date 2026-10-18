import json
import struct
from pathlib import Path

import numpy as np
import pytest

from noisemaker_cpu.kernel_loader import load_kernel
from noisemaker_cpu.pass_runner import Ctx, run_pass
from noisemaker_cpu.runtime import Runtime
from noisemaker_cpu.surface import Surface
from transpiler.codegen import emit_python
from transpiler.parser import parse
from transpiler.preprocess import normalize

DATA = Path(__file__).parent / "data" / "cpu-sync"


def _from_bits(value):
    return struct.unpack("<f", struct.pack("<I", value))[0]


@pytest.mark.parametrize(
    "assignment,expected",
    [
        ("p = vec2(dot(p, vec2(2.0, 0.0)), dot(p, vec2(3.0, 0.0)));", [2, 3]),
        ("p = dot(p, vec2(2.0, 3.0)) * vec2(2.0, 3.0);", [16, 24]),
        ("p = vec2(p.x - 2.0 * p.y, -2.0 * p.x - p.y) / 2.0;", [-1.5, -2]),
        ("p = vec2(dot(p, p));", [5, 5]),
        ("p *= p;", [1, 4]),
        ("p = vec2(p.y, p[0x0]);", [2, 1]),
        ("p = vec2(p.y, p[0u]);", [2, 1]),
        ("p = vec2(p.t, p.s);", [2, 1]),
    ],
)
def test_vector_assignment_evaluates_components_before_writes(assignment, expected):
    source = (
        f"out vec4 fragColor; void main() {{ vec2 p = vec2(1.0, 2.0); {assignment} fragColor = vec4(p, 0.0, 1.0); }}"
    )
    normalized = normalize(source, {})
    kernel = load_kernel(emit_python(parse(normalized["source"]), normalized["outputs"], normalized["varyings"]))
    surface = run_pass(kernel, Ctx(Runtime()), 1, 1)
    assert np.array_equal(surface.data, np.array([*expected, 0, 1], dtype=np.float32))


def test_metal_division_matches_retained_m4_operands():
    from noisemaker_cpu.metal_division import metal_divide

    fixture = json.loads((DATA / "metal-division-m4.json").read_text())
    for a, b, expected in fixture["runtime"] + fixture["special"]:
        actual = np.float32(metal_divide(_from_bits(a), _from_bits(b)))
        wanted = _from_bits(expected)
        assert (np.isnan(actual) and np.isnan(wanted)) or actual.tobytes() == np.float32(wanted).tobytes(), (a, b)


def test_runtime_sampler_matches_retained_m4_boundaries():
    fixture = json.loads((DATA / "nearest-texel-m4.json").read_text())
    rt = Runtime()
    for width, bits, column in fixture["boundaries"]:
        surface = Surface(width, 1)
        surface.data[0::4] = np.arange(width)
        assert rt.texture(surface, [_from_bits(bits), 0.5])[0] == column
    surface = Surface(41, 3)
    for y in range(3):
        for x in range(41):
            start = ((2 - y) * 41 + x) * 4
            surface.data[start : start + 2] = [x, y]
    for u, v, column, row in fixture["special41x3"]:
        assert np.array_equal(rt.texture(surface, [_from_bits(u), _from_bits(v)])[:2], [column, row])


def test_reciprocal_data_reconstructs_the_retained_capture_hash():
    import hashlib

    from noisemaker_cpu._metal_reciprocal import METAL_RECIPROCAL
    from noisemaker_cpu.metal_division import reciprocal_deviations

    deviations = np.unpackbits(np.frombuffer(reciprocal_deviations(), dtype=np.uint8), bitorder="little")
    table = np.zeros(1 << 23, dtype=np.uint8)
    for start in range(1, 1 << 23, 1 << 18):
        end = min(start + (1 << 18), 1 << 23)
        scaled = 140737488355328 / (8388608.0 + np.arange(start, end))
        table[start:end] = deviations[start:end] * np.where(scaled - np.floor(scaled) < 0.5, 1, 2)
    packed = np.bitwise_or.reduce(table.reshape(-1, 4) << np.array([0, 2, 4, 6], dtype=np.uint8), axis=1)
    assert hashlib.sha256(packed.tobytes()).hexdigest() == METAL_RECIPROCAL["tableSha256"]


def test_float_division_classifies_runtime_and_folded_divisors():
    source = """
        uniform float width;
        out vec4 fragColor;
        float helper(float x, float divisor) { return x / divisor; }
        void main() {
            float localWidth = width + 1.0;
            float a = 7.0 / width;
            float b = 7.0 / localWidth;
            float c = 7.0 / 41.0;
            fragColor = vec4(a, b, c, helper(7.0, 41.0));
        }
    """
    normalized = normalize(source, {})
    generated = emit_python(parse(normalized["source"]), normalized["outputs"], normalized["varyings"])
    assert "rt.fdiv(rt.f(7.0), _u_width, 1)" in generated
    assert "rt.fdiv(rt.f(7.0), localWidth, 1)" in generated
    assert 'rt.binary("/", x, divisor, 1, "float")' in generated


def test_murmur_finalizer_routes_by_body_for_arbitrary_names():
    source = """
        uint hash_mix(uint v) {
            v = v ^ (v >> 16u); v = v * 0x7feb352du;
            v = v ^ (v >> 15u); v = v * 0x846ca68bu;
            v = v ^ (v >> 16u); return v;
        }
        out vec4 fragColor;
        void main() { fragColor = vec4(float(hash_mix(0xfedcba98u))); }
    """
    normalized = normalize(source, {})
    generated = emit_python(
        parse(normalized["source"]), normalized["outputs"], normalized["varyings"], effect_id="filter/spookyTicker"
    )
    assert "rt.hash_uint(rt.i(4275878552))" in generated
    kernel = load_kernel(generated)
    assert run_pass(kernel, Ctx(Runtime()), 1, 1).data[0] == np.float32(Runtime().hash_uint(0xFEDCBA98))
    changed = source.replace("v >> 15u", "v >> 14u")
    normalized = normalize(changed, {})
    generated = emit_python(
        parse(normalized["source"]), normalized["outputs"], normalized["varyings"], effect_id="filter/spookyTicker"
    )
    assert "rt.hash_uint(" not in generated


def test_compound_float_division_uses_runtime_reciprocal():
    normalized = normalize(
        "uniform float width; out vec4 fragColor; void main() { vec2 p=vec2(1.0,3.0);"
        " p /= width; float x=1.0; x /= width; fragColor=vec4(p,x,1.0); }",
        {},
    )
    generated = emit_python(parse(normalized["source"]), normalized["outputs"], normalized["varyings"])
    kernel = load_kernel(generated)
    actual = run_pass(kernel, Ctx(Runtime(), uniforms={"width": 41.0}), 1, 1).data
    from noisemaker_cpu.metal_division import metal_divide

    assert np.array_equal(actual, np.array([metal_divide(1, 41), metal_divide(3, 41), 1 / 41, 1], dtype=np.float32))


def test_vector_cast_of_integer_operands_keeps_source_integer_evidence():
    source = (
        "uniform ivec2 dims; uniform ivec2 xy; out vec4 fragColor;"
        " void main() { vec2 p=vec2(xy)/vec2(dims); fragColor=vec4(p,0.0,1.0); }"
    )
    normalized = normalize(source, {})
    generated = emit_python(parse(normalized["source"]), normalized["outputs"], normalized["varyings"])
    assert "rt.fdiv" not in generated


def test_spooky_ternary_integer_divisions_truncate_each_branch():
    source = (
        "out vec4 fragColor; uniform int sx; uniform int CELL_W; void main() {"
        " int cellX=sx >= 0 ? sx / CELL_W : (sx-CELL_W+1)/CELL_W; fragColor=vec4(float(cellX)); }"
    )
    normalized = normalize(source, {})
    kernel = load_kernel(
        emit_python(
            parse(normalized["source"]), normalized["outputs"], normalized["varyings"], effect_id="filter/spookyTicker"
        )
    )
    assert run_pass(kernel, Ctx(Runtime(), uniforms={"sx": -7, "CELL_W": 3}), 1, 1).data[0] == -3


def test_integer_scalar_splat_has_float_division_evidence():
    normalized = normalize(
        "uniform int x; uniform ivec2 dims; out vec4 fragColor;"
        " void main() { vec2 p=vec2(x)/vec2(dims); fragColor=vec4(p,0.0,1.0); }",
        {},
    )
    generated = emit_python(parse(normalized["source"]), normalized["outputs"], normalized["varyings"])
    assert "rt.fdiv" in generated


def test_murmur_named_hash_uint_does_not_route_a_different_body():
    normalized = normalize(
        "uint hash_uint(uint v) { v ^= v >> 16u; v *= 0x7feb352du; v ^= v >> 14u;"
        " v *= 0x846ca68bu; v ^= v >> 16u; return v; }"
        " out vec4 fragColor; void main() { fragColor=vec4(float(hash_uint(7u))); }",
        {},
    )
    generated = emit_python(parse(normalized["source"]), normalized["outputs"], normalized["varyings"])
    assert "rt.hash_uint(" not in generated


def test_ternary_with_nested_calls_keeps_source_fractional_division():
    normalized = normalize(
        "uniform int a; uniform int b; uniform int CW; out vec4 fragColor;"
        " void main() { int x=a>0 ? (abs(a)+b)/CW : (abs(b)+a)/CW; fragColor=vec4(float(x)); }",
        {},
    )
    generated = emit_python(
        parse(normalized["source"]), normalized["outputs"], normalized["varyings"], effect_id="filter/spookyTicker"
    )
    assert "rt.trunc64(" not in generated


@pytest.mark.parametrize(
    "expression,expected",
    [
        ("a>0 ? (a*(b+1))/CW : ((a+b)*2)/CW", 2 / 3),
        ("a>0 ? (-a)/CW : (-b)/CW", 0),
    ],
)
def test_ternary_division_preserves_parenthesis_boundaries(expression, expected):
    normalized = normalize(
        f"uniform int a; uniform int b; uniform int CW; out vec4 fragColor;"
        f" void main() {{ int x={expression}; fragColor=vec4(float(x)); }}",
        {},
    )
    kernel = load_kernel(
        emit_python(
            parse(normalized["source"]), normalized["outputs"], normalized["varyings"], effect_id="filter/spookyTicker"
        )
    )
    actual = run_pass(kernel, Ctx(Runtime(), uniforms={"a": 1, "b": 1, "CW": 3}), 1, 1)
    assert np.array_equal(actual.data, np.full(4, expected, dtype=np.float32))
