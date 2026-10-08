"""External data-texture surfaces for the reactive (MIDI) and mesh (OBJ) effects.

Port of noisemaker-cpu ``src/runtime/external-textures.js`` (the reactive/mesh
import). Data textures uploaded from JS arrays on WebGL2 place array row 0 at GL
texture coordinate y = 0 (bottom-left origin). This port's CPU surfaces store
rows top-down and the GLSL samplers (``sampleNearestBottomLeft``,
``#texelFetch``) flip the y coordinate, so a data-texture surface must store the
uploaded array's rows reversed for both ``texture()`` and ``texelFetch()`` to
read the same texel the GPU reads. The mesh triangles adapter
(``mesh_render.py``) reads the raw uploaded arrays directly (GPU
``texelFetch(x, y)`` = ``data[(y * width + x) * 4]``, no flip) via
``renderOptions.externalInputs``.
"""

from __future__ import annotations

import numpy as np

from .surface import Surface


def flip_rgba_rows(data, width: int, height: int) -> np.ndarray:
    data = np.asarray(data, dtype=np.float32).ravel()
    flipped = np.empty(width * height * 4, dtype=np.float32)
    view = flipped.reshape(height, width * 4)
    source = data.reshape(height, width * 4)
    view[:] = source[::-1]
    return flipped


def external_data_surface(data, width: int, height: int) -> Surface:
    rows = flip_rgba_rows(data, width, height)
    surface = Surface(width, height, rows)
    surface.filter = "nearest"
    return surface