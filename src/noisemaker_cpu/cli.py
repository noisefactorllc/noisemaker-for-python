"""Command-line interface, modeled after the noisemaker CLI
(noisemaker/noisemaker/scripts/noisemaker.py and its js/ equivalent): a click
group with `generate`, `apply`, and `animate`, sharing its option conventions
(--width/--height/--time/--seed/--filename, -h/--help). Where noisemaker renders
a named preset, this renders a catalog effect by id (e.g. `synth/curl`,
`filter/chrome`); `random` picks one at random. As in noisemaker, `generate`
takes no input and `apply` takes the input image as a positional argument, and
`random` is partitioned by kind (generators for generate/animate, filters for
apply) and excludes iterated or external-texture effects, which would be
unexpectedly expensive or lack a required input.
"""

from __future__ import annotations

import os
import random
import shutil
import subprocess
import sys
import tempfile

import click

from .png import decode_png, encode_png
from .renderer import _meta, render_dsl, render_effect

MAX_SEED_VALUE = 2**32 - 1

# Version string - keep in sync with pyproject.toml
__version__ = "0.0.0"

CLICK_CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"], "max_content_width": 160}

# Positive-only dimension/count option type.
POSITIVE = click.IntRange(min=1)


def _resolve_effect(effect: str, kind: str | None = None) -> str:
    """Resolve an EFFECT argument to a catalog id. `random` picks from effects of
    the given `kind` ("generator"/"filter") that are safe without extra inputs;
    an explicit id is used as-is."""
    effects = _meta()["effects"]
    if effect == "random":
        pool = [
            effect_id
            for effect_id, definition in effects.items()
            if (kind is None or definition.get("kind") == kind)
            and definition.get("domain", "image") == "image"
            and not definition.get("iterated")
            and not definition.get("externalTexture")
        ]
        if not pool:
            raise click.ClickException(f"No {kind or 'catalog'} effects are available for random selection")
        return random.choice(pool)
    if effect not in effects:
        raise click.BadParameter(
            f"Unknown effect: {effect}. Pass 'random' or a catalog id like 'synth/curl'.",
            param_hint="EFFECT",
        )
    if kind is not None and effects[effect].get("domain", "image") != "image":
        raise click.BadParameter(
            f"{effect} requires a typed volume chain; use the DSL run command.",
            param_hint="EFFECT",
        )
    return effect


def _prologue(effect: str, seed: int | None, kind: str | None) -> tuple[str, int]:
    """Shared command entry: resolve the effect, default the seed, echo the id."""
    effect = _resolve_effect(effect, kind)
    if seed is None:
        seed = random.randint(1, MAX_SEED_VALUE)
    click.echo(effect)
    return effect, seed


def _parse_params(pairs: tuple[str, ...]) -> dict:
    params = {}
    for kv in pairs:
        key, sep, value = kv.partition("=")
        if not sep:
            raise click.BadParameter(f"Expected NAME=VALUE, received {kv!r}", param_hint="--param")
        params[key] = value
    return params


def _bind_input(effect_id: str, surface) -> dict:
    inputs = {"inputTex": surface}
    # An effect that reads a host texture (filter/text, synth/media) binds the
    # same image, mirroring the noisemaker/js CLI's input (imageTex + textTex).
    external = _meta()["effects"][effect_id].get("externalTexture")
    if external:
        inputs[external] = surface
    return inputs


def _write_png(surface, filename: str) -> None:
    parent = os.path.dirname(filename)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(filename, "wb") as handle:
        handle.write(encode_png(surface))


def _load_png(path: str):
    with open(path, "rb") as handle:
        return decode_png(handle.read())


def _load_external_textures(input_filename: str | None, textures: tuple[str, ...]) -> dict:
    """Build the DSL's external-texture map. --input binds one PNG as both
    imageTex and textTex (mirroring the JS CLI); --texture NAME=FILE binds a
    named sampler (repeatable)."""
    external = {}
    if input_filename:
        surface = _load_png(input_filename)
        external["imageTex"] = surface
        external["textTex"] = surface
    for pair in textures:
        name, sep, path = pair.partition("=")
        if not sep or not name or not path:
            raise click.BadParameter(f"Expected NAME=FILE, received {pair!r}", param_hint="--texture")
        if not os.path.isfile(path):
            raise click.BadParameter(f"No such texture file: {path}", param_hint="--texture")
        external[name] = _load_png(path)
    return external


@click.group(
    help="""
        Noisemaker for Python — render the Noisemaker shader catalog on the CPU.

    https://github.com/noisefactorllc/noisemaker-for-python
        """,
    context_settings=CLICK_CONTEXT_SETTINGS,
)
@click.version_option(version=__version__, prog_name="noisemaker-py")
def main():
    pass


@main.command(help="Render a catalog effect to a .png")
@click.option("--width", type=POSITIVE, default=1024, help="Output width, in pixels")
@click.option("--height", type=POSITIVE, default=1024, help="Output height, in pixels")
@click.option("--time", "time_value", type=float, default=0.0, help="Time value for the Z axis / animation phase")
@click.option("--seed", type=int, default=None, help="Random seed. Might not affect all effects.")
@click.option("--filename", type=click.Path(dir_okay=False), default="art.png", help="Image output filename (.png)")
@click.option("--param", "params", multiple=True, metavar="NAME=VALUE", help="Effect parameter (repeatable)")
@click.argument("effect")
def generate(width, height, time_value, seed, filename, params, effect):
    effect, seed = _prologue(effect, seed, "generator")
    surface = render_effect(effect, _parse_params(params), width=width, height=height, seed=seed, time=time_value)
    _write_png(surface, filename)
    click.echo(f"Rendered {width}x{height} -> {filename}")


