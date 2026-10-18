"""Direct adapter captures from noisemaker-for-cpu d7deb06e03a8.

The 8x8/8x6 fixtures run the source factories with GlslCpuRuntime against
procedural RGBA input, without the generator or texture quantization stages.
"""

import json
from pathlib import Path

import numpy as np
import pytest

from noisemaker_cpu.adapters import crt, get_adapter
from noisemaker_cpu.kernel_loader import load_kernel
from noisemaker_cpu.pass_runner import Ctx, run_pass
from noisemaker_cpu.runtime import Runtime
from noisemaker_cpu.surface import Surface

DATA = Path(__file__).parent / "data" / "cpu-adapter-sync"
CAPTURE = json.loads((DATA / "cases.json").read_text())


def _context(case, rt):
    width, height = case["width"], case["height"]
    source = Surface(width, height)
    xs = np.arange(width * height) % width
    ys = np.arange(width * height) // width
    source.data[0::4] = ((xs * 3 + ys * 5) % 31) / 31
    source.data[1::4] = ((xs * 11 + ys * 7) % 37) / 37
    source.data[2::4] = ((xs * 17 + ys * 23) % 41) / 41
    source.data[3::4] = (np.arange(width * height) % 7) / 7
    uniforms = {
        "resolution": [width, height],
        "fullResolution": [0, 0],
        "tileOffset": [0, 0],
        "renderScale": 1,
        "seed": 1,
        "speed": 1,
        "pause": False,
    }
    uniforms.update(case)
    for key in ("alpha", "seed", "time", "speed", "density", "renderScale"):
        if key in uniforms:
            uniforms[key] = float(np.float32(uniforms[key]))
    return Ctx(
        rt,
        uniforms=uniforms,
        textures={"inputTex": source},
        resolution=np.array([width, height], dtype=np.float32),
        time=case["time"],
        seed=case.get("seed", 1),
    )


def _kernel(effect, rt):
    bundle = Path(__file__).parent.parent / "src/noisemaker_cpu/bundle/kernels/python"
    base = load_kernel((bundle / f"filter__{effect}__{effect}.py").read_text())
    return get_adapter(f"filter/{effect}", effect)(rt, base)


@pytest.mark.parametrize("case", CAPTURE["cases"], ids=lambda case: case["name"])
def test_adapter_matches_current_cpu_capture(case):
    rt = Runtime()
    ctx = _context(case, rt)
    actual = run_pass(_kernel(case["effect"], rt), ctx, case["width"], case["height"])
    expected = np.fromfile(DATA / f"{case['name']}.f32", dtype="<f4")
    np.testing.assert_array_equal(actual.data, expected)


def test_crt_shared_kernel_uses_each_context_uniforms():
    rt = Runtime()
    kernel = _kernel("crt", rt)
    for name in ("crt-default", "crt-tiled", "crt-default"):
        case = next(case for case in CAPTURE["cases"] if case["name"] == name)
        actual = run_pass(kernel, _context(case, rt), case["width"], case["height"])
        np.testing.assert_array_equal(actual.data, np.fromfile(DATA / f"{name}.f32", dtype="<f4"))
    assert kernel.uses_derivatives is False


def test_crt_fma_resolves_double_rounding_ties():
    for case in CAPTURE["fma"]:
        assert crt.fma32(*case["args"]) == case["result"]


@pytest.mark.parametrize("height", [1, 4])
def test_crt_single_column_preserves_cpu_nan_rgb_and_alpha(height):
    # Source crtFactory + GlslCpuRuntime at d7deb06e03a8 returns NaN RGB
    # for width=1: gradient_x is 0/0, while fetch's Int32Array maps NaN to 0.
    case = {"width": 1, "height": height, "alpha": 1, "time": 0.25}
    rt = Runtime()
    ctx = _context(case, rt)
    actual = run_pass(_kernel("crt", rt), ctx, 1, height)
    assert np.isnan(actual.data.reshape(-1, 4)[:, :3]).all()
    np.testing.assert_array_equal(actual.data[3::4], ctx.textures["inputTex"].data[3::4])


@pytest.mark.parametrize("offset", [2**32, -(2**32)])
def test_crt_fragment_coordinates_use_js_int32_wrap(offset):
    # Source crtKernel applies `| 0` before input fetch and CRT coordinates.
    case = next(case for case in CAPTURE["cases"] if case["name"] == "crt-default")
    rt = Runtime()
    ctx = _context(case, rt)
    ctx.frag_coord = np.array([offset + (0.5 if offset > 0 else -0.5), 0.5], dtype=np.float64)
    ctx.uv = np.array([0.5 / 8, 0.5 / 8], dtype=np.float32)
    actual = np.zeros(4, dtype=np.float32)
    _kernel("crt", rt)(ctx, actual)
    expected = np.fromfile(DATA / "crt-default.f32", dtype="<f4").reshape(8, 8, 4)[7, 0]
    np.testing.assert_array_equal(actual, expected)


def test_crt_single_row_retains_finite_cpu_output():
    # Source crtFactory + GlslCpuRuntime at d7deb06e03a8, solid RGBA input.
    case = {"width": 4, "height": 1, "alpha": 1, "time": 0.25}
    rt = Runtime()
    ctx = _context(case, rt)
    ctx.textures["inputTex"].data[:] = np.tile(np.float32([0.2, 0.4, 0.6, 0.75]), 4)
    actual = run_pass(_kernel("crt", rt), ctx, 4, 1)
    expected = np.float32(
        [
            [0.07058824598789215, 0.22352942824363708, 0.3803921937942505, 0.75],
            [0.07058824598789215, 0.22745099663734436, 0.38823533058166504, 0.75],
            [0.07058824598789215, 0.23137256503105164, 0.38823533058166504, 0.75],
            [0.07058824598789215, 0.22745099663734436, 0.38823533058166504, 0.75],
        ]
    )
    np.testing.assert_array_equal(actual.data.reshape(-1, 4), expected)
