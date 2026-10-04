import json
from collections import Counter
from pathlib import Path

import pytest

from transpiler import build as build_module


def _simple_effect(effect_id="synth/test"):
    namespace, func = effect_id.split("/", 1)
    return {
        "id": effect_id,
        "namespace": namespace,
        "func": func,
        "params": {},
        "textures": {},
        "passes": [
            {
                "name": "main",
                "program": "main",
                "inputs": {},
                "outputs": {"fragColor": "outputTex"},
            }
        ],
        "programs": {"main": "out vec4 fragColor; void main() { fragColor = vec4(1.0); }"},
    }


def _tree_snapshot(root):
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in root.rglob("*") if path.is_file()}


def test_bundled_catalog_preserves_scientific_notation_enum_value():
    metadata = json.loads((Path(build_module.BUNDLE) / "metadata.json").read_text())

    choices = metadata["effects"]["classicNoisedeck/coalesce"]["params"]["blendMode"]["choices"]

    assert choices["hueAB"] == 1000


def test_bundled_catalog_has_complete_cpu_domain_partition():
    effects = json.loads((Path(build_module.BUNDLE) / "metadata.json").read_text())["effects"]

    assert len(effects) == 210
    assert Counter(definition["domain"] for definition in effects.values()) == {
        "image": 193,
        "loop-begin": 1,
        "loop-end": 1,
        "volume-filter": 2,
        "volume-generator": 8,
        "volume-renderer": 5,
    }


_DEGAUSS_OFFSET_OLD = "vec2 offset = vec2(cos(angle), sin(angle)) * displacement * vec2(resolution.x, resolution.y);"
_DEGAUSS_OFFSET_NEW = "vec2 offset = vec2(cos(angle), sin(angle)) * displacement * vec2(width, height);"
_DEGAUSS_CLAMP_OLD = "float maxAllowedDisplacement = maxOffsetPixels / max(resolution.x, 1.0);"
_DEGAUSS_CLAMP_NEW = (
    "float maxAllowedDisplacement = isTiling"
    " ? maxOffsetPixels / max(width_f, height_f)"
    " : maxOffsetPixels / max(resolution.x, 1.0);"
)


def test_degauss_tile_awareness_source_adaptation():
    """Upstream 48d25116 tile-awareness: the build must adapt the pinned CDN
    degauss GLSL to displace in GLOBAL pixel space (the full-resolution dims
    main() passes as width/height) and bound the displacement by the 256px
    tile-overlap budget measured against those dims when tiling, mirroring the
    sibling's recompiled canonical kernel. The pinned CDN 1.0.183 snapshot
    predates the fix, so a regeneration without the adaptation silently
    reverts the kernel to the pre-48d25116 behavior."""
    source = f"float x = 1.0;\n{_DEGAUSS_OFFSET_OLD}\n{_DEGAUSS_CLAMP_OLD}\n"
    adapted = build_module._adapt_source("filter/degauss", "degauss", source)
    assert _DEGAUSS_OFFSET_NEW in adapted and _DEGAUSS_CLAMP_NEW in adapted
    assert _DEGAUSS_OFFSET_OLD not in adapted and _DEGAUSS_CLAMP_OLD not in adapted

    # Both patterns are mandatory: a changed canonical form must fail the
    # build loudly instead of silently keeping the stale lowering.
    with pytest.raises(ValueError, match="degauss canonical displacement pattern changed"):
        build_module._adapt_source(
            "filter/degauss", "degauss", source.replace(_DEGAUSS_OFFSET_OLD, _DEGAUSS_OFFSET_NEW)
        )

    # Other effects pass through unmodified.
    assert build_module._adapt_source("filter/blur", "blurH", source) == source


