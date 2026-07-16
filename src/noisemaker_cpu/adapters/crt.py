"""filter/crt:crt adapter — port of noisemaker-cpu src/effects/adapters/crt.js.

The CRT adapter runs the same transpiled kernel but replaces `sin` with a
range-reduced `metalSine`: reducing the phase to a single turn before Math.sin
avoids the large-argument precision loss that shifts scanline/phosphor phases.
"""

from __future__ import annotations

import math

import numpy as np

from . import register

F32 = np.float32
_TAU = float(F32(6.283185307179586))
_INV_TAU = float(F32(1.0 / 6.283185307179586))


def _metal_sine(value):
    turns = float(F32(value * _INV_TAU))
    phase = turns - math.floor(turns)
    return float(F32(math.sin(phase * _TAU)))


def _crt_sin(v):
    if np.isscalar(v) or getattr(v, "ndim", 1) == 0:
        return _metal_sine(float(v))
    return np.array([_metal_sine(float(x)) for x in np.asarray(v)], dtype=F32)


@register("filter/crt:crt")
def crt_factory(rt, base_kernel):
    def kernel(ctx, out):
        prev = rt.stdlib_override
        rt.stdlib_override = {**prev, "sin": _crt_sin}
        try:
            base_kernel(ctx, out)
        finally:
            rt.stdlib_override = prev
    kernel.uses_derivatives = getattr(base_kernel, "uses_derivatives", False)
    return kernel
