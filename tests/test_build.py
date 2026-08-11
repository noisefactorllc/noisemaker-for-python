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

    assert len(effects) == 205
    assert Counter(definition["domain"] for definition in effects.values()) == {
        "image": 190,
        "loop-begin": 1,
        "loop-end": 1,
        "volume-filter": 2,
        "volume-generator": 7,
        "volume-renderer": 4,
    }


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

    assert calls == [{"js_vector_storage": True}]


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
