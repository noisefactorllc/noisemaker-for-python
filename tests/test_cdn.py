"""Integration tests for transpiler.cdn.

These hit the live shaders.noisedeck.app CDN (cached to disk after the
first run, so repeat runs are fast/offline -- see transpiler/cdn.py). Any
test that needs the network skips gracefully if the CDN is unreachable.
"""

from __future__ import annotations

import json5
import pytest

from transpiler import cdn


def _fetch_manifest_or_skip():
    try:
        return cdn.fetch_manifest()
    except cdn.CDNError as exc:
        pytest.skip(f"shaders.noisedeck.app unreachable: {exc}")


def _fetch_effect_or_skip(effect_id):
    try:
        return cdn.fetch_effect(effect_id)
    except cdn.CDNError as exc:
        pytest.skip(f"shaders.noisedeck.app unreachable: {exc}")


def _eligible_ids_or_skip():
    try:
        return cdn.eligible_ids()
    except cdn.CDNError as exc:
        pytest.skip(f"shaders.noisedeck.app unreachable: {exc}")


def test_fetch_manifest_has_expected_shape():
    manifest = _fetch_manifest_or_skip()

    assert isinstance(manifest, dict)
    assert "synth/solid" in manifest
    assert "filter/blur" in manifest
    assert manifest["synth/solid"]["glsl"] == {"solid": "combined"}


def test_fetch_effect_synth_solid():
    effect = _fetch_effect_or_skip("synth/solid")

    assert effect["id"] == "synth/solid"
    assert effect["namespace"] == "synth"
    assert effect["func"] == "solid"

    params = effect["params"]
    assert params["color"]["type"] == "color"
    assert params["color"]["default"] == [0.5, 0.5, 0.5]
    assert params["color"]["uniform"] == "color"
    assert params["alpha"]["type"] == "float"
    assert params["alpha"]["default"] == 1

    assert len(effect["passes"]) == 1
    assert effect["passes"][0]["program"] == "solid"

    solid_glsl = effect["programs"]["solid"]
    assert "void main()" in solid_glsl
    assert "fragColor = vec4(color * alpha, alpha)" in solid_glsl


def test_fetch_effect_filter_invert():
    effect = _fetch_effect_or_skip("filter/invert")

    params = effect["params"]
    assert params["mode"]["type"] == "int"
    assert params["mode"]["uniform"] == "mode"

    inv_glsl = effect["programs"]["inv"]
    assert "textureSize" in inv_glsl
    assert "mode == 1" in inv_glsl


def test_fetch_effect_filter_blur():
    effect = _fetch_effect_or_skip("filter/blur")

    assert len(effect["passes"]) == 2
    programs_in_passes = {p["program"] for p in effect["passes"]}
    assert programs_in_passes == {"blurH", "blurV"}

    for program in ("blurH", "blurV"):
        glsl = effect["programs"][program]
        assert isinstance(glsl, str)
        assert glsl.strip() != ""


def test_eligible_ids():
    ids = _eligible_ids_or_skip()

    # The CPU-iterated stateful/particle catalog expands eligibility to 188.
    # drift over time rather than pinning an exact count.
    assert abs(len(ids) - 188) <= 10, len(ids)
    assert len(ids) == len(set(ids))  # no duplicates

    for effect_id in ids:
        assert "3d" not in effect_id, effect_id

    assert "synth/solid" in ids
    assert "filter/blur" in ids
    assert "synth/cellularAutomata" in ids
    assert "points/attractor" in ids
    assert "render/pointsEmit" in ids

    # Reactive/3D effects stay excluded.
    for excluded in (
        "synth/scope",
        "classicNoisedeck/shapes3d",
    ):
        assert excluded not in ids


def test_eligible_ids_includes_cpu_iterated_catalog(monkeypatch):
    iterated = {
        "filter/convolutionFeedback",
        "filter/feedback",
        "filter/motionBlur",
        "filter/temporalAberration",
        "points/attractor",
        "points/buddhabrot",
        "points/dla",
        "points/flock",
        "points/flow",
        "points/hydraulic",
        "points/lenia",
        "points/life",
        "points/physarum",
        "points/physical",
        "render/pointsBillboardRender",
        "render/pointsEmit",
        "render/pointsRender",
        "synth/cellularAutomata",
        "synth/mnca",
        "synth/navierStokes",
        "synth/reactionDiffusion",
    }
    excluded = {
        "render/loopBegin",
        "render/loopEnd",
        "render/meshRender",
        "render/environmentCubemap",
        "synth/scope",
        "synth/volume3d",
    }
    manifest = {effect_id: {} for effect_id in iterated | excluded | {"synth/solid"}}
    monkeypatch.setattr(cdn, "fetch_manifest", lambda _version: manifest)

    ids = set(cdn.eligible_ids("test-version"))

    assert iterated <= ids
    assert excluded.isdisjoint(ids)


def test_globals_sanitizer_preserves_scientific_notation():
    source = "{small:5e-4, large:1E+3, computed:moduleConstant}"

    parsed = json5.loads(cdn._sanitize_bare_identifiers(source))

    assert parsed == {"small": 0.0005, "large": 1000.0, "computed": 0}


def test_cpu_iteration_metadata_is_injected_for_iterated_effects():
    effect = {"params": {"seed": {"type": "int", "default": 1}}}

    cdn._inject_cpu_iteration("render/pointsEmit", effect)

    assert effect["params"]["iterationCount"] == {
        "type": "int",
        "default": 60,
        "min": 0,
        "max": 10000,
        "cpuOnly": True,
    }


def test_effect_identity_falls_back_to_manifest_id_when_cdn_fields_are_missing():
    effect = {"namespace": None, "func": None, "params": {}}

    normalized = cdn._normalize_effect("synth/cellularAutomata", effect)

    assert normalized["namespace"] == "synth"
    assert normalized["func"] == "cellularAutomata"
