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
