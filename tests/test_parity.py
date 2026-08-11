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


@pytest.mark.parametrize("effect_id", ["classicNoisedeck/noise3d", "classicNoisedeck/shapes3d"])
def test_new_classic_image_effect_parity(tmp_path, effect_id):
    js = _js_render(
        ["effect", effect_id, "--width", "8", "--height", "8", "--seed", "1", "--time", "0.25"],
        str(tmp_path / f"{effect_id.replace('/', '__')}.png"),
    )
    py = render_effect(effect_id, width=8, height=8, seed=1, time=0.25)

    assert _max_diff(js, py) <= 2


def _js_render_dsl(program, out, width=16, height=16, seed=None, time=None) -> Surface:
    args = ["node", CLI, "render", "-", "--width", str(width), "--height", str(height), "--output", out]
    if seed is not None:
        args += ["--seed", str(seed)]
    if time is not None:
        args += ["--time", str(time)]
    subprocess.run(
        args,
        cwd=CPU_DIR,
        input=program.encode(),
        check=True,
        capture_output=True,
    )
    with open(out, "rb") as f:
        return decode_png(f.read())


ITERATED_PROGRAMS = {
    **{
        f"filter/{func}": (
            f"search synth, filter\nnoise(seed: 1, ridges: true).{func}(iterationCount: 2).write(o0)\nrender(o0)\n"
        )
        for func in ("convolutionFeedback", "feedback", "motionBlur", "temporalAberration")
    },
    **{
        f"points/{func}": (
            "search synth, points, render\n"
            "perlin(seed: 0).pointsEmit(seed: 0, stateSize: 64, iterationCount: 2)"
            f".{func}().pointsRender().write(o0)\n"
            "render(o0)\n"
        )
        for func in (
            "attractor",
            "buddhabrot",
            "dla",
            "flock",
            "flow",
            "hydraulic",
            "lenia",
            "life",
            "physarum",
            "physical",
        )
    },
    "render/pointsBillboardRender": (
        "search synth, points, render\n"
        "polygon(radius: 0.7, fgAlpha: 0.1, bgAlpha: 0).write(o0)\n"
        "perlin(seed: 0).pointsEmit(seed: 0, stateSize: 64, iterationCount: 2).physical()"
        ".pointsBillboardRender(seed: 42, tex: read(o0), pointSize: 40).write(o1)\n"
        "render(o1)\n"
    ),
    "render/pointsEmit": (
        "search synth, points, render\n"
        "perlin(seed: 0).pointsEmit(seed: 0, stateSize: 64, iterationCount: 2)"
        ".physical().pointsRender().write(o0)\n"
        "render(o0)\n"
    ),
    "render/pointsRender": (
        "search synth, points, render\n"
        "perlin(seed: 0).pointsEmit(seed: 0, stateSize: 64, iterationCount: 2)"
        ".physical().pointsRender().write(o0)\n"
        "render(o0)\n"
    ),
    **{
        f"synth/{func}": (
            "search synth\n"
            "noise(seed: 1, ridges: true).write(o0)\n"
            f"{func}(seed: 1, tex: read(o0), iterationCount: 2, zoom: 2).write(o1)\n"
            "render(o1)\n"
        )
        for func in ("cellularAutomata", "mnca", "navierStokes", "reactionDiffusion")
    },
}


@pytest.mark.parametrize(("effect_id", "program"), ITERATED_PROGRAMS.items(), ids=ITERATED_PROGRAMS)
def test_iterated_effect_byte_parity(tmp_path, effect_id, program):
    js = _js_render_dsl(
        program,
        str(tmp_path / f"{effect_id.replace('/', '__')}.png"),
        width=8,
        height=8,
        seed=1,
        time=0.25,
    )
    py = render_dsl(program, width=8, height=8, seed=1, time=0.25)

    assert _max_diff(js, py) == 0


def test_loop_region_byte_parity(tmp_path):
    program = (
        "search synth, filter, render\n"
        "solid(color: #336699).loopBegin(iterationCount: 3).invert().loopEnd().write(o0)\n"
        "render(o0)\n"
    )

    js = _js_render_dsl(program, str(tmp_path / "loop.png"), width=2, height=2, seed=1, time=0.25)
    py = render_dsl(program, width=2, height=2, seed=1, time=0.25)

    assert _max_diff(js, py) == 0


def test_loop_region_keeps_step_resources_isolated_byte_parity(tmp_path):
    program = (
        "search synth, filter, render\n"
        "solid(color: #336699).loopBegin(iterationCount: 2).feedback(mix: 50)"
        ".motionBlur(amount: 50).loopEnd().write(o0)\n"
        "render(o0)\n"
    )

    js = _js_render_dsl(program, str(tmp_path / "stateful-loop.png"), width=2, height=2, seed=1, time=0.25)
    py = render_dsl(program, width=2, height=2, seed=1, time=0.25)

    assert _max_diff(js, py) == 0


