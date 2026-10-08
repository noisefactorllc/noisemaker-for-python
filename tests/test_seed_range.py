"""Regression: seed-range enforcement mirrors the pinned
oracle. Out-of-range seeds are rejected with a diagnostic naming the parameter
and the bound, unseeded CLI runs draw inside the declared range of the selected
effect, and the DSL's implicit render-seed threading stays unvalidated exactly
like the reference (runtime/renderer.js spreads the render seed into step
params without a range check while explicit assignments are validated).
"""

import click
import pytest
from click.testing import CliRunner

from noisemaker_cpu import cli
from noisemaker_cpu.renderer import ParameterRangeError, _meta, render_dsl, render_effect

CURL_PROGRAM = "search synth\ncurl().write(o0)\nrender(o0)\n"
CURL_MAX = 1000


def _declared_seed_specs():
    """Every bundled effect whose metadata declares a `seed` parameter with a
    maximum."""
    return {
        effect_id: effect["params"]["seed"]
        for effect_id, effect in _meta()["effects"].items()
        if effect["params"].get("seed") is not None and effect["params"]["seed"].get("max") is not None
    }


def _bound_text(bound) -> str:
    if isinstance(bound, float) and bound.is_integer():
        return str(int(bound))
    return str(bound)


def test_every_declared_seed_max_rejects_max_plus_one():
    # The acceptance command covers EVERY bundled effect with a declared seed
    # maximum: an explicit --seed mirrors the pinned oracle's explicit DSL
    # assignment, which the DSL parser validates before any rendering, so the
    # diagnostic fires even for typed-volume effects whose in-range use is
    # refused by the domain check (matching the reference's exit-1 for
    # `generate synth3d/noise3d --seed 101`).
    runner = CliRunner()
    for effect_id, spec in sorted(_declared_seed_specs().items()):
        maximum = spec["max"]
        expected = f'Parameter "seed" must be at most {_bound_text(maximum)}'
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli.main,
                [
                    "generate",
                    effect_id,
                    "--width",
                    "16",
                    "--height",
                    "16",
                    "--seed",
                    str(int(maximum) + 1),
                    "--filename",
                    "out.png",
                ],
            )
        assert result.exit_code != 0, f"{effect_id} accepted a seed above its declared maximum"
        assert expected in result.output, f"{effect_id}: expected {expected!r}, got {result.output!r}"


def test_typed_volume_generate_rejects_out_of_range_seed_through_the_cli():
    # The pinned oracle's `generate synth3d/noise3d --seed 101` exits 1 with
    # the seed diagnostic (the explicit assignment is validated before any
    # rendering), even though the port refuses in-range volume effects in
    # `generate` with the domain diagnostic.
    with CliRunner().isolated_filesystem():
        result = CliRunner().invoke(
            cli.main,
            ["generate", "synth3d/noise3d", "--width", "16", "--height", "16", "--seed", "101", "--filename", "out.png"],
        )
    assert result.exit_code == 1
    assert 'Parameter "seed" must be at most 100' in result.output


def test_typed_volume_generate_in_range_seed_still_gets_the_domain_refusal():
    # In-range explicit seeds keep the pre-existing contract: `generate` is an
    # image-domain command and volume effects go through the DSL run command.
    with CliRunner().isolated_filesystem():
        result = CliRunner().invoke(
            cli.main,
            ["generate", "synth3d/noise3d", "--width", "16", "--height", "16", "--seed", "50", "--filename", "out.png"],
        )
    assert result.exit_code != 0
    assert "typed volume chain" in result.output


def test_typed_volume_render_effect_api_rejects_out_of_range_seed():
    # The renderer API enforces every declared seed range the same way for
    # volume-domain effects, where the actual volume rendering happens (through
    # the DSL run command).
    for effect_id, spec in sorted(_declared_seed_specs().items()):
        if _meta()["effects"][effect_id].get("domain", "image") == "image":
            continue
        with pytest.raises(ParameterRangeError, match="must be at most"):
            render_effect(effect_id, width=16, height=16, seed=int(spec["max"]) + 1)


