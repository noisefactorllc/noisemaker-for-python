"""osc() parameter automation: evaluator parity against the pinned upstream
oracle plus DSL-level render/error contracts — port of noisemaker-cpu
test/dsl-osc-automation.test.js against the real catalog bundle.

The fixture's expected values were captured from the pinned upstream tree's own
automation evaluator (Pipeline.prototype.resolveUniformValue) at the recorded
sourceRevision. The JS port additionally re-proves the fixture live against
NM_REFERENCE_ROOT with the upstream JavaScript evaluator; that leg needs a JS
runtime and stays in noisemaker-for-cpu's own suite.
"""

import json
import math
from pathlib import Path

import numpy as np
import pytest

from noisemaker_cpu.automation import _js_round, evaluate_automation, is_automation_value, resolve_automation_uniform
from noisemaker_cpu.dsl import DslError
from noisemaker_cpu.renderer import render_dsl

_FIXTURE = json.loads((Path(__file__).parent / "data" / "osc-automation-golden.json").read_text())
_SPECS = [None, {"min": 0, "max": 1}, {"min": -2, "max": 3}, {"type": "int"}, {"type": "int", "min": 1, "max": 5}]


def _rgba8(surface):
    return np.frombuffer(surface.to_rgba8(), dtype=np.uint8)


def test_osc_automation_matches_the_upstream_oracle_captured_at_the_pinned_revision():
    assert len(_FIXTURE["cases"]) > 0
    for case in _FIXTURE["cases"]:
        spec = _SPECS[case["specIndex"]]
        resolved = resolve_automation_uniform(case["config"], case["time"], spec)
        assert resolved == case["expected"], f'{case["label"]} t={case["time"]} spec={case["specIndex"]}'


def test_every_noise2d_case_from_the_upstream_range_is_covered():
    labels = {case["label"] for case in _FIXTURE["cases"] if case["config"]["oscType"] == 6}
    for suffix in ["defaults", "range", "speed2.5", "offset0.3", "seed42", "fm-speed", "nested-min", "negative-speed"]:
        assert f"kind6-{suffix}" in labels, f"missing kind6-{suffix}"


def test_evaluate_automation_keeps_the_unit_contract_and_depth_guard():
    sine = {"type": "Oscillator", "oscType": 0, "min": 0, "max": 1, "speed": 1, "offset": 0, "seed": 1}
    assert abs(evaluate_automation(sine, 0.25) - 0.5) < 1e-12
    assert evaluate_automation(sine, 0) == 0
    assert abs(evaluate_automation(sine, 1)) < 1e-12
    assert is_automation_value(sine) is True
    assert is_automation_value({"type": "Midi"}) is False
    # Depth > 8 collapses nested fields to the range-scaled zero, as upstream's
    # evaluator does; the top-level oscillator still evaluates deterministically.
    deep = sine
    for _ in range(10):
        deep = {"type": "Oscillator", "oscType": 0, "min": deep, "max": 1, "speed": 1, "offset": 0, "seed": 1}
    deep_value = evaluate_automation(deep, 0.5)
    assert math.isfinite(deep_value) and 0 <= deep_value <= 1


def test_an_osc_parameter_renders_byte_identically_to_its_resolved_numeric_value():
    time = 0.25
    animated = render_dsl(
        "search synth, filter\nnoise().threshold(level: osc(type: sine, min: 0.1, max: 0.4)).write(o0)\nrender(o0)",
        width=3,
        height=2,
        time=time,
    )
    expected_value = evaluate_automation(
        {"type": "Oscillator", "oscType": 0, "min": 0.1, "max": 0.4, "speed": 1, "offset": 0, "seed": 1}, time
    )
    numeric = render_dsl(
        f"search synth, filter\nnoise().threshold(level: {expected_value!r}).write(o0)\nrender(o0)",
        width=3,
        height=2,
        time=time,
    )
    assert np.array_equal(_rgba8(animated), _rgba8(numeric))


