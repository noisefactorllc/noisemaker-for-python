"""CPU port of noisemaker-cpu src/runtime/automation.js — upstream oscillator
parameter automation written as `osc(...)` in the Polymorphic DSL. Upstream
resolves these per frame inside Pipeline.resolveUniformValue with a normalized
0..1 loop time; this port resolves them per render in renderer._render_effect_once
with the same `time` the canonical kernels receive as their `time` uniform.

The upstream Midi/Audio automation nodes are not compiled by the DSL (value-position
calls other than osc() are rejected at compile time), so only the Oscillator branch
of upstream's evaluateAutomation is reachable here. The math below is a verbatim
port of the upstream oscillator evaluation, including the noise2d two-stage
periodic noise (speed applied once, after the first periodic wrap, matching the
osc2d shader).

Float fidelity: JS numbers are float64 and `%` follows the dividend's sign, so
every JS remainder is `math.fmod` and every Math.* call maps to `math.*`.
"""

from __future__ import annotations

import math

from .js_trig import js_cos, js_sin

_TAU = math.pi * 2

MAX_AUTOMATION_DEPTH = 8

AUTOMATION_FIELD_RANGES = {
    "unit": {"min": 0, "max": 1},
    "oscillatorSpeed": {"min": -20, "max": 20},
    "oscillatorOffset": {"min": -1, "max": 1},
    "oscillatorSeed": {"min": 1, "max": 9999},
}

# 16-point Gauss-Legendre nodes and weights on [-1, 1]. Fixed quadrature keeps
# noise and deeply nested rate modulation deterministic and seekable.
_INTEGRATION_NODES = [
    -0.9894009349916499, -0.9445750230732326, -0.8656312023878318, -0.755404408355003,
    -0.6178762444026438, -0.4580167776572274, -0.2816035507792589, -0.0950125098376374,
    0.0950125098376374, 0.2816035507792589, 0.4580167776572274, 0.6178762444026438,
    0.755404408355003, 0.8656312023878318, 0.9445750230732326, 0.9894009349916499,
]
_INTEGRATION_WEIGHTS = [
    0.0271524594117541, 0.0622535239386479, 0.0951585116824928, 0.1246289712555339,
    0.1495959888165767, 0.1691565193950025, 0.1826034150449236, 0.1894506104550685,
    0.1894506104550685, 0.1826034150449236, 0.1691565193950025, 0.1495959888165767,
    0.1246289712555339, 0.0951585116824928, 0.0622535239386479, 0.0271524594117541,
]
_INTEGRATION_RULES = [
    {"nodes": _INTEGRATION_NODES, "weights": _INTEGRATION_WEIGHTS},
    {
        "nodes": [
            -0.9602898564975363, -0.7966664774136267, -0.525532409916329,
            -0.1834346424956498, 0.1834346424956498, 0.525532409916329,
            0.7966664774136267, 0.9602898564975363,
        ],
        "weights": [
            0.1012285362903763, 0.2223810344533745, 0.3137066458778873,
            0.362683783378362, 0.362683783378362, 0.3137066458778873,
            0.2223810344533745, 0.1012285362903763,
        ],
    },
    {
        "nodes": [-0.8611363115940526, -0.3399810435848563, 0.3399810435848563, 0.8611363115940526],
        "weights": [0.3478548451374538, 0.6521451548625461, 0.6521451548625461, 0.3478548451374538],
    },
    {
        "nodes": [-0.5773502691896257, 0.5773502691896257],
        "weights": [1, 1],
    },
]


def is_automation_value(value):
    """True for an `osc(...)` automation value ({type: 'Oscillator', ...})."""
    return isinstance(value, dict) and value.get("type") == "Oscillator"


def is_finite_number(value):
    """JS Number.isFinite: booleans and non-numbers are not finite numbers."""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _scale(value, range_):
    if range_ is None or not is_finite_number(range_.get("min")) or not is_finite_number(range_.get("max")):
        return value
    return range_["min"] + value * (range_["max"] - range_["min"])


def _resolve_field(value, normalized_time, range_, depth, stack, fallback):
    if is_automation_value(value):
        return evaluate_automation(value, normalized_time, range_, depth + 1, stack)
    return value if is_finite_number(value) else fallback


