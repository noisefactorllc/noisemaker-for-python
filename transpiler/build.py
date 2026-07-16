"""Regenerate the vendored Python bundle from the CDN.

Pipeline: cdn.fetch_effect -> preprocess.normalize -> parser.parse ->
codegen.emit_python -> write src/noisemaker_cpu/bundle/. Pure Python.

  python -m transpiler.build [--all | --only a,b] [--update-lock]
"""

from __future__ import annotations

import hashlib
import json
import os
import sys

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


def runtime_defines(params: dict) -> dict:
    out = {}
    for spec in params.values():
        if isinstance(spec, dict) and spec.get("define"):
            out[spec["define"]] = "float" if spec.get("type") == "float" else "int"
    return out


def infer_kind(passes) -> str:
    return "filter" if any(p.get("inputs") for p in passes) else "generator"


def _key(eid, program):
    return f"{eid}:{program}"


def _file(key):
    return key.replace("/", "__").replace(":", "__") + ".py"


def build(ids, out_dir=BUNDLE, update_lock=False):
    kdir = os.path.join(out_dir, "kernels", "python")
    os.makedirs(kdir, exist_ok=True)
    lock_path = os.path.join(out_dir, "bundle-lock.json")
    old = json.load(open(lock_path)) if os.path.exists(lock_path) else {"hashes": {}}
    hashes = dict(old.get("hashes", {}))
    drift = []
    bundle = {
        "provenance": {"source": "shaders.noisedeck.app CDN", "version": CDN_VERSION, "base": CDN_BASE},
        "effects": {},
    }
    n_ok = n_skip = 0
    for eid in ids:
        try:
            eff = fetch_effect(eid)
        except Exception as e:  # noqa: BLE001 - a few effects compute defs via JS; skip
            n_skip += 1
            print(f"skip {eid}: cdn: {str(e)[:70]}", file=sys.stderr)
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
                    passes.append({"name": p["name"], "program": p["program"], "key": None,
                                   "drawMode": p["drawMode"], "inputs": p.get("inputs", {}),
                                   "outputs": p.get("outputs", {}), "uniforms": p.get("uniforms", {})})
                continue
            key = _key(eid, p["program"])
            h = hashlib.sha256(glsl.strip().encode("utf-8")).hexdigest()
            try:
                norm = normalize(glsl, defines)
                ast = parse(norm["source"])
                py = emit_python(ast, norm.get("outputs"), norm.get("varyings"))
            except Exception as e:  # noqa: BLE001 - report + skip, keep building
                n_skip += 1
                print(f"skip {key}: {type(e).__name__}: {str(e)[:80]}", file=sys.stderr)
                continue
            with open(os.path.join(kdir, _file(key)), "w") as f:
                f.write(py)
            if old.get("hashes", {}).get(key) and old["hashes"][key] != h:
                drift.append(key)
            hashes[key] = h
            n_ok += 1
            passes.append({"name": p["name"], "program": p["program"], "key": key,
                           "inputs": p.get("inputs") or {}, "outputs": p.get("outputs") or {},
                           "uniforms": p.get("uniforms") or {}})
        if not passes:
            continue
        bundle["effects"][eid] = {
            "namespace": eff["namespace"], "func": eff["func"], "kind": infer_kind(eff["passes"]),
            "params": eff["params"], "textures": eff.get("textures", {}), "passes": passes,
        }
        if eff.get("externalTexture"):
            bundle["effects"][eid]["externalTexture"] = eff["externalTexture"]
    if drift and not update_lock:
        print(f"\nSHADER DRIFT vs bundle-lock.json ({len(drift)}): {drift[:8]}\nRe-run with --update-lock to accept.", file=sys.stderr)
        sys.exit(1)
    with open(os.path.join(out_dir, "metadata.json"), "w") as f:
        json.dump(bundle, f, indent=2)
    with open(lock_path, "w") as f:
        json.dump({"source": CDN_BASE, "version": CDN_VERSION, "hashes": hashes}, f, indent=2)
    print(f"wrote {len(bundle['effects'])} effect(s) ({n_ok} programs, {n_skip} skipped) from CDN {CDN_VERSION}")


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
