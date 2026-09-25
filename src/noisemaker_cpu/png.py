"""PNG codec — faithful port of noisemaker-cpu `src/node/png.js`.

Zero-dependency (stdlib ``zlib`` only). Encodes ``Surface`` objects as 8-bit
RGBA PNGs (color type 6, no interlace, filter type 0/None per scanline) and
decodes arbitrary well-formed 8-bit, non-interlaced PNGs (grayscale, RGB,
palette, grayscale+alpha, RGBA; all five row filters: None/Sub/Up/Average/
Paeth) back into ``Surface`` objects.

Mirrors png.js's structural validation (chunk ordering, CRC32 checks) and its
decompression-bomb / pixel-count guards.
"""

from __future__ import annotations

import zlib

import numpy as np

from noisemaker_cpu.surface import Surface

SIGNATURE = bytes([137, 80, 78, 71, 13, 10, 26, 10])
MAX_PNG_PIXELS = 16_777_216
MAX_PNG_ENCODED_BYTES = 256 * 1024 * 1024
MAX_PNG_DECODED_BYTES = 96 * 1024 * 1024

_COMPONENTS_BY_COLOR_TYPE = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}


def _chunk(chunk_type: str, data: bytes = b"") -> bytes:
    body = chunk_type.encode("ascii") + data
    crc = zlib.crc32(body) & 0xFFFFFFFF
    return len(data).to_bytes(4, "big") + body + crc.to_bytes(4, "big")


def encode_png(surface: Surface) -> bytes:
    """Encode a ``Surface`` (RGBA float32, top-down) as 8-bit RGBA PNG bytes."""
    width, height = surface.width, surface.height
    if height > MAX_PNG_PIXELS // width:
        raise ValueError("PNG exceeds the 16,777,216 pixel limit")

    ihdr = bytearray(13)
    ihdr[0:4] = width.to_bytes(4, "big")
    ihdr[4:8] = height.to_bytes(4, "big")
    ihdr[8] = 8  # bit depth
    ihdr[9] = 6  # color type: truecolor + alpha
    ihdr[10] = 0  # compression method
    ihdr[11] = 0  # filter method
    ihdr[12] = 0  # interlace method

    rgba = surface.to_rgba8()
    stride = width * 4
    scanlines = bytearray((stride + 1) * height)
    for y in range(height):
        target = y * (stride + 1)
        scanlines[target] = 0  # filter type 0 (None) for every row
        scanlines[target + 1 : target + 1 + stride] = rgba[y * stride : (y + 1) * stride]

    idat = zlib.compress(bytes(scanlines), 9)

    return SIGNATURE + _chunk("IHDR", bytes(ihdr)) + _chunk("IDAT", idat) + _chunk("IEND")


def _paeth(left: int, up: int, upper_left: int) -> int:
    estimate = left + up - upper_left
    left_distance = abs(estimate - left)
    up_distance = abs(estimate - up)
    upper_left_distance = abs(estimate - upper_left)
    if left_distance <= up_distance and left_distance <= upper_left_distance:
        return left
    if up_distance <= upper_left_distance:
        return up
    return upper_left


def _ascii(data: bytes) -> str:
    """Match Node's Buffer#toString('ascii'): mask off the high bit of each byte."""
    return "".join(chr(b & 0x7F) for b in data)


def _bounded_inflate(compressed: bytes, max_length: int) -> bytes:
    """Inflate a zlib stream, raising if the output would exceed ``max_length``.

    Mirrors Node's ``inflateSync(compressed, { maxOutputLength })``.
    """
    decompressor = zlib.decompressobj()
    output = decompressor.decompress(bytes(compressed), max_length)
    if decompressor.unconsumed_tail:
        raise ValueError("decompressed data exceeds the expected length")
    output += decompressor.flush()
    if len(output) > max_length:
        raise ValueError("decompressed data exceeds the expected length")
    return output


