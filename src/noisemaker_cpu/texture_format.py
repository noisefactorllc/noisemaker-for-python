"""Per-pass texture-format quantization.

Faithful port of noisemaker-cpu ``src/runtime/texture-format.js``. After each
render pass, the reference engine quantizes the destination surface to that
attachment's declared texture format (``rgba16f`` by default, ``rgba8unorm`` for
some intermediates). Skipping this leaves Python at full float32 and diverges
from the GPU pipeline wherever an intermediate is stored at reduced precision.

- ``rgba16f`` / ``rgba16float``: round-toward-zero truncation to IEEE 754 half.
- ``rgba8`` / ``rgba8unorm``: clamp to [0,1] then round to 8-bit and back.
"""

from __future__ import annotations

import numpy as np

F32 = np.float32


def _float16_truncate(vals: np.ndarray) -> np.ndarray:
    """Match the reference WebGL rgba16f attachment conversion (round toward
    zero — truncate the low mantissa bits, do NOT round to nearest)."""
    v = np.ascontiguousarray(vals, dtype=F32)
    bits = v.view(np.uint32)
    sign = ((bits >> np.uint32(16)) & np.uint32(0x8000)).astype(np.uint32)
    src_exp = ((bits >> np.uint32(23)) & np.uint32(0xFF)).astype(np.int32)
    frac = (bits & np.uint32(0x7FFFFF)).astype(np.uint32)
    exp = src_exp - 127 + 15

    half = np.empty(v.shape, dtype=np.uint32)
    special = src_exp == 0xFF          # inf / nan
    over = (~special) & (exp >= 0x1F)  # overflow -> largest finite half
    under = (~special) & (exp <= 0)    # subnormal / underflow
    normal = (~special) & (~over) & (~under)

    half[normal] = sign[normal] | (exp[normal].astype(np.uint32) << np.uint32(10)) | (frac[normal] >> np.uint32(13))
    half[over] = sign[over] | np.uint32(0x7BFF)

    # inf (frac==0) preserves sign+inf; nan -> canonical nan bits
    half[special] = np.where(frac[special] == 0, sign[special] | np.uint32(0x7C00), np.uint32(0x7E00))

    if np.any(under):
        e = exp[under]
        s = sign[under]
        f = frac[under]
        # exp < -10 flushes to signed zero; else denormalize the mantissa.
        shift = (1 - e).astype(np.int64)
        mant = (f | np.uint32(0x800000)).astype(np.uint64)
        safe = shift < 32
        shifted = np.zeros(e.shape, dtype=np.uint32)
        sh = np.minimum(shift, 63)
        shifted_all = ((mant >> sh.astype(np.uint64)) >> np.uint64(13)).astype(np.uint32)
        shifted = np.where(safe & (e >= -10), shifted_all, np.uint32(0))
        half[under] = s | shifted

    decoded = half.astype(np.uint16).view(np.float16).astype(F32)
    return decoded.reshape(v.shape)


def quantize_texture(surface, fmt: str = "rgba16f"):
    """Quantize ``surface.data`` in place to ``fmt`` and return the surface."""
    if fmt in ("rgba16f", "rgba16float"):
        surface.data = _float16_truncate(surface.data)
    elif fmt in ("rgba8", "rgba8unorm"):
        d = np.clip(surface.data, 0.0, 1.0)
        surface.data = (np.round(d * 255.0) / 255.0).astype(F32)
    return surface