def _can_integrate_exactly(config):
    osc_type = config.get("oscType")
    if not is_finite_number(osc_type) or not 0 <= osc_type <= 4:
        return False
    return all(
        is_finite_number(config.get(field)) for field in ("min", "max", "speed", "offset", "seed")
    )


def _osc_primitive(osc_type, x):
    whole = math.floor(x)
    fraction = x - whole
    if osc_type == 0:
        return x * 0.5 - js_sin(x * _TAU) / (2 * _TAU)
    if osc_type == 1:
        if fraction < 0.5:
            partial = fraction * fraction
        else:
            partial = 2 * fraction - fraction * fraction - 0.5
        return whole * 0.5 + partial
    if osc_type == 2:
        return whole * 0.5 + fraction * fraction * 0.5
    if osc_type == 3:
        return x - (whole * 0.5 + fraction * fraction * 0.5)
    if osc_type == 4:
        return whole * 0.5 + max(0.0, fraction - 0.5)
    return None


def _integrate_simple(config, normalized_time):
    osc_type = config["oscType"]
    min_value = config["min"]
    max_value = config["max"]
    speed = config["speed"]
    offset = config["offset"]
    if speed == 0:
        return _evaluate_oscillator(config, 0, 0, set()) * normalized_time
    start = _osc_primitive(osc_type, offset)
    end = _osc_primitive(osc_type, offset + speed * normalized_time)
    raw_integral = (end - start) / speed
    return min_value * normalized_time + (max_value - min_value) * raw_integral


def _integrate_automation(config, normalized_time, range_, depth, stack):
    if _can_integrate_exactly(config):
        integral = _integrate_simple(config, normalized_time)
    else:
        # Decrease the quadrature order as rate modulators nest. This bounds an
        # eight-level graph to thousands, rather than millions, of evaluations
        # while retaining the highest precision at the user-visible output.
        rule = _INTEGRATION_RULES[min(depth, len(_INTEGRATION_RULES) - 1)]
        midpoint = normalized_time * 0.5
        half_width = normalized_time * 0.5
        total = 0.0
        for node, weight in zip(rule["nodes"], rule["weights"], strict=True):
            sample_time = midpoint + half_width * node
            total += weight * evaluate_automation(config, sample_time, None, depth + 1, stack)
        integral = half_width * total
    if range_ is None or not is_finite_number(range_.get("min")) or not is_finite_number(range_.get("max")):
        return integral
    return range_["min"] * normalized_time + integral * (range_["max"] - range_["min"])


def _hash21(px, py, s):
    x = math.fmod(px * 234.34 + s, 1)
    y = math.fmod(py * 435.345 + s, 1)
    if x < 0:
        x += 1
    if y < 0:
        y += 1
    p = x + y + (x + y) * 34.23
    return math.fmod(x * y * p, 1)


def _noise2d(px, py, s):
    ix = math.floor(px)
    iy = math.floor(py)
    fx = px - ix
    fy = py - iy
    fx = fx * fx * (3 - 2 * fx)
    fy = fy * fy * (3 - 2 * fy)

    a = _hash21(ix, iy, s)
    b = _hash21(ix + 1, iy, s)
    c = _hash21(ix, iy + 1, s)
    d = _hash21(ix + 1, iy + 1, s)

    return a * (1 - fx) * (1 - fy) + b * fx * (1 - fy) + c * (1 - fx) * fy + d * fx * fy


def _osc_noise(t, seed):
    # Looping noise - samples on a circle for seamless temporal loops
    temporal = math.fmod(t, 1)
    angle = temporal * _TAU
    radius = 2
    loop_x = js_cos(angle) * radius
    loop_y = js_sin(angle) * radius
    n1 = _noise2d(loop_x + seed, loop_y + seed, seed)
    n2 = _noise2d(loop_x + seed * 2, loop_y + seed * 2, seed)
    return (n1 + n2) / 2


