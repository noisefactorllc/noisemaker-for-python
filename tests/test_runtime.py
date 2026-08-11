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
