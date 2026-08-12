#!/usr/bin/env python3
"""Render this export's program on the CPU and write a PNG.

Puts the vendored port in `engine/` on the import path and calls it directly,
so nothing has to be installed: this file plus `engine/` is the whole program.
`noisemaker_cpu.renderer.render_dsl` compiles the DSL and evaluates it pixel by
pixel; `noisemaker_cpu.png.encode_png` turns the resulting surface into bytes.
"""

import argparse
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "engine"))

try:
    from noisemaker_cpu.png import encode_png
    from noisemaker_cpu.renderer import render_dsl
except ModuleNotFoundError as missing:  # pragma: no cover - environment guard
    if missing.name != "numpy":
        raise
    raise SystemExit(
        "This export needs numpy to render. Install it with:\n"
        "    python3 -m pip install 'numpy>=1.26'"
    ) from missing


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Render a Noisemaker DSL program on the CPU.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("program", nargs="?", default="program.dsl", help="DSL program to render")
    parser.add_argument("--width", type=int, default=512, help="output width in pixels")
    parser.add_argument("--height", type=int, default=512, help="output height in pixels")
    parser.add_argument("--seed", type=int, default=1, help="deterministic seed")
    parser.add_argument("--time", type=float, default=0.0, help="normalized time")
    parser.add_argument("--output", default="art.png", help="PNG to write")
    args = parser.parse_args(argv)

    try:
        source = pathlib.Path(args.program).read_text(encoding="utf-8")
    except OSError as err:
        # The likeliest mistake by far, since every documented invocation names
        # the program as a bare relative path. One line beats a traceback.
        raise SystemExit(f"cannot read {args.program}: {err.strerror or err}") from err
    surface = render_dsl(
        source,
        width=args.width,
        height=args.height,
        seed=args.seed,
        time=args.time,
    )
    pathlib.Path(args.output).write_bytes(encode_png(surface))
    print(f"Rendered {surface.width}x{surface.height} -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