def _decode_scanlines(compressed: bytes, width: int, height: int, bytes_per_pixel: int) -> bytearray:
    stride = width * bytes_per_pixel
    expected = (stride + 1) * height
    if expected > MAX_PNG_DECODED_BYTES:
        raise ValueError("PNG decoded scanlines exceed the 96 MiB limit")
    try:
        filtered = _bounded_inflate(compressed, expected)
    except (zlib.error, ValueError) as error:
        raise ValueError(
            f"PNG decompressed data exceeds the expected scanline length or is invalid: {error}"
        ) from error
    if len(filtered) != expected:
        raise ValueError("PNG scanline data has an invalid length")

    decoded = bytearray(stride * height)
    for y in range(height):
        source_row = y * (stride + 1)
        target_row = y * stride
        filt = filtered[source_row]
        if filt > 4:
            raise ValueError(f"Unsupported PNG row filter {filt}")
        if filt == 0:
            # None: straight copy (C-speed slice assignment).
            decoded[target_row : target_row + stride] = filtered[source_row + 1 : source_row + 1 + stride]
        elif filt == 2:
            # Up: recon = raw + prior row (mod 256). Rows are independent of
            # their own neighbors, so this vectorizes exactly.
            row = np.frombuffer(filtered, np.uint8, stride, source_row + 1)
            if y == 0:
                decoded[target_row : target_row + stride] = row.tobytes()
            else:
                up = np.frombuffer(decoded, np.uint8, stride, target_row - stride)
                decoded[target_row : target_row + stride] = ((row + up) & 0xFF).tobytes()
        elif filt == 1:
            # Sub: recon[x] = raw[x] + recon[x - bpp] (mod 256). Reshaping the
            # row to (stride // bpp, bpp) puts each byte on the same lane as
            # its `x - bpp` neighbor, so a per-column cumulative sum (uint8
            # wraparound is exactly PNG's mod-256 arithmetic) vectorizes it.
            lanes = np.frombuffer(filtered, np.uint8, stride, source_row + 1).reshape(
                stride // bytes_per_pixel, bytes_per_pixel
            )
            decoded[target_row : target_row + stride] = np.add.accumulate(lanes, axis=0, dtype=np.uint8).tobytes()
        else:
            # Average (3) and Paeth (4) are sequentially dependent byte-by-byte.
            for x in range(stride):
                raw = filtered[source_row + x + 1]
                left = decoded[target_row + x - bytes_per_pixel] if x >= bytes_per_pixel else 0
                up = decoded[target_row + x - stride] if y > 0 else 0
                upper_left = decoded[target_row + x - stride - bytes_per_pixel] if y > 0 and x >= bytes_per_pixel else 0
                if filt == 3:
                    predictor = (left + up) >> 1
                else:
                    predictor = _paeth(left, up, upper_left)
                decoded[target_row + x] = (raw + predictor) & 0xFF
    return decoded


