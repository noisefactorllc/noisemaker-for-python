"""Binding-rule coverage for the GAP-011 parameter matrix, plus the GAP-013
weekly-gate sample that renders recorded matrix cases against the pinned
oracle."""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from importlib.machinery import SourceFileLoader

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)

_loader = SourceFileLoader("_parity_matrix_test_module", os.path.join(_ROOT, "scripts", "parity-matrix"))
_spec = importlib.util.spec_from_loader(_loader.name, _loader)
_pmx = importlib.util.module_from_spec(_spec)
_loader.exec_module(_pmx)


def _values(pname, spec, ospec=None):
    return _pmx._matrix_values(pname, spec, ospec or {})


@pytest.mark.parametrize("name", ["iterationCount", "stateSize", "volumeSize"])
def test_resource_sizing_controls_do_not_create_variants(name):
    assert _values(name, {"type": "int", "default": 64, "min": 1, "max": 128}) == []


def test_build_matrix_excludes_resource_sizing_variants():
    effects = {"test/effect": {"params": {
        "iterationCount": {"type": "int", "min": 1, "max": 10},
        "stateSize": {"type": "int", "min": 64, "max": 2048},
        "volumeSize": {"type": "int", "min": 16, "max": 128},
        "alpha": {"type": "float", "min": 0, "max": 1},
    }}}
    cases = {"test/effect": ("effect", None, 8)}
    matrix = _pmx.build_matrix(effects, cases, {})
    assert [item["case"] for item in matrix] == ["test/effect#alpha@min", "test/effect#alpha@max"]


def test_matrix_renders_every_case_at_8x8():
    effects = _pmx._parity._meta()["effects"]
    cases = _pmx.matrix_cases(effects)
    assert set(cases) == set(effects)
    assert {width for _kind, _payload, width in cases.values()} == {8}
    # The summary keeps its own 2x2 volume and loop chains; the matrix does not.
    assert _pmx._ps._build_cases(effects)["render/render3d"][2] == 2
    assert cases["render/render3d"][2] == 8


def test_oracle_record_binds_parameters_the_port_metadata_omits():
    # synth/remap's per-zone parameters live only in the oracle's records:
    # the union still binds them (both engines thread the uniform), while
    # surface-typed zone inputs stay excluded as resources.
    effects = {"synth/remap": {"params": {
        "zoneCount": {"type": "int", "min": 0, "max": 8},
    }}}
    records = {"synth/remap": {
        "zone0_count": {"type": "int", "default": 0, "min": 0, "max": 64},
        "zone0_alpha": {"type": "float", "default": 1, "min": 0, "max": 1},
        "zone0_bounds": {"type": "vec4", "default": [0, 0, 1, 1]},
        "zone0_tex": {"type": "surface"},
    }}
    cases = {"synth/remap": ("effect", None, 8)}
    matrix = _pmx.build_matrix(effects, cases, records)
    got = [item["case"] for item in matrix]
    assert "synth/remap#zone0_count@min" in got and "synth/remap#zone0_count@max" in got
    assert "synth/remap#zone0_alpha@min" in got and "synth/remap#zone0_alpha@max" in got
    assert "synth/remap#zone0_bounds@min" in got
    assert not [c for c in got if c.startswith("synth/remap#zone0_tex")]


def test_oracle_only_undocumented_types_bind_interiors():
    assert _values("zone0_v0", {}, {"type": "vec4", "default": [0, 0, 0, 0]}) == [
        ("min", [0, 0, 0, 0]),
        ("max", [1, 1, 1, 1]),
    ]
    assert _values("zone_count", {}, {"type": "int", "default": 5}) == [("min", 0), ("max", 6)]


def test_documented_min_max_bind_the_documented_bounds():
    spec = {"type": "float", "default": 0, "min": -1, "max": 1}
    assert _values("blacks", spec) == [("min", -1), ("max", 1)]


def test_generic_int_binds_zero_and_default_plus_one():
    spec = {"type": "int", "default": 3}
    assert _values("mode", spec) == [("min", 0), ("max", 4)]


def _cache_entry(**over):
    entry = {
        "case": "synth/test#mode@max",
        "kind": "effect",
        "eid": "synth/test",
        "params": {"mode": 4},
        "payload": None,
    }
    entry.update(over)
    return entry


