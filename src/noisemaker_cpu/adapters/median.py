"""filter/median compatibility adapter matching noisemaker-for-cpu."""

from __future__ import annotations

import numpy as np

from .. import uintmath
from . import register

F32 = np.float32


def _f32(value) -> float:
    return float(F32(value))


@register("filter/median:median")
def median_factory(rt, _base_kernel):
    brightness = [0] * 49
    red_green = [0] * 49
    blue = [0] * 49

    def swap(left, right):
        brightness[left], brightness[right] = brightness[right], brightness[left]
        red_green[left], red_green[right] = red_green[right], red_green[left]
        blue[left], blue[right] = blue[right], blue[left]

    def kernel(ctx, out):
        rt.begin_pixel(ctx)
        surface = ctx.textures["inputTex"]
        radius = int(ctx.uniforms.get("RADIUS", 0))
        center_x = int(ctx.frag_coord[0])
        center_y = int(ctx.frag_coord[1])
        center_row = surface.height - 1 - center_y
        center_offset = (center_row * surface.width + center_x) * 4
        original_red = float(surface.data[center_offset])
        original_green = float(surface.data[center_offset + 1])
        original_blue = float(surface.data[center_offset + 2])

        index = 0
        for y in range(-radius, radius + 1):
            sample_y = min(max(center_y + y, 0), surface.height - 1)
            sample_row = surface.height - 1 - sample_y
            for x in range(-radius, radius + 1):
                sample_x = min(max(center_x + x, 0), surface.width - 1)
                offset = (sample_row * surface.width + sample_x) * 4
                red = float(surface.data[offset])
                green = float(surface.data[offset + 1])
                sample_blue = float(surface.data[offset + 2])
                luminance = _f32(
                    _f32(_f32(red * 0.2126) + _f32(green * 0.7152)) + _f32(sample_blue * 0.0722)
                )
                packed_red_green = uintmath.pack_half_2x16((red, green))
                brightness[index] = uintmath.float_bits_to_uint(luminance)
                red_green[index] = ((packed_red_green & 0xFFFF) << 16) | (packed_red_green >> 16)
                blue[index] = uintmath.pack_half_2x16((sample_blue, 0.0)) & 0xFFFF
                index += 1

        median_index = (index - 1) >> 1
        left = 0
        right = index - 1
        while left < right:
            pivot_brightness = brightness[median_index]
            pivot_red_green = red_green[median_index]
            pivot_blue = blue[median_index]
            scan_left = left
            scan_right = right

            def less_pivot(
                record,
                pivot_brightness=pivot_brightness,
                pivot_red_green=pivot_red_green,
                pivot_blue=pivot_blue,
            ):
                if brightness[record] != pivot_brightness:
                    return brightness[record] < pivot_brightness
                if red_green[record] != pivot_red_green:
                    return red_green[record] < pivot_red_green
                return blue[record] < pivot_blue

            def pivot_less(
                record,
                pivot_brightness=pivot_brightness,
                pivot_red_green=pivot_red_green,
                pivot_blue=pivot_blue,
            ):
                if pivot_brightness != brightness[record]:
                    return pivot_brightness < brightness[record]
                if pivot_red_green != red_green[record]:
                    return pivot_red_green < red_green[record]
                return pivot_blue < blue[record]

            while scan_left <= scan_right:
                while less_pivot(scan_left):
                    scan_left += 1
                while pivot_less(scan_right):
                    scan_right -= 1
                if scan_left <= scan_right:
                    swap(scan_left, scan_right)
                    scan_left += 1
                    scan_right -= 1
            if scan_right < median_index:
                left = scan_left
            if median_index < scan_left:
                right = scan_right

        packed = red_green[median_index]
        median_red, median_green = uintmath.unpack_half_2x16(((packed & 0xFFFF) << 16) | (packed >> 16))
        median_blue = uintmath.unpack_half_2x16(blue[median_index])[0]
        maximum_difference = max(
            abs(original_red - median_red),
            abs(original_green - median_green),
            abs(original_blue - median_blue),
        )
        threshold = float(ctx.uniforms.get("threshold", 0.0))
        replace = threshold <= 0 or maximum_difference >= threshold / 100
        out[0] = median_red if replace else original_red
        out[1] = median_green if replace else original_green
        out[2] = median_blue if replace else original_blue
        out[3] = float(surface.data[center_offset + 3])

    kernel.uses_derivatives = False
    return kernel
