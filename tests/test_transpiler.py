"""Full Python-transpiler pipeline: CDN -> normalize -> parse -> codegen -> run.

Skips until the transpiler's cdn/preprocess modules are built.
"""

import importlib.util

import numpy as np
import pytest

_HAVE = (
    importlib.util.find_spec("transpiler.cdn") is not None
    and importlib.util.find_spec("transpiler.preprocess") is not None
)
pytestmark = pytest.mark.skipif(not _HAVE, reason="transpiler cdn/preprocess not built yet")


def _transpile(effect_id, program):
    from transpiler.cdn import fetch_effect
    from transpiler.codegen import emit_python
    from transpiler.parser import parse
    from transpiler.preprocess import normalize

    eff = fetch_effect(effect_id)
    defines = {
        s["define"]: ("float" if s.get("type") == "float" else "int")
        for s in eff["params"].values()
        if isinstance(s, dict) and s.get("define")
    }
    norm = normalize(eff["programs"][program], defines)
    return emit_python(parse(norm["source"]), norm["outputs"], norm["varyings"])


def test_pipeline_solid_compiles_and_renders():
    from noisemaker_cpu.kernel_loader import load_kernel
    from noisemaker_cpu.pass_runner import Ctx, run_pass
    from noisemaker_cpu.runtime import F32, Runtime

    py = _transpile("synth/solid", "solid")
    kernel = load_kernel(py)
    ctx = Ctx(
        Runtime(),
        uniforms={"color": np.array([0.25, 0.5, 0.75], dtype=F32), "alpha": 1.0},
        resolution=np.array([2.0, 2.0], dtype=F32),
    )
    surf = run_pass(kernel, ctx, 2, 2)
    assert list(surf.to_rgba8()[:4]) == [64, 128, 191, 255]


def test_pipeline_invert_compiles():
    from noisemaker_cpu.kernel_loader import load_kernel

    load_kernel(_transpile("filter/invert", "inv"))


def test_vector_storage_boundaries_are_preserved_before_uint_conversion():
    from transpiler.codegen import emit_python
    from transpiler.parser import parse
    from transpiler.preprocess import normalize

    source = """
        out vec4 fragColor;
        void main() {
            vec4 p = vec4(0.1234567);
            vec4 ps = p + vec4(0.0000001);
            uvec4 q = uvec4(ps * 1000.0);
            fragColor = vec4(q) / 4294967296.0;
        }
    """
    normalized = normalize(source, {})
    generated = emit_python(
        parse(normalized["source"]),
        normalized["outputs"],
        normalized["varyings"],
        js_vector_storage=True,
    )

    assert "ps = rt.construct(4, rt.binary(" in generated
    assert 'rt.construct(4, rt.construct(4, rt.binary("*", ps' in generated


def test_hash_uint_routes_by_its_glsl_body_not_its_name():
    from transpiler.codegen import emit_python
    from transpiler.parser import parse
    from transpiler.preprocess import normalize

    def generate(body):
        source = f"""
            out vec4 fragColor;
            uint hash_uint(uint seed) {{
                {body}
            }}
            void main() {{
                fragColor = vec4(float(hash_uint(7u)) / 4294967295.0);
            }}
        """
        normalized = normalize(source, {})
        return emit_python(parse(normalized["source"]), normalized["outputs"], normalized["varyings"])

    murmur = generate(
        "uint x = seed; x ^= x >> 16u; x *= 0x7feb352du; x ^= x >> 15u; x *= 0x846ca68bu; x ^= x >> 16u; return x;"
    )
    lcg = generate(
        "uint state = seed * 747796405u + 2891336453u;"
        " uint word = ((state >> ((state >> 28u) + 4u)) ^ state) * 277803737u;"
        " return (word >> 22u) ^ word;"
    )
    other = generate("return seed * 3u + 1u;")

    assert "rt.hash_uint(" in murmur
    assert "rt.hash_uint_lcg(" not in murmur
    assert "rt.hash_uint_lcg(" in lcg
    assert "rt.hash_uint(" not in lcg
    # Neither pinned body: the shader's own function runs.
    assert "rt.hash_uint" not in other
    assert "hash_uint__uint(" in other


