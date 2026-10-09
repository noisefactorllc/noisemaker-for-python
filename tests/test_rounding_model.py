"""The oracle's float32 rounding model, pinned by noisemaker-for-perl 8dffce0f.

The fixture (tests/data/rounding-model.json) holds 59 probe shaders with the
float32 bit patterns the oracle — glsl-transpiler 3.0.3's output run on the
GlslCpuRuntime stdlib — produces for three uniform inputs each. Each case is
compiled through this port's full pipeline (normalize -> parse -> emit_python)
and must reproduce the oracle's bits exactly: the codegen has to round every
operation to float32 at the same points the oracle's compiled JS does
(Float32Array#map, vecN.op, pooled vector declarations, swizzle/spread
typing, indexed stores, and function argument/return boundaries).
"""

import json
from pathlib import Path

import numpy as np
import pytest

from noisemaker_cpu.kernel_loader import load_kernel
from noisemaker_cpu.pass_runner import Ctx
from noisemaker_cpu.runtime import Runtime
from transpiler.codegen import emit_python
from transpiler.parser import parse
from transpiler.preprocess import normalize

_FIXTURE = Path(__file__).parent / "data" / "rounding-model.json"
_MODEL = json.loads(_FIXTURE.read_text())


def _bits(x) -> int:
    """The uint32 bit pattern of a float32 value."""
    return int(np.frombuffer(np.float32(x).tobytes(), dtype=np.uint32)[0])


@pytest.mark.parametrize("index", range(len(_MODEL["cases"])))
def test_rounding_model_case(index):
    case = _MODEL["cases"][index]
    norm = normalize(case["shader"], {})
    kernel = load_kernel(emit_python(parse(norm["source"]), norm["outputs"], norm["varyings"]))
    rt = Runtime()
    got = []
    for values in _MODEL["inputs"]:
        uniforms = {
            name: (np.array(value, dtype=np.float32) if isinstance(value, list) else value)
            for name, value in values.items()
        }
        ctx = Ctx(rt, uniforms=uniforms, resolution=np.array([1.0, 1.0], dtype=np.float32))
        out = [0.0, 0.0, 0.0, 0.0]
        kernel(ctx, out)
        got.append([_bits(v) for v in out[:3]])
    assert got == case["expected"], case["label"]
