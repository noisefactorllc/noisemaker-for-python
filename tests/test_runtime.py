import numpy as np

from noisemaker_cpu.runtime import Runtime


def test_isnan_returns_glsl_boolean_scalar_and_vector_results():
    runtime = Runtime()

    assert runtime.component_wise("isnan", np.float32("nan")) is True
    assert runtime.component_wise("isnan", np.float32(1.0)) is False
    assert np.array_equal(
        runtime.component_wise("isnan", np.array([0.0, np.nan, np.inf], dtype=np.float32)),
        np.array([False, True, False]),
    )


def test_integer_division_matches_javascript_cpu_kernel_semantics():
    runtime = Runtime()

    assert runtime.binary("/", 15, 4, width=1, base="int") == 3.75
    assert np.array_equal(
        runtime.binary(
            "/",
            np.array([15, 9], dtype=np.int64),
            np.array([4, 2], dtype=np.int64),
            width=2,
            base="int",
        ),
        np.array([3.75, 4.5]),
    )


def test_unsigned_vector_arithmetic_preserves_javascript_number_assignments():
    runtime = Runtime(js_uvec_numbers=True)
    q = runtime.construct(4, [62536, 63536, 64536, 65536], base="uint")

    q[:] = runtime.binary(
        "+",
        runtime.binary("*", q, runtime.i(1664525), width=4, base="uint"),
        runtime.i(1013904223),
        width=4,
        base="uint",
    )
    q[0] += q[1] * q[2]
    q[1] += q[2] * q[3]
    q[2] += q[3] * q[0]
    q[3] += q[0] * q[1]
    q[:] = runtime.binary("^", q, runtime.binary(">>", q, 16, width=4, base="uint"), width=4, base="uint")

    assert list(q) == [1516217760, 1757440192, 0, 0]


def test_unsigned_vector_arithmetic_defaults_to_wrapped_glsl_semantics():
    runtime = Runtime()

    result = runtime.binary(
        "*",
        runtime.construct(2, [0xFFFFFFFF, 2], base="uint"),
        2,
        width=2,
        base="uint",
    )

    assert np.array_equal(result, np.array([0xFFFFFFFE, 4], dtype=np.int64))


def test_trunc_scalar_div_follows_the_oracle_probe(monkeypatch):
    """The scalar/scalar int-division truncation (ddf8b19-era lowering, see
    runtime) truncates by default — standalone/deployed renders with no
    mounted oracle — and passes the raw division through when the mounted
    oracle predates the rewrite."""
    from noisemaker_cpu import runtime

    monkeypatch.setattr(runtime, "_ORACLE_SCALAR_INT_DIVISION", True)
    assert runtime.trunc_scalar_div(-7.5) == -7.0
    monkeypatch.setattr(runtime, "_ORACLE_SCALAR_INT_DIVISION", False)
    assert runtime.trunc_scalar_div(-7.5) == -7.5


def test_normalize_divides_by_the_f32_length():
    # glsl-runtime normalize divides by length(), F32(sqrt(dot)), and dot is
    # F32(sum): the squared magnitude rounds to f32 before the sqrt. Expected
    # values are noisemaker-for-cpu's (a shapes3d getNormal vector); dividing
    # by the unrounded magnitude is one ulp off in every component.
    runtime = Runtime()
    v = runtime.construct(3, -0.0015451312065124512, -0.0015643835067749023, -0.0097536444664001465)

    assert [float(c) for c in runtime.normalize(v)] == [-0.1545376181602478, -0.156463161110878, -0.9755191206932068]


def test_distance_rounds_the_difference_and_the_dot_like_the_oracle():
    # glsl-runtime distance is length(subtract(a, b)): the difference is stored
    # f32 per component and the dot rounds to f32 before the sqrt. Expected
    # value is noisemaker-for-cpu's; the float64 path gives 1.523514747619629.
    runtime = Runtime()
    a = np.array([1.3458458185195923, -0.09458716213703156], dtype=np.float32)
    b = np.array([0.556272566318512, -1.3975342512130737], dtype=np.float32)

    assert float(runtime.distance(a, b)) == 1.5235146284103394