def test_bundled_degauss_kernel_carries_tile_awareness():
    kernel = (
        Path(build_module.BUNDLE) / "kernels" / "python" / "filter__degauss__degauss.py"
    ).read_text()

    # The offset scales by the full-resolution dims (width/height of
    # warped_channel_value), not the tile-local resolution uniform...
    assert 'displacement, 2, "float"), rt.array([width, height]), 2, "float")' in kernel
    assert (
        'rt.array([rt.swizzle(_u_resolution, "x"), rt.swizzle(_u_resolution, "y")]), 2, "float")'
        not in kernel
    )
    # ...and the displacement clamp is tile-aware.
    assert (
        'maxAllowedDisplacement = (rt.binary("/", maxOffsetPixels, '
        'rt.component_wise("max", width_f, height_f, width=1), 1, "float") if isTiling else'
    ) in kernel


def test_bundled_degauss_kernel_matches_tiled_oracle_render():
    """Node-free regression pin for the 48d25116 tile-awareness delta, against
    committed oracle bytes. With a 32x32 destination inside a 64x64 full
    resolution (renderScale 2 > 1.01), the pre-48d25116 kernel's tile-local
    offset diverges from the oracle by up to 238 rgba8 levels; the committed
    kernel must reproduce the oracle's rgba8 bytes exactly. Oracle surface
    captured from noisemaker-for-cpu 181bff8bfa74 by running
    bindCanonicalKernel(canonicalKernelFactories['filter/degauss:degauss'])
    with resolution 32x32, fullResolution 64x64, tileOffset [0,0],
    displacement 0.25, direction 30, speed 1, seed 1, time 0.25 over a
    procedural input texture."""
    import numpy as np

    from noisemaker_cpu.kernel_loader import load_kernel
    from noisemaker_cpu.pass_runner import Ctx, run_pass
    from noisemaker_cpu.runtime import Runtime
    from noisemaker_cpu.surface import Surface

    width = height = 32
    full_resolution = 64
    fixture = Path(__file__).parent / "data" / "degauss-tile-oracle" / "degauss-tile-64.f32"
    oracle = np.fromfile(fixture, dtype=np.float32)
    assert oracle.shape == (width * height * 4,)

    input_tex = Surface(width, height)
    xs = np.arange(width * height) % width
    ys = np.arange(width * height) // width
    input_tex.data[0::4] = (((xs * 3 + ys * 5) % 256) / 255).astype(np.float32)
    input_tex.data[1::4] = (((xs * 11 + ys * 7) % 256) / 255).astype(np.float32)
    input_tex.data[2::4] = (((xs * 17 + ys * 23) % 256) / 255).astype(np.float32)
    input_tex.data[3::4] = 1

    f32 = np.float32
    uniforms = {
        "renderScale": f32(1.0),
        "speed": f32(1),
        "seed": 1,
        "centerLoX": 0,
        "centerLoY": 0,
        "size": np.zeros(4, dtype=f32),
        "motion": np.zeros(4, dtype=f32),
        "displacement": f32(0.25),
        "direction": f32(30),
        "resolution": np.array([width, height], dtype=f32),
        "fullResolution": np.array([full_resolution, full_resolution], dtype=f32),
        "tileOffset": np.zeros(2, dtype=f32),
        "aspectRatio": f32(width / height),
        "aspect": f32(width / height),
        "time": f32(0.25),
        "globalTime": f32(0.25),
        "deltaTime": f32(0.0),
        "frame": 0,
    }
    kernel_path = Path(build_module.BUNDLE) / "kernels" / "python" / "filter__degauss__degauss.py"
    kernel = load_kernel(kernel_path.read_text(encoding="utf-8"))
    ctx = Ctx(
        Runtime(),
        uniforms=uniforms,
        textures={"inputTex": input_tex},
        resolution=np.array([width, height], dtype=f32),
        time=0.25,
        seed=1,
    )
    surface = run_pass(kernel, ctx, width, height)

    oracle_rgba8 = Surface(width, height, oracle).to_rgba8()
    assert surface.to_rgba8() == oracle_rgba8