def test_oracle_cache_key_binds_the_case_definition():
    # The same case id at a different bound value must not share a cache key:
    # a stale hit would feed the wrong oracle surface into the comparison.
    assert _pmx._oracle_cache_key(_cache_entry()) == _pmx._oracle_cache_key(_cache_entry())
    assert _pmx._oracle_cache_key(_cache_entry()) != _pmx._oracle_cache_key(_cache_entry(params={"mode": 3}))
    assert _pmx._oracle_cache_key(_cache_entry()) != _pmx._oracle_cache_key(_cache_entry(eid="synth/other"))
    # The render width is part of the oracle inputs: a summary width override
    # (filter/glyphMap at 64) must never hit an 8x8 oracle render's key.
    assert _pmx._oracle_cache_key(_cache_entry()) != _pmx._oracle_cache_key(_cache_entry(width=64))
    # The case-id label alone never moves the key: identical oracle inputs
    # (same effect id, same bindings) are the same oracle render.
    assert _pmx._oracle_cache_key(_cache_entry()) == _pmx._oracle_cache_key(_cache_entry(case="renamed#mode@max"))


def test_oracle_cache_key_binds_the_spliced_program_text():
    # A graph case's oracle render is the final spliced DSL text, so the key
    # must change when the text changes even if the payload label is equal.
    def _fake_splice(program, func, pname, value):
        return f"{program}|{func}:{pname}={value}"

    real_splice = _pmx.splice_bindings
    _pmx.splice_bindings = _fake_splice
    try:
        bound = _pmx._oracle_cache_key(
            _cache_entry(kind="graph", eid="filter/grade", payload="a().b().write(o0)", params={"blacks": 1})
        )
        other = _pmx._oracle_cache_key(
            _cache_entry(kind="graph", eid="filter/grade", payload="a().b().write(o0)", params={"blacks": 0})
        )
        assert bound != other
    finally:
        _pmx.splice_bindings = real_splice


def test_oracle_cache_corrupt_or_missing_entry_falls_back(tmp_path):
    from noisemaker_cpu.png import encode_png
    from noisemaker_cpu.surface import Surface

    good = tmp_path / "good.png"
    good.write_bytes(encode_png(Surface(2, 2)))
    assert _pmx._load_oracle_cache(str(good)) is not None

    bad = tmp_path / "bad.png"
    bad.write_bytes(b"not a png")
    assert _pmx._load_oracle_cache(str(bad)) is None

    assert _pmx._load_oracle_cache(str(tmp_path / "missing.png")) is None


def test_port_cache_key_binds_engine_and_case():
    assert _pmx._port_cache_key(_cache_entry()) == _pmx._port_cache_key(_cache_entry())
    assert _pmx._port_cache_key(_cache_entry()) != _pmx._port_cache_key(_cache_entry(params={"mode": 3}))
    digest = _pmx._port_inputs_digest()
    assert len(digest) == 40
    assert digest == _pmx._port_inputs_digest()


def test_port_cache_roundtrip(tmp_path):
    raw = bytes(range(256))
    path = tmp_path / "case.rgba"
    path.write_bytes(raw)
    wrapped = _pmx._CachedRGBA(path.read_bytes())
    assert wrapped.to_rgba8() == raw


def test_resume_requires_matching_source_fingerprint(tmp_path):
    path = tmp_path / "verdicts.log"
    path.write_text("EXACT test/effect#alpha@min\n")
    with pytest.raises(ValueError, match="source fingerprint"):
        _pmx._read_resume_log(str(path), "current", {"test/effect#alpha@min"})
    path.write_text("PARITY-INPUTS previous\nEXACT test/effect#alpha@min\n")
    with pytest.raises(ValueError, match="source fingerprint"):
        _pmx._read_resume_log(str(path), "current", {"test/effect#alpha@min"})
    path.write_text("PARITY-INPUTS current\nEXACT test/effect#alpha@min\n")
    assert _pmx._read_resume_log(str(path), "current", {"test/effect#alpha@min"}) == {
        "test/effect#alpha@min": "EXACT test/effect#alpha@min"
    }


def test_resume_fingerprint_binds_case_definition(monkeypatch):
    monkeypatch.setattr(_pmx._parity, "_cpu_revision", lambda: {"cpuHead": "pinned"})
    base = _cache_entry()
    changed = _cache_entry(params={"mode": 3})
    assert _pmx._resume_fingerprint([base]) == _pmx._resume_fingerprint([base])
    assert _pmx._resume_fingerprint([base]) != _pmx._resume_fingerprint([changed])


