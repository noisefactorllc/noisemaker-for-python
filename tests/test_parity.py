"""Cross-language parity: Python renders must match the JS oracle within +/-2 bytes."""

import os
import shutil
import subprocess

import numpy as np
import pytest

from noisemaker_cpu.png import decode_png
from noisemaker_cpu.renderer import render_effect
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