_OCTAVEWARP_PX_OLD = "uint(p.x >= 0.0 ? p.x * 2.0 : -p.x * 2.0 + 1.0),"
_OCTAVEWARP_PX_NEW = "uint(abs(p.x) * 2.0) + uint(p.x < 0.0),"
_OCTAVEWARP_PY_OLD = "uint(p.y >= 0.0 ? p.y * 2.0 : -p.y * 2.0 + 1.0),"
_OCTAVEWARP_PY_NEW = "uint(abs(p.y) * 2.0) + uint(p.y < 0.0),"
_OCTAVEWARP_SEED_OLD = "uint(seed)"
_OCTAVEWARP_SEED_NEW = "uint(abs(seed))"


def test_octave_warp_hash21_sign_adaptation():
    """Upstream 058d15dc hash21 sign handling: the build must adapt the pinned
    CDN octaveWarp GLSL from the sign-split ternary seed conversion to
    uint(abs(...)) casts, mirroring the sibling's recompiled canonical kernel.
    The pinned CDN 1.0.183 snapshot predates the fix, so a regeneration without
    the adaptation silently reverts the kernel to the pre-058d15dc behavior."""
    source = f"uvec3 v = uvec3(\n{_OCTAVEWARP_PX_OLD}\n{_OCTAVEWARP_PY_OLD}\n{_OCTAVEWARP_SEED_OLD}\n);\n"
    adapted = build_module._adapt_source("filter/octaveWarp", "octaveWarp", source)
    assert _OCTAVEWARP_PX_NEW in adapted and _OCTAVEWARP_PY_NEW in adapted and _OCTAVEWARP_SEED_NEW in adapted
    assert _OCTAVEWARP_PX_OLD not in adapted and _OCTAVEWARP_PY_OLD not in adapted and _OCTAVEWARP_SEED_OLD not in adapted

    # All three patterns are mandatory: a changed canonical form must fail the
    # build loudly instead of silently keeping the stale lowering.
    with pytest.raises(ValueError, match="octaveWarp canonical hash21 pattern changed"):
        build_module._adapt_source(
            "filter/octaveWarp",
            "octaveWarp",
            source.replace(_OCTAVEWARP_PX_OLD, _OCTAVEWARP_PX_NEW),
        )

    # Other effects pass through unmodified.
    assert build_module._adapt_source("filter/blur", "blurH", source) == source


def test_bundled_octave_warp_kernel_matches_negative_seed_oracle_render():
    """Node-free regression pin for the 058d15dc hash21 sign-handling delta,
    against committed oracle bytes. The whole-catalog parity gate renders
    octaveWarp at seed 1, where the sign-split and abs() seed conversions agree;
    at a negative seed the pre-058d15dc kernel's wrapped negative truncation
    diverges from the oracle by full pixel levels. The committed kernel must
    reproduce the oracle's rgba8 bytes exactly. Oracle surface captured from
    noisemaker-for-cpu 21017a708983 by running
    bindCanonicalKernel(canonicalKernelFactories['filter/octaveWarp:octaveWarp'])
    with resolution 64x48, fullResolution 64x48, tileOffset [0,0], frequency 2,
    octaves 1, displacement 0.25, speed 1, wrap 0, antialias false, seed -2.5,
    time 0.25 over a procedural input texture."""
    import numpy as np

    from noisemaker_cpu.kernel_loader import load_kernel
    from noisemaker_cpu.pass_runner import Ctx, run_pass
    from noisemaker_cpu.runtime import Runtime
    from noisemaker_cpu.surface import Surface

    width, height = 64, 48
    f32 = np.float32
    fixture = Path(__file__).parent / "data" / "octave-warp-sign-oracle" / "octave-warp-negseed-64x48.f32"
    oracle = np.fromfile(fixture, dtype=np.float32)
    assert oracle.shape == (width * height * 4,)

    input_tex = Surface(width, height)
    xs = np.arange(width * height) % width
    ys = np.arange(width * height) // width
    input_tex.data[0::4] = (((xs * 3 + ys * 5) % 256) / 255).astype(np.float32)
    input_tex.data[1::4] = (((xs * 11 + ys * 7) % 256) / 255).astype(np.float32)
    input_tex.data[2::4] = (((xs * 17 + ys * 23) % 256) / 255).astype(np.float32)
    input_tex.data[3::4] = 1

    uniforms = {
        "renderScale": f32(1.0),
        "speed": f32(1),
        "seed": f32(-2.5),
        "centerLoX": 0,
        "centerLoY": 0,
        "size": np.zeros(4, dtype=f32),
        "motion": np.zeros(4, dtype=f32),
        "frequency": f32(2),
        "octaves": f32(1),
        "displacement": f32(0.25),
        "wrap": f32(0),
        "antialias": False,
        "resolution": np.array([width, height], dtype=f32),
        "fullResolution": np.array([width, height], dtype=f32),
        "tileOffset": np.zeros(2, dtype=f32),
        "aspectRatio": f32(width / height),
        "aspect": f32(width / height),
        "time": f32(0.25),
        "globalTime": f32(0.25),
        "deltaTime": f32(0.0),
        "frame": 0,
    }
    kernel_path = Path(build_module.BUNDLE) / "kernels" / "python" / "filter__octaveWarp__octaveWarp.py"
    kernel = load_kernel(kernel_path.read_text(encoding="utf-8"))
    ctx = Ctx(
        Runtime(),
        uniforms=uniforms,
        textures={"inputTex": input_tex},
        resolution=np.array([width, height], dtype=f32),
        time=0.25,
        seed=-2.5,
    )
    surface = run_pass(kernel, ctx, width, height)

    oracle_rgba8 = Surface(width, height, oracle).to_rgba8()
    assert surface.to_rgba8() == oracle_rgba8


