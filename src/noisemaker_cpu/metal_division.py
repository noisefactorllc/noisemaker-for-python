from __future__ import annotations

import base64
import math
import struct
from functools import lru_cache

import numpy as np

from ._metal_reciprocal import BITS, METAL_RECIPROCAL

_MIN_NORMAL = 1.1754943508222875e-38


@lru_cache(maxsize=1)
def reciprocal_deviations():
    stream = np.unpackbits(np.frombuffer(base64.b64decode(BITS), dtype=np.uint8), bitorder="little")
    result = np.zeros(1 << 23, dtype=np.uint8)
    cursor = 0
    for start in range(1, 1 << 23, 1 << 18):
        mantissas = np.arange(start, min(start + (1 << 18), 1 << 23), dtype=np.uint32)
        scaled = 140737488355328 / (8388608.0 + mantissas)
        position = scaled - np.floor(scaled)
        selected = mantissas[(position >= METAL_RECIPROCAL["bandLow"]) & (position <= METAL_RECIPROCAL["bandHigh"])]
        result[selected] = stream[cursor : cursor + len(selected)]
        cursor += len(selected)
    if cursor != METAL_RECIPROCAL["bandBits"] or int(result.sum()) != (
        METAL_RECIPROCAL["positiveDeviations"] + METAL_RECIPROCAL["negativeDeviations"]
    ):
        raise ValueError("Metal reciprocal capture is corrupt")
    return np.packbits(result, bitorder="little").tobytes()


def metal_reciprocal(value):
    rounded = float(np.float32(value))
    word = struct.unpack("<I", struct.pack("<f", rounded))[0]
    exponent = (word >> 23) & 0xFF
    if exponent == 0:
        return -math.inf if word >> 31 else math.inf
    if exponent == 0xFF:
        with np.errstate(invalid="ignore", divide="ignore"):
            return float(np.float32(np.divide(1.0, value)))
    exact = 1.0 / abs(rounded)
    with np.errstate(over="ignore"):
        reciprocal = float(np.float32(exact))
    mantissa = word & 0x7FFFFF
    if mantissa and ((reciprocal_deviations()[mantissa >> 3] >> (mantissa & 7)) & 1):
        bits = struct.unpack("<I", struct.pack("<f", reciprocal))[0]
        bits += 1 if reciprocal < exact else -1
        reciprocal = struct.unpack("<f", struct.pack("<I", bits))[0]
    if reciprocal < _MIN_NORMAL:
        reciprocal = 0.0
    return -reciprocal if word >> 31 else reciprocal


def metal_divide(dividend, divisor):
    with np.errstate(over="ignore", invalid="ignore"):
        rounded = float(np.float32(dividend))
    if rounded != 0 and abs(rounded) < _MIN_NORMAL:
        rounded = math.copysign(0.0, rounded)
    product = rounded * metal_reciprocal(divisor)
    if product != 0 and abs(product) < _MIN_NORMAL:
        return math.copysign(0.0, product)
    return product
