import hashlib

import numpy as np

from noisemaker_cpu.renderer import render_dsl, render_effect
from noisemaker_cpu.surface import Surface


def test_error_diffusion_dither_matches_the_pinned_cpu_frame():
    result = render_dsl(
        "search synth, filter\nnoise(seed: 1, ridges: true).dither(type: errorDiffusion).write(o0)\nrender(o0)",
        width=8,
        height=8,
        time=0.25,
    )

    assert hashlib.sha256(result.to_rgba8()).hexdigest() == (
        "0665d7edb18d3e61a4e6731369c881b045145ca6d0a709ccf070319b0a6f8dc7"
    )


def test_median_matches_latest_cpu_compatibility_route_for_every_radius():
    width, height = 6, 5
    data = np.empty(width * height * 4, dtype=np.float32)
    for y in range(height):
        for x in range(width):
            index = (y * width + x) * 4
            data[index] = (((31 * x + 17 * y + 7) % 97) + 1) / 101
            data[index + 1] = (((13 * x + 37 * y + 11) % 89) + 2) / 97
            data[index + 2] = (((43 * x + 5 * y + 3) % 83) + 3) / 91
            data[index + 3] = 1
    input_surface = Surface(width, height, data)
    expected = {
        1: "c977bad100bc84f0c6d14246860ab5084b4ce23208701cf88c51322c51335bda",
        2: "a36571e1856f4e964b4f14f3957915dcee87a9381e944f6104df329e6914bcd7",
        3: "73d5a67ab88331c89b89f6e95fbb4fa63101e340e92e94ecc2e15a12f9f57b69",
    }

    for radius, expected_hash in expected.items():
        program = f"search filter\nread(o0).median(radius: {radius}).write(o7)\nrender(o7)"
        result = render_dsl(program, width=width, height=height, seed_surfaces={"o0": input_surface})
        assert hashlib.sha256(result.to_rgba8()).hexdigest() == expected_hash


def test_median_preserves_negative_packed_channels():
    input_surface = Surface(3, 3).clear([-0.5, 0.25, 0.5, 1])

    result = render_effect(
        "filter/median",
        {"radius": 3},
        {"inputTex": input_surface},
        width=3,
        height=3,
    )

    assert result.data[:4].tolist() == [-0.5, 0.25, 0.5, 1.0]