def test_bundled_artifact_sets_match():
    bundle_dir = Path(build_module.BUNDLE)
    metadata = json.loads((bundle_dir / "metadata.json").read_text())
    lock = json.loads((bundle_dir / "bundle-lock.json").read_text())
    pass_keys = {
        render_pass["key"]
        for definition in metadata["effects"].values()
        for render_pass in definition["passes"]
        if render_pass["key"] is not None
    }
    kernel_files = {path.name for path in (bundle_dir / "kernels" / "python").iterdir()}

    assert set(lock["hashes"]) == pass_keys
    assert kernel_files == {build_module._file(key) for key in pass_keys}


def test_build_preserves_iterated_effect_and_pass_execution_metadata(tmp_path, monkeypatch):
    effect = {
        "id": "render/pointsRender",
        "namespace": "render",
        "func": "pointsRender",
        "params": {
            "iterationCount": {"type": "int", "default": 60, "cpuOnly": True},
            "iterations": {"type": "int", "default": 3, "uniform": "iterations"},
        },
        "textures": {"trail": {"width": "50%", "height": "50%", "format": "rgba32f"}},
        "passes": [
            {
                "name": "deposit",
                "program": "deposit",
                "inputs": {"trailTex": "trail"},
                "outputs": {"fragColor": "trail"},
                "uniforms": {"count": "iterations"},
                "repeat": "iterations",
                "blend": ["ONE", "ONE_MINUS_SRC_ALPHA"],
                "clear": False,
                "drawMode": "points",
                "count": "input",
                "countUniform": "iterations",
                "drawBuffers": 1,
                "conditions": {"runIf": [{"uniform": "iterations", "equals": 3}]},
            }
        ],
        "programs": {"deposit": "out vec4 fragColor; void main() { fragColor = vec4(1.0); }"},
    }
    monkeypatch.setattr(build_module, "fetch_effect", lambda _effect_id: effect)

    build_module.build([effect["id"]], out_dir=tmp_path)

    metadata = json.loads((tmp_path / "metadata.json").read_text())
    built = metadata["effects"][effect["id"]]
    assert built["kind"] == "filter"
    assert built["iterated"] is True
    assert built["textures"] == effect["textures"]
    assert built["passes"][0] == {
        **effect["passes"][0],
        "key": "render/pointsRender:deposit",
    }


