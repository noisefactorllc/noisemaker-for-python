#!/usr/bin/env python
"""Cross-language parity harness: render every bundled effect in Python vs the JS
oracle (noisemaker-cpu `effect` CLI) at cpu's parity settings, and categorize.

Usage: .venv/bin/python scripts/parity.py [--size N] [--only id,id]
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np

from noisemaker_cpu.png import decode_png, encode_png
from noisemaker_cpu.renderer import _meta, render_dsl, render_effect

CPU_DIR = os.environ.get("NOISEMAKER_CPU_DIR") or os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "noisemaker-for-cpu")
)
CLI = os.path.join(CPU_DIR, "bin", "noisemaker-cpu.js")

_PINNED_ORACLE_URL = "https://github.com/noisefactorllc/noisemaker-for-cpu.git"


def _pinned_oracle_pin():
    """The pinned noisemaker-for-cpu revision and tree the gates compare
    against, read from scripts/test (CI's oracle setup reads the same
    constants)."""
    rev = tree = None
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test")
    with open(path, encoding="utf-8") as stream:
        for line in stream:
            if line.startswith("CPU_PINNED_REVISION="):
                rev = line.split("=", 1)[1].strip()
            elif line.startswith("CPU_PINNED_TREE="):
                tree = line.split("=", 1)[1].strip()
    return rev, tree


def _git_head_and_tree(cpu_dir):
    if not os.path.isdir(cpu_dir):
        return None, None
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=cpu_dir, capture_output=True, text=True)
    tree = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=cpu_dir, capture_output=True, text=True)
    return head.stdout.strip(), tree.stdout.strip()


def ensure_oracle(url=_PINNED_ORACLE_URL):
    """Resolve the pinned parity oracle for the entrypoints.

    NOISEMAKER_CPU_DIR (CI) wins unchanged. Otherwise the default sibling
    checkout is used only when it sits exactly at the pin recorded in
    scripts/test; every other case provisions a shallow clone of the pinned
    oracle into the oracle cache and verifies its revision and tree. A bare
    audit container (node, python3, network, no oracle mount) then compares
    against the pinned authority instead of failing per case or comparing
    against an unpinned checkout.
    """
    global CPU_DIR, CLI
    if os.environ.get("NOISEMAKER_CPU_DIR"):
        return
    rev, tree = _pinned_oracle_pin()
    if not (rev and tree):
        return  # no pin recorded: keep the default resolution, failures stay visible
    if os.path.isdir(CPU_DIR) and _git_head_and_tree(CPU_DIR) == (rev, tree):
        return
    cache_root = os.environ.get("NOISEMAKER_ORACLE_CACHE") or os.path.expanduser(
        os.path.join("~", ".cache", "noisemaker")
    )
    target = os.path.join(cache_root, "cpu-oracle-py", rev)
    if _git_head_and_tree(target) != (rev, tree):
        shutil.rmtree(target, ignore_errors=True)
        os.makedirs(target, exist_ok=True)
        for cmd in (
            ["git", "init", "-q", target],
            ["git", "-C", target, "remote", "add", "origin", url],
            ["git", "-C", target, "fetch", "-q", "--depth", "1", url, rev],
            ["git", "-C", target, "checkout", "-q", "--detach", "FETCH_HEAD"],
        ):
            run = subprocess.run(cmd, capture_output=True, text=True)
            if run.returncode != 0:
                raise RuntimeError(f"pinned oracle checkout failed ({' '.join(cmd[:2])}): {run.stderr.strip()[:200]}")
        got_head, got_tree = _git_head_and_tree(target)
        if (got_head, got_tree) != (rev, tree):
            raise RuntimeError(
                f"pinned oracle mismatch at {rev}: head {got_head or 'unknown'} tree {got_tree or 'unknown'}"
            )
    CPU_DIR = target
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


_SCRATCH = tempfile.TemporaryDirectory(prefix="noisemaker-python-parity-")
EXT_PNG = os.path.join(_SCRATCH.name, "external.png")
JS_PNG = os.path.join(_SCRATCH.name, "oracle.png")
_EXT_TEX = None

# Deterministic external-input fixtures for the reactive (MIDI/audio) and mesh
# (OBJ) parity cases — the Python mirror of the oracle's
# scripts/parity/reactive-fixtures.js. Keep the fixture constants byte-identical
# across both sides: the oracle driver (scripts/parity-js-driver.mjs) feeds the
# oracle checkout's own fixtures module, and this side constructs the equivalent
# state through noisemaker_cpu.external_input.

# MIDI: channel 1 C-major triad (60/64/67, velocities 100/80/90), channel 2 low C
# (48, velocity 64), then 24 clock pulses — one beat at 24 PPQ.
MIDI_MESSAGES = [
    [0x90, 60, 100], [0x90, 64, 80], [0x90, 67, 90],
    [0x91, 48, 64],
] + [[0xF8]] * 24

# Mesh: a 12-triangle cube (8 vertices, 6 quad faces with per-face normals).
CUBE_OBJ = "\n".join(
    [
        "v -0.7 -0.7 -0.7", "v 0.7 -0.7 -0.7", "v 0.7 0.7 -0.7", "v -0.7 0.7 -0.7",
        "v -0.7 -0.7 0.7", "v 0.7 -0.7 0.7", "v 0.7 0.7 0.7", "v -0.7 0.7 0.7",
        "vn 0 0 -1", "vn 0 0 1", "vn 0 -1 0", "vn 0 1 0", "vn -1 0 0", "vn 1 0 0",
        "f 1//1 2//1 3//1 4//1", "f 5//2 8//2 7//2 6//2", "f 1//3 5//3 6//3 2//3",
        "f 2//4 6//4 7//4 3//4", "f 3//5 7//5 8//5 4//5", "f 4//6 8//6 5//6 1//6",
        "",
    ]
)

MESH_TEX_WIDTH = 256
MESH_TEX_HEIGHT = 256

_MIDI_FIXTURE = None
_AUDIO_FIXTURE = None
_MESH_FIXTURE = None


def midi_fixture():
    global _MIDI_FIXTURE
    if _MIDI_FIXTURE is None:
        from noisemaker_cpu.external_input import MidiState

        midi_state = MidiState()
        for message in MIDI_MESSAGES:
            midi_state.handle_message(message)
        midi_state.update_note_grid()
        _MIDI_FIXTURE = midi_state
    return _MIDI_FIXTURE


def audio_fixture():
    global _AUDIO_FIXTURE
    if _AUDIO_FIXTURE is None:
        import math

        from noisemaker_cpu.external_input import AudioState

        audio_state = AudioState()
        waveform = [0.5 + 0.5 * math.sin((2 * math.pi * 3 * i) / 128) for i in range(128)]
        spectrum = [(1 - i / 127) ** 2 for i in range(128)]
        audio_state.set_waveform(waveform)
        audio_state.set_spectrum(spectrum)
        _AUDIO_FIXTURE = audio_state
    return _AUDIO_FIXTURE


def mesh_fixture():
    global _MESH_FIXTURE
    if _MESH_FIXTURE is None:
        from noisemaker_cpu.external_input import pack_mesh_data_for_textures, parse_obj

        parsed = parse_obj(CUBE_OBJ)
        packed = pack_mesh_data_for_textures(parsed["positions"], parsed["normals"], parsed["uvs"], MESH_TEX_WIDTH, MESH_TEX_HEIGHT)
        packed["texWidth"] = MESH_TEX_WIDTH
        packed["texHeight"] = MESH_TEX_HEIGHT
        _MESH_FIXTURE = packed
    return _MESH_FIXTURE


EXTERNAL_INPUT_EFFECT_IDS = ("synth/roll", "synth/scope", "synth/spectrum", "render/meshLoader", "render/meshRender")


def external_inputs_for_case(case_id: str):
    external_inputs = {}
    if case_id == "synth/roll":
        external_inputs["midiState"] = midi_fixture()
    if case_id in ("synth/scope", "synth/spectrum"):
        external_inputs["audioState"] = audio_fixture()
    if case_id in ("render/meshLoader", "render/meshRender"):
        external_inputs["meshData"] = mesh_fixture()
    return external_inputs or None


def _external_case_dsl(case_id: str) -> str:
    """The oracle's parity DSL for one external-input case (the same programs its
    own gate renders, parity/upstream-defaults/<name>.dsl). When the mounted
    oracle predates the reactive/mesh import (the CI tarball carries only
    src/bin/scripts/upstream), the byte-identical committed copy in
    tests/data/reactive-mesh-oracle/ is used — the programs are part of the
    synced sibling contract."""
    name = case_id.replace("/", "__")
    path = os.path.join(CPU_DIR, "parity", "upstream-defaults", f"{name}.dsl")
    if not os.path.exists(path):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tests", "data", "reactive-mesh-oracle", f"{name}.dsl")
    with open(path, encoding="utf-8") as f:
        return f.read()


def js_effect_external(case_id: str, out: str, width: int = SIZE, seed: int = SEED, time: float = TIME):
    """Render one external-input case with the oracle through
    scripts/parity-js-driver.mjs (the CLI binds no fixture)."""
    dsl_path = os.path.join(_SCRATCH.name, f"{case_id.replace('/', '__')}.dsl")
    with open(dsl_path, "w", encoding="utf-8") as f:
        f.write(_external_case_dsl(case_id))
    driver = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parity-js-driver.mjs")
    cmd = [
        "node",
        driver,
        case_id,
        dsl_path,
        out,
        "--width",
        str(width),
        "--height",
        str(width),
        "--seed",
        str(seed),
        "--time",
        str(time),
    ]
    subprocess.run(cmd, cwd=CPU_DIR, check=True, capture_output=True, timeout=120)
    with open(out, "rb") as f:
        return decode_png(f.read())


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
    # The reactive/mesh external-input cases need an oracle that carries the
    # sibling's reactive/mesh import (its reactive-fixtures.js + parity DSL).
    # An oracle that predates the import (the CI tarball b61b658399f1) cannot
    # render them at all; like the iterated effects it cannot serve, they count
    # as skipped here — they are covered by the committed-reference pytest cases
    # and by scripts/parity-summary at a current authority.
    oracle_supports_external = os.path.exists(os.path.join(CPU_DIR, "scripts", "parity", "reactive-fixtures.js"))

    # Phase 1 — oracle renders, batched. Each CLI spawn pays interpreter +
    # module load, so render every case through one node process
    # (scripts/parity-js-batch.mjs): it reuses the CLI's own effect→DSL
    # helpers imported from the pinned checkout. Per-job failures come back as
    # "<out>.err" markers and map to oracle errors exactly like a failed spawn.
    # A batch that cannot run at all (no node) falls back to per-effect spawns.
    batch_jobs = []
    _ext_texture()
    for eid in ids:
        if eid in EXTERNAL_INPUT_EFFECT_IDS:
            if not oracle_supports_external:
                continue
            batch_jobs.append(
                {
                    "id": eid,
                    "out": os.path.join(_SCRATCH.name, f"oracle-{eid.replace('/', '__')}.png"),
                    "program": _external_case_dsl(eid),
                    "externalInputs": True,
                }
            )
            continue
        ext = effects[eid].get("externalTexture")
        job = {"id": eid, "out": os.path.join(_SCRATCH.name, f"oracle-{eid.replace('/', '__')}.png")}
        if ext:
            job["input"] = EXT_PNG
        batch_jobs.append(job)
    jobs_path = os.path.join(_SCRATCH.name, "jobs.json")
    import json

    with open(jobs_path, "w", encoding="utf-8") as f:
        json.dump(batch_jobs, f)
    batch_env = dict(os.environ)
    batch_env["NOISEMAKER_CPU_DIR"] = CPU_DIR
    driver = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parity-js-batch.mjs")
    oracle_failed = set()
    oracle_results = {}
    try:
        subprocess.run(
            ["node", driver, jobs_path],
            cwd=CPU_DIR,
            check=True,
            capture_output=True,
            timeout=120 * max(1, len(batch_jobs)),
            env=batch_env,
        )
    except Exception:
        # Batch unavailable: fall back to the per-effect CLI spawns.
        for eid in ids:
            try:
                ext = effects[eid].get("externalTexture")
                input_png = _ext_texture() and EXT_PNG if ext else None
                out = os.path.join(_SCRATCH.name, f"oracle-{eid.replace('/', '__')}.png")
                if eid in EXTERNAL_INPUT_EFFECT_IDS:
                    js = js_effect_external(eid, out)
                else:
                    js = js_effect(eid, out, input_png)
                with open(out, "rb") as f:
                    oracle_results[eid] = (js, _sha256_file(out))
            except Exception:
                oracle_failed.add(eid)
    else:
        for job in batch_jobs:
            eid = job["id"]
            err_path = job["out"] + ".err"
            if os.path.exists(err_path):
                oracle_failed.add(eid)
                continue
            with open(job["out"], "rb") as f:
                oracle_results[eid] = (decode_png(f.read()), _sha256_file(job["out"]))
    if not oracle_supports_external:
        oracle_failed.update(eid for eid in EXTERNAL_INPUT_EFFECT_IDS if eid in ids)

    # Phase 2 — port renders and comparison, sequential and in candidate order.
    for eid in ids:
        kind = effects[eid]["kind"]
        ext = effects[eid].get("externalTexture")
        if eid in EXTERNAL_INPUT_EFFECT_IDS:
            if not oracle_supports_external:
                skipped.append(eid)
                continue
            if eid in oracle_failed:
                oracle_err.append(eid)
                continue
            js, js_png_sha = oracle_results[eid]
            try:
                py = render_dsl(
                    _external_case_dsl(eid),
                    width=SIZE,
                    height=SIZE,
                    seed=SEED,
                    time=TIME,
                    external_inputs=external_inputs_for_case(eid),
                )
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
            continue
        if eid in oracle_failed:
            oracle_err.append(eid)
            continue
        js, js_png_sha = oracle_results[eid]
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