def _osc_noise2d(time, speed, seed):
    # Two-stage periodic noise (noise2d, kind 6) - mirrors the osc2d effect:
    #   scaledTime = periodicValue(time, timeNoise) * speed
    #   value      = periodicValue(scaledTime, valueNoise)
    # `time` is the normalized loop time plus the phase offset; speed is applied
    # once, after the first periodic wrap, exactly as in the osc2d shader.
    # osc() has no spatial position, so both noise stages are sampled at a fixed
    # position derived from the seed (the osc2d shader salts the second stage with
    # +12345). periodicValue() has period 1 in time, so whole-number speeds loop
    # seamlessly.
    def periodic_value(x, v):
        return (js_sin((x - v) * _TAU) + 1) * 0.5

    px = (abs(math.fmod(seed, 16)) + 0.5) / 16
    py = (abs(math.fmod(math.floor(seed / 16), 16)) + 0.5) / 16
    time_noise = _noise2d(px, py, seed + 12345)
    value_noise = _noise2d(px, py, seed)
    scaled_time = periodic_value(time, time_noise) * speed
    return periodic_value(scaled_time, value_noise)


def _evaluate_oscillator(osc, normalized_time, depth, stack):
    osc_type = osc["oscType"]
    min_value = _resolve_field(osc.get("min"), normalized_time, AUTOMATION_FIELD_RANGES["unit"], depth, stack, 0)
    max_value = _resolve_field(osc.get("max"), normalized_time, AUTOMATION_FIELD_RANGES["unit"], depth, stack, 1)
    offset = _resolve_field(osc.get("offset"), normalized_time, AUTOMATION_FIELD_RANGES["oscillatorOffset"], depth, stack, 0)
    seed = _resolve_field(osc.get("seed"), normalized_time, AUTOMATION_FIELD_RANGES["oscillatorSeed"], depth, stack, 1)

    # A modulated rate is frequency modulation, so phase is the integral of
    # rate. Literal rates keep the existing closed form exactly.
    if is_automation_value(osc.get("speed")):
        phase = _integrate_automation(
            osc["speed"], normalized_time, AUTOMATION_FIELD_RANGES["oscillatorSpeed"], depth, stack
        )
    else:
        speed = osc.get("speed")
        phase = normalized_time * (speed if is_finite_number(speed) else 1)
    t = phase + offset

    # Get raw oscillator value (0..1)
    if osc_type == 0:
        value = (1.0 - js_cos(t * _TAU)) * 0.5
    elif osc_type == 1:
        tf = t - math.floor(t)
        value = 1.0 - abs(tf * 2.0 - 1.0)
    elif osc_type == 2:
        value = t - math.floor(t)
    elif osc_type == 3:
        value = 1.0 - (t - math.floor(t))
    elif osc_type == 4:
        value = 1.0 if (t - math.floor(t)) >= 0.5 else 0.0
    elif osc_type == 5:
        value = _osc_noise(t, seed)
    elif osc_type == 6:
        speed = _resolve_field(
            osc.get("speed"), normalized_time, AUTOMATION_FIELD_RANGES["oscillatorSpeed"], depth, stack, 1
        )
        value = _osc_noise2d(normalized_time + offset, speed if is_finite_number(speed) else 1, seed)
    else:
        value = 0

    # Map to min..max range
    return min_value + value * (max_value - min_value)


def evaluate_automation(config, normalized_time, range_=None, depth=0, stack=None):
    if not is_automation_value(config) or depth > MAX_AUTOMATION_DEPTH or (stack is not None and id(config) in stack):
        return _scale(0, range_)
    if stack is None:
        stack = set()
    stack.add(id(config))
    try:
        value = _evaluate_oscillator(config, normalized_time, depth, stack)
    finally:
        stack.discard(id(config))
    return _scale(value, range_)


def resolve_automation_uniform(value, normalized_time, spec):
    """Port of upstream Pipeline.resolveUniformValue: resolve an automation value
    for the current frame, scaled into the consumer parameter's declared range,
    with the upstream integer rounding for `type: 'int'` consumers. Non-automation
    values pass through unchanged."""
    if not is_automation_value(value):
        return value
    resolved = evaluate_automation(value, normalized_time, spec)
    if spec is not None and spec.get("type") == "int":
        return _js_round(resolved)
    return resolved


def _js_round(x):
    """JS Math.round: nearest integer, exact .5 ties toward +infinity. Unlike
    floor(x + 0.5), this is exact for x = 0.49999999999999994, where the addition
    rounds up to 1.0 but Math.round returns 0 (the fixture pins that case)."""
    floor_ = math.floor(x)
    diff = x - floor_
    if diff > 0.5:
        return floor_ + 1
    if diff < 0.5:
        return floor_
    return floor_ + 1
