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
