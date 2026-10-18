"""Non-default parity cases for the CPU d7deb06e03a8 synchronization."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

from noisemaker_cpu.kernel_loader import load_kernel
from noisemaker_cpu.pass_runner import Ctx
from noisemaker_cpu.renderer import render_dsl
from noisemaker_cpu.runtime import Runtime

ROOT = Path(__file__).parent.parent
CPU_DIR = Path(os.environ.get("NOISEMAKER_CPU_DIR", ROOT.parent / "noisemaker-for-cpu"))
DATA = Path(__file__).parent / "data" / "cpu-sync"

# Exact programs from CPU test/fixtures/authority/vector-writes-m4.json.
# Comparisons below use the current CPU's bytes, rather than GPU tolerances.
VECTOR_PROGRAMS = {
    "edge-channel-luminance": (
        "search filter, synth\n\nnoise(seed: 1, ridges: true)\n"
        "  .edge(channel: luminance)\n  .write(o0)\n\nrender(o0)\n"
    ),
    "shapeMask-triangle": (
        "search mixer, synth\n\nnoise(seed: 1, ridges: true, colorMode: mono)\n.write(o0)\n\n"
        "noise(seed: 1, ridges: true)\n.shapeMask(tex: read(o0), shape: triangle)\n.write(o1)\n\nrender(o1)\n"
    ),
    "mandelbrot-outputMode-distance": (
        "search synth\n\nmandelbrot(outputMode: distance)\n  .write(o0)\n\nrender(o0)\n"
    ),
}

IMAGE_CASES = [
    {"id": name, "program": program, "width": 8, "height": 8, "seed": 1, "time": 0.25}
    for name, program in VECTOR_PROGRAMS.items()
]
for name, effect in (
    ("scatter-anisotropic", "scatter(seed: 7, mode: anisotropic)"),
    ("reverb-mirror", "reverb(wrap: mirror)"),
    ("extrude-default", "extrude()"),
):
    IMAGE_CASES.append(
        {
            "id": name,
            "program": f"search filter, synth\n\nnoise(seed: 7, ridges: true)\n  .{effect}\n"
            "  .write(o0)\n\nrender(o0)\n",
            "width": 41,
            "height": 23,
            "seed": 7,
            "time": 0.75,
        }
    )
IMAGE_CASES.append(
    {
        "id": "spookyTicker-readable-glyph",
        "program": "search filter, synth\n\nperlin(seed: 7)\n  .spookyTicker(seed: 7)\n  .write(o0)\n",
        "width": 41,
        "height": 23,
        "seed": 7,
        "time": 0.75,
    }
)

# Import the public CPU renderer directly. Unlike the general CLI batch helper,
# this driver does not create a temporary module in the source checkout.
NODE_RENDER_DRIVER = r"""
import {readFileSync, writeFileSync} from 'node:fs'
import {resolve} from 'node:path'
import {pathToFileURL} from 'node:url'
const {CpuRenderer, createDefaultRegistry, kernelFactories} = await import(
  pathToFileURL(resolve(process.env.NOISEMAKER_CPU_DIR, 'src/index.js')).href)
for (const job of JSON.parse(readFileSync(0, 'utf8'))) {
  const renderer = new CpuRenderer({registry: createDefaultRegistry(), kernelFactories})
  const result = renderer.render(job.program,
    {width: job.width, height: job.height, seed: job.seed, time: job.time})
  writeFileSync(job.out, result.toRgba8())
}
"""


@pytest.fixture(scope="module")
def cpu_sync_image_batch(tmp_path_factory):
    directory = tmp_path_factory.mktemp("cpu-sync-images")
    jobs = [{**case, "out": str(directory / f"{case['id']}.rgba")} for case in IMAGE_CASES]
    subprocess.run(
        ["node", "--input-type=module", "-e", NODE_RENDER_DRIVER],
        input=json.dumps(jobs),
        text=True,
        capture_output=True,
        check=True,
        timeout=60,
        env={**os.environ, "NOISEMAKER_CPU_DIR": str(CPU_DIR.resolve())},
    )
    return {job["id"]: Path(job["out"]).read_bytes() for job in jobs}


@pytest.mark.oracle
@pytest.mark.skipif(
    not (shutil.which("node") and (CPU_DIR / "src/index.js").is_file()),
    reason="JS CPU oracle is unavailable",
)
@pytest.mark.parametrize("case", IMAGE_CASES, ids=lambda case: case["id"])
def test_sync_nondefault_image_matches_cpu_bytes(case, cpu_sync_image_batch):
    actual = render_dsl(
        case["program"], width=case["width"], height=case["height"], seed=case["seed"], time=case["time"]
    ).to_rgba8()
    expected = cpu_sync_image_batch[case["id"]]
    assert len(expected) == case["width"] * case["height"] * 4
    assert actual == expected


VOLUME_PROBES = json.loads((DATA / "seeded-volume-probes.json").read_text())["fixtures"]


@pytest.mark.parametrize("case", VOLUME_PROBES, ids=lambda case: f"{case['effect']}-seed{case['seed']}")
def test_sync_seeded_volume_sparse_raw_outputs(case):
    """Twelve atlas pixels retain all eight f32 lanes, including geoOut."""
    width, height = case["width"], case["height"]
    resolution = np.array([width, height], dtype=np.float32)
    uniforms = {
        "renderScale": 1,
        "speed": 0,
        "centerLoX": 0,
        "centerLoY": 0,
        "size": np.zeros(4, dtype=np.float32),
        "motion": np.zeros(4, dtype=np.float32),
        **case["uniforms"],
        "resolution": resolution,
        "fullResolution": resolution,
        "tileOffset": np.zeros(2, dtype=np.float32),
        "aspectRatio": float(np.float32(width / height)),
        "aspect": float(np.float32(width / height)),
        "aspectInv": float(np.float32(height / width)),
        "invFullResolution": np.array([1 / width, 1 / height], dtype=np.float32),
        "globalTime": case["time"],
        "deltaTime": 0,
        "frame": 0,
    }
    path = ROOT / "src/noisemaker_cpu/bundle/kernels/python" / (
        case["effect"].replace("/", "__") + "__precompute.py"
    )
    kernel = load_kernel(path.read_text())
    rt = Runtime()
    ctx = Ctx(rt, uniforms=uniforms, resolution=resolution, time=case["time"], seed=case["seed"])
    for probe in case["probes"]:
        x, y = probe["x"], probe["y"]
        ctx.frag_coord = np.array([x + 0.5, y + 0.5, 0, 1], dtype=np.float32)
        ctx.uv = np.array([(x + 0.5) / width, (y + 0.5) / height], dtype=np.float32)
        rt.begin_pixel(ctx)
        actual = np.zeros((2, 4), dtype=np.float32)
        kernel(ctx, actual)
        np.testing.assert_array_equal(actual.reshape(-1).view(np.uint32), np.uint32(probe["outputBits"]))