def test_scalar_arithmetic_on_a_vector_call_rounds_like_float32array_map():
    from noisemaker_cpu.kernel_loader import load_kernel
    from noisemaker_cpu.pass_runner import Ctx, run_pass
    from noisemaker_cpu.runtime import Runtime
    from transpiler.codegen import emit_python
    from transpiler.parser import parse
    from transpiler.preprocess import normalize

    # Simplex noise's `h = 1.0 - abs(x) - abs(y)` compiles in the sibling to
    # vec4.subtract([], abs(x).map(_ => 1 - _), abs(y)): the map stores
    # 1 - |x| into a Float32Array before |y| is subtracted. These lanes are
    # classicNoisedeck/noise3d's snoise at offsetX 100; rounding once gives
    # 0.14285710453987122, the sibling gives 0.14285707473754883.
    source = """
        uniform vec4 xs;
        uniform vec4 ys;
        out vec4 fragColor;
        void main() {
            vec4 h = 1.0 - abs(xs) - abs(ys);
            vec4 h2 = vec4(0.0);
            h2 = 1.0 - abs(xs) - abs(ys);
            fragColor = vec4(h.x, h2.x, h.w, h2.w);
        }
    """
    normalized = normalize(source, {})
    kernel = load_kernel(emit_python(parse(normalized["source"]), normalized["outputs"], normalized["varyings"]))
    lane = (-0.07142850756645203, 0.7857143878936768)
    uniforms = {
        "xs": np.array([lane[0], 0.0, 0.0, lane[0]], dtype=np.float32),
        "ys": np.array([lane[1], 0.0, 0.0, lane[1]], dtype=np.float32),
    }

    surface = run_pass(kernel, Ctx(Runtime(), uniforms=uniforms), 1, 1)

    assert [float(c) for c in surface.data] == [0.14285707473754883] * 4


def test_vector_vector_arithmetic_on_a_call_keeps_float64_until_stored():
    from transpiler.codegen import emit_python
    from transpiler.parser import parse
    from transpiler.preprocess import normalize

    # vec2 * vec2 with a call operand compiles to vec2.multiply([], a, b): a
    # plain array, so the product stays float64 into the int conversion.
    source = """
        uniform vec2 uv;
        out vec4 fragColor;
        void main() {
            ivec2 coord = ivec2(fract(uv) * vec2(64.0, 64.0));
            fragColor = vec4(vec2(coord), 0.0, 1.0);
        }
    """
    normalized = normalize(source, {})
    generated = emit_python(parse(normalized["source"]), normalized["outputs"], normalized["varyings"])

    assert "rt.copy(rt.binary" not in generated


def test_nested_inout_call_is_an_expression_and_updates_caller():
    from noisemaker_cpu.kernel_loader import load_kernel
    from noisemaker_cpu.pass_runner import Ctx, run_pass
    from noisemaker_cpu.runtime import Runtime
    from transpiler.codegen import emit_python
    from transpiler.parser import parse
    from transpiler.preprocess import normalize

    source = """
        out vec4 fragColor;
        float bump(inout float seed) { seed += 1.0; return seed; }
        void main() {
            float seed = 1.0;
            float doubled = bump(seed) * 2.0;
            fragColor = vec4(doubled, seed, 0.0, 1.0);
        }
    """
    normalized = normalize(source, {})
    kernel = load_kernel(emit_python(parse(normalized["source"]), normalized["outputs"], normalized["varyings"]))

    surface = run_pass(kernel, Ctx(Runtime()), 1, 1)

    assert np.array_equal(surface.data, np.array([4.0, 2.0, 0.0, 1.0], dtype=np.float32))


def test_local_vector_constructor_assignment_matches_sequential_js_aliasing():
    from noisemaker_cpu.kernel_loader import load_kernel
    from noisemaker_cpu.pass_runner import Ctx, run_pass
    from noisemaker_cpu.runtime import Runtime
    from transpiler.codegen import emit_python
    from transpiler.parser import parse
    from transpiler.preprocess import normalize

    source = """
        out vec4 fragColor;
        void main() {
            vec2 p = vec2(1.0, 2.0);
            p = vec2(dot(p, vec2(2.0, 0.0)), dot(p, vec2(3.0, 0.0)));
            fragColor = vec4(p, 0.0, 1.0);
        }
    """
    normalized = normalize(source, {})
    kernel = load_kernel(emit_python(parse(normalized["source"]), normalized["outputs"], normalized["varyings"]))

    surface = run_pass(kernel, Ctx(Runtime()), 1, 1)

    assert np.array_equal(surface.data, np.array([2.0, 6.0, 0.0, 1.0], dtype=np.float32))


def test_local_vector_constructor_member_reads_are_evaluated_atomically():
    from noisemaker_cpu.kernel_loader import load_kernel
    from noisemaker_cpu.pass_runner import Ctx, run_pass
    from noisemaker_cpu.runtime import Runtime
    from transpiler.codegen import emit_python
    from transpiler.parser import parse
    from transpiler.preprocess import normalize

    source = """
        out vec4 fragColor;
        void main() {
            vec2 p = vec2(1.0, 2.0);
            p = vec2(p.y, -p.x);
            fragColor = vec4(p, 0.0, 1.0);
        }
    """
    normalized = normalize(source, {})
    kernel = load_kernel(emit_python(parse(normalized["source"]), normalized["outputs"], normalized["varyings"]))

    surface = run_pass(kernel, Ctx(Runtime()), 1, 1)

    assert np.array_equal(surface.data, np.array([2.0, -1.0, 0.0, 1.0], dtype=np.float32))


