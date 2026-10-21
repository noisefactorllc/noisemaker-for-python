"""Regenerate the vendored Python bundle from the CDN.

Pipeline: cdn.fetch_effect -> preprocess.normalize -> parser.parse ->
codegen.emit_python -> write src/noisemaker_cpu/bundle/. Pure Python.

  python -m transpiler.build [--all | --only a,b] [--update-lock]
"""

from __future__ import annotations

import hashlib
import json
import os
import re
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
# These canonical JS kernels materialize vector declarations in Float32Array
# storage before later hash conversions or pigment calculations.
_JS_VECTOR_STORAGE_KEYS = frozenset({"synth3d/noise3d:precompute", "filter/strokes:stkSmear"})
# Effects whose canonical CPU implementation is a hand-written adapter with
# scalar temporaries (scripts/upstream compile-glsl adapters): every vector
# assignment there reads pre-assignment values, so compound assignments keep
# the atomic reduce form instead of the transpiler's component-wise expansion.
_ATOMIC_COMPOUND_KEYS = frozenset(
    {
        "classicNoisedeck/bitEffects:bitEffects",
        "classicNoisedeck/fractal:fractal",
        "filter/crt:crt",
        "filter/historicPalette:historicPalette",
        "filter/median:median",
        "filter/palette:palette",
        "filter/pixelSort:luminance",
        "filter/reindex:nmReindexApply",
        "filter/reindex:nmReindexStats",
        "filter/snow:snow",
        "synth/julia:julia",
        "synth/remap:remap",
    }
)


