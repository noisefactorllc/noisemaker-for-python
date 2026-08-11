"""Regenerate the vendored Python bundle from the CDN.

Pipeline: cdn.fetch_effect -> preprocess.normalize -> parser.parse ->
codegen.emit_python -> write src/noisemaker_cpu/bundle/. Pure Python.

  python -m transpiler.build [--all | --only a,b] [--update-lock]
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile

from .cdn import CDN_BASE, CDN_VERSION, eligible_ids, fetch_effect
from .codegen import emit_python
from .parser import parse
from .preprocess import normalize
from .shared_enums import SHARED_ENUMS


def _resolve_shared_enums(params: dict) -> None:
    """Inline choices for member params that reference a shared enum by name only
    (the CDN bundle omits the name->index table). Mutates params in place."""
    for spec in params.values():
        if isinstance(spec, dict) and spec.get("type") == "member" and not spec.get("choices"):
            choices = SHARED_ENUMS.get(spec.get("enum"))
            if choices:
                spec["choices"] = dict(choices)


_HERE = os.path.dirname(__file__)
BUNDLE = os.path.normpath(os.path.join(_HERE, "..", "src", "noisemaker_cpu", "bundle"))
# This canonical JS kernel materializes intermediate vec4 values in
# Float32Array storage before converting them to uvec4 hash lanes.
_JS_VECTOR_STORAGE_KEYS = frozenset({"synth3d/noise3d:precompute"})


def runtime_defines(params: dict) -> dict:
    out = {}
    for spec in params.values():
        if isinstance(spec, dict) and spec.get("define"):
            out[spec["define"]] = "float" if spec.get("type") == "float" else "int"
    return out


def infer_kind(namespace: str, passes: list[dict], textures: dict) -> str:
    if namespace in {"synth", "synth3d"}:
        return "generator"
    if namespace == "filter3d":
        return "filter"
    if namespace == "mixer":
        return "mixer"
    if namespace in {"points", "render"}:
        return "filter"
    has_inputs = False
    external = False
    for render_pass in passes:
        for value in (render_pass.get("inputs") or {}).values():
            has_inputs = True
            if not isinstance(value, str):
                continue
            if value in {"inputTex", "outputTex", "selfTex", "feedback"}:
                continue
            if value.startswith(("_", "global_")):
                continue
            texture = textures.get(value)
            if (
                texture
                and isinstance(texture.get("width"), (int, float))
                and isinstance(texture.get("height"), (int, float))
            ):
                continue
            external = True
    if not has_inputs:
        return "generator"
    return "mixer" if external else "filter"


def infer_domain(effect_id: str) -> str:
    namespace = effect_id.split("/", 1)[0]
    if effect_id == "render/loopBegin":
        return "loop-begin"
    if effect_id == "render/loopEnd":
        return "loop-end"
    if namespace == "synth3d":
        return "volume-generator"
    if namespace == "filter3d":
        return "volume-filter"
    if effect_id.startswith("render/render"):
        return "volume-renderer"
    return "image"


def _key(eid, program):
    return f"{eid}:{program}"


def _file(key):
    return key.replace("/", "__").replace(":", "__") + ".py"


_PASS_EXECUTION_KEYS = (
    "uniforms",
    "repeat",
    "blend",
    "clear",
    "drawMode",
    "count",
    "countUniform",
    "type",
    "entryPoint",
    "drawBuffers",
    "conditions",
    "viewport",
)


def _pass_metadata(render_pass: dict, key: str | None) -> dict:
    outputs = {
        ("fragColor" if render_pass.get("drawBuffers", 0) >= 2 and name == "color" else name): texture
        for name, texture in (render_pass.get("outputs") or {}).items()
    }
    metadata = {
        "name": render_pass["name"],
        "program": render_pass["program"],
        "key": key,
        "inputs": render_pass.get("inputs") or {},
        "outputs": outputs,
    }
    for field in _PASS_EXECUTION_KEYS:
        if field in render_pass:
            metadata[field] = render_pass[field]
    return metadata


def _validate_artifacts(bundle: dict, hashes: dict, kernel_dir: str) -> None:
    pass_keys = {
        render_pass["key"]
        for effect in bundle["effects"].values()
        for render_pass in effect["passes"]
        if render_pass["key"] is not None
    }
    kernel_files = set(os.listdir(kernel_dir))
    expected_files = {_file(key) for key in pass_keys}
    if set(hashes) != pass_keys or kernel_files != expected_files:
        raise RuntimeError(
            f"bundle artifact mismatch: metadata={len(pass_keys)}, hashes={len(hashes)}, kernels={len(kernel_files)}"
        )


def _publish_bundle(staged_dir: str, out_dir: str) -> None:
    parent = os.path.dirname(out_dir)
    backup_dir = None
    if os.path.lexists(out_dir):
        backup_dir = tempfile.mkdtemp(prefix=f".{os.path.basename(out_dir)}.backup-", dir=parent)
        os.rmdir(backup_dir)
        os.replace(out_dir, backup_dir)
    try:
        os.replace(staged_dir, out_dir)
    except BaseException:
        if backup_dir is not None:
            os.replace(backup_dir, out_dir)
        raise
    if backup_dir is not None:
        shutil.rmtree(backup_dir, ignore_errors=True)


def build(ids, out_dir=BUNDLE, update_lock=False):
    ids = list(ids)
    out_dir = os.path.abspath(os.fspath(out_dir))
    parent = os.path.dirname(out_dir)
    os.makedirs(parent, exist_ok=True)
    lock_path = os.path.join(out_dir, "bundle-lock.json")
    if os.path.exists(lock_path):
        with open(lock_path) as f:
            old = json.load(f)
    else:
        old = {"hashes": {}}
    staged_dir = tempfile.mkdtemp(prefix=f".{os.path.basename(out_dir)}.build-", dir=parent)
    kdir = os.path.join(staged_dir, "kernels", "python")
    os.makedirs(kdir)
    old_hashes = old.get("hashes", {})
    hashes = {}
    drift = []
    failures = []
    bundle = {
        "provenance": {"source": "shaders.noisedeck.app CDN", "version": CDN_VERSION, "base": CDN_BASE},
        "effects": {},
    }
    n_ok = 0
    try:
        for eid in ids:
            try:
                eff = fetch_effect(eid)
            except Exception as e:
                failures.append(f"{eid}: cdn: {type(e).__name__}: {str(e)[:80]}")
                continue
            _resolve_shared_enums(eff["params"])
            defines = runtime_defines(eff["params"])
            passes = []
            for p in eff["passes"]:
                glsl = eff["programs"].get(p["program"])
                if glsl is None:
                    # A pass without GLSL is a CPU-only draw op (e.g. wormhole's
                    # point-scatter deposit). Keep it so the renderer can run its
                    # native adapter; it has no transpiled kernel key.
                    if p.get("drawMode"):
                        passes.append(_pass_metadata(p, None))
                    else:
                        failures.append(f"{_key(eid, p['program'])}: missing GLSL program")
                    continue
                key = _key(eid, p["program"])
                h = hashlib.sha256(glsl.strip().encode("utf-8")).hexdigest()
                try:
                    norm = normalize(glsl, defines)
                    ast = parse(norm["source"])
                    py = emit_python(
                        ast,
                        norm.get("outputs"),
                        norm.get("varyings"),
                        js_vector_storage=key in _JS_VECTOR_STORAGE_KEYS,
                    )
                except Exception as e:
                    failures.append(f"{key}: {type(e).__name__}: {str(e)[:80]}")
                    continue
                with open(os.path.join(kdir, _file(key)), "w") as f:
                    f.write(py)
                if old_hashes.get(key) and old_hashes[key] != h:
                    drift.append(key)
                hashes[key] = h
                n_ok += 1
                passes.append(_pass_metadata(p, key))
            if not passes:
                if not any(message.startswith(f"{eid}:") for message in failures):
                    failures.append(f"{eid}: no executable passes")
                continue
            bundle["effects"][eid] = {
                "namespace": eff["namespace"],
                "func": eff["func"],
                "kind": infer_kind(eff["namespace"], eff["passes"], eff.get("textures", {})),
                "domain": eff.get("domain", infer_domain(eid)),
                "params": eff["params"],
                "textures": eff.get("textures", {}),
                "passes": passes,
            }
            if eff["params"].get("iterationCount", {}).get("cpuOnly"):
                bundle["effects"][eid]["iterated"] = True
            for field in ("outputTex", "outputTex3d", "outputGeo", "loopRole"):
                if eff.get(field) is not None:
                    bundle["effects"][eid][field] = eff[field]
            if eff.get("externalTexture"):
                bundle["effects"][eid]["externalTexture"] = eff["externalTexture"]
        if failures:
            raise RuntimeError(f"bundle build failed ({len(failures)} failure(s)):\n" + "\n".join(failures))
        if set(bundle["effects"]) != set(ids):
            raise RuntimeError("bundle effect inventory does not match requested effect ids")
        if drift and not update_lock:
            print(
                f"\nSHADER DRIFT vs bundle-lock.json ({len(drift)}): {drift[:8]}\nRe-run with --update-lock to accept.",
                file=sys.stderr,
            )
            raise SystemExit(1)
        with open(os.path.join(staged_dir, "metadata.json"), "w") as f:
            json.dump(bundle, f, indent=2)
        with open(os.path.join(staged_dir, "bundle-lock.json"), "w") as f:
            json.dump({"source": CDN_BASE, "version": CDN_VERSION, "hashes": hashes}, f, indent=2)
        _validate_artifacts(bundle, hashes, kdir)
        _publish_bundle(staged_dir, out_dir)
        staged_dir = None
    finally:
        if staged_dir is not None and os.path.exists(staged_dir):
            shutil.rmtree(staged_dir)
    print(f"wrote {len(bundle['effects'])} effect(s) ({n_ok} programs, 0 skipped) from CDN {CDN_VERSION}")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--all" in argv:
        ids = eligible_ids()
    elif "--only" in argv:
        ids = argv[argv.index("--only") + 1].split(",")
    else:
        ids = ["synth/solid", "filter/invert"]
    build(ids, update_lock="--update-lock" in argv)


if __name__ == "__main__":
    main()
