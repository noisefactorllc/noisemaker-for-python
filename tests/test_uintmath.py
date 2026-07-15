"""Golden-vector tests for `noisemaker_cpu.uintmath`.

Every expected literal below was captured by *executing* the real JS source
(`noisemaker-cpu/src/csl/glsl-runtime.js`, via `GlslCpuRuntime().stdlib` and
its named exports) with Node, not hand-derived — so a mismatch here means a
real fidelity bug, not a transcription error in the expected value. The
values from the task spec / `noisemaker-cpu/test/glsl-runtime.test.js` are
marked "(spec)"; the rest are additional coverage generated the same way.
"""

import math

from noisemaker_cpu.uintmath import (
    float_bits_to_uint,
    glsl_mod,
    hash_uint,
    hash_uint32,
    pack_half_2x16,
    pcg3d,
    u32,
    uadd,
    uand,
    uint_bits_to_float,
    umul,
    unpack_half_2x16,
    uor,
    ushl,
    ushr,
    usub,
    uxor,
)


# ---------------------------------------------------------------------------
# u32 (JS `value >>> 0`)
# ---------------------------------------------------------------------------

def test_u32_wraps_overflow_spec():
    assert u32(0xFFFFFFFF + 2) == 1  # (spec)


def test_u32_of_negative_one_is_max_uint32_spec():
    assert u32(-1) == 4294967295  # (spec)


def test_u32_zero():
    assert u32(0) == 0


def test_u32_wraps_exactly_two_pow_32_to_zero():
    assert u32(4294967296) == 0


def test_u32_truncates_floats_toward_zero():
    assert u32(3.9) == 3
    assert u32(-3.9) == 4294967293


def test_u32_nan_and_infinity_coerce_to_zero_like_js():
    # JS: `NaN >>> 0 === 0`, `Infinity >>> 0 === 0`, `-Infinity >>> 0 === 0`.
    assert u32(float("nan")) == 0
    assert u32(float("inf")) == 0
    assert u32(float("-inf")) == 0


# ---------------------------------------------------------------------------
# umul (JS `Math.imul(a, b) >>> 0`)
# ---------------------------------------------------------------------------

def test_umul_matches_math_imul_unsigned_spec():
    assert umul(0xFFFFFFFF, 374761393) == 3920205903  # (spec)


def test_umul_negative_operand_matches_unsigned_equivalent():
    # -1 and 0xffffffff are the same 32-bit bit pattern; Math.imul's ToInt32
    # coercion of the operand must not change the result.
    assert umul(-1, 374761393) == umul(0xFFFFFFFF, 374761393) == 3920205903


def test_umul_small_values_no_wraparound():
    assert umul(2, 3) == 6
    assert umul(-2, -3) == 6


def test_umul_both_max_uint32():
    assert umul(0xFFFFFFFF, 0xFFFFFFFF) == 1


def test_umul_power_of_two_overflow_wraps_to_zero():
    # 0x80000000 * 2 == 2**32, which wraps to 0 mod 2**32.
    assert umul(0x80000000, 2) == 0


# ---------------------------------------------------------------------------
# uadd / usub / ushl / ushr / uand / uor / uxor
# ---------------------------------------------------------------------------

def test_uadd_wraps():
    assert uadd(0xFFFFFFFF, 2) == 1


def test_usub_wraps_below_zero():
    assert usub(0, 1) == 4294967295


def test_ushl_basic_and_overflow_bit():
    assert ushl(1, 31) == 2147483648
    assert ushl(0xFF, 24) == 4278190080


def test_ushl_shift_count_masked_to_five_bits():
    # JS masks the shift count with `& 0x1F`, so a shift of 32 behaves as a
    # shift of 0 (NOT a shift of 32, which would zero everything out).
    assert ushl(1, 32) == 1


def test_ushr_is_logical_not_arithmetic():
    # A logical (unsigned) right shift of the top bit must fill with a
    # zero, not sign-extend — 0x80000000 >>> 16 == 0x8000, not something
    # with the high bits set.
    assert ushr(0x80000000, 16) == 32768


def test_ushr_of_all_ones_by_one():
    assert ushr(0xFFFFFFFF, 1) == 2147483647


def test_uand_uor_uxor_bit_patterns():
    assert uand(0xF0F0F0F0, 0x0F0F0F0F) == 0
    assert uor(0xF0F0F0F0, 0x0F0F0F0F) == 4294967295
    assert uxor(0xFFFFFFFF, 0xAAAAAAAA) == 1431655765


# ---------------------------------------------------------------------------
# pcg3d
# ---------------------------------------------------------------------------

def test_pcg3d_golden_vector_spec():
    assert pcg3d([1, 2, 3]) == [4204755366, 1223881804, 1500469937]  # (spec)


def test_pcg3d_zero_vector():
    assert pcg3d([0, 0, 0]) == [2611992518, 2833812075, 1058359340]


def test_pcg3d_arbitrary_vector():
    assert pcg3d([123456789, 987654321, 42]) == [33413632, 634159986, 380911738]


def test_pcg3d_max_uint32_vector():
    assert pcg3d([0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF]) == [2784268096, 2756918915, 1364953698]


def test_pcg3d_returns_a_plain_list_of_three():
    result = pcg3d([1, 2, 3])
    assert isinstance(result, list)
    assert len(result) == 3


