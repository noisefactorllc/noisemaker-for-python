"""The scripts/test changed-files selector and its dotless-basename branch.

The selector in scripts/test runs only the tests that exercise the paths the
supervisor passes in NM_CHANGED_FILES. Its basename matching must not turn an
extensionless basename such as `test` (the path scripts/test itself) into a
token that matches every test file.
"""

from __future__ import annotations

import io
import os
import re
import sys
import textwrap
from pathlib import Path

REPO = Path(__file__).parents[1]


def _selector_code() -> str:
    text = (REPO / "scripts" / "test").read_text(encoding="utf-8")
    match = re.search(r"<<-'PY'\n(.*?)\n\s*PY", text, re.S)
    assert match, "scripts/test must embed the selector heredoc"
    return textwrap.dedent(match.group(1))


def _run_selection(changed: str, repo_root: Path, monkeypatch) -> list[str]:
    code = _selector_code()
    out = io.StringIO()
    argv = sys.argv
    stdout = sys.stdout
    sys.argv = ["select_tests", changed]
    sys.stdout = out
    monkeypatch.chdir(repo_root)
    try:
        exec(code, {"pathlib": Path, "sys": sys})
    finally:
        sys.stdout = stdout
        sys.argv = argv
    return [os.path.normpath(entry) for entry in out.getvalue().strip().split(" ") if entry]


def test_dotless_basename_does_not_match_test_files(tmp_path, monkeypatch):
    tests = tmp_path / "tests"
    tests.mkdir()
    # The file text contains the bare word "test"; the old basename matching
    # selected every such file for the dotless changed path scripts/test.
    (tests / "test_word.py").write_text("this file names the word test\n")
    (tests / "test_other.py").write_text("no matching tokens here\n")

    selected = _run_selection("scripts/test", tmp_path, monkeypatch)
    assert selected == [], selected


def test_dotted_paths_still_select_their_covering_tests(tmp_path, monkeypatch):
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_kernel.py").write_text("covers kernel/render.py behavior\n")
    (tests / "test_unrelated.py").write_text("unrelated\n")

    selected = _run_selection("kernel/render.py", tmp_path, monkeypatch)
    assert selected == [os.path.normpath("tests/test_kernel.py")], selected

    # A changed test file runs itself directly; its stem does not over-select
    # other test files that merely mention it.
    selected = _run_selection("tests/test_unrelated.py", tmp_path, monkeypatch)
    assert selected == [os.path.normpath("tests/test_unrelated.py")], selected
