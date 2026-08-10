import numpy as np

from noisemaker_cpu.kernel_loader import load_kernel
from noisemaker_cpu.pass_runner import Ctx
from noisemaker_cpu.runtime import Runtime
from transpiler.codegen import emit_python
from transpiler.parser import parse
from transpiler.preprocess import normalize


def test_multi_output_kernel_renders_distinct_attachments():
    source = """
        layout(location = 0) out vec4 outA;
        layout(location = 1) out vec4 outB;
        void main() {
            outA = vec4(1.0, 0.0, 0.0, 1.0);
            outB = vec4(0.0, 1.0, 0.0, 1.0);
        }
    """
    normalized = normalize(source, {})
    kernel = load_kernel(emit_python(parse(normalized["source"]), normalized["outputs"], normalized["varyings"]))
    from noisemaker_cpu.pass_runner import run_pass_mrt

    surfaces = run_pass_mrt(kernel, Ctx(Runtime()), 1, 1)

    assert kernel.output_names == ("outA", "outB")
    assert np.array_equal(surfaces[0].data, np.array([1.0, 0.0, 0.0, 1.0], dtype=np.float32))
    assert np.array_equal(surfaces[1].data, np.array([0.0, 1.0, 0.0, 1.0], dtype=np.float32))


def test_texture_dimensions_support_catalog_size_specs():
    from noisemaker_cpu.renderer import _texture_dimensions

    params = {"stateSize": 64, "zoom": 4}

    assert _texture_dimensions({}, params, 80, 40) == (80, 40)
    assert _texture_dimensions({"width": "50%", "height": "25%"}, params, 80, 40) == (40, 10)
    assert _texture_dimensions({"width": {"param": "stateSize", "default": 256}}, params, 80, 40) == (64, 40)
    assert _texture_dimensions({"height": {"screenDivide": "zoom", "default": 8}}, params, 80, 40) == (80, 10)
    assert _texture_dimensions(
        {
            "width": {"screenDivide": "zoom", "default": 8},
            "height": {"screenDivide": "zoom", "default": 8},
        },
        params,
        65,
        63,
    ) == (17, 16)
    assert _texture_dimensions({"width": 8, "height": 4}, params, 80, 40) == (8, 4)
