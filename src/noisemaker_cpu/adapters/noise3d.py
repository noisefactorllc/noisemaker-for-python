"""Canonical JavaScript-number semantics required by synth3d/noise3d."""

from __future__ import annotations

from . import register


@register("synth3d/noise3d:precompute")
def noise3d_factory(runtime, kernel):
    runtime.js_uvec_numbers = True
    return kernel
