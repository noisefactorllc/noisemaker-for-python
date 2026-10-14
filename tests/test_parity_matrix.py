"""Binding-rule coverage for scripts/parity-matrix._matrix_values.

The matrix derives one variant per bindable parameter at its documented
minimum and maximum; an exclusive or unbounded documented bound falls back to
the nearest valid interior value. These tests pin the interior rules that a
wrong ordering would silently break: a documented choice domain (the 16..128
of most volumeSize parameters) must bind through the choices path, and only
parameters with neither documented bounds nor a documented choice set take
the interior values.
"""

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


def test_documented_choice_volumeSize_binds_choice_extremes():
    # filter3d/flow3d's volumeSize documents a 16..128 choice domain: the
    # sweep must bind those documented extremes, not interior values.
    spec = {"type": "int", "default": 16, "choices": {k: v for k, v in ((f"{v}", v) for v in (16, 32, 64, 128))}}
    assert _values("volumeSize", spec) == [("min", 16), ("max", 128)]


def test_oracle_documented_choice_volumeSize_binds_choice_extremes():
    # A choice set the bundled catalog omits but the pinned oracle documents
    # binds the oracle's documented extremes too.
    spec = {"type": "int", "default": 16}
    ospec = {"type": "int", "choices": {"s16": 16, "s128": 128}}
    assert _values("volumeSize", spec, ospec) == [("min", 16), ("max", 128)]


def test_undocumented_volumeSize_binds_valid_interior():
    # render/renderLandscape3d's volumeSize documents neither bounds nor
    # choices, and volumeSize=0 is invalid on both engines: the interior is
    # 1 at the minimum and default+1 at the maximum.
    spec = {"type": "int", "default": 64}
    assert _values("volumeSize", spec) == [("min", 1), ("max", 65)]


def test_undocumented_stateSize_binds_documented_domain():
    # points/attractor's stateSize records omit the bounds every other
    # stateSize effect documents: the interior uses that documented domain.
    spec = {"type": "int", "default": 64}
    assert _values("stateSize", spec) == [("min", 64), ("max", 2048)]


def test_documented_min_max_bind_the_documented_bounds():
    spec = {"type": "float", "default": 0, "min": -1, "max": 1}
    assert _values("blacks", spec) == [("min", -1), ("max", 1)]


def test_generic_int_binds_zero_and_default_plus_one():
    spec = {"type": "int", "default": 3}
    assert _values("mode", spec) == [("min", 0), ("max", 4)]
