#!/usr/bin/env python
"""Release gate over a complete `scripts/parity-summary` output.

The Python mirror of noisemaker-for-cpu's scripts/parity/release-gate.js: the
kit release runs it after the summary and releases only when it exits 0.

The gate passes only when all of these are true:
  - the output carries exactly one PARITY-SUMMARY line;
  - every authority-manifest effect is reported exactly once, and no other
    id is;
  - no case is MISSING and the near and defer counts are zero;
  - the SKIP cases are exactly the declared skip set (an undeclared skip
    fails, and a declared skip that is graded fails until the declaration
    drops it);
  - the FAIL cases are exactly the accepted failures;
  - the PARITY-SUMMARY counts agree with the per-case verdict lines.

The port's published contract is byte-exact against the oracle at zero
tolerance: it declares no skips and no accepted failures, so the release
invocation passes empty declarations:

    python scripts/parity/release_gate.py <log> --declared-skips '' --accepted-failures ''

Exit code is 0 on a pass, 1 when the gate has findings, 2 on a usage error.
"""

from __future__ import annotations

import json
import re
import sys

VERDICT = re.compile(r"^(EXACT|STRICT|FAIL|SKIP|MISSING|NEAR|DEFER) (\S+)")
SUMMARY = re.compile(r"^PARITY-SUMMARY (.*)$")

USAGE = "usage: release_gate.py <parity-summary log> --declared-skips <ids> --accepted-failures <ids>"


def _authority_ids() -> list[str]:
    """The authority manifest: every bundled effect id, in catalog order."""
    from noisemaker_cpu.renderer import _meta

    return list(_meta()["effects"])


def parse_summary_output(text: str) -> dict:
    verdicts: dict[str, str] = {}
    duplicates: list[str] = []
    summaries: list[str] = []
    for line in text.splitlines():
        summary_match = SUMMARY.match(line)
        if summary_match:
            summaries.append(summary_match.group(1))
            continue
        match = VERDICT.match(line)
        if not match:
            continue
        verdict, case_id = match.group(1), match.group(2)
        if case_id in verdicts:
            duplicates.append(case_id)
        verdicts[case_id] = verdict
    return {"verdicts": verdicts, "duplicates": duplicates, "summaries": summaries}


def _sorted_ids(verdicts: dict, verdict: str) -> list[str]:
    return sorted(case_id for case_id, value in verdicts.items() if value == verdict)


