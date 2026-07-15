import numpy as np
import pytest

from noisemaker_cpu.surface import Surface


def test_from_rgba8_roundtrip_exact():
    b = bytes([10, 20, 30, 40, 200, 150, 100, 255, 0, 0, 0, 0, 255, 255, 255, 255])
    s = Surface.from_rgba8(2, 2, b)
    assert s.to_rgba8() == b


def test_from_rgba8_scales_like_fround():
    s = Surface.from_rgba8(1, 1, bytes([200, 0, 0, 0]))
    assert float(s.data[0]) == float(np.float32(200 / 255))


def test_to_rgba8_clamps_and_zeroes_nonfinite():
    # Non-finite is checked FIRST in JS byteFromFloat, so inf -> 0 (not clamp-to-255).
    s = Surface(1, 1, np.array([1.5, -0.2, float("nan"), float("inf")], dtype=np.float32))
    assert s.to_rgba8() == bytes([255, 0, 0, 0])


def test_to_rgba8_rounds_ties_toward_positive():
    # 0.5/255 boundary: floor(x*255+0.5). 100.5/255 -> round to 101 (ties up), not banker's 100.
    v = np.float32(100.5 / 255.0)
    s = Surface(1, 1, np.array([v, 0, 0, 0], dtype=np.float32))
    assert s.to_rgba8()[0] == 101


def test_rejects_bad_dimensions():
    with pytest.raises(ValueError):
        Surface(0, 4)
    with pytest.raises(ValueError):
        Surface(4, -1)
