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

from noisemaker_cpu.png import decode_png, encode_png
from noisemaker_cpu.renderer import _meta, render_effect

CPU_DIR = os.environ.get("NOISEMAKER_CPU_DIR") or os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "noisemaker-for-cpu")
)
CLI = os.path.join(CPU_DIR, "bin", "noisemaker-cpu.js")

SIZE = 8
SEED = 1
TIME = 0.25


def _sha256_file(path: str) -> str:
    import hashlib

    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _sha256_bytes(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()


def _cpu_revision() -> dict:
    """Binds a receipt to the exact -cpu revision it was generated against."""
    lock = {}
    lock_path = os.path.join(CPU_DIR, "scripts", "upstream", "source-lock.js")
    with open(lock_path, encoding="utf-8") as f:
        lock_text = f.read()
    for line in lock_text.splitlines():
        if line.startswith("export const PINNED_UPSTREAM_REVISION"):
            lock["revision"] = line.split("'")[1]
        elif line.startswith("export const PINNED_SOURCE_DIGEST"):
            lock["sourceDigest"] = line.split("'")[1]
    snapshot_path = os.path.join(CPU_DIR, "src", "effects", "generated", "upstream-snapshot.js")
    with open(snapshot_path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("export const UPSTREAM_REVISION"):
                lock["snapshotRevision"] = line.split('"')[1]
                break
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=CPU_DIR, capture_output=True, text=True)
    lock["cpuHead"] = head.stdout.strip() if head.returncode == 0 else None
    tree = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=CPU_DIR, capture_output=True, text=True)
    lock["cpuTree"] = tree.stdout.strip() if tree.returncode == 0 else None
    return lock


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
    json_out = None
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    if "--json" in sys.argv:
        json_out = sys.argv[sys.argv.index("--json") + 1]
    effects = _meta()["effects"]
    unknown = sorted(only - effects.keys()) if only is not None else []
    candidates = [i for i in effects if only is None or i in only]
    skipped = [i for i in candidates if effects[i].get("iterated") or effects[i].get("domain", "image") != "image"]
    ids = [i for i in candidates if i not in skipped]

    ok, diffs, errors, oracle_err = [], [], {}, []
    receipt = {}
    for eid in ids:
        kind = effects[eid]["kind"]
        ext = effects[eid].get("externalTexture")
        input_png = _ext_texture() and EXT_PNG if ext else None
        try:
            js = js_effect(eid, "/tmp/ph_js.png", input_png)
            js_png_sha = _sha256_file("/tmp/ph_js.png")
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
        py_png_sha = _sha256_bytes(encode_png(py))
        py_rgba8_sha = _sha256_bytes(py.to_rgba8())
        js_rgba8_sha = _sha256_bytes(js.to_rgba8())
        if d == 0:
            ok.append(eid)
            receipt[eid] = {
                "oraclePngSha256": js_png_sha,
                "oracleRgba8Sha256": js_rgba8_sha,
                "pythonPngSha256": py_png_sha,
                "pythonRgba8Sha256": py_rgba8_sha,
            }
        else:
            diffs.append((eid, d))

    print(
        f"\n=== PARITY: {len(ok)}/{len(ids)} pass (byte-exact)  |  {len(diffs)} diff  |  "
        f"{sum(len(v) for v in errors.values())} runtime-error  |  {len(oracle_err)} oracle-error  |  "
        f"{len(skipped)} skipped ===\n"
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
    if skipped:
        print(f"\nSKIPPED (iterated/typed-chain; covered by DSL parity tests): {len(skipped)}  e.g. {skipped[:5]}")
    print(f"\nPASS: {len(ok)}")
    if unknown:
        print(f"UNKNOWN EFFECTS: {unknown}")
    if json_out:
        import json

        doc = {
            "settings": {"size": SIZE, "seed": SEED, "time": TIME, "tolerance": 0},
            "cpu": _cpu_revision(),
            "counts": {
                "byteExact": len(ok),
                "diffs": len(diffs),
                "runtimeErrors": sum(len(v) for v in errors.values()),
                "oracleErrors": len(oracle_err),
                "skipped": len(skipped),
                "considered": len(ids),
            },
            "diffs": [{"id": i, "maxDiff": d} for i, d in diffs],
            "errors": {k: v for k, v in errors.items()},
            "oracleErrors": oracle_err,
            "skipped": skipped,
            "byteExact": receipt,
        }
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2, sort_keys=True)
            f.write("\n")
    return 1 if not ids or diffs or errors or oracle_err or unknown else 0


if __name__ == "__main__":
    sys.exit(main())
