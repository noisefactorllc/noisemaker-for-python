"""Command-line interface, modeled after the noisemaker CLI
(noisemaker/noisemaker/scripts/noisemaker.py and its js/ equivalent): a click
group with `generate`, `apply`, and `animate`, sharing its option conventions
(--width/--height/--time/--seed/--filename, -h/--help). Where noisemaker renders
a named preset, this renders a catalog effect by id (e.g. `synth/curl`,
`filter/chrome`); `random` picks one at random. As in noisemaker, `generate`
takes no input and `apply` takes the input image as a positional argument.
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
from .renderer import _meta, render_effect

MAX_SEED_VALUE = 2**32 - 1

# Version string - keep in sync with pyproject.toml
__version__ = "0.0.0"

CLICK_CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"], "max_content_width": 160}


def _effect_ids() -> list[str]:
    return sorted(_meta()["effects"])


def _resolve_effect(effect: str) -> str:
    if effect == "random":
        return random.choice(_effect_ids())
    if effect not in _meta()["effects"]:
        raise click.BadParameter(
            f"Unknown effect: {effect}. Pass 'random' or a catalog id like 'synth/curl'.",
            param_hint="EFFECT",
        )
    return effect


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
@click.option("--width", type=int, default=1024, help="Output width, in pixels")
@click.option("--height", type=int, default=1024, help="Output height, in pixels")
@click.option("--time", "time_value", type=float, default=0.0, help="Time value for the Z axis / animation phase")
@click.option("--seed", type=int, default=None, help="Random seed. Might not affect all effects.")
@click.option("--filename", type=click.Path(dir_okay=False), default="art.png", help="Image output filename (.png)")
@click.option("--param", "params", multiple=True, metavar="NAME=VALUE", help="Effect parameter (repeatable)")
@click.argument("effect")
def generate(width, height, time_value, seed, filename, params, effect):
    effect = _resolve_effect(effect)
    if seed is None:
        seed = random.randint(1, MAX_SEED_VALUE)
    click.echo(effect)
    surface = render_effect(effect, _parse_params(params), width=width, height=height, seed=seed, time=time_value)
    with open(filename, "wb") as handle:
        handle.write(encode_png(surface))
    click.echo(f"Rendered {width}x{height} -> {filename}")


@main.command(help="Apply an effect to a .png image")
@click.option("--time", "time_value", type=float, default=0.0, help="Time value for the Z axis / animation phase")
@click.option("--seed", type=int, default=None, help="Random seed. Might not affect all effects.")
@click.option("--filename", type=click.Path(dir_okay=False), default="mangled.png", help="Image output filename (.png)")
@click.option("--param", "params", multiple=True, metavar="NAME=VALUE", help="Effect parameter (repeatable)")
@click.argument("effect")
@click.argument("input_filename", type=click.Path(exists=True, dir_okay=False))
def apply(time_value, seed, filename, params, effect, input_filename):
    effect = _resolve_effect(effect)
    if seed is None:
        seed = random.randint(1, MAX_SEED_VALUE)
    click.echo(effect)
    with open(input_filename, "rb") as handle:
        source = decode_png(handle.read())
    surface = render_effect(
        effect,
        _parse_params(params),
        _bind_input(effect, source),
        width=source.width,
        height=source.height,
        seed=seed,
        time=time_value,
    )
    with open(filename, "wb") as handle:
        handle.write(encode_png(surface))
    click.echo(f"Rendered {source.width}x{source.height} -> {filename}")


@main.command(help="Render an effect over time to an animation (.mp4)")
@click.option("--width", type=int, default=512, help="Output width, in pixels")
@click.option("--height", type=int, default=512, help="Output height, in pixels")
@click.option("--seed", type=int, default=None, help="Random seed. Might not affect all effects.")
@click.option(
    "--filename", type=click.Path(dir_okay=False), default="animation.mp4", help="Animation output filename (.mp4)"
)
@click.option("--frame-count", type=int, default=50, help="How many frames total")
@click.option("--fps", type=int, default=30, help="Frames per second for the encoded video")
@click.option("--speed", type=float, default=1.0, help="Time-sweep multiplier (loops of the [0,1) time phase)")
@click.option(
    "--save-frames", type=click.Path(file_okay=False), default=None, help="Directory to also write the PNG frames into"
)
@click.option("--param", "params", multiple=True, metavar="NAME=VALUE", help="Effect parameter (repeatable)")
@click.argument("effect")
def animate(width, height, seed, filename, frame_count, fps, speed, save_frames, params, effect):
    effect = _resolve_effect(effect)
    if seed is None:
        seed = random.randint(1, MAX_SEED_VALUE)
    click.echo(effect)
    parsed = _parse_params(params)

    frames_dir = save_frames or tempfile.mkdtemp(prefix="noisemaker-py-")
    os.makedirs(frames_dir, exist_ok=True)
    with click.progressbar(range(frame_count), label="Rendering frames") as frames:
        for i in frames:
            time_value = (i / frame_count) * speed  # sweep the [0,1) phase, `speed` loops
            surface = render_effect(effect, parsed, width=width, height=height, seed=seed, time=time_value)
            with open(os.path.join(frames_dir, f"frame_{i:04d}.png"), "wb") as handle:
                handle.write(encode_png(surface))

    if shutil.which("ffmpeg") is None:
        if save_frames:
            click.echo(f"ffmpeg not found; wrote {frame_count} frames to {frames_dir} (no video).")
            return
        raise click.ClickException("ffmpeg not found; install it, or pass --save-frames DIR to keep the PNG frames.")
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
    click.echo(f"Rendered {frame_count} frames ({width}x{height}) -> {filename}")


if __name__ == "__main__":
    sys.exit(main())
