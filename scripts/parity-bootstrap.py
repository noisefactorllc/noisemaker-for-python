"""Bare-container runtime bootstrap for the parity entrypoints.

The check container has python3 and network but no prepared environment: the
system interpreter may lack numpy and the port package, so the gates would
crash on import before they can render anything. ensure_runtime detects that
case, builds or reuses the scripts/test venv (same layout and path scripts/test
uses), installs this checkout into it, and re-execs the entrypoint through the
venv's interpreter. When the runtime already imports, it is a no-op.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import urllib.request


def _default_venv():
    return os.path.join(os.environ.get("TMPDIR") or tempfile.gettempdir(), "noisemaker-py-test-venv")


def _run(cmd):
    run = subprocess.run(cmd, capture_output=True, text=True)
    if run.returncode != 0:
        detail = (run.stderr or run.stdout or "").strip()[-400:]
        raise SystemExit(f"parity runtime bootstrap failed ({' '.join(cmd[:2])}): {detail}")


def ensure_venv(root, venv_dir):
    """Create or reuse a venv with this checkout installed. Returns the venv's
    python path."""
    if os.name == "nt":
        python = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        python = os.path.join(venv_dir, "bin", "python")
    if not os.path.exists(python):
        _run([sys.executable, "-m", "venv", "--without-pip", venv_dir])
        get_pip = os.path.join(venv_dir, "get-pip.py")
        try:
            urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", get_pip)
        except OSError as fail:
            raise SystemExit(f"parity runtime bootstrap could not fetch get-pip: {fail}") from fail
        _run([python, get_pip])
        os.remove(get_pip)
    _run([python, "-m", "pip", "install", "-q", "-e", f"{root}[dev]"])
    return python


def ensure_runtime(root, venv_dir=None):
    """Re-exec through a prepared venv when this interpreter cannot import the
    port's runtime (numpy and noisemaker_cpu). A no-op otherwise."""
    try:
        import numpy  # noqa: F401
        import pytest  # noqa: F401

        import noisemaker_cpu  # noqa: F401
        return
    except Exception as fail:
        if os.environ.get("NOISEMAKER_PARITY_BOOTSTRAP"):
            raise SystemExit(f"parity runtime unavailable after bootstrap: {fail}") from fail
    python = ensure_venv(root, venv_dir or _default_venv())
    script = os.path.abspath(sys.argv[0])
    args = [python, script, *sys.argv[1:]]
    env = dict(os.environ, NOISEMAKER_PARITY_BOOTSTRAP="1")
    if os.name == "nt":
        raise SystemExit(subprocess.run(args, env=env).returncode)
    os.execve(python, args, env)
