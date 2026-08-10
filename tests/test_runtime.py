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