def test_build_preserves_typed_effect_outputs_and_viewport(tmp_path, monkeypatch):
    effect = {
        "id": "synth3d/testVolume",
        "namespace": "synth3d",
        "func": "testVolume",
        "params": {"volumeSize": {"type": "int", "default": 4, "uniform": "volumeSize"}},
        "textures": {
            "volumeCache": {
                "width": {"param": "volumeSize", "default": 4},
                "height": {"param": "volumeSize", "power": 2, "default": 16},
            },
            "geoBuffer": {
                "width": {"param": "volumeSize", "default": 4},
                "height": {"param": "volumeSize", "power": 2, "default": 16},
            },
        },
        "passes": [
            {
                "name": "precompute",
                "program": "precompute",
                "inputs": {},
                "outputs": {"color": "volumeCache", "geoOut": "geoBuffer"},
                "drawBuffers": 2,
                "viewport": {
                    "width": {"param": "volumeSize", "default": 4},
                    "height": {"param": "volumeSize", "power": 2, "default": 16},
                },
            }
        ],
        "outputTex3d": "volumeCache",
        "outputGeo": "geoBuffer",
        "programs": {
            "precompute": (
                "layout(location = 0) out vec4 fragColor; "
                "layout(location = 1) out vec4 geoOut; "
                "void main() { fragColor = vec4(1.0); geoOut = vec4(0.0); }"
            )
        },
    }
    monkeypatch.setattr(build_module, "fetch_effect", lambda _effect_id: effect)

    build_module.build([effect["id"]], out_dir=tmp_path)

    built = json.loads((tmp_path / "metadata.json").read_text())["effects"][effect["id"]]
    assert built["kind"] == "generator"
    assert built["domain"] == "volume-generator"
    assert built["outputTex3d"] == "volumeCache"
    assert built["outputGeo"] == "geoBuffer"
    assert built["passes"][0]["viewport"] == effect["passes"][0]["viewport"]
    assert built["passes"][0]["outputs"] == {"fragColor": "volumeCache", "geoOut": "geoBuffer"}


def test_build_enables_javascript_vector_storage_for_noise3d(tmp_path, monkeypatch):
    effect = {
        "id": "synth3d/noise3d",
        "namespace": "synth3d",
        "func": "noise3d",
        "params": {},
        "textures": {},
        "passes": [
            {
                "name": "precompute",
                "program": "precompute",
                "inputs": {},
                "outputs": {"fragColor": "outputTex"},
            }
        ],
        "programs": {"precompute": "out vec4 fragColor; void main() { fragColor = vec4(1.0); }"},
    }
    calls = []
    emit_python = build_module.emit_python

    def capture_emit(*args, **kwargs):
        calls.append(kwargs)
        return emit_python(*args, **kwargs)

    monkeypatch.setattr(build_module, "fetch_effect", lambda _effect_id: effect)
    monkeypatch.setattr(build_module, "emit_python", capture_emit)

    build_module.build([effect["id"]], out_dir=tmp_path)

    assert calls == [{"js_vector_storage": True, "effect_id": "synth3d/noise3d"}]


def test_build_failure_preserves_existing_bundle(tmp_path, monkeypatch):
    out_dir = tmp_path / "bundle"
    kernel_dir = out_dir / "kernels" / "python"
    kernel_dir.mkdir(parents=True)
    (out_dir / "metadata.json").write_text("original metadata")
    (out_dir / "bundle-lock.json").write_text(json.dumps({"hashes": {"original:key": "original hash"}}))
    (kernel_dir / "original.py").write_text("original kernel")
    before = _tree_snapshot(out_dir)

    def fetch_effect(effect_id):
        if effect_id == "synth/fetchFailure":
            raise OSError("fetch failed")
        return _simple_effect(effect_id)

    monkeypatch.setattr(build_module, "fetch_effect", fetch_effect)
    monkeypatch.setattr(
        build_module, "emit_python", lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("bad kernel"))
    )

    with pytest.raises(RuntimeError) as exc_info:
        build_module.build(["synth/fetchFailure", "synth/kernelFailure"], out_dir=out_dir)

    assert "synth/fetchFailure" in str(exc_info.value)
    assert "synth/kernelFailure:main" in str(exc_info.value)
    assert _tree_snapshot(out_dir) == before