def test_indexed_vector_conditional_assignment_matches_js_true_branch_noop():
    from noisemaker_cpu.kernel_loader import load_kernel
    from noisemaker_cpu.pass_runner import Ctx, run_pass
    from noisemaker_cpu.runtime import Runtime
    from transpiler.codegen import emit_python
    from transpiler.parser import parse
    from transpiler.preprocess import normalize

    source = """
        out vec4 fragColor;
        void main() {
            vec4 slots[2];
            vec4 current = vec4(1.0, 0.5, 0.25, 1.0);
            vec4 history = vec4(0.0);
            slots[1] = history.a < 0.5 ? current : history;
            fragColor = slots[1];
        }
    """
    normalized = normalize(source, {})
    kernel = load_kernel(emit_python(parse(normalized["source"]), normalized["outputs"], normalized["varyings"]))

    surface = run_pass(kernel, Ctx(Runtime()), 1, 1)

    assert np.array_equal(surface.data, np.zeros(4, dtype=np.float32))


def test_scalar_int_division_declarations_mirror_the_sibling_lowering():
    """ddf8b19-era restoreIntegerDivision scalar/scalar form (see codegen):
    both operands must be in the sibling's file-global intNames set (int
    uniform, int scalar declaration, or ivec — never function parameters,
    which the sibling's regexes cannot match), and filter/spookyTicker is
    exempt entirely."""
    from transpiler.codegen import emit_python
    from transpiler.parser import parse
    from transpiler.preprocess import normalize

    source = """
        out vec4 fragColor;
        uniform int volSize;
        int pick(int localX, int iScale) {
            int g = localX / iScale;
            return g;
        }
        void main() {
            int yAtlas = int(gl_FragCoord.y);
            int z = yAtlas / volSize;
            int same = volSize / volSize;
            fragColor = vec4(float(z + pick(3, 2) + same), 0.0, 0.0, 1.0);
        }
    """
    normalized = normalize(source, {})

    def emit(effect_id):
        return emit_python(parse(normalized["source"]), normalized["outputs"], normalized["varyings"], effect_id=effect_id)

    generated = emit("synth3d/shape3d")
    assert 'trunc_scalar_div(rt.binary("/", yAtlas, _u_volSize, 1, "int"))' in generated
    # function parameters are not in intNames; the self-division stays live
    assert 'trunc_scalar_div(rt.binary("/", localX, iScale' not in generated
    assert 'trunc_scalar_div(rt.binary("/", _u_volSize, _u_volSize' not in generated
    # the sibling exempts filter/spookyTicker from the scalar/scalar rewrite
    assert "trunc_scalar_div" not in emit("filter/spookyTicker")
    # larger expressions, non-identifier operands, and assignments stay fractional
    assert 'trunc_scalar_div(rt.binary("/", yAtlas, rt.i(2)' not in generated


def test_scalar_int_division_declarations_truncate_toward_zero_at_runtime(monkeypatch):
    from noisemaker_cpu import runtime
    from noisemaker_cpu.kernel_loader import load_kernel
    from noisemaker_cpu.pass_runner import Ctx, run_pass
    from noisemaker_cpu.runtime import Runtime
    from transpiler.codegen import emit_python
    from transpiler.parser import parse
    from transpiler.preprocess import normalize

    # The published runtime carries the post-ddf8b19 truncating semantics; pin
    # the probe so the value contract is asserted against any mounted oracle
    # (a pre-ddf8b19 oracle keeps its published fractional pass-through).
    monkeypatch.setattr(runtime, "_ORACLE_SCALAR_INT_DIVISION", True)

    source = """
        out vec4 fragColor;
        uniform int volSize;
        void main() {
            int yAtlas = int(-7.0);
            int z = yAtlas / volSize;
            fragColor = vec4(float(z), 0.0, 0.0, 1.0);
        }
    """
    normalized = normalize(source, {})
    kernel = load_kernel(
        emit_python(parse(normalized["source"]), normalized["outputs"], normalized["varyings"], effect_id="synth3d/shape3d")
    )

    surface = run_pass(kernel, Ctx(Runtime(), uniforms={"volSize": 2}), 1, 1)

    # GLSL int/int division truncates toward zero: -7 / 2 is -3, not floor's -4
    assert np.array_equal(surface.data, np.array([-3.0, 0.0, 0.0, 1.0], dtype=np.float32))