# ---------------------------------------------------------------------------
# GAP-013: an executable gate renders the parameter matrix against the pinned
# oracle. The recorded sample binds the two filters that historically diverged
# at parameter extremes (filter/spookyTicker, filter/osd) plus one effect of
# every catalog family, chosen so the whole sample renders well inside the
# weekly gate's budget. The guard test below runs in the push gate and keeps
# the recorded sample aligned with the catalog; the oracle test runs only in
# the weekly full gate (`pytest -q -ra`).
_MATRIX_SAMPLE = (
    "filter/spookyTicker",
    "filter/osd",
    "classicNoisedeck/composite",
    "filter3d/palette3d",
    "mixer/alphaMask",
    "points/attractor",
    "render/loopEnd",
    "synth/roll",
    "synth3d/heightmap3d",
)
_MATRIX_SUBPROCESS_TIMEOUT = 540  # ~8x the observed wall clock for the sample


def test_recorded_matrix_sample_covers_every_family_and_the_prior_divergers():
    effects = _pmx._parity._meta()["effects"]
    families = {eid.split("/")[0] for eid in effects}
    assert {eid.split("/")[0] for eid in _MATRIX_SAMPLE} == families
    assert len(_MATRIX_SAMPLE) == len(set(_MATRIX_SAMPLE))
    unknown = [eid for eid in _MATRIX_SAMPLE if eid not in effects]
    assert unknown == []
    assert "filter/spookyTicker" in _MATRIX_SAMPLE
    assert "filter/osd" in _MATRIX_SAMPLE


def test_recorded_matrix_sample_binds_parameter_variants():
    # Every sampled effect must actually reach the matrix: an effect id the
    # catalog lists but whose case the matrix cannot build would silently
    # shrink the rendered sample. This guard uses the port's own parameter
    # metadata so it can run in the push gate without the oracle; the oracle
    # run below re-derives the union with the pinned oracle's records.
    effects = _pmx._parity._meta()["effects"]
    cases = _pmx.matrix_cases(effects)
    matrix = _pmx.build_matrix(effects, cases, {}, set(_MATRIX_SAMPLE))
    assert [entry["case"] for entry in matrix if entry.get("kind") == "missing"] == []
    assert len({entry["case"] for entry in matrix}) >= len(_MATRIX_SAMPLE)


CPU_DIR = os.environ.get("NOISEMAKER_CPU_DIR") or os.path.normpath(
    os.path.join(_ROOT, "..", "noisemaker-for-cpu")
)


@pytest.mark.oracle
@pytest.mark.slow
@pytest.mark.skipif(
    not (shutil.which("node") and os.path.exists(os.path.join(CPU_DIR, "bin", "noisemaker-cpu.js"))),
    reason="JS oracle (node + noisemaker-cpu) not available",
)
def test_sampled_parameter_matrix_matches_the_pinned_oracle_byte_exact():
    """Run scripts/parity-matrix --only over the recorded sample and require
    an exact (byte-identical) verdict for every sampled case."""
    result = subprocess.run(
        [sys.executable, os.path.join(_ROOT, "scripts", "parity-matrix"), "--only", ",".join(_MATRIX_SAMPLE)],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        timeout=_MATRIX_SUBPROCESS_TIMEOUT,
    )
    verdicts = {
        line.split()[1]: line
        for line in result.stdout.splitlines()
        if line.startswith(("EXACT ", "FAIL "))
    }
    summary = next((line for line in result.stdout.splitlines() if line.startswith("PARITY-SUMMARY ")), None)
    assert summary is not None, (
        f"matrix produced no summary (exit {result.returncode})\n"
        f"stdout:\n{result.stdout[-4000:]}\nstderr:\n{result.stderr[-2000:]}"
    )
    counts = json.loads(summary[len("PARITY-SUMMARY "):])
    assert counts["expected"] == counts["executed"] == counts["exact"] > 0, counts
    assert counts["fail"] == counts["near"] == counts["defer"] == counts["skip"] == counts["missing"] == 0, counts
    assert result.returncode == 0, (
        f"matrix exited {result.returncode}\n"
        f"stderr:\n{result.stderr[-2000:]}"
    )
    failures = [text for text in verdicts.values() if text.startswith("FAIL ")]
    assert not failures, failures[:8]
    assert len(verdicts) == counts["expected"], counts
