import os

import click
import pytest
from click.testing import CliRunner

from noisemaker_cpu import cli
from noisemaker_cpu.png import decode_png
from noisemaker_cpu.renderer import _meta


def run(*args):
    return CliRunner().invoke(cli.main, list(args))


def _png(path):
    with open(path, "rb") as handle:
        return decode_png(handle.read())


def test_help_and_version():
    assert run("--help").exit_code == 0
    version = run("--version")
    assert version.exit_code == 0
    assert "noisemaker-py" in version.output
    for cmd in ("generate", "apply", "animate"):
        assert run(cmd, "--help").exit_code == 0


def test_parse_params_ok_and_error():
    assert cli._parse_params(("a=1", "b=x=y")) == {"a": "1", "b": "x=y"}  # value keeps trailing '='
    with pytest.raises(click.BadParameter):
        cli._parse_params(("nokey",))


def test_resolve_effect_unknown():
    with pytest.raises(click.BadParameter):
        cli._resolve_effect("no/such/effect")


def test_resolve_random_is_partitioned_by_kind():
    effects = _meta()["effects"]
    for _ in range(25):
        assert effects[cli._resolve_effect("random", "generator")]["kind"] == "generator"
        assert effects[cli._resolve_effect("random", "filter")]["kind"] == "filter"


def test_generate_writes_a_png():
    with CliRunner().isolated_filesystem():
        result = run("generate", "synth/curl", "--width", "8", "--height", "8", "--seed", "1", "--filename", "out.png")
        assert result.exit_code == 0, result.output
        surface = _png("out.png")
        assert (surface.width, surface.height) == (8, 8)


def test_generate_creates_missing_output_dirs():
    with CliRunner().isolated_filesystem():
        result = run("generate", "synth/solid", "--width", "4", "--height", "4", "--filename", "a/b/out.png")
        assert result.exit_code == 0, result.output
        assert os.path.exists("a/b/out.png")


def test_generate_random_picks_a_generator():
    with CliRunner().isolated_filesystem():
        result = run("generate", "random", "--width", "8", "--height", "8", "--seed", "1", "--filename", "r.png")
        assert result.exit_code == 0, result.output
        chosen = result.output.splitlines()[0]  # first echo line is the effect id
        assert _meta()["effects"][chosen]["kind"] == "generator"


def test_generate_param_vec_and_color():
    with CliRunner().isolated_filesystem():
        result = run(
            "generate", "synth/solid", "--param", "color=#f30", "--width", "4", "--height", "4", "--filename", "c.png"
        )
        assert result.exit_code == 0, result.output
        px = _png("c.png").to_rgba8()[:3]
        assert list(px) == [0xFF, 0x33, 0x00]


def test_apply_renders_at_input_dimensions():
    with CliRunner().isolated_filesystem():
        run("generate", "synth/curl", "--width", "12", "--height", "10", "--seed", "1", "--filename", "in.png")
        result = run("apply", "filter/invert", "in.png", "--filename", "out.png")
        assert result.exit_code == 0, result.output
        surface = _png("out.png")
        assert (surface.width, surface.height) == (12, 10)


def test_animate_writes_frames():
    with CliRunner().isolated_filesystem():
        result = run(
            "animate",
            "synth/curl",
            "--width",
            "8",
            "--height",
            "8",
            "--frame-count",
            "3",
            "--seed",
            "1",
            "--save-frames",
            "frames",
            "--filename",
            "a.mp4",
        )
        assert result.exit_code == 0, result.output
        assert os.path.exists("frames/frame_0000.png")
        assert os.path.exists("frames/frame_0002.png")


def test_animate_without_ffmpeg_gives_clean_error(monkeypatch):
    monkeypatch.setattr(cli.shutil, "which", lambda _name: None)
    with CliRunner().isolated_filesystem():
        result = run("animate", "synth/curl", "--width", "8", "--height", "8", "--frame-count", "2", "--seed", "1")
        assert result.exit_code != 0
        assert "ffmpeg not found" in result.output


def test_error_paths():
    assert "Unknown effect" in run("generate", "no/such").output
    assert run("generate", "synth/curl", "--param", "nokey").exit_code != 0
    assert run("apply", "filter/invert", "does-not-exist.png").exit_code != 0
    assert run("generate", "synth/curl", "--width", "0").exit_code != 0  # POSITIVE IntRange
