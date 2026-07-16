#!/usr/bin/env python
"""Cross-language parity harness: render every bundled effect in Python vs the JS
oracle (noisemaker-cpu `effect` CLI) at cpu's parity settings, and categorize.

Usage: .venv/bin/python scripts/parity.py [--size N] [--only id,id]
"""

from __future__ import annotations

import os
import subprocess
import sys

import numpy as np

from noisemaker_cpu.png import decode_png
from noisemaker_cpu.renderer import _meta, render_effect

CPU_DIR = os.environ.get("NOISEMAKER_CPU_DIR") or os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "noisemaker-cpu")
)
CLI = os.path.join(CPU_DIR, "bin", "noisemaker-cpu.js")

SIZE = 8
SEED = 1
TIME = 0.25


EXT_PNG = "/tmp/ph_ext.png"
_EXT_TEX = None


def _ext_texture():
    """Deterministic non-uniform 8-bit texture for external-texture effects
    (text/media). Written to a PNG so both engines read the identical input;
    a solid would hide any texture-orientation/sampling divergence."""
    global _EXT_TEX
    if _EXT_TEX is None:
        from noisemaker_cpu.png import encode_png
        from noisemaker_cpu.surface import Surface

        d = np.zeros(SIZE * SIZE * 4, dtype=np.float32)
        for y in range(SIZE):
            for x in range(SIZE):
                i = (y * SIZE + x) * 4
                d[i] = x / (SIZE - 1)
                d[i + 1] = y / (SIZE - 1)
                d[i + 2] = ((x + y) % SIZE) / (SIZE - 1)
                d[i + 3] = 1.0
        with open(EXT_PNG, "wb") as f:
            f.write(encode_png(Surface(SIZE, SIZE, d)))
        with open(EXT_PNG, "rb") as f:
            _EXT_TEX = decode_png(f.read())
    return _EXT_TEX


def js_effect(effect_id: str, out: str, input_png: str | None = None):
    cmd = [
        "node",
        CLI,
        "effect",
        effect_id,
        "--width",
        str(SIZE),
        "--height",
        str(SIZE),
        "--seed",
        str(SEED),
        "--time",
        str(TIME),
        "--output",
        out,
    ]
    if input_png:
        cmd += ["--input", input_png]
    subprocess.run(cmd, cwd=CPU_DIR, check=True, capture_output=True, timeout=120)
    with open(out, "rb") as f:
        return decode_png(f.read())


def _solid(color=None):
    return render_effect(
        "synth/solid", {} if color is None else {"color": color}, width=SIZE, height=SIZE, seed=SEED, time=TIME
    )


def py_render(effect_id: str, kind: str, ext: str | None = None):
    if kind == "generator":
        inputs = {ext: _ext_texture()} if ext else {}
        return render_effect(effect_id, {}, inputs, width=SIZE, height=SIZE, seed=SEED, time=TIME)
    # Replicate the JS `effect` CLI: primary input is a default solid; each
    # surface param (mixers) gets solid(#f30 / #0cf), alternating by index.
    inputs = {"inputTex": _solid()}
    if ext:
        inputs[ext] = _ext_texture()
    surf = [
        pn
        for pn, sp in _meta()["effects"][effect_id]["params"].items()
        if isinstance(sp, dict) and sp.get("type") == "surface"
    ]
    for i, pname in enumerate(surf):
        src = _solid("#0cf" if i % 2 else "#f30")
        spec = _meta()["effects"][effect_id]["params"][pname]
        for name in {spec.get("uniform"), spec.get("texture"), pname}:
            if name:
                inputs[name] = src
    return render_effect(effect_id, {}, inputs, width=SIZE, height=SIZE, seed=SEED, time=TIME)


def main():
    only = None
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    effects = _meta()["effects"]
    ids = [i for i in effects if not only or i in only]

    ok, diffs, errors, oracle_err = [], [], {}, []
    for eid in ids:
        kind = effects[eid]["kind"]
        ext = effects[eid].get("externalTexture")
        input_png = _ext_texture() and EXT_PNG if ext else None
        try:
            js = js_effect(eid, "/tmp/ph_js.png", input_png)
        except Exception:
            oracle_err.append(eid)
            continue
        try:
            py = py_render(eid, kind, ext)
        except Exception as e:
            key = f"{type(e).__name__}: {e}".splitlines()[0][:70]
            errors.setdefault(key, []).append(eid)
            continue
        ja = np.frombuffer(js.to_rgba8(), np.uint8).astype(int)
        pa = np.frombuffer(py.to_rgba8(), np.uint8).astype(int)
        if ja.shape != pa.shape:
            errors.setdefault("shape-mismatch", []).append(eid)
            continue
        d = int(np.max(np.abs(ja - pa)))
        (ok if d <= 2 else diffs).append(eid if d <= 2 else (eid, d))

    print(
        f"\n=== PARITY: {len(ok)}/{len(ids)} pass (<=2)  |  {len(diffs)} diff  |  "
        f"{sum(len(v) for v in errors.values())} runtime-error  |  {len(oracle_err)} oracle-error ===\n"
    )
    if errors:
        print("RUNTIME ERRORS (grouped — these drive runtime-stdlib work):")
        for msg, lst in sorted(errors.items(), key=lambda kv: -len(kv[1])):
            print(f"  {len(lst):3}  {msg}   e.g. {lst[0]}")
    if diffs:
        print("\nDIFFS (rendered but off):")
        for eid, d in sorted(diffs, key=lambda x: -x[1])[:20]:
            print(f"  {d:4}  {eid}")
    if oracle_err:
        print(f"\nORACLE ERRORS (JS effect CLI failed): {len(oracle_err)}  e.g. {oracle_err[:5]}")
    print(f"\nPASS: {len(ok)}")


if __name__ == "__main__":
    main()
