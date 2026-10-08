"""Release-gate tests: the Python mirror of noisemaker-for-cpu's
test/parity-release-gate.test.js. They run the gate over synthetic
parity-summary outputs shaped like the real one — a MISSING case, an
undeclared skip, an unreported case, or counts that disagree with the verdict
lines must fail the gate, and the real-shaped summary must pass — without
rendering anything or needing the oracle."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
GATE = ROOT / "scripts" / "parity" / "release_gate.py"

_spec = importlib.util.spec_from_file_location("release_gate", GATE)
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)

AUTHORITY = gate._authority_ids()
EMPTY_POLICY = {"declared_skips": [], "accepted_failures": []}


def summary_output(*, verdicts=None, counts=None, drop=(), extra=()) -> str:
    """A summary output shaped like the real run: every authority case graded
    EXACT unless overridden, the port's byte-exact counting contract."""
    verdicts = dict(verdicts or {})
    lines = ["parity-summary provenance: portHead=synthetic portTree=synthetic cpuHead=synthetic"]
    tally = {"expected": 0, "executed": 0, "exact": 0, "strict": 0, "near": 0, "defer": 0, "skip": 0, "fail": 0, "missing": 0}
    for case_id in AUTHORITY:
        if case_id in drop:
            continue
        verdict = verdicts.pop(case_id, "EXACT")
        tally["expected"] += 1
        if verdict in ("EXACT", "STRICT"):
            tally["exact" if verdict == "EXACT" else "strict"] += 1
            tally["executed"] += 1
        elif verdict in ("FAIL", "SKIP", "MISSING", "NEAR", "DEFER"):
            tally[verdict.lower()] += 1
        lines.append(f"FAIL {case_id} (max-diff 80)" if verdict == "FAIL" else f"{verdict} {case_id} (synthetic)")
    lines.extend(extra)
    tally.update(counts or {})
    lines.append("PARITY-SUMMARY " + json.dumps(tally))
    return "\n".join(lines) + "\n"


def test_the_real_shaped_summary_passes():
    result = gate.evaluate_release_gate(summary_output(), **EMPTY_POLICY)
    assert result["errors"] == []
    assert result["ok"] is True
    assert result["counts"] == {"reported": len(AUTHORITY), "missing": 0, "skip": 0, "fail": 0}


def test_a_missing_case_fails_the_gate_even_when_its_counts_are_consistent():
    result = gate.evaluate_release_gate(summary_output(verdicts={"synth/roll": "MISSING"}), **EMPTY_POLICY)
    assert result["ok"] is False
    assert any(error.startswith("MISSING synth/roll") for error in result["errors"]), result["errors"]
    assert "PARITY-SUMMARY missing=1, expected 0" in result["errors"], result["errors"]


def test_an_undeclared_skip_fails_the_gate():
    result = gate.evaluate_release_gate(summary_output(verdicts={"filter/adjust": "SKIP"}), **EMPTY_POLICY)
    assert result["ok"] is False
    assert "SKIP filter/adjust is not in the declared skip set" in result["errors"], result["errors"]


def test_a_declared_skip_that_is_graded_fails_until_the_declaration_drops_it():
    result = gate.evaluate_release_gate(
        summary_output(verdicts={"filter/adjust": "EXACT"}),
        declared_skips=["filter/adjust"],
        accepted_failures=[],
    )
    assert result["ok"] is False
    assert any(
        error == "declared skip filter/adjust was reported EXACT; remove it from the declared skip set"
        for error in result["errors"]
    ), result["errors"]


def test_a_failure_other_than_the_accepted_one_fails_the_gate():
    result = gate.evaluate_release_gate(summary_output(verdicts={"synth/roll": "FAIL"}), **EMPTY_POLICY)
    assert result["ok"] is False
    assert "FAIL synth/roll is not an accepted failure" in result["errors"], result["errors"]


def test_an_accepted_failure_that_is_graded_fails_until_the_declaration_drops_it():
    result = gate.evaluate_release_gate(
        summary_output(verdicts={"synth/roll": "EXACT"}),
        declared_skips=[],
        accepted_failures=["synth/roll"],
    )
    assert result["ok"] is False
    assert any(
        error == "accepted failure synth/roll was reported EXACT; remove it from the accepted failures"
        for error in result["errors"]
    ), result["errors"]


def test_near_and_deferred_cases_fail_the_gate():
    result = gate.evaluate_release_gate(summary_output(counts={"near": 1, "defer": 1}), **EMPTY_POLICY)
    assert result["ok"] is False
    assert "PARITY-SUMMARY near=1, expected 0" in result["errors"]
    assert "PARITY-SUMMARY defer=1, expected 0" in result["errors"]


