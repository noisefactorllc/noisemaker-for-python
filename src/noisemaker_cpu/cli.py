"""Command-line interface — P0 subset (`effect` subcommand)."""

from __future__ import annotations

import argparse
import sys

from .png import decode_png, encode_png
from .renderer import render_effect


def _parse_param(kv: str):
    key, _, value = kv.partition("=")
    return key, value


def _cmd_effect(args) -> int:
    params = dict(_parse_param(p) for p in (args.param or []))
    inputs = {}
    if args.input:
        with open(args.input, "rb") as f:
            inputs["inputTex"] = decode_png(f.read())
    surface = render_effect(
        args.effect,
        params=params,
        inputs=inputs,
        width=args.width,
        height=args.height,
        seed=args.seed,
        time=args.time,
    )
    with open(args.output, "wb") as f:
        f.write(encode_png(surface))
    print(f"Rendered {args.width}x{args.height} -> {args.output}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="noisemaker-cpu")
    sub = parser.add_subparsers(dest="command", required=True)

    eff = sub.add_parser("effect", help="render a single catalog effect")
    eff.add_argument("effect")
    eff.add_argument("--param", action="append", default=[], help="name=value (repeatable)")
    eff.add_argument("--input", help="input PNG (bound as inputTex)")
    eff.add_argument("--output", default="art.png")
    eff.add_argument("--width", type=int, default=512)
    eff.add_argument("--height", type=int, default=512)
    eff.add_argument("--seed", type=int, default=1)
    eff.add_argument("--time", type=float, default=0.0)
    eff.set_defaults(func=_cmd_effect)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
