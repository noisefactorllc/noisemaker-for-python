import os
import shutil
import subprocess
import zlib

import pytest

from noisemaker_cpu.png import decode_png, encode_png
from noisemaker_cpu.surface import Surface

SIGNATURE = bytes([137, 80, 78, 71, 13, 10, 26, 10])

# The JS PNG-encoder cross-check needs a sibling noisemaker-cpu checkout + node.
CPU_DIR = os.environ.get("NOISEMAKER_CPU_DIR") or os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "noisemaker-cpu")
)


def _png_chunk(chunk_type: str, data: bytes = b"") -> bytes:
    """Independent PNG chunk builder (length + type + data + CRC32) used only by
    tests that hand-construct PNG bytes, so decode_png is exercised against
    input it did not itself produce."""
    body = chunk_type.encode("ascii") + data
    crc = zlib.crc32(body) & 0xFFFFFFFF
    return len(data).to_bytes(4, "big") + body + crc.to_bytes(4, "big")


def _ihdr(width: int, height: int, color_type: int = 6) -> bytes:
    ihdr = bytearray(13)
    ihdr[0:4] = width.to_bytes(4, "big")
    ihdr[4:8] = height.to_bytes(4, "big")
    ihdr[8] = 8  # bit depth
    ihdr[9] = color_type
    ihdr[10] = 0  # compression method
    ihdr[11] = 0  # filter method
    ihdr[12] = 0  # interlace method
    return bytes(ihdr)


def _paeth_predictor(left: int, up: int, upper_left: int) -> int:
    estimate = left + up - upper_left
    left_distance = abs(estimate - left)
    up_distance = abs(estimate - up)
    upper_left_distance = abs(estimate - upper_left)
    if left_distance <= up_distance and left_distance <= upper_left_distance:
        return left
    if up_distance <= upper_left_distance:
        return up
    return upper_left


def _filter4_encode(pixels: bytes, width: int, height: int, bpp: int) -> bytes:
    """Hand-filter raw top-down RGBA scanlines with PNG filter type 4 (Paeth)."""
    stride = width * bpp
    out = bytearray((stride + 1) * height)
    for y in range(height):
        src_row = y * stride
        dst_row = y * (stride + 1)
        out[dst_row] = 4  # filter type: Paeth
        for x in range(stride):
            raw = pixels[src_row + x]
            left = pixels[src_row + x - bpp] if x >= bpp else 0
            up = pixels[src_row - stride + x] if y > 0 else 0
            upper_left = pixels[src_row - stride + x - bpp] if y > 0 and x >= bpp else 0
            predictor = _paeth_predictor(left, up, upper_left)
            out[dst_row + 1 + x] = (raw - predictor) & 0xFF
    return bytes(out)


def _build_png(width: int, height: int, filtered_scanlines: bytes) -> bytes:
    idat = zlib.compress(filtered_scanlines, 9)
    return SIGNATURE + _png_chunk("IHDR", _ihdr(width, height)) + _png_chunk("IDAT", idat) + _png_chunk("IEND")


def test_encode_png_has_signature_and_chunk_markers():
    surface = Surface.from_rgba8(2, 2, bytes([255, 0, 0, 255, 0, 255, 0, 255, 0, 0, 255, 255, 255, 255, 255, 255]))
    output = encode_png(surface)
    assert output[:8] == SIGNATURE
    assert b"IHDR" in output
    assert b"IDAT" in output
    assert b"IEND" in output


def test_round_trip_3x2_surface():
    raw = bytes(
        [
            10,
            20,
            30,
            255,
            40,
            50,
            60,
            200,
            70,
            80,
            90,
            128,
            100,
            110,
            120,
            64,
            130,
            140,
            150,
            32,
            160,
            170,
            180,
            0,
        ]
    )
    surface = Surface.from_rgba8(3, 2, raw)
    decoded = decode_png(encode_png(surface))
    assert decoded.width == 3
    assert decoded.height == 2
    assert decoded.to_rgba8() == surface.to_rgba8()


def test_cross_check_against_js_encoder(tmp_path):
    if shutil.which("node") is None or not os.path.isdir(CPU_DIR):
        pytest.skip("needs node + a sibling noisemaker-cpu checkout")
    output_path = str(tmp_path / "nmpng_fix.png")
    subprocess.run(
        [
            "node",
            "bin/noisemaker-cpu.js",
            "effect",
            "synth/solid",
            "--width",
            "4",
            "--height",
            "4",
            "--param",
            "color=#4080c0",
            "--output",
            output_path,
        ],
        cwd=CPU_DIR,
        check=True,
        capture_output=True,
    )
    with open(output_path, "rb") as handle:
        data = handle.read()

    surface = decode_png(data)
    assert surface.width == 4
    assert surface.height == 4
    rgba = surface.to_rgba8()
    expected_pixel = bytes([0x40, 0x80, 0xC0, 0xFF])
    for i in range(0, len(rgba), 4):
        assert rgba[i : i + 4] == expected_pixel


def test_decode_png_paeth_filter_round_trip():
    width, height, bpp = 2, 2, 4
    raw = bytes(
        [
            10,
            20,
            30,
            40,
            50,
            60,
            70,
            80,
            90,
            100,
            110,
            120,
            200,
            210,
            220,
            230,
        ]
    )
    filtered = _filter4_encode(raw, width, height, bpp)
    # Sanity: the hand-filter actually used filter type 4 on every row.
    assert filtered[0] == 4
    assert filtered[(width * bpp + 1)] == 4

    png_bytes = _build_png(width, height, filtered)
    surface = decode_png(png_bytes)
    assert surface.width == width
    assert surface.height == height
    assert surface.to_rgba8() == raw


def test_decode_png_rejects_oversized_pixel_count():
    bogus_ihdr = _ihdr(16_777_217, 1)
    bogus = (
        SIGNATURE + _png_chunk("IHDR", bogus_ihdr) + _png_chunk("IDAT", zlib.compress(bytes(5))) + _png_chunk("IEND")
    )
    with pytest.raises(ValueError, match="16,777,216 pixel limit"):
        decode_png(bogus)


def test_decode_png_rejects_decompression_bomb():
    bomb_idat = zlib.compress(bytes(1024 * 1024))
    bomb = SIGNATURE + _png_chunk("IHDR", _ihdr(1, 1)) + _png_chunk("IDAT", bomb_idat) + _png_chunk("IEND")
    with pytest.raises(ValueError, match="exceeds the expected scanline length"):
        decode_png(bomb)
