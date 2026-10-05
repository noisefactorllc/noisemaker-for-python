"""GAP-008 (issue 4) regression: the README quick start gives a practical
first result. The first example states its expected render time and documents
the CLI's silent wait, and a fast seeded alternative renders a nondegenerate
PNG in under 60 s on one CPU. The fast alternative is executed exactly as the
README writes it, pinned to a single core when the platform allows.
"""

import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

from noisemaker_cpu.png import decode_png

README = Path(__file__).resolve().parents[1] / "README.md"
FAST_COMMAND_BUDGET_SECONDS = 60


def _render_section() -> str:
    text = README.read_text()
    match = re.search(r"^## Render an effect\n(.*?)(?=^## )", text, re.S | re.M)
    assert match, "README has no '## Render an effect' section"
    return match.group(1)


def _generate_commands(section: str) -> list[list[str]]:
    """Every `noisemaker-py generate ...` line in the section, as argv."""
    return [
        shlex.split(line)
        for line in re.findall(r"^noisemaker-py generate \S.+$", section, re.M)
    ]


def test_first_example_states_expected_render_time_and_silent_wait():
    section = _render_section()
    # The literal first example is still present ...
    assert any(
        "--width" in argv and "--height" in argv and "512" in argv for argv in _generate_commands(section)
    ), "README no longer shows the 512x512 first example"
    # ... and the quick start states its expected render time ...
    assert re.search(r"512\s*x\s*512", section), "expected-time note does not name the first example's size"
    assert re.search(r"\bminutes\b", section, re.I), "expected render time of the first example is not stated"
    # ... and documents the CLI's silent wait (criterion 3 alternative: the CLI
    # prints nothing between the effect id and the finished file).
    assert re.search(r"nothing (?:more )?until", section, re.I), "the silent wait is not documented"


def test_fast_first_render_alternative_is_seeded_and_small():
    commands = _generate_commands(_render_section())
    seeded = [argv for argv in commands if "--seed" in argv]
    assert len(seeded) == 1, f"expected exactly one explicitly seeded generate example, got {seeded}"
    argv = seeded[0]
    width = int(argv[argv.index("--width") + 1])
    height = int(argv[argv.index("--height") + 1])
    seed = int(argv[argv.index("--seed") + 1])
    # A fast first render: a small canvas keeps the one-CPU wall time well
    # inside the 60 s budget measured by test_fast_first_render_...
    assert width * height <= 48 * 48, f"fast alternative {width}x{height} is not a fast first render"
    assert 0 <= seed <= 1000, "fast alternative's seed must be inside the effect's declared range"


def _pin_to_one_cpu():
    """preexec callback pinning the child to a single core (Linux); None elsewhere."""
    if not hasattr(os, "sched_setaffinity"):
        return None
    allowed = sorted(os.sched_getaffinity(0))

    def _pin():
        os.sched_setaffinity(0, {allowed[0]})

    return _pin


def test_fast_first_render_produces_nondegenerate_png_under_60s(tmp_path):
    section = _render_section()
    seeded = [argv for argv in _generate_commands(section) if "--seed" in argv]
    assert len(seeded) == 1, f"expected exactly one explicitly seeded generate example, got {seeded}"
    argv = seeded[0]
    # Run the README line exactly as written, through the same entry point the
    # console script installs. Redirect --filename into the test's tmp dir.
    assert argv[0] == "noisemaker-py"
    assert "--filename" in argv, "the fast alternative must name its output file"
    out_name = argv[argv.index("--filename") + 1]
    command = [sys.executable, "-m", "noisemaker_cpu.cli", *argv[1:]]

    started = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=tmp_path,
        preexec_fn=_pin_to_one_cpu(),
        timeout=FAST_COMMAND_BUDGET_SECONDS + 30,
        capture_output=True,
        text=True,
    )
    elapsed = time.monotonic() - started
    assert completed.returncode == 0, completed.stderr or completed.stdout
    assert (
        elapsed < FAST_COMMAND_BUDGET_SECONDS
    ), f"fast first render took {elapsed:.1f}s (budget {FAST_COMMAND_BUDGET_SECONDS}s)"

    out_path = tmp_path / out_name
    assert out_path.is_file(), f"no PNG written to {out_path}"
    surface = decode_png(out_path.read_bytes())
    distinct = len(set(bytes(surface.data)))
    # Nondegenerate: the unseeded all-white failure mode (GAP-007) rendered
    # exactly one distinct pixel value; a real synth/curl render varies.
    assert distinct > 8, f"fast first render is degenerate: {distinct} distinct pixel values"
