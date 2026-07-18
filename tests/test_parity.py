"""Cross-language parity: Python renders must match the JS oracle within +/-2 bytes."""

import json
import os
import shutil
import subprocess

import numpy as np
import pytest

from noisemaker_cpu.png import decode_png, encode_png
from noisemaker_cpu.renderer import render_dsl, render_effect
from noisemaker_cpu.surface import Surface

CPU_DIR = os.environ.get("NOISEMAKER_CPU_DIR") or os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "noisemaker-cpu")
)
CLI = os.path.join(CPU_DIR, "bin", "noisemaker-cpu.js")

pytestmark = pytest.mark.skipif(
    not (shutil.which("node") and os.path.exists(CLI)),
    reason="JS oracle (node + noisemaker-cpu) not available",
)


def _js_render(args, out) -> Surface:
    subprocess.run(["node", CLI, *args, "--output", out], cwd=CPU_DIR, check=True, capture_output=True)
    with open(out, "rb") as f:
        return decode_png(f.read())


def _max_diff(a: Surface, b: Surface) -> int:
    da = np.frombuffer(a.to_rgba8(), dtype=np.uint8).astype(int)
    db = np.frombuffer(b.to_rgba8(), dtype=np.uint8).astype(int)
    assert da.shape == db.shape
    return int(np.max(np.abs(da - db)))


def test_solid_parity(tmp_path):
    js = _js_render(
        ["effect", "synth/solid", "--width", "16", "--height", "16", "--param", "color=#4080c0"],
        str(tmp_path / "js.png"),
    )
    py = render_effect("synth/solid", {"color": "#4080c0"}, width=16, height=16)
    assert _max_diff(js, py) <= 2


def _js_render_dsl(program, out, width=16, height=16) -> Surface:
    subprocess.run(
        ["node", CLI, "render", "-", "--width", str(width), "--height", str(height), "--output", out],
        cwd=CPU_DIR,
        input=program.encode(),
        check=True,
        capture_output=True,
    )
    with open(out, "rb") as f:
        return decode_png(f.read())


@pytest.mark.parametrize("mode", [0, 1])
def test_invert_parity(tmp_path, mode):
    # Oracle is the DSL `solid(#4080c0).invert(mode:N)` — the `effect` CLI would
    # instead invert a default gray, so it can't validate a known input.
    program = f"search synth, filter\nsolid(color: #4080c0).invert(mode: {mode}).write(o0)\nrender(o0)\n"
    js = _js_render_dsl(program, str(tmp_path / f"jsinv{mode}.png"))
    src = render_effect("synth/solid", {"color": "#4080c0"}, width=16, height=16)
    py = render_effect("filter/invert", {"mode": mode}, {"inputTex": src}, width=16, height=16)
    assert _max_diff(js, py) <= 2


# DSL `run` path: Python render_dsl must match the JS engine (node `render -`)
# for whole programs, not just single effects — chains, mixers, cross-chain
# read/write, `let` bindings, arithmetic, and inputTex-default surface params.
# Warp/displacement/refraction filters (which sample the input at fractional
# offsets) are covered by WARP_FIXED_PROGRAMS below; the two that still diverge in
# sparse outlier pixels are tracked in WARP_PROGRAMS.
RUN_PROGRAMS = {
    "solid": "search synth\nsolid(color: #336699).write(o0)\nrender(o0)\n",
    "noise-chain": (
        "search synth, filter\n"
        "noise(type: simplex, scaleX: 8, scaleY: 8, seed: 3, octaves: 1).vignette().write(o0)\n"
        "render(o0)\n"
    ),
    "mixer-cellsplit": "search synth, mixer\nnoise(seed: 3).cellSplit(invert: sourceB).write(o0)\nrender(o0)\n",
    "read-crosschain": (
        "search synth, mixer\n"
        "solid(color: #f80).write(o0)\n"
        "noise(seed: 2).cellSplit(tex: read(o0)).write(o1)\n"
        "render(o1)\n"
    ),
    "let-bindings": (
        "search synth, filter\n"
        "let amt = 3\n"
        "let base = noise(scaleX: 7, scaleY: 7)\n"
        "base(seed: 11).posterize(levels: amt).write(o0)\n"
        "render(o0)\n"
    ),
    "arithmetic": "search synth\nnoise(scaleX: 4 * 2, scaleY: 16 / 2, seed: 3).write(o0)\nrender(o0)\n",
    "multi-chain": (
        "search synth, mixer\n"
        "solid(color: #123).write(o0)\n"
        "solid(color: #abc).write(o1)\n"
        "read(o0).cellSplit(tex: o1).write(o2)\n"
        "render(o2)\n"
    ),
    # Exercises the inputTex-default surface binding (filter/lighting.heightMap
    # defaults to "inputTex"): omitted -> the compiler must bind the noise as the
    # height map, exactly as JS buildBindings does. lighting is derivative-based,
    # not a coordinate-warp, so it stays within tolerance.
    "lighting-default-heightmap": (
        "search synth, filter\nnoise(seed: 4, ridges: true).lighting().write(o0)\nrender(o0)\n"
    ),
}


@pytest.mark.parametrize("name", list(RUN_PROGRAMS))
def test_run_dsl_parity(tmp_path, name):
    program = RUN_PROGRAMS[name]
    js = _js_render_dsl(program, str(tmp_path / f"{name}.png"))
    py = render_dsl(program, width=16, height=16)
    assert _max_diff(js, py) <= 2


