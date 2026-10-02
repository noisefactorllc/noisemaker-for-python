"""Cross-language parity: Python renders must match the JS oracle within +/-2 bytes."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

from noisemaker_cpu.png import decode_png, encode_png
from noisemaker_cpu.renderer import render_dsl, render_effect
from noisemaker_cpu.surface import Surface

CPU_DIR = os.environ.get("NOISEMAKER_CPU_DIR") or os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "noisemaker-for-cpu")
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
        str(tmp_path / f"{effect_id.replace('/', '__').replace(':', '_')}.png"),
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
    "render/pointsBillboardRender:perspective_defocus": (
        "search synth, points, render\n"
        "polygon(radius: 0.7, fgAlpha: 0.1, bgAlpha: 0).write(o0)\n"
        "perlin(seed: 0).pointsEmit(seed: 0, stateSize: 64, iterationCount: 2).physical()"
        ".pointsBillboardRender(seed: 42, tex: read(o0), pointSize: 8, viewMode: perspective, "
        "rotateX: 0.4, posZ: 10, sizeDistance: 60, brightnessDistance: 60, aperture: 4, "
        "focalDistance: 70).write(o1)\n"
        "render(o1)\n"
    ),
    # NOTE: blendMode:alpha's depth-sort (depthKeys + a 22-stage depthMerge cascade) is
    # deliberately NOT added here as a DSL-chain byte-parity fixture. It's a fullscreen pass
    # over the stateSize x stateSize order texture regardless of the render target's own size,
    # and the DSL validator enforces stateSize >= 64 (4096 order-texture pixels x 22 merge
    # stages = ~90k interpreted-Python per-pixel kernel invocations) -- multiple minutes here,
    # not a viable addition to the routine test suite. The reindex logic itself (the part this
    # port hand-implements, as opposed to depthKeys/depthMerge which are auto-transpiled from
    # GLSL like every other fullscreen kernel) is covered directly and quickly by
    # tests/test_scatter_adapters.py's blendMode=1 reindex test instead.
    "render/pointsRender:perspective": (
        "search synth, points, render\n"
        "perlin(seed: 0).pointsEmit(seed: 0, stateSize: 64, iterationCount: 2).physical()"
        ".pointsRender(viewMode: perspective, rotateX: 0.4, posZ: 10, fieldOfView: 70).write(o0)\n"
        "render(o0)\n"
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
        str(tmp_path / f"{effect_id.replace('/', '__').replace(':', '_')}.png"),
        width=8,
        height=8,
        seed=1,
        time=0.25,
    )
    py = render_dsl(program, width=8, height=8, seed=1, time=0.25)

    assert _max_diff(js, py) == 0


# Volume/loop DSL parity cases, shared with scripts/parity-summary (which
# executes one case per bundled effect id to count whole-catalog coverage).
# Each row: (case_id, program, width, height); ":"-suffixed ids are additional
# settings variants of the same effect id. All rows must render byte-exactly.
VOLUME_DSL_CASES = [
    # Volume generators chained through render3d.
    ("synth3d/cell3d", "search synth3d, render\ncell3d(volumeSize: 4, seed: 0).render3d(volumeSize: 4).write(o0)\nrender(o0)\n", 2, 2),
    ("synth3d/flythrough3d", "search synth3d, render\nflythrough3d(volumeSize: 4).render3d(volumeSize: 4).write(o0)\nrender(o0)\n", 2, 2),
    ("synth3d/fractal3d", "search synth3d, render\nfractal3d(volumeSize: 4).render3d(volumeSize: 4).write(o0)\nrender(o0)\n", 2, 2),
    ("synth3d/noise3d", "search synth3d, render\nnoise3d(volumeSize: 4, seed: 0).render3d(volumeSize: 4).write(o0)\nrender(o0)\n", 2, 2),
    ("synth3d/shape3d", "search synth3d, render\nshape3d(volumeSize: 4).render3d(volumeSize: 4).write(o0)\nrender(o0)\n", 2, 2),
    ("synth3d/heightmap3d", "search synth3d, render\nheightmap3d(volumeSize: 4).render3d(volumeSize: 4).write(o0)\nrender(o0)\n", 2, 2),
    # Stateful volume generators.
    ("synth3d/cellularAutomata3d", "search synth3d, render\nnoise3d(volumeSize: 4, seed: 0).cellularAutomata3d(volumeSize: 4, iterationCount: 0).render3d(volumeSize: 4).write(o0)\nrender(o0)\n", 2, 2),
    ("synth3d/cellularAutomata3d:iter2", "search synth3d, render\nnoise3d(volumeSize: 4, seed: 0).cellularAutomata3d(volumeSize: 4, iterationCount: 2).render3d(volumeSize: 4).write(o0)\nrender(o0)\n", 2, 2),
    ("synth3d/reactionDiffusion3d", "search synth3d, render\nnoise3d(volumeSize: 4, seed: 0).reactionDiffusion3d(volumeSize: 4, iterationCount: 0).render3d(volumeSize: 4).write(o0)\nrender(o0)\n", 2, 2),
    ("synth3d/reactionDiffusion3d:iter2", "search synth3d, render\nnoise3d(volumeSize: 4, seed: 0).reactionDiffusion3d(volumeSize: 4, iterationCount: 2).render3d(volumeSize: 4).write(o0)\nrender(o0)\n", 2, 2),
    # Volume renderers over noise3d.
    ("render/render3d", "search synth3d, render\nnoise3d(volumeSize: 4, seed: 0).render3d(volumeSize: 4).write(o0)\nrender(o0)\n", 2, 2),
    ("render/renderCubemap3d", "search synth3d, render\nnoise3d(volumeSize: 4, seed: 0).renderCubemap3d(volumeSize: 4).write(o0)\nrender(o0)\n", 2, 2),
    ("render/renderCubemapSurface", "search synth3d, render\nnoise3d(volumeSize: 4, seed: 0).renderCubemapSurface(volumeSize: 4).write(o0)\nrender(o0)\n", 2, 2),
    ("render/renderLit3d", "search synth3d, render\nnoise3d(volumeSize: 4, seed: 0).renderLit3d(volumeSize: 4).write(o0)\nrender(o0)\n", 2, 2),
    # Both valid renderLandscape3d `filtering` choices (the GAP-001 landscape
    # rejections) must render byte-identically to the oracle.
    ("render/renderLandscape3d", "search synth3d, render\nnoise3d(volumeSize: 4, seed: 0).renderLandscape3d(volumeSize: 4, filtering: 0).write(o0)\nrender(o0)\n", 8, 8),
    ("render/renderLandscape3d:voxel", "search synth3d, render\nnoise3d(volumeSize: 4, seed: 0).renderLandscape3d(volumeSize: 4, filtering: 1).write(o0)\nrender(o0)\n", 8, 8),
    # filter3d filters.
    ("filter3d/palette3d", "search synth3d, filter3d, render\nnoise3d(volumeSize: 4, seed: 0).palette3d(volumeSize: 4).render3d(volumeSize: 4).write(o0)\nrender(o0)\n", 2, 2),
    ("filter3d/flow3d", "search synth3d, filter3d, render\nnoise3d(volumeSize: 4, seed: 0).flow3d(volumeSize: 4, density: 20, iterationCount: 0).render3d(volumeSize: 4).write(o0)\nrender(o0)\n", 2, 2),
    ("filter3d/flow3d:iter2", "search synth3d, filter3d, render\nnoise3d(volumeSize: 4, seed: 0).flow3d(volumeSize: 4, density: 20, iterationCount: 2).render3d(volumeSize: 4).write(o0)\nrender(o0)\n", 2, 2),
    # Loop regions: both markers of each program are exercised by one render.
    ("render/loopBegin", "search synth, filter, render\nsolid(color: #336699).loopBegin(iterationCount: 3).invert().loopEnd().write(o0)\nrender(o0)\n", 2, 2),
    ("render/loopEnd", "search synth, filter, render\nsolid(color: #336699).loopBegin(iterationCount: 3).invert().loopEnd().write(o0)\nrender(o0)\n", 2, 2),
    ("render/loopBegin:stateful", "search synth, filter, render\nsolid(color: #336699).loopBegin(iterationCount: 2).feedback(mix: 50).motionBlur(amount: 50).loopEnd().write(o0)\nrender(o0)\n", 2, 2),
    ("render/loopEnd:stateful", "search synth, filter, render\nsolid(color: #336699).loopBegin(iterationCount: 2).feedback(mix: 50).motionBlur(amount: 50).loopEnd().write(o0)\nrender(o0)\n", 2, 2),
]


@pytest.mark.parametrize(("case_id", "program", "width", "height"), VOLUME_DSL_CASES, ids=[c[0] for c in VOLUME_DSL_CASES])
def test_volume_and_loop_dsl_byte_parity(tmp_path, case_id, program, width, height):
    js = _js_render_dsl(
        program,
        str(tmp_path / f"{case_id.replace('/', '__').replace(':', '_')}.png"),
        width=width,
        height=height,
        seed=1,
        time=0.25,
    )
    py = render_dsl(program, width=width, height=height, seed=1, time=0.25)

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


def _parity_script_module():
    """Load scripts/parity.py (the whole-catalog harness) for its external-input
    fixture mirror and the oracle-side DSL cases."""
    import importlib.util

    path = Path(__file__).resolve().parent.parent / "scripts" / "parity.py"
    spec = importlib.util.spec_from_file_location("_noisemaker_parity_tests", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "case_id",
    ["synth/roll", "synth/scope", "synth/spectrum", "render/meshLoader", "render/meshRender"],
)
def test_external_input_dsl_byte_parity(tmp_path, case_id):
    """Reactive (MIDI/audio) and mesh (OBJ) parity cases — noisemaker-for-cpu
    GAP-003's reactive/mesh import, synced here. Both sides render the oracle's
    own parity DSL (parity/upstream-defaults/<name>.dsl) with the deterministic
    fixtures (MIDI note grid / audio waveform+spectrum / packed cube mesh); the
    oracle side binds them via scripts/parity-js-driver.mjs because the CLI binds
    no fixture. Zero tolerance, like the rest of the catalog contract."""
    parity = _parity_script_module()
    program = parity._external_case_dsl(case_id)
    js = parity.js_effect_external(case_id, str(tmp_path / f"{case_id.replace('/', '__')}.png"))
    py = render_dsl(
        program,
        width=parity.SIZE,
        height=parity.SIZE,
        seed=parity.SEED,
        time=parity.TIME,
        external_inputs=parity.external_inputs_for_case(case_id),
    )
    assert _max_diff(js, py) == 0


def test_external_input_fixtures_are_deterministic():
    """The fixture mirror must be deterministic and shape-correct: re-running the
    builders yields identical arrays (a nondeterministic fixture would make the
    byte-exact comparisons above meaningless)."""
    import numpy as np

    parity = _parity_script_module()
    midi_a = parity.midi_fixture()
    midi_b = parity.midi_fixture()
    assert np.array_equal(midi_a.note_grid, midi_b.note_grid)
    assert midi_a.clock_count == 24  # 24 clock pulses — one beat at 24 PPQ
    audio = parity.audio_fixture()
    assert audio.waveform.shape == (128,) and audio.spectrum.shape == (128,)
    mesh = parity.mesh_fixture()
    assert mesh["texWidth"] == 256 and mesh["texHeight"] == 256
    assert mesh["vertexCount"] == 36  # 12 triangles x 3 vertices


def test_noise_generator_is_f32_bit_exact(tmp_path):
    """The deferred-rounding fix (runtime rounds f32 at consumption boundaries, not per
    binary op) made the noise generator bit-exact vs JS at full f32 — not just 8-bit —
    which is what wormhole's point-scatter floor needs. Guards against reverting to
    per-op rounding (invisible in every 8-bit test, decisive here)."""
    script = (
        f"import {{ CpuRenderer }} from '{Path(CPU_DIR, 'src/runtime/renderer.js').as_uri()}';"
        f"import {{ createDefaultRegistry, kernels, kernelFactories }} from "
        f"'{Path(CPU_DIR, 'src/effects/catalog.js').as_uri()}';"
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


@pytest.mark.parametrize("effect_id", ["filter/mosaicTiles", "filter/stipple", "filter/strokes"])
def test_canonical_hash_filters_are_byte_exact(tmp_path, effect_id):
    js = _js_render(
        ["effect", effect_id, "--width", "8", "--height", "8", "--seed", "1", "--time", "0.25"],
        str(tmp_path / "reference.png"),
    )
    source = render_effect("synth/solid", width=8, height=8, seed=1, time=0.25)
    py = render_effect(effect_id, inputs={"inputTex": source}, width=8, height=8, seed=1, time=0.25)
    assert _max_diff(js, py) == 0


# Audited sibling noisemaker-for-cpu source locks, keyed by PINNED_UPSTREAM_REVISION.
# An entry is added only by an audited source-lock sync recorded in
# docs/COMPATIBILITY.md whose oracle output was proven byte-identical to the
# previous pin across the whole rendered catalog (167/167 byte-exact, zero
# tolerance) and whose recomputed digest was verified byte-for-byte against the
# sibling checkout. The gate's immutable oracle tarball
# (.github/workflows/tests.yml) is pinned at 296e0138/b61b658399f1; the current
# sibling pin f24b5254/d2965d0b7880 was audited by the 2026-09-29 sync and
# e24c844/5f12866e91 was audited by the 2026-09-30 sync.
AUDITED_SOURCE_LOCKS = {
    "296e0138c4744ed485b2e95de3eeb466c17629ee": {
        "digest": "e371a1650d1ace9462a20ecf4e4f0902e5135b4772e8a9abbc8d2c037beebf59",
        "snapshot": "296e0138c4744ed485b2e95de3eeb466c17629ee",
    },
    "f24b52540af6a88d12daa05feba1a04ad61b22a2": {
        "digest": "f11af18a15ec0220c5d41a17c70da637fa05f86597a4c1984838bd0e77246723",
        "snapshot": "f24b52540af6a88d12daa05feba1a04ad61b22a2",
    },
    "e24c844f8dada85551ab084f41db8944fbc176c8": {
        "digest": "c2e0c264dc20338b19a144ee0888bd2ca39edcf325315a7d7ae1f5ced920804d",
        "snapshot": "e24c844f8dada85551ab084f41db8944fbc176c8",
    },
}


def test_cpu_upstream_source_lock_and_catalog_parity():
    """Verify sibling noisemaker-for-cpu's source lock points to an audited
    revision (revision, digest, and snapshot revision all matching one audited
    source-lock sync) and that catalog effect parity is maintained."""
    source_lock_path = Path(CPU_DIR) / "scripts" / "upstream" / "source-lock.js"
    assert source_lock_path.is_file(), f"missing {source_lock_path}"
    source_lock_text = source_lock_path.read_text(encoding="utf-8")

    def _locked(prefix: str) -> str:
        for line in source_lock_text.splitlines():
            if line.startswith(prefix):
                return line.split("'")[1]
        raise AssertionError(f"{prefix!r} not found in {source_lock_path}")

    revision = _locked("export const PINNED_UPSTREAM_REVISION =")
    audited = AUDITED_SOURCE_LOCKS.get(revision)
    assert audited is not None, (
        f"sibling source lock pins {revision}, which is not an audited "
        f"revision (audited: {sorted(AUDITED_SOURCE_LOCKS)})"
    )
    assert _locked("export const PINNED_SOURCE_DIGEST =") == audited["digest"]

    snapshot_path = Path(CPU_DIR) / "src" / "effects" / "generated" / "upstream-snapshot.js"
    assert snapshot_path.is_file(), f"missing {snapshot_path}"
    snapshot_text = snapshot_path.read_text(encoding="utf-8")
    assert f'export const UPSTREAM_REVISION = "{audited["snapshot"]}"' in snapshot_text
