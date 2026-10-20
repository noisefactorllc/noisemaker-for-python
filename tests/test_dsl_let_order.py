"""Unit tests for DSL statement-order lets (no oracle).

Mirrors noisemaker-cpu test/dsl-let-order.test.js against the real catalog
bundle. Upstream commit 9cc041d0 (statement-order lets): a chain sees only the
lets declared at or before its own statement index, a later let of the same
name reassigns it for later chains, and reading a pending name reports S003.
Lets may still refer to each other in any order.
"""

import pytest

from noisemaker_cpu.dsl import DslError, compile_dsl
from noisemaker_cpu.renderer import _meta


def _effects():
    return _meta()["effects"]


def test_a_chain_uses_the_latest_let_declared_before_it_and_reassignment_is_allowed():
    program = compile_dsl(
        "search synth\nlet x = 10\nnoise(scaleX: x).write(o0)\nlet x = 90\nnoise(scaleX: x).write(o1)\n",
        _effects(),
    )
    assert program["chains"][0]["steps"][0]["params"]["scaleX"] == 10
    assert program["chains"][1]["steps"][0]["params"]["scaleX"] == 90


def test_a_chain_reading_a_let_declared_by_a_later_statement_reports_s003():
    with pytest.raises(DslError, match="Variable used before assignment: 'x'"):
        compile_dsl("search synth\nnoise(scaleX: x).write(o0)\nlet x = 20\n", _effects())


def test_a_let_may_reference_a_later_let_inside_its_value_expression():
    program = compile_dsl(
        "search synth\nlet a = b + 1\nlet b = 5\nnoise(scaleX: a).write(o0)\n",
        _effects(),
    )
    assert program["chains"][0]["steps"][0]["params"]["scaleX"] == 6


def test_a_bare_identifier_naming_a_later_let_reports_s003_at_declaration():
    with pytest.raises(DslError, match="Variable used before assignment: 'b'"):
        compile_dsl(
            "search synth\nlet a = b\nlet b = 5\nnoise(scaleX: a).write(o0)\n",
            _effects(),
        )


def test_a_value_call_may_reference_a_later_let_in_its_arguments():
    program = compile_dsl(
        "search synth\n"
        "let outer = osc(type: oscKind.sine, speed: inner)\n"
        "let inner = osc(type: oscKind.tri, speed: 2)\n"
        "noise(scaleX: outer).write(o0)\n",
        _effects(),
    )
    descriptor = program["chains"][0]["steps"][0]["params"]["scaleX"]
    assert descriptor["type"] == "Oscillator"
    assert descriptor["oscType"] == 0
    assert descriptor["speed"]["type"] == "Oscillator"
    assert descriptor["speed"]["oscType"] == 1
    assert descriptor["speed"]["speed"] == 2


def test_a_cyclic_let_set_fails_with_a_cycle_report():
    with pytest.raises(DslError, match="Automation cycle detected: a -> b -> a"):
        compile_dsl(
            "search synth\nlet a = b + 1\nlet b = a + 1\nnoise(scaleX: a).write(o0)\n",
            _effects(),
        )


def test_a_let_whose_bare_identifier_names_nothing_resolvable_reports_s003_at_declaration():
    with pytest.raises(DslError, match="Variable used before assignment: 'x'"):
        compile_dsl("search synth\nlet y = x\nnoise().write(o0)\n", _effects())


def test_a_bare_identifier_value_that_names_no_effect_reports_s003():
    # Upstream's validator reports S003 for a bare identifier value that names
    # nothing resolvable at declaration (no earlier binding, no effect in the
    # searched namespaces); the JS port mirrors it in test/dsl-grammar-forms.
    with pytest.raises(DslError, match="Variable used before assignment: 'wobble'"):
        compile_dsl("search synth\nlet pattern = wobble\npattern().write(o0)\nrender(o0)\n", _effects())

def test_a_cyclic_let_set_through_a_list_fails_with_a_cycle_report():
    # The list branch threads the resolving chain like every other recursive
    # value position, so a cycle that passes through a list reports instead of
    # recursing until RecursionError.
    with pytest.raises(DslError, match="Automation cycle detected: a -> b -> a"):
        compile_dsl(
            "search synth\nlet a = [b]\nlet b = [a]\nnoise(scaleX: a).write(o0)\n",
            _effects(),
        )
