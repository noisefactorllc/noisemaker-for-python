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


def test_dot_folds_each_accumulated_term_like_the_oracle(monkeypatch):
    """glsl-runtime's dot folds into a fused-multiply-add chain (2df5168abbe1:
    GPU backends round once per accumulated term, `sum = F32(left[i] *
    right[i] + sum)`; pre-fix oracles accumulate in float64 and round once).
    Expected values are noisemaker-for-cpu's at the folded tip; the
    single-rounding path diverges on every example."""
    from noisemaker_cpu import runtime

    rt = Runtime()
    a4 = np.array([0.7645993232727051, 2.686253547668457, 0.4626176953315735, -0.6199171543121338], dtype=np.float32)
    b4 = np.array([2.8575305938720703, -2.720503807067871, 2.150810718536377, -1.262344241142273], dtype=np.float32)
    a3 = np.array([-0.20638880133628845, 2.5406482219696045, -0.8305058479309082], dtype=np.float32)
    b3 = np.array([-1.509440541267395, -1.921399474143982, 1.6789777278900146], dtype=np.float32)
    a2 = np.array([-0.8672153353691101, 0.665517270565033, -0.0378420315682888], dtype=np.float32)
    b2 = np.array([-1.6907533407211304, -1.275408387184143, 1.430180311203003], dtype=np.float32)

    monkeypatch.setattr(runtime, "_ORACLE_DOT_FMA", True)
    assert rt.dot(a4, b4) == -3.3455448150634766
    assert rt.dot(a3, b3) == -5.964468955993652
    assert rt.dot(a2, b2) == 0.5633199214935303

    monkeypatch.setattr(runtime, "_ORACLE_DOT_FMA", False)
    assert rt.dot(a4, b4) == -3.3455450534820557
    assert rt.dot(a3, b3) == -5.9644694328308105
    assert rt.dot(a2, b2) == 0.563319981098175


def test_dot_probe_defaults_to_the_folded_tip(monkeypatch):
    """The published runtime folds by default (standalone/deployed renders with
    no mounted oracle); a mounted pre-fix oracle keeps its published
    single-rounding dot."""
    from noisemaker_cpu import runtime

    monkeypatch.setattr(runtime, "_ORACLE_DOT_FMA", None)
    pre_fix_dot = (
        "let sum = 0\n      for (let index = 0; index < left.length; index += 1) sum += left[index] * right[index]"
    )
    monkeypatch.setattr(runtime, "_mounted_oracle_text", lambda path: pre_fix_dot)
    assert runtime._oracle_dot_fma() is False

    monkeypatch.setattr(runtime, "_ORACLE_DOT_FMA", None)
    monkeypatch.setattr(runtime, "_mounted_oracle_text", lambda path: "sum = F32(left[index] * right[index] + sum)")
    assert runtime._oracle_dot_fma() is True

    monkeypatch.setattr(runtime, "_ORACLE_DOT_FMA", None)
    monkeypatch.setattr(runtime, "_mounted_oracle_text", lambda path: None)
    assert runtime._oracle_dot_fma() is True