def decode_png(data: bytes) -> Surface:
    """Decode a non-interlaced, 8-bit PNG into a ``Surface`` (RGBA float32, top-down)."""
    png = bytes(data)
    if len(png) > MAX_PNG_ENCODED_BYTES:
        raise ValueError("PNG exceeds the 256 MiB encoded input limit")
    if len(png) < len(SIGNATURE) or png[: len(SIGNATURE)] != SIGNATURE:
        raise ValueError("Input is not a PNG image")

    offset = len(SIGNATURE)
    width = 0
    height = 0
    bit_depth = 0
    color_type = -1
    interlace = 0
    palette: bytes | None = None
    transparency: bytes | None = None
    seen_header = False
    seen_palette = False
    seen_transparency = False
    seen_idat = False
    idat_closed = False
    seen_end = False
    idat_chunks: list[bytes] = []

    while offset + 12 <= len(png):
        length = int.from_bytes(png[offset : offset + 4], "big")
        end = offset + 12 + length
        if end > len(png):
            raise ValueError("PNG contains a truncated chunk")
        chunk_type = _ascii(png[offset + 4 : offset + 8])
        chunk_data = png[offset + 8 : offset + 8 + length]
        expected_crc = int.from_bytes(png[offset + 8 + length : end], "big")
        actual_crc = zlib.crc32(png[offset + 4 : offset + 8 + length]) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            raise ValueError(f"PNG CRC mismatch in {chunk_type}")

        if chunk_type == "IHDR":
            if seen_header or offset != len(SIGNATURE):
                raise ValueError("PNG IHDR must appear exactly once and first")
            if length != 13:
                raise ValueError("PNG IHDR has an invalid length")
            seen_header = True
            width = int.from_bytes(chunk_data[0:4], "big")
            height = int.from_bytes(chunk_data[4:8], "big")
            if width == 0 or height == 0:
                raise ValueError("PNG dimensions must be positive")
            if height > MAX_PNG_PIXELS // width:
                raise ValueError("PNG exceeds the 16,777,216 pixel limit")
            bit_depth = chunk_data[8]
            color_type = chunk_data[9]
            if chunk_data[10] != 0 or chunk_data[11] != 0:
                raise ValueError("Unsupported PNG compression or filter method")
            interlace = chunk_data[12]
        elif chunk_type == "PLTE":
            if not seen_header or seen_palette or seen_idat:
                raise ValueError("PNG PLTE must appear at most once before IDAT")
            seen_palette = True
            palette = bytes(chunk_data)
        elif chunk_type == "tRNS":
            if not seen_header or seen_transparency or seen_idat:
                raise ValueError("PNG tRNS must appear at most once before IDAT")
            seen_transparency = True
            transparency = bytes(chunk_data)
        elif chunk_type == "IDAT":
            if not seen_header or idat_closed:
                raise ValueError("PNG IDAT chunks must be consecutive and follow IHDR")
            seen_idat = True
            idat_chunks.append(chunk_data)
        elif chunk_type == "IEND":
            if not seen_idat or length != 0:
                raise ValueError("PNG IEND must be empty and follow IDAT")
            seen_end = True
            offset = end
            break
        else:
            if seen_idat:
                idat_closed = True
            if chunk_type[:1] == chunk_type[:1].upper():
                raise ValueError(f"Unsupported critical PNG chunk {chunk_type}")
        offset = end

    if not (seen_header and seen_idat and seen_end):
        raise ValueError("PNG is missing required IHDR, IDAT, or IEND chunks")
    if offset != len(png):
        raise ValueError("PNG contains trailing data after IEND")
    if bit_depth != 8:
        raise ValueError(f"Unsupported PNG bit depth {bit_depth}; expected 8")
    if interlace != 0:
        raise ValueError("Interlaced PNG images are not supported")

    components = _COMPONENTS_BY_COLOR_TYPE.get(color_type)
    if not components:
        raise ValueError(f"Unsupported PNG color type {color_type}")
    if color_type == 3 and (palette is None or len(palette) == 0 or len(palette) % 3 != 0):
        raise ValueError("Indexed PNG is missing a valid palette")
    if transparency is not None:
        if color_type == 0 and len(transparency) != 2:
            raise ValueError("Grayscale PNG tRNS must contain one 16-bit sample")
        if color_type == 2 and len(transparency) != 6:
            raise ValueError("True-color PNG tRNS must contain three 16-bit samples")
        if color_type == 3 and len(transparency) > len(palette) / 3:
            raise ValueError("Indexed PNG tRNS exceeds its palette length")
        if color_type in (4, 6):
            raise ValueError(f"PNG color type {color_type} cannot contain tRNS")

    transparent_gray = int.from_bytes(transparency[0:2], "big") if color_type == 0 and transparency is not None else -1
    transparent_red = int.from_bytes(transparency[0:2], "big") if color_type == 2 and transparency is not None else -1
    transparent_green = int.from_bytes(transparency[2:4], "big") if color_type == 2 and transparency is not None else -1
    transparent_blue = int.from_bytes(transparency[4:6], "big") if color_type == 2 and transparency is not None else -1

    decoded = _decode_scanlines(b"".join(idat_chunks), width, height, components)
    count = width * height
    dec = np.frombuffer(bytes(decoded), np.uint8).reshape(count, components)
    rgba = np.empty((count, 4), dtype=np.uint8)
    if color_type == 0:
        value = dec[:, 0]
        rgba[:, 0:3] = value[:, None]
        rgba[:, 3] = np.where(value == transparent_gray, 0, 255)
    elif color_type == 2:
        rgba[:, 0:3] = dec
        rgba[:, 3] = np.where(
            (dec[:, 0] == transparent_red) & (dec[:, 1] == transparent_green) & (dec[:, 2] == transparent_blue),
            0,
            255,
        )
    elif color_type == 3:
        indices = dec[:, 0].astype(np.int64)
        out_of_range = indices * 3 + 2 >= len(palette)
        if out_of_range.any():
            raise ValueError(f"PNG palette index {indices[out_of_range][0]} is out of range")
        rgb = np.frombuffer(palette, np.uint8, len(palette)).reshape(-1, 3)[indices]
        rgba[:, 0:3] = rgb
        if transparency is not None:
            alpha = np.full(count, 255, dtype=np.uint8)
            in_key = indices < len(transparency)
            key = np.frombuffer(transparency, np.uint8)[indices[in_key]]
            alpha[in_key] = key
            rgba[:, 3] = alpha
        else:
            rgba[:, 3] = 255
    elif color_type == 4:
        rgba[:, 0:3] = dec[:, 0:1]
        rgba[:, 3] = dec[:, 1]
    else:
        rgba[:] = dec

    return Surface.from_rgba8(width, height, rgba.tobytes())