@pytest.mark.parametrize(
    ("generator", "generator_params"),
    [
        ("cell3d", "volumeSize: 4, seed: 0"),
        ("flythrough3d", "volumeSize: 4"),
        ("fractal3d", "volumeSize: 4"),
        ("noise3d", "volumeSize: 4, seed: 0"),
        ("shape3d", "volumeSize: 4"),
    ],
)
def test_volume_generator_render3d_byte_parity(tmp_path, generator, generator_params):
    program = f"search synth3d, render\n{generator}({generator_params}).render3d(volumeSize: 4).write(o0)\nrender(o0)\n"

    js = _js_render_dsl(program, str(tmp_path / f"{generator}.png"), width=2, height=2, seed=1, time=0.25)
    py = render_dsl(program, width=2, height=2, seed=1, time=0.25)

    assert _max_diff(js, py) == 0


@pytest.mark.parametrize(
    "renderer_name",
    ["render3d", "renderCubemap3d", "renderCubemapSurface", "renderLit3d"],
)
def test_volume_renderer_byte_parity(tmp_path, renderer_name):
    program = (
        "search synth3d, render\n"
        f"noise3d(volumeSize: 4, seed: 0).{renderer_name}(volumeSize: 4).write(o0)\n"
        "render(o0)\n"
    )

    js = _js_render_dsl(program, str(tmp_path / f"{renderer_name}.png"), width=2, height=2, seed=1, time=0.25)
    py = render_dsl(program, width=2, height=2, seed=1, time=0.25)

    assert _max_diff(js, py) == 0


def test_palette3d_filter_byte_parity(tmp_path):
    program = (
        "search synth3d, filter3d, render\n"
        "noise3d(volumeSize: 4, seed: 0).palette3d(volumeSize: 4).render3d(volumeSize: 4).write(o0)\n"
        "render(o0)\n"
    )

    js = _js_render_dsl(program, str(tmp_path / "palette3d.png"), width=2, height=2, seed=1, time=0.25)
    py = render_dsl(program, width=2, height=2, seed=1, time=0.25)

    assert _max_diff(js, py) == 0


@pytest.mark.parametrize("iteration_count", [0, 2])
def test_flow3d_filter_byte_parity(tmp_path, iteration_count):
    program = (
        "search synth3d, filter3d, render\n"
        "noise3d(volumeSize: 4, seed: 0)"
        f".flow3d(volumeSize: 4, density: 20, iterationCount: {iteration_count})"
        ".render3d(volumeSize: 4).write(o0)\n"
        "render(o0)\n"
    )

    js = _js_render_dsl(
        program,
        str(tmp_path / f"flow3d-{iteration_count}.png"),
        width=2,
        height=2,
        seed=1,
        time=0.25,
    )
    py = render_dsl(program, width=2, height=2, seed=1, time=0.25)

    assert _max_diff(js, py) == 0


@pytest.mark.parametrize("iteration_count", [0, 2])
@pytest.mark.parametrize("effect", ["cellularAutomata3d", "reactionDiffusion3d"])
def test_stateful_volume_generator_byte_parity(tmp_path, effect, iteration_count):
    program = (
        "search synth3d, render\n"
        f"noise3d(volumeSize: 4, seed: 0).{effect}(volumeSize: 4, iterationCount: {iteration_count})"
        ".render3d(volumeSize: 4).write(o0)\n"
        "render(o0)\n"
    )

    js = _js_render_dsl(
        program,
        str(tmp_path / f"{effect}-{iteration_count}.png"),
        width=2,
        height=2,
        seed=1,
        time=0.25,
    )
    py = render_dsl(program, width=2, height=2, seed=1, time=0.25)

    assert _max_diff(js, py) == 0


@pytest.mark.parametrize("func", ("cellularAutomata", "mnca", "navierStokes", "reactionDiffusion"))
def test_simulation_effect_non_divisible_byte_parity(tmp_path, func):
    program = (
        "search synth\n"
        "noise(seed: 1, ridges: true).write(o0)\n"
        f"{func}(seed: 1, tex: read(o0), iterationCount: 2, zoom: 32).write(o1)\n"
        "render(o1)\n"
    )

    js = _js_render_dsl(
        program,
        str(tmp_path / f"{func}-non-divisible.png"),
        width=65,
        height=63,
        seed=1,
        time=0.25,
    )
    py = render_dsl(program, width=65, height=63, seed=1, time=0.25)

    assert _max_diff(js, py) == 0


@pytest.mark.parametrize("mode", [0, 1])
def test_invert_parity(tmp_path, mode):
    # Oracle is the DSL `solid(#4080c0).invert(mode:N)` — the `effect` CLI would
    # instead invert a default gray, so it can't validate a known input.
    program = f"search synth, filter\nsolid(color: #4080c0).invert(mode: {mode}).write(o0)\nrender(o0)\n"
    js = _js_render_dsl(program, str(tmp_path / f"jsinv{mode}.png"))
    src = render_effect("synth/solid", {"color": "#4080c0"}, width=16, height=16)
    py = render_effect("filter/invert", {"mode": mode}, {"inputTex": src}, width=16, height=16)
    assert _max_diff(js, py) <= 2


def test_coalesce_hue_ab_byte_parity(tmp_path):
    program = (
        "search synth, classicNoisedeck\n"
        "solid(color: #ff2200).write(o0)\n"
        "solid(color: #00ccff).coalesce(tex: read(o0), blendMode: hueAB).write(o1)\n"
        "render(o1)\n"
    )

    js = _js_render_dsl(program, str(tmp_path / "coalesce-hue-ab.png"))
    py = render_dsl(program, width=16, height=16)

    assert _max_diff(js, py) == 0


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
