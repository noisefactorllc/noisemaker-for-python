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


def _adapt_source(effect_id: str, program: str, source: str) -> str:
    # Match the canonical CPU hash casts without changing runtime arithmetic:
    # the sibling's adaptCanonicalSource rewrites these hash returns for every
    # effect except filter/scatter, so the add and the multiply each round.
    if effect_id != "filter/scatter":
        source = source.replace(
            "return fract((p3.x + p3.y) * p3.z);",
            "return fract(float(float(p3.x + p3.y) * p3.z));",
        ).replace(
            "return fract((p3.xx + p3.yz) * p3.zy);",
            "return fract(vec2(float(float(p3.x + p3.y) * p3.z), float(float(p3.x + p3.z) * p3.y)));",
        )
    if effect_id == "filter/strokes" and program == "stkSmear":
        # The canonical typed-array product rounds before accumulation.
        pigment = "pigmentSum += srcSample(centerUV).rgb * mark;"
        if source.count(pigment) != 1:
            raise ValueError("strokes canonical pigment pattern changed")
        source = source.replace(pigment, "pigmentSum += vec3(srcSample(centerUV).rgb * mark);")
    if effect_id == "classicNoisedeck/glitch" and program == "glitch":
        # Upstream Noisemaker a1a3fa2a quantizes the glitch result's rgb
        # channels to 8-bit color before the scanlines/snow stages. The
        # locked CDN build in bundle-lock.json predates that revision, so
        # the transpiler applies the same statement here.
        glitch_call = "color = glitch(uv);"
        quantize = "color.rgb = floor(clamp(color.rgb, 0.0, 1.0) * 255.0 + 0.5) / 255.0;"
        if source.count(glitch_call) != 1:
            raise ValueError("glitch canonical call pattern changed")
        source = source.replace(glitch_call, glitch_call + "\n    " + quantize)
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
    if effect_id == "filter/crt" and program == "crt":
        # Upstream a1a3fa2a quantizes the foreground color to 8-bit before
        # blending it with base_color; same locked-build constraint as
        # classicNoisedeck/glitch above.
        crt_mix = "color = mix(base_color, color, alphaVal);"
        if source.count(crt_mix) != 1:
            raise ValueError("crt canonical mix pattern changed")
        source = source.replace(
            crt_mix,
            "vec3 effectColor8 = floor(clamp(color, 0.0, 1.0) * 255.0 + 0.5) / 255.0;\n"
            "    color = mix(base_color, effectColor8, alphaVal);",
        )
    if effect_id == "classicNoisedeck/effects" and program == "effects":
        # Upstream Noisemaker 6cb1a3c3 makes the classicNoisedeck effect stack
        # tile-aware: the block grids (pixellate, checkerboard dither, stripe
        # mask) anchor to fullResolution, one convolution step measures one
        # full-image texel, input taps map through the tile mapping
        # ((st * fullResolution - tileOffset) / textureSize), the radial zoom
        # clamps each tap to a 256 px budget under tiling, and the checker
        # phase advances by tileOffset. Untiled the two resolutions are equal
        # and tileOffset is zero, so untiled output is unchanged. The locked
        # CDN build in bundle-lock.json predates that revision, so the
        # transpiler applies the same statements here.
        tile_rules = [
            # pixellate: the block grid anchors to the full image
            ("float dx = size * (1.0 / resolution.x);",
             "float dx = size * (1.0 / fullResolution.x);", 1),
            ("float dy = size * (1.0 / resolution.y);",
             "float dy = size * (1.0 / fullResolution.y);", 1),
            ("return texture(inputTex, coord).rgb;",
             "return texture(inputTex, (coord * fullResolution - tileOffset)"
             " / vec2(textureSize(inputTex, 0))).rgb;", 1),
            # convolve: one kernel step is one full-image pixel
            ("vec2 steps = 1.0 / resolution;",
             "vec2 steps = 1.0 / fullResolution;", 1),
            # dither: the block count uses the full resolution and the snapped
            # block center is a full-image coordinate
            ("float amount = resolution.x / size;",
             "float amount = fullResolution.x / size;", 1),
            ("vec4 base = texture( inputTex, vec2( sx, sy ) );",
             "vec4 base = texture( inputTex, (vec2( sx, sy ) * fullResolution"
             " - tileOffset) / vec2(textureSize(inputTex, 0)) );", 1),
            # checker phase anchored to the full image
            ("mod( gl_FragCoord.x, dSize )",
             "mod( gl_FragCoord.x + tileOffset.x, dSize )", 1),
            ("mod( gl_FragCoord.y, dSize )",
             "mod( gl_FragCoord.y + tileOffset.y, dSize )", 2),
            # stripes anchored to full-image pixels
            ("st *= resolution;",
             "st *= fullResolution;", 1),
            # bloom: every tap maps through the tile mapping
            ("vec3 orig = texture(inputTex, st).rgb;",
             "vec3 orig = texture(inputTex, (st * fullResolution - tileOffset)"
             " / vec2(textureSize(inputTex, 0))).rgb;", 1),
            ("sum += texture(inputTex, st + vec2(j, i) * 0.004).rgb * strength;",
             "sum += texture(inputTex, ((st + vec2(j, i) * 0.004)"
             " * fullResolution - tileOffset) / vec2(textureSize(inputTex, 0)))"
             ".rgb * strength;", 1),
            # radial zoom: clamp each tap to a 256 px budget under tiling
            ("vec4 tex = texture(inputTex, st + tapB);",
             "if (tileOffset.x != 0.0 || tileOffset.y != 0.0) {\n"
             "            vec2 tapBudget = vec2(256.0) * invFullResolution;\n"
             "            tapB = min(max(tapB, -tapBudget), tapBudget);\n"
             "        }\n"
             "        vec4 tex = texture(inputTex, ((st + tapB)"
             " * fullResolution - tileOffset) / vec2(textureSize(inputTex, 0)));", 1),
            # the zoom center anchors to the full image
            ("vec2 imageSize = resolution;",
             "vec2 imageSize = fullResolution;", 1),
        ]
        for old, new, count in tile_rules:
            if source.count(old) != count:
                raise ValueError(
                    f"classicNoisedeck/effects tile-awareness source changed: {old!r}"
                )
            source = source.replace(old, new)
    if effect_id == "filter/glyphMap" and program == "glyphMap":
        # Upstream Noisemaker 6cb1a3c3 detects tiling from the full-image size
        # differing from the local render size instead of from tileOffset:
        # the origin tile's offset is (0, 0), the same value the runtime
        # writes when not tiling. Untiled the two resolutions are equal, so
        # output is unchanged. Same locked-build constraint as
        # classicNoisedeck/effects above.
        is_tile = "bool isTileRendering = length(tileOffset) > 0.0;"
        if source.count(is_tile) != 1:
            raise ValueError("glyphMap tiling detection source changed")
        source = source.replace(
            is_tile,
            "bool isTileRendering = any(notEqual(fullResolution, resolution));",
        )
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
                        effect_id=eid,
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
