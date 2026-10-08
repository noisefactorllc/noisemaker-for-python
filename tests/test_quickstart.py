"""Regression: the README quick start gives a practical
first result. Every quick-start generate example states its expected one-CPU
render time in its own comment block, the CLI's silent wait is documented,
and a fast seeded alternative renders a nondegenerate PNG in under 60 s on
one CPU. The fast alternative is executed exactly as the README writes it,
pinned to a single core when the platform allows.
"""

import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

import pytest

from noisemaker_cpu.png import decode_png

README = Path(__file__).resolve().parents[1] / "README.md"
FAST_COMMAND_BUDGET_SECONDS = 60


def _render_section() -> str:
    text = README.read_text()
    match = re.search(r"^## Render an effect\n(.*?)(?=^## )", text, re.S | re.M)
    assert match, "README has no '## Render an effect' section"
    return match.group(1)


def _command_blocks(section: str) -> list[tuple[str, list[str]]]:
    """Each `noisemaker-py generate ...` line as (its comment block, argv). The
    comment block directly above a command is the one describing it; comments
    reset on any blank, prose, or non-generate command line, so a time note
    asserted here belongs to that exact example."""
    blocks = []
    comments: list[str] = []
    for raw in section.splitlines():
        line = raw.strip()
        if line.startswith("#"):
            comments.append(line.lstrip("#").strip())
        elif line.startswith("noisemaker-py generate "):
            blocks.append((" ".join(comments), shlex.split(line)))
            comments = []
        else:
            comments = []
    return blocks


def _fast_block(blocks: list[tuple[str, list[str]]]) -> tuple[str, list[str]]:
    seeded = [block for block in blocks if "--seed" in block[1]]
    assert len(seeded) == 1, f"expected exactly one explicitly seeded generate example, got {[b[1] for b in seeded]}"
    return seeded[0]


def _full_size_block(blocks: list[tuple[str, list[str]]]) -> tuple[str, list[str]]:
    full = [block for block in blocks if "--width" in block[1] and "--height" in block[1] and "512" in block[1]]
    assert len(full) == 1, f"expected the 512x512 example, got {[b[1] for b in full]}"
    return full[0]


def test_each_generate_example_states_its_expected_render_time_and_the_silent_wait():
    blocks = _command_blocks(_render_section())
    fast_comments, _ = _fast_block(blocks)
    full_comments, _ = _full_size_block(blocks)

    # Criterion 1: every quick-start generate example states its expected
    # render time on one CPU core, bound to that example's own comment block.
    # The full-size 512x512 example states its time in minutes ...
    assert re.search(r"512\s*x\s*512", full_comments), "the 512x512 time note does not name the example's size"
    assert re.search(r"\bminutes\b", full_comments, re.I), "the 512x512 example does not state its render time"
    # ... and the fast first example states a sub-minute seconds figure.
    match = re.search(r"~\s*(\d+)\s*s\b", fast_comments)
    assert match, "the fast first example does not state its expected render time in seconds"
    assert int(match.group(1)) < FAST_COMMAND_BUDGET_SECONDS, "the fast example's stated time is not sub-minute"
    assert "one CPU core" in fast_comments and "one CPU core" in full_comments, (
        "the stated times must be qualified as one-CPU-core times"
    )

    # Criterion 3 alternative: the README documents the CLI's silent wait (the
    # CLI prints nothing between the effect id and the finished file).
    assert re.search(r"nothing (?:more )?until", full_comments, re.I), "the silent wait is not documented"


def test_fast_first_render_alternative_is_seeded_and_small():
    _, argv = _fast_block(_command_blocks(_render_section()))
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


@pytest.mark.slow
def test_fast_first_render_produces_nondegenerate_png_under_60s(tmp_path):
    _, argv = _fast_block(_command_blocks(_render_section()))
    # Run the README line exactly as written, through the same entry point a
    # plain source checkout can execute (`python -m`). --filename goes into
    # the test's tmp dir.
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
    # Nondegenerate: the unseeded all-white failure mode rendered
    # exactly one distinct pixel value; a real synth/curl render varies.
    assert distinct > 8, f"fast first render is degenerate: {distinct} distinct pixel values"