def _adapt_source(effect_id: str, program: str, source: str) -> str:
    source = source.replace(
        "return fract((p3.x + p3.y) * p3.z);",
        "return fract(float(float(p3.x + p3.y) * p3.z));",
    ).replace(
        "return fract((p3.xx + p3.yz) * p3.zy);",
        "return fract(vec2(float(float(p3.x + p3.y) * p3.z), float(float(p3.x + p3.z) * p3.y)));",
    )
    source = re.sub(
        r"\bmod\(\s*([A-Za-z_]\w*(?:\.[xyzw]{1,4})?)\s*\+\s*1\.0\s*,\s*2\.0\s*\)\s*-\s*1\.0\b",
        r"(\1 - 2.0 * floor((\1 + 1.0) * 0.5))",
        source,
    )
    if effect_id == "synth/navierStokes" and program == "nsSplat":
        old = "return fract(sin(x * 12.9898) * 43758.5453);"
        if source.count(old) != 1:
            raise ValueError("navierStokes hash11 source changed")
        source = source.replace(old, "return fract(float(float(sin(float(float(x) * 12.9898))) * 43758.5453));")
    if effect_id == "filter/scatter" and program == "scatterJitter":
        old = "hash22(hashCoord + float(seed) * 101.7)"
        if source.count(old) != 1:
            raise ValueError("scatter seed term source changed")
        source = source.replace(old, "hash22(hashCoord + float(float(seed) * 101.7))")
    if effect_id == "filter/extrude":
        replacements = [
            ("float s = 1.0 + h * (depth / 100.0) * 0.4;", "float s = float(1.0 + h * (depth / 100.0) * 0.4);"),
            (
                "bool topHit = all(lessThanEqual(abs(P - faceCenter), faceHalf));",
                "bool topHit = all(lessThanEqual(abs((P - imgCenter) - (cellC - imgCenter) * s), faceHalf));",
            ),
        ]
        for old, new in replacements:
            if source.count(old) != 1:
                raise ValueError("extrude block face source changed")
            source = source.replace(old, new)
    if effect_id == "synth3d/noise3d" and program == "precompute":
        replacements = [
            (
                "float hash4(vec4 p) {\n    vec4 ps = p + float(seed) * 0.1;",
                "float hash4(vec4 p, vec4 k) {\n"
                "    float cpuSeedOffset = float(float(seed) * 0.1);\n"
                "    vec4 cpuLatticeOffset = k + cpuSeedOffset;\n"
                "    vec4 ps = p + cpuLatticeOffset;",
            ),
            (
                "vec4 grad4(vec4 p) {\n    float h1 = hash4(p);\n    float h2 = hash4(p + 127.1);\n"
                "    float h3 = hash4(p + 269.5);\n    float h4 = hash4(p + 419.2);",
                "vec4 grad4(vec4 p, vec4 k) {\n    float h1 = hash4(p, k);\n    float h2 = hash4(p, k + 127.1);\n"
                "    float h3 = hash4(p, k + 269.5);\n    float h4 = hash4(p, k + 419.2);",
            ),
        ]
        for old, new in replacements:
            if source.count(old) != 1:
                raise ValueError("noise3d seeded lattice source changed")
            source = source.replace(old, new)
        source, corners = re.subn(
            r"grad4\(vec4\(i\.xyz, (iw[01])\) \+ (vec4\([01],[01],[01],0\))\)", r"grad4(vec4(i.xyz, \1), \2)", source
        )
        if corners != 16:
            raise ValueError(f"noise3d expected 16 corner hashes, found {corners}")
    if effect_id == "synth/perlin" and program == "perlin":
        replacements = [
            (
                "float hash3(vec3 p) {\n    // Add seed to input to vary the noise pattern\n"
                "    p = p + float(seed) * 0.1;",
                "float hash3(vec3 p, vec3 k) {\n"
                "    float cpuSeedOffset = float(float(seed) * 0.1);\n"
                "    vec2 cpuLatticeOffset = k.xy + cpuSeedOffset;\n"
                "    p = vec3(p.x + cpuLatticeOffset.x, p.y + cpuLatticeOffset.y,"
                " float(p.z + cpuSeedOffset) + k.z);",
            ),
            (
                "vec3 grad3(vec3 p) {\n    // Generate 3 independent random values\n"
                "    float h1 = hash3(p);\n    float h2 = hash3(p + 127.1);\n"
                "    float h3 = hash3(p + 269.5);",
                "vec3 grad3(vec3 p, vec3 k) {\n    float h1 = hash3(p, k);\n"
                "    float h2 = hash3(p, k + 127.1);\n    float h3 = hash3(p, k + 269.5);",
            ),
        ]
        for old, new in replacements:
            if source.count(old) != 1:
                raise ValueError("perlin seeded lattice source changed")
            source = source.replace(old, new)
        source, corners = re.subn(
            r"grad3\(vec3\(i\.xy, (iz[01])\) \+ (vec3\([01],[01],0\))\)",
            r"grad3(vec3(i.xy, \1), \2)",
            source,
        )
        if corners != 8:
            raise ValueError(f"perlin expected 8 corner hashes, found {corners}")
    if effect_id in {"synth3d/reactionDiffusion3d", "synth3d/cellularAutomata3d"} and program == "simulate":
        old = (
            "float hash3(vec3 p) {\n"
            "    p = p + float(seed) * 0.1;\n"
            "    p = fract(p * vec3(0.1031, 0.1030, 0.0973));\n"
            "    p += dot(p, p.yxz + 33.33);\n"
            "    return fract((p.x + p.y) * p.z);\n}"
        )
        if source.count(old) != 1:
            raise ValueError(f"{effect_id} seeding hash source changed")
        source = source.replace(
            old,
            "float hash3(vec3 p) {\n"
            "    p = p + float(float(seed) * 0.1);\n"
            "    p = fract(p * vec3(0.1031, 0.1030, 0.0973));\n"
            "    float cpuHashDot = dot(p, p.yxz + 33.33);\n"
            "    return fract(float(float(float(p.x + p.y) + float(cpuHashDot + cpu"
            "HashDot)) * float(p.z + cpuHashDot)));\n}",
        )
    if effect_id == "synth3d/cellularAutomata3d" and program == "simulate":
        if "uniform int colorMode;" not in source:
            replacements = [
                ("uniform float weight;", "uniform float weight;\nuniform int colorMode;"),
                (
                    "int countMooreNeighbors(ivec3 voxel, int volSize) {",
                    "vec4 packState(float alive, float age) {\n"
                    "    if (colorMode == 1) return vec4(alive, age, 0.0, 1.0);\n"
                    "    return vec4(alive, alive, alive, 1.0);\n}\n\n"
                    "int countMooreNeighbors(ivec3 voxel, int volSize) {",
                ),
                ("fragColor = vec4(alive, alive, alive, 1.0);", "fragColor = packState(alive, age);"),
                (
                    "fragColor = vec4(finalAlive, finalAlive, finalAlive, 1.0);",
                    "fragColor = packState(finalAlive, finalAge);",
                ),
            ]
            for old, new in replacements:
                if source.count(old) != 1:
                    raise ValueError("cellularAutomata3d state source changed")
                source = source.replace(old, new)
    if effect_id == "synth3d/cell3d" and program == "precompute":
        old = "vec3 hash3(vec3 p) {\n    p = p + float(seed) * 0.1;"
        if source.count(old) != 1 or source.count("vec3 randomOffset = hash3(cellPos);") != 1:
            raise ValueError("cell3d seeded lattice source changed")
        source = source.replace(
            old,
            "vec3 hash3(vec3 base, vec3 neighbor) {\n"
            "    float cpuSeedOffset = float(float(seed) * 0.1);\n"
            "    vec3 cpuCellPos = base + neighbor;\n"
            "    vec3 p = vec3(base.x + float(neighbor.x + cpuSeedOffset),"
            " cpuCellPos.y + cpuSeedOffset, cpuCellPos.z + cpuSeedOffset);",
        )
        source = source.replace("vec3 randomOffset = hash3(cellPos);", "vec3 randomOffset = hash3(i, neighbor);")
    if effect_id == "filter/strokes" and program == "stkSmear":
        # The canonical typed-array product rounds before accumulation.
        pigment = "pigmentSum += srcSample(centerUV).rgb * mark;"
        if source.count(pigment) != 1:
            raise ValueError("strokes canonical pigment pattern changed")
        source = source.replace(pigment, "pigmentSum += vec3(srcSample(centerUV).rgb * mark);")
    if effect_id == "synth/testPattern" and program == "testPattern":
        # Mirror the sibling's compile-glsl.js restoreIntegerDivision addition
        # (GAP-035): testPattern's numbered checkerboard divides an int digit
        # accumulator in place. Raw JS `/=` leaves a fractional digit and
        # drops glyph-table lookups; the lowered form truncates. Same exact
        # source guards as the sibling's pass.
        digit_decl = "int temp = number;"
        digit_step = "temp /= 10;"
        if digit_decl not in source or digit_step not in source:
            raise ValueError("testPattern digit division source changed")
        source = source.replace(digit_step, "temp = int(temp / 10.0);", 1)
    if effect_id == "synth/polygon" and program == "shape":
        # Upstream Noisemaker 6cb1a3c3 special-cases the degenerate
        # smoothing=0 edge: GLSL smoothstep is undefined when edge0 == edge1,
        # so the reference picks foreground/background by d <= radius instead
        # of the undefined smoothstep. Same locked-build constraint as
        # classicNoisedeck/effects above.
        degenerate = "float m = smoothstep(radius, radius - smoothing, d);"
        if source.count(degenerate) != 1:
            raise ValueError("polygon degenerate smoothing source changed")
        source = source.replace(
            degenerate,
            "float m = smoothing == 0.0 ? (d <= radius ? 1.0 : 0.0)"
            " : smoothstep(radius, radius - smoothing, d);",
        )
    # The sibling's adaptCanonicalSource also temps matrix self-assignments
    # (`v = matN(...) * v;`) before the transpiler sees them, so the multiply
    # reads the pre-assignment vector.
    source = preserve_matrix_self_assignments(source)
    # The sibling's adaptCanonicalSource ends with preserveVectorAssignmentReads:
    # a single-line `v = vecN(...);` whose arguments swizzle-read `v` compiles
    # from a temporary, so the assignment is atomic. Multi-line constructor
    # statements escape that pass and keep the glsl-transpiler's component-wise
    # in-place expansion, where later components read the already-stored earlier
    # ones (mandelbrot's derivative, shapeMask's hexagram SDF).
    return preserve_vector_assignment_reads(source)