def test_an_unreported_authority_case_fails_the_gate():
    result = gate.evaluate_release_gate(summary_output(drop={"filter/adjust"}), **EMPTY_POLICY)
    assert result["ok"] is False
    assert any(
        error == "1 authority cases are not reported: filter/adjust" for error in result["errors"]
    ), result["errors"]


def test_a_duplicate_or_unknown_case_id_fails_the_gate():
    result = gate.evaluate_release_gate(
        summary_output(extra=["EXACT filter/adjust (again)", "EXACT filter/bogus (x)"]),
        **EMPTY_POLICY,
    )
    assert result["ok"] is False
    assert "filter/adjust is reported more than once" in result["errors"]
    assert "filter/bogus is reported but is not an authority-manifest case" in result["errors"]


def test_a_missing_or_repeated_parity_summary_line_fails_the_gate():
    without_summary = summary_output().replace("PARITY-SUMMARY ", "PARITY-SUMMARY-REMOVED ", 1)
    without_summary = "\n".join(line for line in without_summary.splitlines() if not line.startswith("PARITY-SUMMARY "))
    assert "expected one PARITY-SUMMARY line, found 0" in gate.evaluate_release_gate(without_summary, **EMPTY_POLICY)["errors"]
    output = summary_output()
    repeated = output + output.splitlines()[-1] + "\n"
    assert "expected one PARITY-SUMMARY line, found 2" in gate.evaluate_release_gate(repeated, **EMPTY_POLICY)["errors"]


def test_summary_counts_that_disagree_with_the_case_lines_fail_the_gate():
    result = gate.evaluate_release_gate(summary_output(counts={"expected": 209}), **EMPTY_POLICY)
    assert result["ok"] is False
    assert f"PARITY-SUMMARY expected=209, expected {len(AUTHORITY)}" in result["errors"]
    assert "PARITY-SUMMARY expected does not equal executed + fail + missing" in result["errors"]


def test_the_gate_requires_explicit_declarations():
    with pytest.raises(TypeError, match="explicit declared_skips and accepted_failures"):
        gate.evaluate_release_gate(summary_output(), declared_skips=[])
    with pytest.raises(TypeError, match="explicit declared_skips and accepted_failures"):
        gate.evaluate_release_gate(summary_output(), accepted_failures=[])


def test_declared_cases_must_be_authority_manifest_cases():
    result = gate.evaluate_release_gate(
        summary_output(), declared_skips=["filter/bogus"], accepted_failures=[]
    )
    assert "declared case filter/bogus is not an authority-manifest case" in result["errors"]


def test_parse_args_requires_both_declarations():
    with pytest.raises(TypeError, match="--declared-skips is required"):
        gate.parse_args(["log.txt", "--accepted-failures", ""])
    with pytest.raises(TypeError, match="--accepted-failures is required"):
        gate.parse_args(["log.txt", "--declared-skips", ""])
    assert gate.parse_args(["log.txt", "--declared-skips", "", "--accepted-failures", "filter/crt"]) == {
        "log": "log.txt",
        "declared_skips": [],
        "accepted_failures": ["filter/crt"],
    }
    with pytest.raises(TypeError, match="Unknown release-gate option"):
        gate.parse_args(["log.txt", "--bogus"])
    with pytest.raises(TypeError, match="usage:"):
        gate.parse_args([])


def _run_gate(log_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(GATE), str(log_path), "--declared-skips", "", "--accepted-failures", ""],
        capture_output=True,
        text=True,
    )


def test_the_cli_passes_the_real_shaped_summary(tmp_path):
    log = tmp_path / "parity-summary.log"
    log.write_text(summary_output(), encoding="utf-8")
    result = _run_gate(log)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "release gate: PASS" in result.stdout


def test_the_cli_fails_a_summary_with_a_missing_case(tmp_path):
    log = tmp_path / "parity-summary.log"
    log.write_text(summary_output(verdicts={"synth/roll": "MISSING"}), encoding="utf-8")
    result = _run_gate(log)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "release gate: FAIL" in result.stdout


def test_the_cli_usage_errors_exit_2(tmp_path):
    result = subprocess.run([sys.executable, str(GATE)], capture_output=True, text=True)
    assert result.returncode == 2
    result = subprocess.run(
        [sys.executable, str(GATE), str(tmp_path / "missing.log"), "--declared-skips", "", "--accepted-failures", ""],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
