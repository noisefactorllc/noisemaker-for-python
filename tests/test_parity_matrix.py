"""Binding-rule coverage for the GAP-011 parameter matrix."""

import importlib.util
import os
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