def test_an_osc_value_survives_compile_unchanged_and_animates_across_time():
    source = "search synth, filter\nnoise().threshold(level: osc(tri)).write(o0)\nrender(o0)"
    early = render_dsl(source, width=2, height=1, time=0.1)
    mid = render_dsl(source, width=2, height=1, time=0.5)
    assert not np.array_equal(_rgba8(early), _rgba8(mid))


def test_int_choices_params_round_the_resolved_automation_value():
    # The conditional int selector receives Math.round of the resolved automation
    # value (upstream resolveUniformValue's spec.type === 'int' contract); a
    # fractional value leaking into the integer uniform would render differently.
    time = 0.25
    raw = evaluate_automation(
        {"type": "Oscillator", "oscType": 0, "min": 0, "max": 1, "speed": 1, "offset": 0, "seed": 1}, time
    )
    result = render_dsl(
        "search synth, filter\nnoise().invert(mode: osc(sine)).write(o0)\nrender(o0)", width=2, height=1, time=time
    )
    numeric = render_dsl(
        f"search synth, filter\nnoise().invert(mode: {_js_round(raw)}).write(o0)\nrender(o0)",
        width=2,
        height=1,
        time=time,
    )
    assert np.array_equal(_rgba8(result), _rgba8(numeric))
    # And the rounded selection is observable: mode 0 and mode 1 render differently.
    assert not np.array_equal(
        _rgba8(render_dsl("search synth, filter\nnoise().invert(mode: 0).write(o0)\nrender(o0)", width=2, height=1, time=time)),
        _rgba8(render_dsl("search synth, filter\nnoise().invert(mode: 1).write(o0)\nrender(o0)", width=2, height=1, time=time)),
    )


def test_osc_compile_errors_mirror_the_upstream_contract():
    with pytest.raises(DslError, match="oscKind"):
        render_dsl("search synth, filter\nnoise().threshold(level: osc(wobble)).write(o0)\nrender(o0)", width=1, height=1)
    with pytest.raises(DslError, match="oscKind"):
        render_dsl("search synth, filter\nnoise().threshold(level: osc(7)).write(o0)\nrender(o0)", width=1, height=1)
    with pytest.raises(DslError, match="unknown parameter 'phase'"):
        render_dsl(
            "search synth, filter\nnoise().threshold(level: osc(type: sine, phase: 1)).write(o0)\nrender(o0)",
            width=1,
            height=1,
        )
    with pytest.raises(DslError, match="min must be a number"):
        render_dsl(
            "search synth, filter\nnoise().threshold(level: osc(type: sine, min: [1, 2])).write(o0)\nrender(o0)",
            width=1,
            height=1,
        )
    # A color param rejects automation (the JS EffectDefinition rejects anything
    # but float/int at normalization); the Python port surfaces the rejection at
    # coercion time instead of compile time.
    with pytest.raises(TypeError):
        render_dsl("search synth\nsolid(color: osc(sine)).write(o0)\nrender(o0)", width=1, height=1)


def test_osc_nesting_beyond_the_upstream_depth_limit_is_rejected_at_compile_time():
    nested = "osc(type: sine)"
    for _ in range(9):
        nested = f"osc(type: sine, min: {nested})"
    with pytest.raises(DslError, match=r"Automation nesting exceeds the maximum depth of 8"):
        render_dsl(
            f"search synth, filter\nnoise().threshold(level: {nested}).write(o0)\nrender(o0)", width=1, height=1
        )


def test_a_binding_can_hold_an_osc_value_for_reuse_across_steps():
    time = 0.25
    bound = render_dsl(
        "search synth, filter\nlet wobble = osc(type: sine, min: 0.1, max: 0.4)\n"
        "noise().threshold(level: wobble).write(o0)\nrender(o0)",
        width=3,
        height=2,
        time=time,
    )
    expected_value = evaluate_automation(
        {"type": "Oscillator", "oscType": 0, "min": 0.1, "max": 0.4, "speed": 1, "offset": 0, "seed": 1}, time
    )
    numeric = render_dsl(
        f"search synth, filter\nnoise().threshold(level: {expected_value!r}).write(o0)\nrender(o0)",
        width=3,
        height=2,
        time=time,
    )
    assert np.array_equal(_rgba8(bound), _rgba8(numeric))