def test_curl_rejects_1001_and_5000_like_reference():
    runner = CliRunner()
    for seed in ("1001", "5000"):
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli.main,
                ["generate", "synth/curl", "--width", "16", "--height", "16", "--seed", seed, "--filename", "out.png"],
            )
        assert result.exit_code != 0
        assert 'Parameter "seed" must be at most 1000' in result.output


def test_curl_rejects_below_min_like_reference():
    with CliRunner().isolated_filesystem():
        result = CliRunner().invoke(
            cli.main,
            ["generate", "synth/curl", "--width", "16", "--height", "16", "--seed", "-1", "--filename", "out.png"],
        )
    assert result.exit_code != 0
    assert 'Parameter "seed" must be at least 0' in result.output


def test_curl_seed_zero_still_renders():
    with CliRunner().isolated_filesystem():
        result = CliRunner().invoke(
            cli.main,
            ["generate", "synth/curl", "--width", "16", "--height", "16", "--seed", "0", "--filename", "out.png"],
        )
        assert result.exit_code == 0, result.output


def test_in_range_max_seed_still_renders():
    with CliRunner().isolated_filesystem():
        result = CliRunner().invoke(
            cli.main,
            ["generate", "synth/curl", "--width", "16", "--height", "16", "--seed", "1000", "--filename", "out.png"],
        )
        assert result.exit_code == 0, result.output


def test_apply_and_animate_reject_out_of_range_seed():
    runner = CliRunner()
    with runner.isolated_filesystem():
        generate = runner.invoke(
            cli.main,
            ["generate", "synth/curl", "--width", "8", "--height", "8", "--seed", "1", "--filename", "in.png"],
        )
        assert generate.exit_code == 0, generate.output
        apply_result = runner.invoke(
            cli.main,
            ["apply", "synth/curl", "in.png", "--seed", str(CURL_MAX + 1), "--filename", "out.png"],
        )
        assert apply_result.exit_code != 0
        assert 'Parameter "seed" must be at most 1000' in apply_result.output
        animate_result = runner.invoke(
            cli.main,
            [
                "animate",
                "synth/curl",
                "--width",
                "8",
                "--height",
                "8",
                "--frame-count",
                "1",
                "--seed",
                str(CURL_MAX + 1),
                "--save-frames",
                "frames",
            ],
        )
        assert animate_result.exit_code != 0
        assert 'Parameter "seed" must be at most 1000' in animate_result.output


def test_unseeded_generate_draws_inside_declared_range(monkeypatch):
    # CLI-level check on representative effects (the full catalog draw bounds
    # are asserted by test_draw_seed_bounds_cover_every_declared_range; heavy
    # iterated generators would render for minutes here).
    real_randint = cli.random.randint
    draws = []

    def spy(low, high):
        draws.append((low, high))
        return real_randint(low, high)

    monkeypatch.setattr(cli.random, "randint", spy)
    runner = CliRunner()
    for effect_id in ("synth/curl", "filter/warp", "classicNoisedeck/glitch"):
        spec = _meta()["effects"][effect_id]["params"]["seed"]
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli.main,
                ["generate", effect_id, "--width", "8", "--height", "8", "--filename", "out.png"],
            )
        assert result.exit_code == 0, (effect_id, result.output)
        assert draws[-1] == _declared_draw_bounds(spec), effect_id


def _declared_draw_bounds(spec):
    declared_min = spec.get("min")
    low = int(declared_min) if declared_min is not None else 1
    return (low, int(spec["max"]))