# Warp/displacement/refraction filters fed a *textured* input — the hardest parity
# cases, since they sample the input at data-dependent (fractional) offsets and a
# nearest-snap or ray-march break amplifies any sub-8-bit divergence. scripts/parity.py
# never caught these because it feeds every filter a solid() (a warped solid is still
# solid → 0 diff either way). All ARE now byte-exact, after three root-cause fixes:
#   1. Texture filter mode — render_effect forced every input to 'linear'; the JS
#      oracle binds only the declared externalTexture linear and leaves pooled surfaces
#      'nearest' (fixed 6 of these).
#   2. Transpiler aliasing — JS reuses a pooled array for the ray-march `rayUV`, so
#      `prevUV = rayUV` aliased it and the refinement `mix(rayUV, prevUV, w)` collapsed
#      to a no-op; codegen.py now emits in-place vector reassignment (fixed parallax).
#   3. Deferred float32 rounding — the runtime used to round after EVERY vector binary
#      op, but JS evaluates a whole component expression in float64 and rounds once at
#      the Float32Array store. Per-op rounding double-rounded and accumulated sub-ULP
#      error through the noise generator's simplex, which wormhole's point-scatter floor
#      amplified. runtime.binary/unary now defer rounding; the consumption boundaries
#      (swizzle/dot/component_wise/assign_swizzle/construct) snap to f32 (fixed wormhole,
#      and made the noise generator bit-exact).
WARP_FIXED_PROGRAMS = {
    "parallax": "search synth, filter\nnoise(seed: 3, ridges: true).parallax().write(o0)\nrender(o0)\n",
    "wormhole": "search synth, filter\nnoise(seed: 3, ridges: true).wormhole().write(o0)\nrender(o0)\n",
    "octaveWarp": "search synth, filter\nnoise(seed: 3, ridges: true).octaveWarp().write(o0)\nrender(o0)\n",
    "lowPoly": "search synth, filter\nnoise(seed: 3, ridges: true).lowPoly().write(o0)\nrender(o0)\n",
    "patchwork": "search synth, filter\nnoise(seed: 3, ridges: true).patchwork().write(o0)\nrender(o0)\n",
    "extrude": "search synth, filter\nnoise(seed: 3, ridges: true).extrude().write(o0)\nrender(o0)\n",
    "refract": "search synth, classicNoisedeck\nnoise(seed: 3, ridges: true).refract().write(o0)\nrender(o0)\n",
    "kaleido": "search synth, classicNoisedeck\nnoise(seed: 3, ridges: true).kaleido().write(o0)\nrender(o0)\n",
    "cellRefract": "search synth, classicNoisedeck\nnoise(seed: 3, ridges: true).cellRefract().write(o0)\nrender(o0)\n",
}


@pytest.mark.parametrize("name", list(WARP_FIXED_PROGRAMS))
def test_run_dsl_warp_parity(tmp_path, name):
    program = WARP_FIXED_PROGRAMS[name]
    js = _js_render_dsl(program, str(tmp_path / f"{name}.png"))
    py = render_dsl(program, width=16, height=16)
    assert _max_diff(js, py) <= 2


def test_noise_generator_is_f32_bit_exact(tmp_path):
    """The deferred-rounding fix (runtime rounds f32 at consumption boundaries, not per
    binary op) made the noise generator bit-exact vs JS at full f32 — not just 8-bit —
    which is what wormhole's point-scatter floor needs. Guards against reverting to
    per-op rounding (invisible in every 8-bit test, decisive here)."""
    script = (
        f"import {{ CpuRenderer }} from '{CPU_DIR}/src/runtime/renderer.js';"
        f"import {{ createDefaultRegistry, kernels, kernelFactories }} from '{CPU_DIR}/src/effects/catalog.js';"
        "const r=new CpuRenderer({registry:createDefaultRegistry(),kernels,kernelFactories});"
        "const s=r.render('search synth\\nnoise(seed: 3, octaves: 1).write(o0)\\nrender(o0)\\n',"
        "{width:16,height:16,seed:3}).surface;"
        "process.stdout.write(JSON.stringify([...s.data]));"
    )
    path = tmp_path / "noise.mjs"
    path.write_text(script)
    out = subprocess.run(["node", str(path)], capture_output=True, text=True, check=True)
    js = np.array(json.loads(out.stdout), dtype=np.float32)
    py = render_effect("synth/noise", {"seed": 3, "octaves": 1}, width=16, height=16).data
    assert np.array_equal(py, js), f"noise f32 differs at {int((py != js).sum())}/{py.size} elements"


def test_wormhole_kernel_is_byte_exact(tmp_path):
    """wormhole's residual is upstream (noise f32), not its kernel: applied to a
    byte-identical input, Python's wormhole matches node's exactly."""
    src = render_effect("synth/noise", {"seed": 5, "ridges": True}, width=24, height=24, seed=5)
    png = tmp_path / "src.png"
    png.write_bytes(encode_png(src))
    py = render_effect("filter/wormhole", {}, {"inputTex": decode_png(png.read_bytes())}, width=24, height=24, seed=1)
    js = _js_render(["apply", "filter/wormhole", str(png), "--seed", "1"], str(tmp_path / "js.png"))
    assert _max_diff(js, py) == 0