# ---------------------------------------------------------------------------
# hash_uint32 / hash_uint
# ---------------------------------------------------------------------------

def test_hash_uint32_golden_vector_spec():
    assert hash_uint32(0x1234ABCD) == 737574769  # (spec)


def test_hash_uint32_zero_and_one():
    assert hash_uint32(0) == 0
    assert hash_uint32(1) == 1753845952


def test_hash_uint32_max_uint32_and_negative_one_agree():
    assert hash_uint32(0xFFFFFFFF) == 1734902346
    assert hash_uint32(-1) == 1734902346


def test_hash_uint_is_an_alias_for_hash_uint32():
    # `stdlib.hashUint` in glsl-runtime.js is literally `hashUint32` bound
    # under a second name (`hashUint: hashUint32`), not a distinct function.
    assert hash_uint is hash_uint32
    assert hash_uint(0x1234ABCD) == 737574769


# ---------------------------------------------------------------------------
# glsl_mod (floored modulo, NOT Python's `%`)
# ---------------------------------------------------------------------------

def test_glsl_mod_negative_dividend_spec():
    assert glsl_mod(-1, 3) == 2  # (spec)


def test_glsl_mod_negative_divisor_spec():
    assert glsl_mod(7, -3) == -2  # (spec)


def test_glsl_mod_matches_pythons_percent_for_these_signs():
    # Python's `%` already floors toward -infinity (same convention as GLSL
    # `mod`), so this is a belt-and-suspenders cross-check, not proof on its
    # own — the JS-derived vectors above are the ones that pin the contract.
    assert glsl_mod(-1, 3) == (-1 % 3)
    assert glsl_mod(7, -3) == (7 % -3)


# ---------------------------------------------------------------------------
# float_bits_to_uint / uint_bits_to_float
# ---------------------------------------------------------------------------

def test_float_bits_to_uint_of_one_spec():
    assert float_bits_to_uint(1.0) == 0x3F800000 == 1065353216  # (spec)


def test_float_bits_to_uint_zero_and_negative_one():
    assert float_bits_to_uint(0.0) == 0
    assert float_bits_to_uint(-1.0) == 3212836864


def test_float_bits_to_uint_pi_rounds_to_float32_first():
    # math.pi is a float64; float_bits_to_uint must round it to float32
    # (like JS's `Float32Array[0] = value`) before taking its bit pattern.
    assert float_bits_to_uint(math.pi) == 1078530011


def test_float_bits_to_uint_arbitrary_value():
    assert float_bits_to_uint(0.15625) == 1042284544


def test_uint_bits_to_float_is_the_exact_inverse():
    for value in (0.0, 1.0, -1.0, 0.15625, -2.5, 65504.0):
        bits = float_bits_to_uint(value)
        assert uint_bits_to_float(bits) == value


def test_uint_bits_to_float_of_known_bit_pattern():
    assert uint_bits_to_float(0x3F800000) == 1.0


# ---------------------------------------------------------------------------
# pack_half_2x16 / unpack_half_2x16
# ---------------------------------------------------------------------------

def test_pack_half_2x16_golden_bit_patterns():
    assert pack_half_2x16([0.0, 0.0]) == 0
    assert pack_half_2x16([1.0, 1.0]) == 1006648320
    assert pack_half_2x16([0.5, -2.0]) == 3221239808


def test_pack_unpack_half_2x16_round_trips_exact_values():
    for value in (0.0, 1.0, 0.5, -2.0):
        packed = pack_half_2x16([value, value])
        assert unpack_half_2x16(packed) == [value, value]


def test_unpack_half_2x16_of_pack_0_0():
    assert unpack_half_2x16(pack_half_2x16([0.0, 0.0])) == [0.0, 0.0]


def test_unpack_pack_half_2x16_approximates_irrational_inputs():
    # math.pi/math.e are not exactly representable in binary16, so the
    # round trip is lossy — but must match JS's *exact* lossy result, not
    # merely be "close".
    packed = pack_half_2x16([math.pi, math.e])
    assert packed == 1097876040
    a, b = unpack_half_2x16(packed)
    assert (a, b) == (3.140625, 2.71875)


def test_unpack_pack_half_2x16_subnormal_values():
    packed = pack_half_2x16([1e-7, -1e-7])
    assert packed == 2147614722
    a, b = unpack_half_2x16(packed)
    assert (a, b) == (1.1920928955078125e-07, -1.1920928955078125e-07)


def test_pack_half_2x16_infinities():
    packed = pack_half_2x16([math.inf, -math.inf])
    assert packed == 4227890176
    a, b = unpack_half_2x16(packed)
    assert a == math.inf
    assert b == -math.inf


def test_pack_half_2x16_overflow_saturates_to_infinity():
    # 1e9 is far beyond binary16 range (max ~65504) -> saturates to
    # +/-Infinity, same bit pattern as packing Infinity directly.
    packed = pack_half_2x16([1e9, -1e9])
    assert packed == 4227890176
    a, b = unpack_half_2x16(packed)
    assert a == math.inf
    assert b == -math.inf


def test_pack_half_2x16_nan():
    packed = pack_half_2x16([math.nan, 0.0])
    assert packed == 32256
    a, b = unpack_half_2x16(packed)
    assert math.isnan(a)
    assert b == 0.0
