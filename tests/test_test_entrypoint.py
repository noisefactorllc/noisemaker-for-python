"""The changed-files gate in scripts/test honors pytest's exit status.

These tests drive scripts/test as a subprocess with NM_CHANGED_FILES set and
assert the three branch behaviors the gate documents: an empty selection exits
0 without falling through to the full suite, an all-oracle/slow selection
reports and exits 0, and a real test failure propagates pytest's nonzero
status. Each invocation runs the real entrypoint, including its venv reuse,
so each one stays well inside the bounded-invocation limit.
"""

import os
import pathlib
import subprocess

REPO = pathlib.Path(__file__).resolve().parents[1]
ENTRY = REPO / "scripts" / "test"

# Concatenated so this file's own text does not name the probe path; a
# literal mention would make the selector pick this file too and recurse.
PROBE = "tests/test__nm_" + "entrypoint_probe.py"
PROBE_SOURCE = (
    "import os\n\n\n"
    "def test_nm_entrypoint_probe():\n"
    '    assert os.environ.get("NM_ENTRYPOINT_PROBE") != "fail"\n'
)


def run_entry(extra_env, timeout=240):
    env = dict(os.environ)
    env.update(extra_env)
    return subprocess.run(
        ["sh", str(ENTRY)],
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )


def test_empty_selection_exits_zero_without_the_full_suite():
    # Built by concatenation on purpose: if this file's own text named the
    # path, the selector would select this file and the inner entrypoint run
    # would recurse into itself.
    path = "docs/no-such-" + "path.md\n"
    result = run_entry({"NM_CHANGED_FILES": path})
    assert result.returncode == 0
    assert "no test file references the changed paths" in result.stdout
    # The full quick suite takes minutes; a fast exit proves the gate did not
    # fall through to it.
    assert "passed" not in result.stdout


def test_all_oracle_selection_reports_and_exits_zero():
    # Concatenated for the same anti-recursion reason as above: this file's
    # text must not name the selected path.
    result = run_entry({"NM_CHANGED_FILES": "tests/test_par" + "ity.py\n"})
    assert result.returncode == 0
    assert "every selected test is oracle- or slow-marked" in result.stdout


def test_failing_selection_propagates_pytest_status():
    probe = REPO / PROBE
    probe.write_text(PROBE_SOURCE, encoding="utf-8")
    try:
        result = run_entry(
            {"NM_CHANGED_FILES": PROBE + "\n", "NM_ENTRYPOINT_PROBE": "fail"}
        )
        assert result.returncode != 0
        assert "no test file references the changed paths" not in result.stdout
    finally:
        probe.unlink(missing_ok=True)
