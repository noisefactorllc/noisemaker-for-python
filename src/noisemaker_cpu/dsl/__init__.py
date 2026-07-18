"""Polymorphic DSL front-end (tokenizer + parser + compiler), ported from
noisemaker-cpu src/dsl/. compile_dsl() lowers a program to a render plan that
noisemaker_cpu.renderer.render_dsl evaluates against the effect catalog."""

from __future__ import annotations

from .compiler import compile_dsl
from .error import DslError
from .parser import parse_dsl
from .tokenizer import tokenize_dsl

__all__ = ["DslError", "compile_dsl", "parse_dsl", "tokenize_dsl"]
