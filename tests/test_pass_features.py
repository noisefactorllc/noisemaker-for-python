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


def test_texture_dimensions_ported_cpu_specs():
    """Mirrors noisemaker-for-cpu's canonical-render-graph viewport-scale test
    and the textureDimension semantics introduced through noisemaker@8eeb7b5a."""
    from noisemaker_cpu.renderer import _texture_dimensions

    # w/h aliases with scale + clamp: 64 -> floor(32)/floor(16); 8 -> min clamp 8; 512 -> max clamp 128.
    spec = {"w": {"scale": 0.5, "clamp": {"min": 8, "max": 128}}, "h": {"scale": 0.25}}
    assert _texture_dimensions(spec, {}, 64, 64) == (32, 16)
    assert _texture_dimensions(spec, {}, 8, 8) == (8, 2)
    assert _texture_dimensions(spec, {}, 512, 512) == (128, 128)

    # 'auto' resolves like 'screen'.
    assert _texture_dimensions({"width": "auto", "height": "auto"}, {}, 48, 24) == (48, 24)

    # { param } with multiply: applied to the param value.
    assert _texture_dimensions({"width": {"param": "size", "multiply": 2}}, {"size": 12}, 80, 40) == (24, 40)
    # Param absent: paramDefault/default chain bottoms out at 64 (then the
    # transform applies); a transform present with an explicit default
    # restores that default verbatim.
    assert _texture_dimensions({"width": {"param": "size", "multiply": 2}}, {}, 80, 40) == (128, 40)
    assert (
        _texture_dimensions({"width": {"param": "size", "multiply": 2, "paramDefault": 5, "default": 9}}, {}, 80, 40)[0]
        == 9
    )
    assert (
        _texture_dimensions({"width": {"param": "size", "power": 2, "paramDefault": 5, "default": 9}}, {}, 80, 40)[0]
        == 9
    )
    # Without a transform, paramDefault is the plain fallback.
    assert _texture_dimensions({"width": {"param": "size", "paramDefault": 5}}, {}, 80, 40) == (5, 40)

    # JS Math.round is half-up; Python round() is banker's. Fractional specs
    # landing exactly on .5 must resolve like the -cpu engine.
    assert _texture_dimensions({"width": 2.5, "height": "50%"}, {}, 9, 9) == (3, 5)
    assert _texture_dimensions({"width": {"param": "size", "multiply": 0.5}}, {"size": 5}, 80, 40) == (3, 40)
    assert _texture_dimensions({"width": "25%"}, {}, 6, 6) == (2, 6)
