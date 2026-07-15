"""Surface — an RGBA float32 pixel buffer, top-down row order.

Faithful port of noisemaker-cpu `src/runtime/surface.js`. Conversion to/from
8-bit RGBA is a naive ``/255`` linear scale (no sRGB curve). ``to_rgba8`` clamps
to ``[0, 1]``, maps non-finite values to zero, and rounds to straight 8-bit —
using ``floor(x*255 + 0.5)`` to match JS ``Math.round`` (ties toward +inf), NOT
Python's banker's ``round``.
"""

from __future__ import annotations

import numpy as np


def _assert_dim(value: int, name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


class Surface:
    __slots__ = ("width", "height", "data", "filter")

    def __init__(self, width: int, height: int, data: np.ndarray | None = None):
        _assert_dim(width, "width")
        _assert_dim(height, "height")
        length = width * height * 4
        if data is None:
            data = np.zeros(length, dtype=np.float32)
        else:
            data = np.asarray(data, dtype=np.float32)
            if data.ndim != 1 or data.shape[0] != length:
                raise TypeError(f"data must be a float32 array of length {length}")
        self.width = width
        self.height = height
        self.data = data
        # "nearest" (canonical internal default) or "linear" (external images).
        self.filter = "nearest"

    @staticmethod
    def from_rgba8(width: int, height: int, byts) -> "Surface":
        _assert_dim(width, "width")
        _assert_dim(height, "height")
        length = width * height * 4
        arr = np.frombuffer(bytes(byts), dtype=np.uint8)
        if arr.shape[0] != length:
            raise TypeError(f"bytes must have length {length}")
        # Match JS: data[i] = fround(bytes[i] * (1/255)) — float64 product, then f32.
        data = (arr.astype(np.float64) * (1.0 / 255.0)).astype(np.float32)
        return Surface(width, height, data)

    def clone(self) -> "Surface":
        s = Surface(self.width, self.height, self.data.copy())
        s.filter = self.filter
        return s

    def clear(self, color=(0.0, 0.0, 0.0, 0.0)) -> "Surface":
        if len(color) != 4:
            raise TypeError("color must contain four components")
        rgba = np.asarray(color, dtype=np.float32)
        self.data.reshape(-1, 4)[:] = rgba
        return self

    def to_rgba8(self) -> bytes:
        d = self.data
        v = np.where(np.isfinite(d), d, 0.0)
        v = np.clip(v, 0.0, 1.0)
        out = np.floor(v * 255.0 + 0.5).astype(np.uint8)
        return out.tobytes()