_VECTOR_ASSIGNMENT = re.compile(
    r"^(\s*)([A-Za-z_]\w*)\s*=\s*((?:[biu]?vec[234])\s*\([^;\n]*\)[^;\n]*)\s*;$",
    re.M,
)


_MATRIX_SELF_ASSIGNMENT = re.compile(
    r"^(\s*)([A-Za-z_]\w*)\s*=\s*(mat([234])\s*\([^;\n]*\)\s*\*\s*\2)\s*;$",
    re.M,
)


def preserve_matrix_self_assignments(source: str) -> str:
    counter = 0

    def replace(match: re.Match) -> str:
        nonlocal counter
        indent, target, expression, width = match.groups()
        temporary = f"cpu_matrix_assignment_{counter}"
        counter += 1
        return (
            f"{indent}vec{width} {temporary} = {expression};\n"
            f"{indent}{target} = {temporary};"
        )

    return _MATRIX_SELF_ASSIGNMENT.sub(replace, source)


def preserve_vector_assignment_reads(source: str) -> str:
    counter = 0

    def replace(match: re.Match) -> str:
        nonlocal counter
        indent, target, expression = match.groups()
        if not re.search(rf"\b{target}\.[xyzwrgba]", expression):
            return match.group(0)
        declared = re.match(r"^([biu]?vec[234])\s*\(", expression)
        if not declared:
            return match.group(0)
        temporary = f"cpu_vector_assignment_{counter}"
        counter += 1
        return (
            f"{indent}{declared.group(1)} {temporary} = {expression};\n"
            f"{indent}{target} = {temporary};"
        )

    return _VECTOR_ASSIGNMENT.sub(replace, source)


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
    "defines",
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
            # Pass-level defines (reference 0ed489ec's `.flatMap()` per-viewMode/
            # blendMode/blurLayer pass-cloning pattern): each clone bakes a
            # different literal into e.g. VIEW_MODE at the reference's compile
            # time, but since this transpiler lowers every `define:` name to a
            # runtime-branch uniform (see runtime_defines/normalize above), all
            # clones of the same program share one kernel -- the clone-specific
            # value differs only in which uniform binding renderer.py supplies
            # per pass-instance (_pass_metadata below). Union every pass.defines
            # key across the whole effect so the shared kernel declares the
            # uniform regardless of which clone's iteration transpiles first.
            for p in eff["passes"]:
                for name in (p.get("defines") or {}):
                    defines.setdefault(name, "int")
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
                    norm = normalize(_adapt_source(eid, p["program"], glsl), defines)
                    ast = parse(norm["source"])
                    py = emit_python(
                        ast,
                        norm.get("outputs"),
                        norm.get("varyings"),
                        js_vector_storage=key in _JS_VECTOR_STORAGE_KEYS,
                        atomic_compound=key in _ATOMIC_COMPOUND_KEYS,
                        effect_id=eid,
                        constant_divisors=defines,
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
