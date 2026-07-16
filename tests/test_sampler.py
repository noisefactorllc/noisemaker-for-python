import numpy as np

from noisemaker_cpu.sampler import (
    sample_bilinear,
    sample_nearest,
    sample_nearest_bottom_left,
)
from noisemaker_cpu.surface import Surface

# Distinct, dyadic (exactly float32-representable) colors per texel, so
# averaging/blending in the bilinear tests is exact rather than approximate.
# Named by their *visual* position once GLSL bottom-left addressing is
# applied; in raw top-down storage, row 0 holds TOP_LEFT/TOP_RIGHT and row 1
# holds BOTTOM_LEFT/BOTTOM_RIGHT.
TOP_LEFT = np.array([0.0, 0.25, 0.5, 1.0], dtype=np.float32)
TOP_RIGHT = np.array([0.25, 0.5, 1.0, 0.0], dtype=np.float32)
BOTTOM_LEFT = np.array([0.5, 1.0, 0.0, 0.25], dtype=np.float32)
BOTTOM_RIGHT = np.array([1.0, 0.0, 0.25, 0.5], dtype=np.float32)


def make_surface() -> Surface:
    # Flat, top-down: row 0 = [TOP_LEFT, TOP_RIGHT], row 1 = [BOTTOM_LEFT, BOTTOM_RIGHT].
    data = np.concatenate([TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT]).astype(np.float32)
    return Surface(2, 2, data)


def test_sample_nearest_addresses_storage_top_down_with_no_flip():
    # Plain sample_nearest addresses storage rows directly: v near 0 hits
    # storage row 0 (TOP_*), v near 1 hits storage row 1 (BOTTOM_*).
    s = make_surface()
    np.testing.assert_array_equal(sample_nearest(s, 0.25, 0.25), TOP_LEFT)
    np.testing.assert_array_equal(sample_nearest(s, 0.75, 0.25), TOP_RIGHT)
    np.testing.assert_array_equal(sample_nearest(s, 0.25, 0.75), BOTTOM_LEFT)
    np.testing.assert_array_equal(sample_nearest(s, 0.75, 0.75), BOTTOM_RIGHT)


def test_sample_nearest_bottom_left_flips_integer_texel_row():
    # GLSL v=0 is the bottom of the image. Storage is top-down, so v near 0
    # must land on the LAST storage row (height - 1, i.e. BOTTOM_*), not the
    # first — the defining behavior this sampler exists for.
    s = make_surface()
    np.testing.assert_array_equal(sample_nearest_bottom_left(s, 0.25, 0.25), BOTTOM_LEFT)
    np.testing.assert_array_equal(sample_nearest_bottom_left(s, 0.75, 0.25), BOTTOM_RIGHT)
    np.testing.assert_array_equal(sample_nearest_bottom_left(s, 0.25, 0.75), TOP_LEFT)
    np.testing.assert_array_equal(sample_nearest_bottom_left(s, 0.75, 0.75), TOP_RIGHT)


def test_sample_nearest_bottom_left_clamps_without_wraparound():
    s = make_surface()
    # Deep out-of-range coordinates in every direction must still land on a
    # real edge texel (clamp), never wrap around to the opposite side.
    np.testing.assert_array_equal(sample_nearest_bottom_left(s, -1.0, -1.0), BOTTOM_LEFT)
    np.testing.assert_array_equal(sample_nearest_bottom_left(s, 2.0, -1.0), BOTTOM_RIGHT)
    np.testing.assert_array_equal(sample_nearest_bottom_left(s, -1.0, 2.0), TOP_LEFT)
    np.testing.assert_array_equal(sample_nearest_bottom_left(s, 2.0, 2.0), TOP_RIGHT)
    np.testing.assert_array_equal(sample_nearest_bottom_left(s, -100.0, -100.0), BOTTOM_LEFT)
    np.testing.assert_array_equal(sample_nearest_bottom_left(s, 100.0, 100.0), TOP_RIGHT)


def test_sample_nearest_clamps_without_wraparound():
    s = make_surface()
    np.testing.assert_array_equal(sample_nearest(s, -1.0, -1.0), TOP_LEFT)
    np.testing.assert_array_equal(sample_nearest(s, 2.0, 2.0), BOTTOM_RIGHT)


def test_sample_bilinear_center_averages_all_four_texels():
    # sample_bilinear never flips rows, so uv=(0.5, 0.5) sits exactly at the
    # shared corner of all four texels regardless of naming/orientation.
    s = make_surface()
    expected = (
        TOP_LEFT.astype(np.float64)
        + TOP_RIGHT.astype(np.float64)
        + BOTTOM_LEFT.astype(np.float64)
        + BOTTOM_RIGHT.astype(np.float64)
    ) / 4.0

    result = sample_bilinear(s, 0.5, 0.5)

    assert result.dtype == np.float32
    assert result.shape == (4,)
    np.testing.assert_allclose(result, expected.astype(np.float32), rtol=0, atol=1e-6)


def test_sample_bilinear_exact_texel_center_returns_that_texel():
    # (0.25, 0.25) etc. are the exact half-texel centers of each storage texel;
    # bilinear uses GL bottom-left row addressing (flips the integer texel row),
    # so v maps top<->bottom, each landing on its texel with zero blending.
    s = make_surface()
    np.testing.assert_array_equal(sample_bilinear(s, 0.25, 0.25), BOTTOM_LEFT)
    np.testing.assert_array_equal(sample_bilinear(s, 0.75, 0.25), BOTTOM_RIGHT)
    np.testing.assert_array_equal(sample_bilinear(s, 0.25, 0.75), TOP_LEFT)
    np.testing.assert_array_equal(sample_bilinear(s, 0.75, 0.75), TOP_RIGHT)


def test_returns_fresh_array_not_a_view_into_surface_data():
    s = make_surface()
    original = s.data.copy()
    for fn in (sample_nearest, sample_nearest_bottom_left, sample_bilinear):
        out = fn(s, 0.25, 0.25)
        out[:] = -1.0
        np.testing.assert_array_equal(s.data, original)


def test_return_dtype_and_shape():
    s = make_surface()
    for fn in (sample_nearest, sample_nearest_bottom_left, sample_bilinear):
        out = fn(s, 0.3, 0.6)
        assert isinstance(out, np.ndarray)
        assert out.dtype == np.float32
        assert out.shape == (4,)