def evaluate_release_gate(text: str, *, declared_skips=None, accepted_failures=None, authority: list | None = None) -> dict:
    if not isinstance(declared_skips, list) or not isinstance(accepted_failures, list):
        raise TypeError("evaluate_release_gate needs explicit declared_skips and accepted_failures lists")
    if authority is None:
        authority = _authority_ids()
    errors: list[str] = []
    parsed = parse_summary_output(text)
    verdicts = parsed["verdicts"]
    authority_set = set(authority)

    for case_id in list(declared_skips) + list(accepted_failures):
        if case_id not in authority_set:
            errors.append(f"declared case {case_id} is not an authority-manifest case")

    summary = None
    if len(parsed["summaries"]) != 1:
        errors.append(f"expected one PARITY-SUMMARY line, found {len(parsed['summaries'])}")
    else:
        try:
            summary = json.loads(parsed["summaries"][0])
        except ValueError as error:
            errors.append(f"PARITY-SUMMARY line is not JSON: {error}")
    if summary is not None and not isinstance(summary, dict):
        errors.append("PARITY-SUMMARY line is not a JSON object")
        summary = None

    for case_id in parsed["duplicates"]:
        errors.append(f"{case_id} is reported more than once")
    for case_id in verdicts:
        if case_id not in authority_set:
            errors.append(f"{case_id} is reported but is not an authority-manifest case")
    unreported = [case_id for case_id in authority if case_id not in verdicts]
    if unreported:
        errors.append(f"{len(unreported)} authority cases are not reported: {', '.join(unreported)}")

    missing = _sorted_ids(verdicts, "MISSING")
    skips = _sorted_ids(verdicts, "SKIP")
    fails = _sorted_ids(verdicts, "FAIL")
    near = _sorted_ids(verdicts, "NEAR")
    defer = _sorted_ids(verdicts, "DEFER")

    for case_id in missing:
        errors.append(f"MISSING {case_id}: a release needs zero missing cases")
    for case_id in near:
        errors.append(f"NEAR {case_id}: a release accepts no near cases")
    for case_id in defer:
        errors.append(f"DEFER {case_id}: a release accepts no deferred cases")

    declared_skip_set = set(declared_skips)
    for case_id in skips:
        if case_id not in declared_skip_set:
            errors.append(f"SKIP {case_id} is not in the declared skip set")
    for case_id in declared_skips:
        if case_id in verdicts and verdicts[case_id] != "SKIP":
            errors.append(f"declared skip {case_id} was reported {verdicts[case_id]}; remove it from the declared skip set")

    accepted_failure_set = set(accepted_failures)
    for case_id in fails:
        if case_id not in accepted_failure_set:
            errors.append(f"FAIL {case_id} is not an accepted failure")
    for case_id in accepted_failures:
        if case_id in verdicts and verdicts[case_id] != "FAIL":
            errors.append(f"accepted failure {case_id} was reported {verdicts[case_id]}; remove it from the accepted failures")

    if summary is not None:
        exact = _sorted_ids(verdicts, "EXACT")
        strict = _sorted_ids(verdicts, "STRICT")
        expected_counts = {
            "expected": len(authority),
            "executed": len(exact) + len(strict),
            "exact": len(exact),
            "strict": len(strict),
            "near": 0,
            "defer": 0,
            "skip": len(skips),
            "fail": len(fails),
            "missing": 0,
        }
        for key, value in expected_counts.items():
            if summary.get(key) != value:
                errors.append(f"PARITY-SUMMARY {key}={summary.get(key)}, expected {value}")
        if summary.get("expected") != summary.get("executed", 0) + summary.get("fail", 0) + summary.get("missing", 0):
            errors.append("PARITY-SUMMARY expected does not equal executed + fail + missing")

    return {
        "ok": not errors,
        "errors": errors,
        "counts": {
            "reported": len(verdicts),
            "missing": len(missing),
            "skip": len(skips),
            "fail": len(fails),
        },
    }


def parse_args(argv: list[str]) -> dict:
    log = None
    declared_skips = None
    accepted_failures = None
    index = 0
    while index < len(argv):
        argument = argv[index]
        if argument == "--declared-skips":
            index += 1
            if index >= len(argv):
                raise TypeError("--declared-skips needs a value (use '' for none)")
            declared_skips = [v for v in re.split(r"[\s,]+", argv[index]) if v]
        elif argument == "--accepted-failures":
            index += 1
            if index >= len(argv):
                raise TypeError("--accepted-failures needs a value (use '' for none)")
            accepted_failures = [v for v in re.split(r"[\s,]+", argv[index]) if v]
        elif argument.startswith("--"):
            raise TypeError(f"Unknown release-gate option {argument}")
        elif log is None:
            log = argument
        else:
            raise TypeError(f"Unexpected argument {argument}")
        index += 1
    if log is None:
        raise TypeError(USAGE)
    if declared_skips is None:
        raise TypeError("--declared-skips is required")
    if accepted_failures is None:
        raise TypeError("--accepted-failures is required")
    return {"log": log, "declared_skips": declared_skips, "accepted_failures": accepted_failures}


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
    except TypeError as error:
        print(error, file=sys.stderr)
        return 2
    try:
        with open(args["log"], encoding="utf-8") as f:
            text = f.read()
        result = evaluate_release_gate(
            text,
            declared_skips=args["declared_skips"],
            accepted_failures=args["accepted_failures"],
        )
    except (OSError, TypeError) as error:
        print(error, file=sys.stderr)
        return 2
    counts = result["counts"]
    print(
        f"release gate: {counts['reported']} cases reported, missing {counts['missing']}, "
        f"skip {counts['skip']} (declared {len(args['declared_skips'])}), "
        f"fail {counts['fail']} (accepted {len(args['accepted_failures'])})"
    )
    for error in result["errors"]:
        print(f"::error::{error}")
    print("release gate: PASS" if result["ok"] else f"release gate: FAIL ({len(result['errors'])} findings)")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