def test_draw_seed_bounds_cover_every_declared_range(monkeypatch):
    real_randint = cli.random.randint
    draws = []

    def spy(low, high):
        draws.append((low, high))
        return real_randint(low, high)

    monkeypatch.setattr(cli.random, "randint", spy)
    for effect_id, spec in sorted(_declared_seed_specs().items()):
        cli._draw_seed(effect_id)
        assert draws[-1] == _declared_draw_bounds(spec), effect_id


def test_unseeded_apply_and_animate_draw_inside_declared_range(monkeypatch):
    real_randint = cli.random.randint
    draws = []

    def spy(low, high):
        draws.append((low, high))
        return real_randint(low, high)

    monkeypatch.setattr(cli.random, "randint", spy)
    runner = CliRunner()
    with runner.isolated_filesystem():
        generate = runner.invoke(
            cli.main,
            ["generate", "synth/curl", "--width", "8", "--height", "8", "--seed", "1", "--filename", "in.png"],
        )
        assert generate.exit_code == 0, generate.output
        apply_result = runner.invoke(cli.main, ["apply", "synth/curl", "in.png", "--filename", "out.png"])
        assert apply_result.exit_code == 0, apply_result.output
        assert draws[-1] == (0, CURL_MAX)
        animate_result = runner.invoke(
            cli.main,
            ["animate", "synth/curl", "--width", "8", "--height", "8", "--frame-count", "1", "--save-frames", "frames"],
        )
        assert animate_result.exit_code == 0, animate_result.output
        assert draws[-1] == (0, CURL_MAX)


def test_dsl_implicit_threaded_seed_is_not_range_checked_like_reference():
    # The pinned oracle's `run` command threads the render seed into step
    # params without a range check (runtime/renderer.js): `run --seed 5000`
    # exits 0 there, so the port must too.
    surface = render_dsl(CURL_PROGRAM, width=8, height=8, seed=CURL_MAX + 1)
    assert (surface.width, surface.height) == (8, 8)


def test_dsl_explicit_out_of_range_seed_assignment_is_rejected():
    # Explicit assignments go through the range check, exactly like the pinned
    # oracle's DSL parser (`curl(seed: 5000)` exits 1 there).
    with pytest.raises(ParameterRangeError, match='Parameter "seed" must be at most 1000'):
        render_dsl("search synth\ncurl(seed: 5000).write(o0)\nrender(o0)\n", width=8, height=8)


def test_render_effect_api_rejects_out_of_range_seed():
    # The library entry point carries the effect-command contract: the CLI
    # threads its --seed into the effect's declared seed param and the pinned
    # oracle rejects values above the declared maximum.
    with pytest.raises(ParameterRangeError, match='Parameter "seed" must be at most 1000'):
        render_effect("synth/curl", width=8, height=8, seed=CURL_MAX + 1)


def test_out_of_range_non_seed_param_is_rejected():
    # The range check is generic over numeric parameters, mirroring the pinned
    # oracle's per-parameter min/max enforcement.
    spec = None
    for effect_id, effect in _meta()["effects"].items():
        for pname, pspec in effect["params"].items():
            if pspec.get("max") is not None and pspec["type"] in ("int", "float", "enum", "member"):
                spec = (effect_id, pname, pspec)
                break
        if spec:
            break
    effect_id, pname, pspec = spec
    with pytest.raises(ParameterRangeError, match=f'Parameter "{pname}" must be at most'):
        render_effect(effect_id, {pname: int(pspec["max"]) + 1}, width=8, height=8)


def test_clean_range_error_is_a_click_exception():
    # The CLI converts the renderer error into the reference's exit-1
    # diagnostic, not a traceback and not a usage exit code.
    assert issubclass(ParameterRangeError, ValueError)
    with CliRunner().isolated_filesystem():
        result = CliRunner().invoke(
            cli.main, ["generate", "synth/curl", "--width", "8", "--height", "8", "--seed", "5000"]
        )
    assert result.exit_code == 1
    assert not isinstance(result.exception, SystemExit) or result.exception.code == 1