@main.command(help="Apply an effect to a .png image")
@click.option("--time", "time_value", type=float, default=0.0, help="Time value for the Z axis / animation phase")
@click.option("--seed", type=int, default=None, help="Random seed. Might not affect all effects.")
@click.option("--filename", type=click.Path(dir_okay=False), default="mangled.png", help="Image output filename (.png)")
@click.option("--param", "params", multiple=True, metavar="NAME=VALUE", help="Effect parameter (repeatable)")
@click.argument("effect")
@click.argument("input_filename", type=click.Path(exists=True, dir_okay=False))
def apply(time_value, seed, filename, params, effect, input_filename):
    effect, seed = _prologue(effect, seed, "filter")
    source = _load_png(input_filename)
    surface = render_effect(
        effect,
        _parse_params(params),
        _bind_input(effect, source),
        width=source.width,
        height=source.height,
        seed=seed,
        time=time_value,
    )
    _write_png(surface, filename)
    click.echo(f"Rendered {source.width}x{source.height} -> {filename}")


@main.command(help="Render an effect over time to an animation (.mp4)")
@click.option("--width", type=POSITIVE, default=512, help="Output width, in pixels")
@click.option("--height", type=POSITIVE, default=512, help="Output height, in pixels")
@click.option("--seed", type=int, default=None, help="Random seed. Might not affect all effects.")
@click.option(
    "--filename", type=click.Path(dir_okay=False), default="animation.mp4", help="Animation output filename (.mp4)"
)
@click.option("--frame-count", type=POSITIVE, default=50, help="How many frames total")
@click.option("--fps", type=POSITIVE, default=30, help="Frames per second for the encoded video")
@click.option("--speed", type=float, default=1.0, help="Time-sweep multiplier (loops of the [0,1) time phase)")
@click.option(
    "--save-frames", type=click.Path(file_okay=False), default=None, help="Directory to also write the PNG frames into"
)
@click.option("--param", "params", multiple=True, metavar="NAME=VALUE", help="Effect parameter (repeatable)")
@click.argument("effect")
def animate(width, height, seed, filename, frame_count, fps, speed, save_frames, params, effect):
    effect, seed = _prologue(effect, seed, "generator")
    parsed = _parse_params(params)

    frames_dir = save_frames or tempfile.mkdtemp(prefix="noisemaker-py-")
    os.makedirs(frames_dir, exist_ok=True)
    try:
        with click.progressbar(range(frame_count), label="Rendering frames") as frames:
            for i in frames:
                time_value = (i / frame_count) * speed  # sweep the [0,1) phase, `speed` loops
                surface = render_effect(effect, parsed, width=width, height=height, seed=seed, time=time_value)
                _write_png(surface, os.path.join(frames_dir, f"frame_{i:04d}.png"))

        if shutil.which("ffmpeg") is None:
            if save_frames:
                click.echo(f"ffmpeg not found; wrote {frame_count} frames to {frames_dir} (no video).")
                return
            raise click.ClickException(
                "ffmpeg not found; install it, or pass --save-frames DIR to keep the PNG frames."
            )
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-framerate",
                    str(fps),
                    "-i",
                    os.path.join(frames_dir, "frame_%04d.png"),
                    "-vf",
                    "pad=ceil(iw/2)*2:ceil(ih/2)*2",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    filename,
                ],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as exc:
            tail = (exc.stderr or b"").decode(errors="replace").strip().splitlines()[-5:]
            raise click.ClickException("ffmpeg failed:\n" + "\n".join(tail)) from exc
        click.echo(f"Rendered {frame_count} frames ({width}x{height}) -> {filename}")
    finally:
        if not save_frames:
            shutil.rmtree(frames_dir, ignore_errors=True)


@main.command(help="Render a Polymorphic DSL program read from STDIN")
@click.option("--width", type=POSITIVE, default=512, help="Output width, in pixels")
@click.option("--height", type=POSITIVE, default=512, help="Output height, in pixels")
@click.option("--time", "time_value", type=float, default=0.0, help="Time value for the Z axis / animation phase")
@click.option("--seed", type=int, default=1, help="Deterministic render seed threaded into effect seed params")
@click.option("--filename", type=click.Path(dir_okay=False), default="art.png", help="Image output filename (.png)")
@click.option(
    "--input",
    "input_filename",
    type=click.Path(exists=True, dir_okay=False),
    help="PNG bound as imageTex and textTex",
)
@click.option("--texture", "textures", multiple=True, metavar="NAME=FILE", help="External PNG texture (repeatable)")
def run(width, height, time_value, seed, filename, input_filename, textures):
    source = sys.stdin.read()
    external = _load_external_textures(input_filename, textures)
    surface = render_dsl(source, width=width, height=height, seed=seed, time=time_value, external_textures=external)
    _write_png(surface, filename)
    click.echo(f"Rendered {surface.width}x{surface.height} -> {filename}")


if __name__ == "__main__":
    sys.exit(main())