def test_build_replaces_stale_bundle_artifacts(tmp_path, monkeypatch):
    out_dir = tmp_path / "bundle"
    kernel_dir = out_dir / "kernels" / "python"
    kernel_dir.mkdir(parents=True)
    (out_dir / "metadata.json").write_text("{}")
    (out_dir / "bundle-lock.json").write_text(
        json.dumps({"source": "old", "version": "old", "hashes": {"synth/stale:old": "old hash"}})
    )
    (kernel_dir / "synth__stale__old.py").write_text("stale kernel")
    effect = _simple_effect()
    monkeypatch.setattr(build_module, "fetch_effect", lambda _effect_id: effect)

    build_module.build([effect["id"]], out_dir=out_dir)

    metadata = json.loads((out_dir / "metadata.json").read_text())
    lock = json.loads((out_dir / "bundle-lock.json").read_text())
    pass_keys = {
        render_pass["key"]
        for definition in metadata["effects"].values()
        for render_pass in definition["passes"]
        if render_pass["key"] is not None
    }
    assert pass_keys == {"synth/test:main"}
    assert set(lock["hashes"]) == pass_keys
    assert {path.name for path in (out_dir / "kernels" / "python").iterdir()} == {"synth__test__main.py"}


def test_export_kit_config_is_valid_and_matches_catalog():
    root = Path(__file__).resolve().parent.parent
    config_path = root / "export-kit" / "kit.config.json"
    assert config_path.is_file(), "missing export-kit/kit.config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    assert config.get("id") == "python"
    assert config.get("compat", {}).get("mode") == "list"

    for subtree in config.get("subtrees", []):
        assert (root / subtree["from"]).exists(), f"missing subtree source {subtree['from']}"
    for license_entry in config.get("licenses", []):
        assert (root / license_entry["from"]).is_file(), f"missing license source {license_entry['from']}"

    metadata_rel = config.get("compat", {}).get("fromBundleMetadata")
    assert metadata_rel is not None, "compat.fromBundleMetadata missing"
    metadata_path = root / metadata_rel
    assert metadata_path.is_file(), f"missing {metadata_rel}"

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    effects = metadata.get("effects", {})
    assert len(effects) == 210, "expected 210 catalog effects"
    for effect_id, effect in effects.items():
        assert effect.get("func"), f"effect {effect_id} should declare non-empty func"
        assert effect.get("domain"), f"effect {effect_id} should declare non-empty domain"

    pass_keys = {
        render_pass["key"]
        for effect in effects.values()
        for render_pass in effect.get("passes", [])
        if render_pass.get("key") is not None
    }

    lock_path = metadata_path.parent / "bundle-lock.json"
    assert lock_path.is_file(), "missing bundle-lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    assert len(lock.get("hashes", {})) == 300, "expected 300 locked program hashes"
    assert set(lock.get("hashes", {}).keys()) == pass_keys


def test_package_data_config_covers_runtime_bundle(tmp_path):
    """GAP-004 regression guard: wheels and sdists must ship the runtime
    bundle. ``renderer.bundle_dir()`` loads metadata.json, bundle-lock.json and
    bundle/kernels/python/*.py from the installed package directory, so the
    [tool.setuptools.package-data] globs must match those paths."""
    import tomllib

    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    patterns = data["tool"]["setuptools"]["package-data"]["noisemaker_cpu"]

    from noisemaker_cpu.renderer import bundle_dir

    bundle = Path(bundle_dir())
    runtime_files = [bundle / "metadata.json", bundle / "bundle-lock.json"]
    runtime_files += sorted((bundle / "kernels" / "python").glob("*.py"))

    assert runtime_files, "bundle runtime files missing from source tree"

    def fnmatch(python_path, pattern):
        import fnmatch as _fnmatch

        posix = python_path.relative_to(bundle.parent.parent).as_posix()
        return _fnmatch.fnmatch(posix, f"noisemaker_cpu/{pattern}")

    for runtime_file in runtime_files:
        assert any(fnmatch(runtime_file, pattern) for pattern in patterns), (
            f"{runtime_file.name} is not covered by package-data patterns {patterns}; "
            "built distributions would omit a runtime-required file (GAP-004)"
        )
