"""Regenerate the vendored Python bundle from the CDN.

Pipeline: cdn.fetch_effect -> preprocess.normalize -> parser.parse ->
codegen.emit_python -> write src/noisemaker_cpu/bundle/. Pure Python.

  python -m transpiler.build [--all | --only a,b] [--update-lock]
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

from .cdn import CDN_BASE, CDN_VERSION, eligible_ids, fetch_effect
from .codegen import emit_python
from .locked_particle_texture_sources import PARTICLE_TEXTURE_INPUT_SOURCES
from .parser import parse
from .preprocess import normalize
from .shared_enums import SHARED_ENUMS


def _resolve_shared_enums(params: dict) -> None:
    """Inline choices for member params that reference a shared enum by name only
    (the CDN bundle omits the name->index table). Mutates params in place."""
    for spec in params.values():
        if isinstance(spec, dict) and spec.get("type") == "member" and not spec.get("choices"):
            choices = SHARED_ENUMS.get(spec.get("enum"))
            if choices:
                spec["choices"] = dict(choices)


_HERE = os.path.dirname(__file__)
BUNDLE = os.path.normpath(os.path.join(_HERE, "..", "src", "noisemaker_cpu", "bundle"))
# These canonical JS kernels materialize vector declarations in Float32Array
# storage before later hash conversions or pigment calculations.
_JS_VECTOR_STORAGE_KEYS = frozenset({"synth3d/noise3d:precompute", "filter/strokes:stkSmear"})
# Effects whose canonical CPU implementation is a hand-written adapter with
# scalar temporaries (scripts/upstream compile-glsl adapters): every vector
# assignment there reads pre-assignment values, so compound assignments keep
# the atomic reduce form instead of the transpiler's component-wise expansion.
_ATOMIC_COMPOUND_KEYS = frozenset(
    {
        "classicNoisedeck/bitEffects:bitEffects",
        "classicNoisedeck/fractal:fractal",
        "filter/crt:crt",
        "filter/historicPalette:historicPalette",
        "filter/median:median",
        "filter/palette:palette",
        "filter/pixelSort:luminance",
        "filter/reindex:nmReindexApply",
        "filter/reindex:nmReindexStats",
        "filter/snow:snow",
        "synth/julia:julia",
        "synth/remap:remap",
    }
)


_LOCKED_BUILD_PROGRAM_SOURCES = {
    ("synth/media", "mediaInput"): {
        "locked_sha256": "68bacdb76940f91100e3d4a1e2bdfe8c70cb8565ccffbdfdfbc101262c05ab3b",
        "locked": "/*\n * Media input shader.\n * Normalizes camera or video textures and exposes crop controls while preserving aspect ratio.\n * Offset sliders are remapped prior to sampling so live adjustments never read outside the source texture.\n */\n\n#ifdef GL_ES\nprecision highp float;\n#endif\n\nuniform sampler2D imageTex;\nuniform vec2 imageSize;\nuniform vec2 resolution;\nuniform float time;\nuniform int position;\nuniform float rotation;\nuniform float scaleAmt;\nuniform float offsetX;\nuniform float offsetY;\nuniform int tiling;\nuniform int flip;\nuniform vec3 bgColor;\nuniform float bgAlpha;\n\nout vec4 fragColor;\n\n#define PI 3.14159265359\n#define TAU 6.28318530718\n\nfloat map(float value, float inMin, float inMax, float outMin, float outMax) {\n    return outMin + (outMax - outMin) * (value - inMin) / (inMax - inMin);\n}\n\nvec2 rotate2D(vec2 st, float rot) {\n    rot = map(rot, -180.0, 180.0, 0.5, -0.5);\n    float angle = rot * TAU * -1.0;\n\n    // Handle aspect ratio of input media\n    vec2 size = imageSize;\n    float aspect = size.x / size.y;\n    st -= vec2(0.5 * aspect, 0.5);\n    st = mat2(cos(angle), -sin(angle), sin(angle), cos(angle)) * st;\n    st += vec2(0.5 * aspect, 0.5);\n    return st;\n}\n\nvec2 tile(vec2 st) {\n    if (tiling == 0) {\n        // no tiling\n        return st;\n    } else if (tiling == 1) {\n        // tile both\n        return fract(st);\n    } else if (tiling == 2) {\n        // horiz only\n        return vec2(fract(st.x), st.y);\n    } else if (tiling == 3) {\n        // vert only\n        return vec2(st.x, fract(st.y));\n    }\n    return st;\n}\n\n// External uploads use straight alpha. Interpolate premultiplied texels so\n// transparent pixels cannot darken edges or bleed their hidden RGB into them.\nvec4 mediaTexel(ivec2 p, ivec2 size) {\n    vec4 c = texelFetch(imageTex, clamp(p, ivec2(0), size - 1), 0);\n    return vec4(c.rgb * c.a, c.a);\n}\n\nvec4 sampleMedia(vec2 uv) {\n    ivec2 size = textureSize(imageTex, 0);\n    vec2 p = uv * vec2(size) - 0.5;\n    ivec2 lo = ivec2(floor(p));\n    vec2 f = fract(p);\n    return mix(mix(mediaTexel(lo, size), mediaTexel(lo + ivec2(1, 0), size), f.x),\n               mix(mediaTexel(lo + ivec2(0, 1), size), mediaTexel(lo + ivec2(1, 1), size), f.x), f.y);\n}\n\nvec4 getImage(vec2 st) {\n    vec2 size = imageSize;\n    st = gl_FragCoord.xy / size;\n    st.y = 1.0 - st.y;\n\n    float scale = 100.0 / scaleAmt;\n\n    if (scale == 0.0) {\n        scale = 1.0;\n    }\n    st *= scale;\n\n    // Position adjustments based on anchor point\n    if (position == 0) {\n        // top left\n        st.y += (resolution.y / size.y * scale) - (scale - (1.0 / size.y * scale));\n    } else if (position == 1) {\n        // top center\n        st.x -= (resolution.x / size.x * scale * 0.5) - (0.5 - (1.0 / size.x * scale));\n        st.y += (resolution.y / size.y * scale) - (scale - (1.0 / size.y * scale));\n    } else if (position == 2) {\n        // top right\n        st.x -= (resolution.x / size.x * scale) - (1.0 - (1.0 / size.x * scale));\n        st.y += (resolution.y / size.y * scale) - (scale - (1.0 / size.y * scale));\n    } else if (position == 3) {\n        // mid left\n        st.y += (resolution.y / size.y * scale * 0.5) + (0.5 - (1.0 / size.y * scale)) - (scale);\n    } else if (position == 4) {\n        // mid center\n        st.x -= (resolution.x / size.x * scale * 0.5) - (0.5 - (1.0 / size.x * scale));\n        st.y += (resolution.y / size.y * scale * 0.5) + (0.5 - (1.0 / size.y * scale)) - (scale);\n    } else if (position == 5) {\n        // mid right\n        st.x -= (resolution.x / size.x * scale) - (1.0 - (1.0 / size.x * scale));\n        st.y += (resolution.y / size.y * scale * 0.5) + (0.5 - (1.0 / size.y * scale)) - (scale);\n    } else if (position == 6) {\n        // bottom left\n        st.y += 1.0 - (scale - (1.0 / size.y * scale));\n    } else if (position == 7) {\n        // bottom center\n        st.x -= (resolution.x / size.x * scale * 0.5) - (0.5 - (1.0 / size.x * scale));\n        st.y += 1.0 - (scale - (1.0 / size.y * scale));\n    } else if (position == 8) {\n        // bottom right\n        st.x -= (resolution.x / size.x * scale) - (1.0 - (1.0 / size.x * scale));\n        st.y += 1.0 - (scale - (1.0 / size.y * scale));\n    }\n\n    st.x -= map(offsetX, -100.0, 100.0, -resolution.x / size.x * scale, resolution.x / size.x * scale) * 1.5;\n    st.y -= map(offsetY, -100.0, 100.0, -resolution.y / size.y * scale, resolution.y / size.y * scale) * 1.5;\n\n    // Correct for aspect ratio before rotation\n    st.x *= size.x / size.y;\n    // Zero rotation is an exact identity. Avoid backend-dependent rounding\n    // in the remap/trigonometry path before bilinear texture filtering.\n    if (rotation != 0.0) st = rotate2D(st, rotation);\n    st.x /= size.x / size.y;\n\n    st = tile(st);\n\n    // Nudge 1px up and left to center properly\n    st += 1.0 / size;\n\n    // Flip and mirror operations\n    if (flip == 1) {\n       // flip both\n       st.x = 1.0 - st.x;\n       st.y = 1.0 - st.y;\n    } else if (flip == 2) {\n       // flip h\n       st.x = 1.0 - st.x;\n    } else if (flip == 3) {\n       // flip v\n       st.y = 1.0 - st.y;\n    } else if (flip == 11) {\n       // mirror lr\n       if (st.x > 0.5) {\n           st.x = 1.0 - st.x;\n       }\n    } else if (flip == 12) {\n       // mirror rl\n       if (st.x < 0.5) {\n           st.x = 1.0 - st.x;\n       }\n    } else if (flip == 13) {\n       // mirror ud\n       if (st.y > 0.5) {\n           st.y = 1.0 - st.y;\n       }\n    } else if (flip == 14) {\n       // mirror du\n       if (st.y < 0.5) {\n           st.y = 1.0 - st.y;\n       }\n    } else if (flip == 15) {\n       // mirror lr ud\n       if (st.x > 0.5) {\n           st.x = 1.0 - st.x;\n       }\n       if (st.y > 0.5) {\n           st.y = 1.0 - st.y;\n       }\n    } else if (flip == 16) {\n       // mirror lr du\n       if (st.x > 0.5) {\n           st.x = 1.0 - st.x;\n       }\n       if (st.y < 0.5) {\n           st.y = 1.0 - st.y;\n       }\n    } else if (flip == 17) {\n       // mirror rl ud\n       if (st.x < 0.5) {\n           st.x = 1.0 - st.x;\n       }\n       if (st.y > 0.5) {\n           st.y = 1.0 - st.y;\n       }\n    } else if (flip == 18) {\n       // mirror rl du\n       if (st.x < 0.5) {\n           st.x = 1.0 - st.x;\n       }\n       if (st.y < 0.5) {\n           st.y = 1.0 - st.y;\n       }\n    }\n\n    vec4 text = sampleMedia(st);\n\n    if (st.x < 0.0 || st.x > 1.0 || st.y < 0.0 || st.y > 1.0) {\n        // Don't draw texture if out of coordinate bounds\n        return vec4(bgColor * bgAlpha, bgAlpha);\n    }\n\n    return text;\n}\n\n\nvoid main() {\n    vec2 st = gl_FragCoord.xy / resolution;\n    st.y = 1.0 - st.y;\n\n    fragColor = getImage(st);\n}",
        "source": "/*\n * Media input shader.\n * Normalizes camera or video textures and exposes crop controls while preserving aspect ratio.\n * Offset sliders are remapped prior to sampling so live adjustments never read outside the source texture.\n */\n\n#ifdef GL_ES\nprecision highp float;\n#endif\n\nuniform sampler2D imageTex;\nuniform vec2 imageSize;\nuniform vec2 resolution;\nuniform vec2 tileOffset;\nuniform vec2 fullResolution;\nuniform float time;\nuniform int position;\nuniform float rotation;\nuniform float scaleAmt;\nuniform float offsetX;\nuniform float offsetY;\nuniform int tiling;\nuniform int flip;\nuniform vec3 bgColor;\nuniform float bgAlpha;\n\nout vec4 fragColor;\n\n#define PI 3.14159265359\n#define TAU 6.28318530718\n\nfloat map(float value, float inMin, float inMax, float outMin, float outMax) {\n    return outMin + (outMax - outMin) * (value - inMin) / (inMax - inMin);\n}\n\nvec2 rotate2D(vec2 st, float rot) {\n    rot = map(rot, -180.0, 180.0, 0.5, -0.5);\n    float angle = rot * TAU * -1.0;\n\n    // Handle aspect ratio of input media\n    vec2 size = imageSize;\n    float aspect = size.x / size.y;\n    st -= vec2(0.5 * aspect, 0.5);\n    st = mat2(cos(angle), -sin(angle), sin(angle), cos(angle)) * st;\n    st += vec2(0.5 * aspect, 0.5);\n    return st;\n}\n\nvec2 tile(vec2 st) {\n    if (tiling == 0) {\n        // no tiling\n        return st;\n    } else if (tiling == 1) {\n        // tile both\n        return fract(st);\n    } else if (tiling == 2) {\n        // horiz only\n        return vec2(fract(st.x), st.y);\n    } else if (tiling == 3) {\n        // vert only\n        return vec2(st.x, fract(st.y));\n    }\n    return st;\n}\n\n// External uploads use straight alpha. Interpolate premultiplied texels so\n// transparent pixels cannot darken edges or bleed their hidden RGB into them.\nvec4 mediaTexel(ivec2 p, ivec2 size) {\n    vec4 c = texelFetch(imageTex, clamp(p, ivec2(0), size - 1), 0);\n    return vec4(c.rgb * c.a, c.a);\n}\n\nvec4 sampleMedia(vec2 uv) {\n    ivec2 size = textureSize(imageTex, 0);\n    vec2 p = uv * vec2(size) - 0.5;\n    ivec2 lo = ivec2(floor(p));\n    vec2 f = fract(p);\n    return mix(mix(mediaTexel(lo, size), mediaTexel(lo + ivec2(1, 0), size), f.x),\n               mix(mediaTexel(lo + ivec2(0, 1), size), mediaTexel(lo + ivec2(1, 1), size), f.x), f.y);\n}\n\nvec4 getImage(vec2 st) {\n    vec2 size = imageSize;\n    // Under tiled print export gl_FragCoord is tile-local. Add the tile's\n    // global offset so every tile and the untiled reference sample the same\n    // absolute image pixel. Branch on the runtime offset so the untiled\n    // path keeps the original expression bit-for-bit across compilers with\n    // relaxed math (tileOffset is 0 when not tiling).\n    if (tileOffset.x == 0.0 && tileOffset.y == 0.0) {\n        st = gl_FragCoord.xy / size;\n    } else {\n        st = (gl_FragCoord.xy + tileOffset) / size;\n    }\n    st.y = 1.0 - st.y;\n\n    float scale = 100.0 / scaleAmt;\n\n    if (scale == 0.0) {\n        scale = 1.0;\n    }\n    st *= scale;\n\n    // Keep the original untiled math exact on both backends.\n    if (fullResolution.x > 0.0 && (fullResolution.x != resolution.x || fullResolution.y != resolution.y)) {\n        // Position adjustments based on anchor point\n        if (position == 0) {\n            // top left\n            st.y += (fullResolution.y / size.y * scale) - (scale - (1.0 / size.y * scale));\n        } else if (position == 1) {\n            // top center\n            st.x -= (fullResolution.x / size.x * scale * 0.5) - (0.5 - (1.0 / size.x * scale));\n            st.y += (fullResolution.y / size.y * scale) - (scale - (1.0 / size.y * scale));\n        } else if (position == 2) {\n            // top right\n            st.x -= (fullResolution.x / size.x * scale) - (1.0 - (1.0 / size.x * scale));\n            st.y += (fullResolution.y / size.y * scale) - (scale - (1.0 / size.y * scale));\n        } else if (position == 3) {\n            // mid left\n            st.y += (fullResolution.y / size.y * scale * 0.5) + (0.5 - (1.0 / size.y * scale)) - (scale);\n        } else if (position == 4) {\n            // mid center\n            st.x -= (fullResolution.x / size.x * scale * 0.5) - (0.5 - (1.0 / size.x * scale));\n            st.y += (fullResolution.y / size.y * scale * 0.5) + (0.5 - (1.0 / size.y * scale)) - (scale);\n        } else if (position == 5) {\n            // mid right\n            st.x -= (fullResolution.x / size.x * scale) - (1.0 - (1.0 / size.x * scale));\n            st.y += (fullResolution.y / size.y * scale * 0.5) + (0.5 - (1.0 / size.y * scale)) - (scale);\n        } else if (position == 6) {\n            // bottom left\n            st.y += 1.0 - (scale - (1.0 / size.y * scale));\n        } else if (position == 7) {\n            // bottom center\n            st.x -= (fullResolution.x / size.x * scale * 0.5) - (0.5 - (1.0 / size.x * scale));\n            st.y += 1.0 - (scale - (1.0 / size.y * scale));\n        } else if (position == 8) {\n            // bottom right\n            st.x -= (fullResolution.x / size.x * scale) - (1.0 - (1.0 / size.x * scale));\n            st.y += 1.0 - (scale - (1.0 / size.y * scale));\n        }\n\n        st.x -= map(offsetX, -100.0, 100.0, -fullResolution.x / size.x * scale, fullResolution.x / size.x * scale) * 1.5;\n        st.y -= map(offsetY, -100.0, 100.0, -fullResolution.y / size.y * scale, fullResolution.y / size.y * scale) * 1.5;\n    } else {\n        // Position adjustments based on anchor point\n        if (position == 0) {\n            // top left\n            st.y += (resolution.y / size.y * scale) - (scale - (1.0 / size.y * scale));\n        } else if (position == 1) {\n            // top center\n            st.x -= (resolution.x / size.x * scale * 0.5) - (0.5 - (1.0 / size.x * scale));\n            st.y += (resolution.y / size.y * scale) - (scale - (1.0 / size.y * scale));\n        } else if (position == 2) {\n            // top right\n            st.x -= (resolution.x / size.x * scale) - (1.0 - (1.0 / size.x * scale));\n            st.y += (resolution.y / size.y * scale) - (scale - (1.0 / size.y * scale));\n        } else if (position == 3) {\n            // mid left\n            st.y += (resolution.y / size.y * scale * 0.5) + (0.5 - (1.0 / size.y * scale)) - (scale);\n        } else if (position == 4) {\n            // mid center\n            st.x -= (resolution.x / size.x * scale * 0.5) - (0.5 - (1.0 / size.x * scale));\n            st.y += (resolution.y / size.y * scale * 0.5) + (0.5 - (1.0 / size.y * scale)) - (scale);\n        } else if (position == 5) {\n            // mid right\n            st.x -= (resolution.x / size.x * scale) - (1.0 - (1.0 / size.x * scale));\n            st.y += (resolution.y / size.y * scale * 0.5) + (0.5 - (1.0 / size.y * scale)) - (scale);\n        } else if (position == 6) {\n            // bottom left\n            st.y += 1.0 - (scale - (1.0 / size.y * scale));\n        } else if (position == 7) {\n            // bottom center\n            st.x -= (resolution.x / size.x * scale * 0.5) - (0.5 - (1.0 / size.x * scale));\n            st.y += 1.0 - (scale - (1.0 / size.y * scale));\n        } else if (position == 8) {\n            // bottom right\n            st.x -= (resolution.x / size.x * scale) - (1.0 - (1.0 / size.x * scale));\n            st.y += 1.0 - (scale - (1.0 / size.y * scale));\n        }\n\n        st.x -= map(offsetX, -100.0, 100.0, -resolution.x / size.x * scale, resolution.x / size.x * scale) * 1.5;\n        st.y -= map(offsetY, -100.0, 100.0, -resolution.y / size.y * scale, resolution.y / size.y * scale) * 1.5;\n    }\n\n    // Correct for aspect ratio before rotation\n    st.x *= size.x / size.y;\n    // Zero rotation is an exact identity. Avoid backend-dependent rounding\n    // in the remap/trigonometry path before bilinear texture filtering.\n    if (rotation != 0.0) st = rotate2D(st, rotation);\n    st.x /= size.x / size.y;\n\n    st = tile(st);\n\n    // Nudge 1px up and left to center properly\n    st += 1.0 / size;\n\n    // Flip and mirror operations\n    if (flip == 1) {\n       // flip both\n       st.x = 1.0 - st.x;\n       st.y = 1.0 - st.y;\n    } else if (flip == 2) {\n       // flip h\n       st.x = 1.0 - st.x;\n    } else if (flip == 3) {\n       // flip v\n       st.y = 1.0 - st.y;\n    } else if (flip == 11) {\n       // mirror lr\n       if (st.x > 0.5) {\n           st.x = 1.0 - st.x;\n       }\n    } else if (flip == 12) {\n       // mirror rl\n       if (st.x < 0.5) {\n           st.x = 1.0 - st.x;\n       }\n    } else if (flip == 13) {\n       // mirror ud\n       if (st.y > 0.5) {\n           st.y = 1.0 - st.y;\n       }\n    } else if (flip == 14) {\n       // mirror du\n       if (st.y < 0.5) {\n           st.y = 1.0 - st.y;\n       }\n    } else if (flip == 15) {\n       // mirror lr ud\n       if (st.x > 0.5) {\n           st.x = 1.0 - st.x;\n       }\n       if (st.y > 0.5) {\n           st.y = 1.0 - st.y;\n       }\n    } else if (flip == 16) {\n       // mirror lr du\n       if (st.x > 0.5) {\n           st.x = 1.0 - st.x;\n       }\n       if (st.y < 0.5) {\n           st.y = 1.0 - st.y;\n       }\n    } else if (flip == 17) {\n       // mirror rl ud\n       if (st.x < 0.5) {\n           st.x = 1.0 - st.x;\n       }\n       if (st.y > 0.5) {\n           st.y = 1.0 - st.y;\n       }\n    } else if (flip == 18) {\n       // mirror rl du\n       if (st.x < 0.5) {\n           st.x = 1.0 - st.x;\n       }\n       if (st.y < 0.5) {\n           st.y = 1.0 - st.y;\n       }\n    }\n\n    vec4 text = sampleMedia(st);\n\n    if (st.x < 0.0 || st.x > 1.0 || st.y < 0.0 || st.y > 1.0) {\n        // Don't draw texture if out of coordinate bounds\n        return vec4(bgColor * bgAlpha, bgAlpha);\n    }\n\n    return text;\n}\n\n\nvoid main() {\n    vec2 st = gl_FragCoord.xy / resolution;\n    st.y = 1.0 - st.y;\n\n    fragColor = getImage(st);\n}\n",
    },
    ("synth3d/cellularAutomata3d", "simulate"): {
        "locked_sha256": "d5533f317f8ffe545386591fa317750bdca679402d027740b2d2488978575482",
        "locked": '/*\n * 3D Cellular Automata simulation shader (GLSL)\n * Implements various 3D CA rules with Moore (26) or Von Neumann (6) neighborhoods\n * Self-initializing: detects empty buffer and seeds on first frame\n */\n\n#version 300 es\nprecision highp float;\n\nuniform float time;\nuniform int seed;\nuniform int volumeSize;\nuniform int ruleIndex;\nuniform int neighborMode;\nuniform float speed;\nuniform float density;\nuniform float weight;\nuniform bool resetState;\nuniform sampler2D stateTex;\nuniform sampler2D seedTex;  // 3D input volume atlas (inputTex3d)\n\nout vec4 fragColor;\n\n// Hash for initialization\nfloat hash3(vec3 p) {\n    p = p + float(seed) * 0.1;\n    p = fract(p * vec3(0.1031, 0.1030, 0.0973));\n    p += dot(p, p.yxz + 33.33);\n    return fract((p.x + p.y) * p.z);\n}\n\n// Helper to convert 3D voxel coords to 2D atlas texel coords\nivec2 atlasTexel(ivec3 p, int volSize) {\n    // Wrap coordinates for periodic boundary\n    ivec3 wrapped = ivec3(\n        (p.x + volSize) % volSize,\n        (p.y + volSize) % volSize,\n        (p.z + volSize) % volSize\n    );\n    return ivec2(wrapped.x, wrapped.y + wrapped.z * volSize);\n}\n\n// Sample state at voxel coordinate with wrapping\nvec4 sampleState(ivec3 voxel, int volSize) {\n    return texelFetch(stateTex, atlasTexel(voxel, volSize), 0);\n}\n\n// Sample seed texture at voxel coordinate (for inputTex3d seeding)\nvec4 sampleSeed(ivec3 voxel, int volSize) {\n    return texelFetch(seedTex, atlasTexel(voxel, volSize), 0);\n}\n\n// Count alive neighbors using Moore neighborhood (26 neighbors)\nint countMooreNeighbors(ivec3 voxel, int volSize) {\n    int count = 0;\n    for (int dz = -1; dz <= 1; dz++) {\n        for (int dy = -1; dy <= 1; dy++) {\n            for (int dx = -1; dx <= 1; dx++) {\n                if (dx == 0 && dy == 0 && dz == 0) continue;\n                vec4 neighbor = sampleState(voxel + ivec3(dx, dy, dz), volSize);\n                if (neighbor.r > 0.5) count++;\n            }\n        }\n    }\n    return count;\n}\n\n// Count alive neighbors using Von Neumann neighborhood (6 neighbors)\nint countVonNeumannNeighbors(ivec3 voxel, int volSize) {\n    int count = 0;\n    vec4 xp = sampleState(voxel + ivec3(1, 0, 0), volSize);\n    vec4 xn = sampleState(voxel + ivec3(-1, 0, 0), volSize);\n    vec4 yp = sampleState(voxel + ivec3(0, 1, 0), volSize);\n    vec4 yn = sampleState(voxel + ivec3(0, -1, 0), volSize);\n    vec4 zp = sampleState(voxel + ivec3(0, 0, 1), volSize);\n    vec4 zn = sampleState(voxel + ivec3(0, 0, -1), volSize);\n    \n    if (xp.r > 0.5) count++;\n    if (xn.r > 0.5) count++;\n    if (yp.r > 0.5) count++;\n    if (yn.r > 0.5) count++;\n    if (zp.r > 0.5) count++;\n    if (zn.r > 0.5) count++;\n    \n    return count;\n}\n\n/*\n * 3D CA Rulesets (Born/Survive notation with Moore 26-neighborhood)\n * \n * 0: 445M       - B4/S4 (stable crystalline structures)\n * 1: 678 678    - B6,7,8/S6,7,8 (cloud-like growth)\n * 2: Amoeba     - B9-26/S5-7,12-13,15 (organic amoeba shapes)\n * 3: Builder1   - B4,6,8-9/S3-6,9 (structured builders)\n * 4: Builder2   - B3/S2-3 (classic 3D life variant)\n * 5: Clouds     - B13-26/S13-26 (dense cloud formations)\n * 6: Crystal    - B1,3/S1-2,4 (crystal growth patterns)\n * 7: Diamoeba   - B5-7,12/S5-8 (diamond-like amoeba)\n * 8: Pyroclastic- B4,5,6,7/S6,7,8 (volcanic-like expansion)\n * 9: Slow Decay - B4/S3,4 (slowly decaying structures)\n * 10: Spikey    - B5-8/S5-6,9 (spikey growth patterns)\n */\n\n// Check if cell should be born\nbool shouldBeBorn(int n, int rule) {\n    if (rule == 0) return n == 4;                                       // 445M\n    if (rule == 1) return n >= 6 && n <= 8;                             // 678 678\n    if (rule == 2) return n >= 9;                                        // Amoeba\n    if (rule == 3) return n == 4 || n == 6 || n == 8 || n == 9;         // Builder1\n    if (rule == 4) return n == 3;                                        // Builder2 (3D Life)\n    if (rule == 5) return n >= 13;                                       // Clouds\n    if (rule == 6) return n == 1 || n == 3;                              // Crystal\n    if (rule == 7) return n >= 5 && n <= 7 || n == 12;                  // Diamoeba\n    if (rule == 8) return n >= 4 && n <= 7;                              // Pyroclastic\n    if (rule == 9) return n == 4;                                        // Slow Decay\n    if (rule == 10) return n >= 5 && n <= 8;                             // Spikey\n    return false;\n}\n\n// Check if cell should survive\nbool shouldSurvive(int n, int rule) {\n    if (rule == 0) return n == 4;                                        // 445M\n    if (rule == 1) return n >= 6 && n <= 8;                              // 678 678\n    if (rule == 2) return (n >= 5 && n <= 7) || n == 12 || n == 13 || n == 15;  // Amoeba\n    if (rule == 3) return (n >= 3 && n <= 6) || n == 9;                  // Builder1\n    if (rule == 4) return n == 2 || n == 3;                              // Builder2 (3D Life)\n    if (rule == 5) return n >= 13;                                       // Clouds\n    if (rule == 6) return n == 1 || n == 2 || n == 4;                    // Crystal\n    if (rule == 7) return n >= 5 && n <= 8;                              // Diamoeba\n    if (rule == 8) return n >= 6 && n <= 8;                              // Pyroclastic\n    if (rule == 9) return n == 3 || n == 4;                              // Slow Decay\n    if (rule == 10) return n == 5 || n == 6 || n == 9;                   // Spikey\n    return false;\n}\n\nvoid main() {\n    int volSize = volumeSize;\n    float volSizeF = float(volSize);\n    \n    // Decode voxel position from atlas\n    ivec2 pixelCoord = ivec2(gl_FragCoord.xy);\n    int x = pixelCoord.x;\n    int y = pixelCoord.y % volSize;\n    int z = pixelCoord.y / volSize;\n    ivec3 voxel = ivec3(x, y, z);\n    \n    // Bounds check\n    if (x >= volSize || y >= volSize || z >= volSize) {\n        fragColor = vec4(0.0);\n        return;\n    }\n    \n    // Current state\n    vec4 state = sampleState(voxel, volSize);\n    float alive = state.r;\n    float age = state.g;\n    \n    // Self-initialization or reset: detect empty buffer (first frame) or reset button\n    bool bufferIsEmpty = (state.r == 0.0 && state.g == 0.0 && state.b == 0.0 && state.a == 0.0);\n    \n    if (bufferIsEmpty || resetState) {\n        // Check if we have input from seedTex (inputTex3d)\n        vec4 seedVal = sampleSeed(voxel, volSize);\n        bool hasSeedInput = (seedVal.r > 0.0 || seedVal.g > 0.0 || seedVal.b > 0.0);\n        \n        if (hasSeedInput) {\n            // Use seed texture luminance to determine initial alive state\n            float lum = 0.299 * seedVal.r + 0.587 * seedVal.g + 0.114 * seedVal.b;\n            alive = lum > 0.5 ? 1.0 : 0.0;\n            age = 0.0;\n        } else {\n            // Initialize with random sparse distribution\n            vec3 p = vec3(float(x), float(y), float(z));\n            float h = hash3(p);\n            float threshold = density * 0.01;\n            \n            // Seed a sphere in the center plus random cells\n            vec3 center = vec3(volSizeF * 0.5);\n            float dist = length(p - center);\n            float radius = volSizeF * 0.15;\n            \n            if (h < threshold || dist < radius) {\n                alive = 1.0;\n                age = 0.0;\n            } else {\n                alive = 0.0;\n                age = 0.0;\n            }\n        }\n        \n        fragColor = vec4(alive, alive, alive, 1.0);\n        return;\n    }\n    \n    // Count neighbors based on neighborhood mode\n    int neighbors;\n    if (neighborMode == 0) {\n        neighbors = countMooreNeighbors(voxel, volSize);\n    } else {\n        neighbors = countVonNeumannNeighbors(voxel, volSize);\n    }\n    \n    // Apply CA rules\n    float newAlive = 0.0;\n    float newAge = age;\n    \n    if (alive > 0.5) {\n        // Cell is alive - check survival\n        if (shouldSurvive(neighbors, ruleIndex)) {\n            newAlive = 1.0;\n            newAge = min(age + 0.01, 1.0);  // Age increases while alive\n        } else {\n            newAlive = 0.0;\n            newAge = 0.0;\n        }\n    } else {\n        // Cell is dead - check birth\n        if (shouldBeBorn(neighbors, ruleIndex)) {\n            newAlive = 1.0;\n            newAge = 0.0;\n        } else {\n            newAlive = 0.0;\n            newAge = 0.0;\n        }\n    }\n    \n    // Speed control - interpolate between states\n    float animSpeed = speed * 0.01;\n    float finalAlive = mix(alive, newAlive, animSpeed);\n    float finalAge = mix(age, newAge, animSpeed);\n    \n    // Apply input weight blending from seedTex (inputTex3d)\n    if (weight > 0.0) {\n        vec4 seedVal = sampleSeed(voxel, volSize);\n        float seedLum = 0.299 * seedVal.r + 0.587 * seedVal.g + 0.114 * seedVal.b;\n        finalAlive = mix(finalAlive, seedLum, weight * 0.01);\n    }\n    \n    fragColor = vec4(finalAlive, finalAlive, finalAlive, 1.0);\n}',
        "source": '/*\n * 3D Cellular Automata simulation shader (GLSL)\n * Implements various 3D CA rules with Moore (26) or Von Neumann (6) neighborhoods\n * Self-initializing: detects empty buffer and seeds on first frame\n */\n\n#version 300 es\nprecision highp float;\n\nuniform float time;\nuniform int seed;\nuniform int volumeSize;\nuniform int ruleIndex;\nuniform int neighborMode;\nuniform float speed;\nuniform float density;\nuniform float weight;\nuniform int colorMode;\nuniform bool resetState;\nuniform sampler2D stateTex;\nuniform sampler2D seedTex;  // 3D input volume atlas (inputTex3d)\n\nout vec4 fragColor;\n\n// Hash for initialization\nfloat hash3(vec3 p) {\n    p = p + float(seed) * 0.1;\n    p = fract(p * vec3(0.1031, 0.1030, 0.0973));\n    p += dot(p, p.yxz + 33.33);\n    return fract((p.x + p.y) * p.z);\n}\n\n// Helper to convert 3D voxel coords to 2D atlas texel coords\nivec2 atlasTexel(ivec3 p, int volSize) {\n    // Wrap coordinates for periodic boundary\n    ivec3 wrapped = ivec3(\n        (p.x + volSize) % volSize,\n        (p.y + volSize) % volSize,\n        (p.z + volSize) % volSize\n    );\n    return ivec2(wrapped.x, wrapped.y + wrapped.z * volSize);\n}\n\n// Sample state at voxel coordinate with wrapping\nvec4 sampleState(ivec3 voxel, int volSize) {\n    return texelFetch(stateTex, atlasTexel(voxel, volSize), 0);\n}\n\n// Sample seed texture at voxel coordinate (for inputTex3d seeding)\nvec4 sampleSeed(ivec3 voxel, int volSize) {\n    return texelFetch(seedTex, atlasTexel(voxel, volSize), 0);\n}\n\n// The state keeps alive in red and age in green. render3d reads density from\n// red and shades with the RGB color unless it is gray, so mono writes alive to\n// every channel, and age keeps the age in green and shades young cells red and\n// older cells toward yellow.\nvec4 packState(float alive, float age) {\n    if (colorMode == 1) return vec4(alive, age, 0.0, 1.0);\n    return vec4(alive, alive, alive, 1.0);\n}\n\n// Count alive neighbors using Moore neighborhood (26 neighbors)\nint countMooreNeighbors(ivec3 voxel, int volSize) {\n    int count = 0;\n    for (int dz = -1; dz <= 1; dz++) {\n        for (int dy = -1; dy <= 1; dy++) {\n            for (int dx = -1; dx <= 1; dx++) {\n                if (dx == 0 && dy == 0 && dz == 0) continue;\n                vec4 neighbor = sampleState(voxel + ivec3(dx, dy, dz), volSize);\n                if (neighbor.r > 0.5) count++;\n            }\n        }\n    }\n    return count;\n}\n\n// Count alive neighbors using Von Neumann neighborhood (6 neighbors)\nint countVonNeumannNeighbors(ivec3 voxel, int volSize) {\n    int count = 0;\n    vec4 xp = sampleState(voxel + ivec3(1, 0, 0), volSize);\n    vec4 xn = sampleState(voxel + ivec3(-1, 0, 0), volSize);\n    vec4 yp = sampleState(voxel + ivec3(0, 1, 0), volSize);\n    vec4 yn = sampleState(voxel + ivec3(0, -1, 0), volSize);\n    vec4 zp = sampleState(voxel + ivec3(0, 0, 1), volSize);\n    vec4 zn = sampleState(voxel + ivec3(0, 0, -1), volSize);\n    \n    if (xp.r > 0.5) count++;\n    if (xn.r > 0.5) count++;\n    if (yp.r > 0.5) count++;\n    if (yn.r > 0.5) count++;\n    if (zp.r > 0.5) count++;\n    if (zn.r > 0.5) count++;\n    \n    return count;\n}\n\n/*\n * 3D CA Rulesets (Born/Survive notation with Moore 26-neighborhood)\n * \n * 0: 445M       - B4/S4 (stable crystalline structures)\n * 1: 678 678    - B6,7,8/S6,7,8 (cloud-like growth)\n * 2: Amoeba     - B9-26/S5-7,12-13,15 (organic amoeba shapes)\n * 3: Builder1   - B4,6,8-9/S3-6,9 (structured builders)\n * 4: Builder2   - B3/S2-3 (classic 3D life variant)\n * 5: Clouds     - B13-26/S13-26 (dense cloud formations)\n * 6: Crystal    - B1,3/S1-2,4 (crystal growth patterns)\n * 7: Diamoeba   - B5-7,12/S5-8 (diamond-like amoeba)\n * 8: Pyroclastic- B4,5,6,7/S6,7,8 (volcanic-like expansion)\n * 9: Slow Decay - B4/S3,4 (slowly decaying structures)\n * 10: Spikey    - B5-8/S5-6,9 (spikey growth patterns)\n */\n\n// Check if cell should be born\nbool shouldBeBorn(int n, int rule) {\n    if (rule == 0) return n == 4;                                       // 445M\n    if (rule == 1) return n >= 6 && n <= 8;                             // 678 678\n    if (rule == 2) return n >= 9;                                        // Amoeba\n    if (rule == 3) return n == 4 || n == 6 || n == 8 || n == 9;         // Builder1\n    if (rule == 4) return n == 3;                                        // Builder2 (3D Life)\n    if (rule == 5) return n >= 13;                                       // Clouds\n    if (rule == 6) return n == 1 || n == 3;                              // Crystal\n    if (rule == 7) return n >= 5 && n <= 7 || n == 12;                  // Diamoeba\n    if (rule == 8) return n >= 4 && n <= 7;                              // Pyroclastic\n    if (rule == 9) return n == 4;                                        // Slow Decay\n    if (rule == 10) return n >= 5 && n <= 8;                             // Spikey\n    return false;\n}\n\n// Check if cell should survive\nbool shouldSurvive(int n, int rule) {\n    if (rule == 0) return n == 4;                                        // 445M\n    if (rule == 1) return n >= 6 && n <= 8;                              // 678 678\n    if (rule == 2) return (n >= 5 && n <= 7) || n == 12 || n == 13 || n == 15;  // Amoeba\n    if (rule == 3) return (n >= 3 && n <= 6) || n == 9;                  // Builder1\n    if (rule == 4) return n == 2 || n == 3;                              // Builder2 (3D Life)\n    if (rule == 5) return n >= 13;                                       // Clouds\n    if (rule == 6) return n == 1 || n == 2 || n == 4;                    // Crystal\n    if (rule == 7) return n >= 5 && n <= 8;                              // Diamoeba\n    if (rule == 8) return n >= 6 && n <= 8;                              // Pyroclastic\n    if (rule == 9) return n == 3 || n == 4;                              // Slow Decay\n    if (rule == 10) return n == 5 || n == 6 || n == 9;                   // Spikey\n    return false;\n}\n\nvoid main() {\n    int volSize = volumeSize;\n    float volSizeF = float(volSize);\n    \n    // Decode voxel position from atlas\n    ivec2 pixelCoord = ivec2(gl_FragCoord.xy);\n    int x = pixelCoord.x;\n    int y = pixelCoord.y % volSize;\n    int z = pixelCoord.y / volSize;\n    ivec3 voxel = ivec3(x, y, z);\n    \n    // Bounds check\n    if (x >= volSize || y >= volSize || z >= volSize) {\n        fragColor = vec4(0.0);\n        return;\n    }\n    \n    // Current state\n    vec4 state = sampleState(voxel, volSize);\n    float alive = state.r;\n    float age = state.g;\n    \n    // Self-initialization or reset: detect empty buffer (first frame) or reset button\n    bool bufferIsEmpty = (state.r == 0.0 && state.g == 0.0 && state.b == 0.0 && state.a == 0.0);\n    \n    if (bufferIsEmpty || resetState) {\n        // Check if we have input from seedTex (inputTex3d)\n        vec4 seedVal = sampleSeed(voxel, volSize);\n        bool hasSeedInput = (seedVal.r > 0.0 || seedVal.g > 0.0 || seedVal.b > 0.0);\n        \n        if (hasSeedInput) {\n            // Use seed texture luminance to determine initial alive state\n            float lum = 0.299 * seedVal.r + 0.587 * seedVal.g + 0.114 * seedVal.b;\n            alive = lum > 0.5 ? 1.0 : 0.0;\n            age = 0.0;\n        } else {\n            // Initialize with random sparse distribution\n            vec3 p = vec3(float(x), float(y), float(z));\n            float h = hash3(p);\n            float threshold = density * 0.01;\n            \n            // Seed a sphere in the center plus random cells\n            vec3 center = vec3(volSizeF * 0.5);\n            float dist = length(p - center);\n            float radius = volSizeF * 0.15;\n            \n            if (h < threshold || dist < radius) {\n                alive = 1.0;\n                age = 0.0;\n            } else {\n                alive = 0.0;\n                age = 0.0;\n            }\n        }\n        \n        fragColor = packState(alive, age);\n        return;\n    }\n    \n    // Count neighbors based on neighborhood mode\n    int neighbors;\n    if (neighborMode == 0) {\n        neighbors = countMooreNeighbors(voxel, volSize);\n    } else {\n        neighbors = countVonNeumannNeighbors(voxel, volSize);\n    }\n    \n    // Apply CA rules\n    float newAlive = 0.0;\n    float newAge = age;\n    \n    if (alive > 0.5) {\n        // Cell is alive - check survival\n        if (shouldSurvive(neighbors, ruleIndex)) {\n            newAlive = 1.0;\n            newAge = min(age + 0.01, 1.0);  // Age increases while alive\n        } else {\n            newAlive = 0.0;\n            newAge = 0.0;\n        }\n    } else {\n        // Cell is dead - check birth\n        if (shouldBeBorn(neighbors, ruleIndex)) {\n            newAlive = 1.0;\n            newAge = 0.0;\n        } else {\n            newAlive = 0.0;\n            newAge = 0.0;\n        }\n    }\n    \n    // Speed control - interpolate between states\n    float animSpeed = speed * 0.01;\n    float finalAlive = mix(alive, newAlive, animSpeed);\n    float finalAge = mix(age, newAge, animSpeed);\n    \n    // Apply input weight blending from seedTex (inputTex3d)\n    if (weight > 0.0) {\n        vec4 seedVal = sampleSeed(voxel, volSize);\n        float seedLum = 0.299 * seedVal.r + 0.587 * seedVal.g + 0.114 * seedVal.b;\n        finalAlive = mix(finalAlive, seedLum, weight * 0.01);\n    }\n    \n    fragColor = packState(finalAlive, finalAge);\n}\n',
    },
    ("filter/scatter", "scatterJitter"): {
        "locked_sha256": "2cf31ef7d6afceb95e3114c8f5a17d3626c7cba0226fe020f8cf637cf5254c19",
        "locked": "/*\n * Scatter - jitter pass (Diffuse / Spatter / frosted glass).\n * Each pixel samples the input at a random offset within [-radius, radius]\n * px on each axis, drawn from a 2D hash seeded by the pixel's global\n * (tile-aware) coordinate. \\`mode\\` selects how the offset is derived and how\n * the sampled pixel combines with the source pixel:\n *   normal (0)      - raw random offset; sampled value used directly.\n *   darkenOnly (1)  - raw random offset; min(src, sampled) per channel\n *                     (Diffuse Darken Only).\n *   lightenOnly (2) - raw random offset; max(src, sampled) per channel\n *                     (Diffuse Lighten Only).\n *   anisotropic (3) - the offset is projected onto the direction\n *                     perpendicular to the local luminance gradient, so the\n *                     scatter smears along edges/contours instead of\n *                     scattering isotropically (Diffuse\n *                     Anisotropic). Falls back to the raw offset where the\n *                     local gradient is ~zero (flat regions have no edge\n *                     direction to follow).\n *   clumped (4)     - the hash coordinate is quantized to 3px blocks before\n *                     hashing, so every pixel in a block shares the same\n *                     random offset, producing blocky clumps of shared\n *                     displacement instead of per-pixel grain.\n * scatterSmooth (the second pass) re-blends this pass's output with a 3x3\n * tent blur by \\`smoothness\\`.\n */\n\n#ifdef GL_ES\nprecision highp float;\n#endif\n\n// MODE is a compile-time define injected by the runtime (see definition.js\n// \\`globals.mode.define\\`), so the compiler drops the dead mode arms below.\n#ifndef MODE\n#define MODE 0\n#endif\n\nuniform sampler2D inputTex;\nuniform vec2 resolution;\nuniform vec2 tileOffset;\nuniform float radius;\nuniform int seed;\n\nout vec4 fragColor;\n\nvec2 hash22(vec2 p) {\n    vec3 p3 = fract(vec3(p.xyx) * vec3(0.1031, 0.1030, 0.0973));\n    p3 += dot(p3, p3.yzx + 33.33);\n    return fract((p3.xx + p3.yz) * p3.zy);\n}\n\nfloat lum(vec3 c) { return dot(c, vec3(0.2126, 0.7152, 0.0722)); }\n\n// Sobel gradient of luminance; used by anisotropic mode to find the local\n// edge direction (perpendicular to the gradient = along the edge).\nvec2 lumGradient(vec2 uv) {\n    vec2 px = 1.0 / resolution;\n    float tl = lum(texture(inputTex, uv + px * vec2(-1.0,  1.0)).rgb);\n    float  l = lum(texture(inputTex, uv + px * vec2(-1.0,  0.0)).rgb);\n    float bl = lum(texture(inputTex, uv + px * vec2(-1.0, -1.0)).rgb);\n    float tr = lum(texture(inputTex, uv + px * vec2( 1.0,  1.0)).rgb);\n    float  r = lum(texture(inputTex, uv + px * vec2( 1.0,  0.0)).rgb);\n    float br = lum(texture(inputTex, uv + px * vec2( 1.0, -1.0)).rgb);\n    float  t = lum(texture(inputTex, uv + px * vec2( 0.0,  1.0)).rgb);\n    float  b = lum(texture(inputTex, uv + px * vec2( 0.0, -1.0)).rgb);\n    return vec2(tr + 2.0 * r + br - tl - 2.0 * l - bl,\n                tl + 2.0 * t + tr - bl - 2.0 * b - br);\n}\n\nvoid main() {\n    vec2 uv = gl_FragCoord.xy / resolution;\n\n    // Seed with the global (tile-aware) coordinate, not gl_FragCoord.xy\n    // alone, so the scatter field is continuous across CLI render tiles\n    // instead of restarting at each tile's local origin.\n    vec2 globalCoord = gl_FragCoord.xy + tileOffset;\n\n    // Clumped mode: quantize the hash coordinate to 3px blocks BEFORE\n    // hashing so every pixel in a block shares the same random offset.\n    vec2 hashCoord = globalCoord;\n    #if MODE == 4\n        hashCoord = floor(globalCoord / 3.0) * 3.0;\n    #endif\n\n    vec2 rnd = hash22(hashCoord + float(seed) * 101.7) - 0.5;\n    vec2 offset = rnd * 2.0 * radius;\n\n    #if MODE == 3\n        // Anisotropic: project the offset onto the direction perpendicular\n        // to the local luminance gradient (edge-following smear).\n        vec2 grad = lumGradient(uv);\n        float gradLen = length(grad);\n        if (gradLen > 1e-5) {\n            vec2 perp = vec2(-grad.y, grad.x) / gradLen;\n            offset = dot(offset, perp) * perp;\n        }\n        // else: gradient ~zero (flat region) -- fall back to raw offset.\n    #endif\n\n    vec2 sampleUV = clamp((gl_FragCoord.xy + offset) / resolution, 0.0, 1.0);\n\n    vec4 src = texture(inputTex, uv);\n    vec4 samp = texture(inputTex, sampleUV);\n\n    vec4 result = samp;\n    #if MODE == 1\n        result = min(src, samp);\n    #elif MODE == 2\n        result = max(src, samp);\n    #endif\n\n    fragColor = result;\n}",
        "source": "/*\n * Scatter - jitter pass (Diffuse / Spatter / frosted glass).\n * Each pixel samples the input at a random offset within [-radius, radius]\n * px on each axis, drawn from an integer hash (PCG3D) of the pixel's global\n * (tile-aware) coordinate and `seed`, and reads the input texel nearest that\n * offset position. `mode` selects how the offset is derived and how\n * the sampled pixel combines with the source pixel:\n *   normal (0)      - raw random offset; sampled value used directly.\n *   darkenOnly (1)  - raw random offset; min(src, sampled) per channel\n *                     (Diffuse Darken Only).\n *   lightenOnly (2) - raw random offset; max(src, sampled) per channel\n *                     (Diffuse Lighten Only).\n *   anisotropic (3) - the offset is projected onto the direction\n *                     perpendicular to the local luminance gradient, so the\n *                     scatter smears along edges/contours instead of\n *                     scattering isotropically (Diffuse\n *                     Anisotropic). Falls back to the raw offset where the\n *                     local gradient is ~zero (flat regions have no edge\n *                     direction to follow).\n *   clumped (4)     - the hash coordinate is quantized to 3px blocks before\n *                     hashing, so every pixel in a block shares the same\n *                     random offset, producing blocky clumps of shared\n *                     displacement instead of per-pixel grain.\n * scatterSmooth (the second pass) re-blends this pass's output with a 3x3\n * tent blur by `smoothness`.\n */\n\n#ifdef GL_ES\nprecision highp float;\nprecision highp int;\n#endif\n\n// MODE is a compile-time define injected by the runtime (see definition.js\n// `globals.mode.define`), so the compiler drops the dead mode arms below.\n#ifndef MODE\n#define MODE 0\n#endif\n\nuniform sampler2D inputTex;\nuniform vec2 resolution;\nuniform vec2 tileOffset;\nuniform float radius;\nuniform int seed;\n\nout vec4 fragColor;\n\n// PCG3D integer hash (Jarzynski & Olano 2020). Unsigned arithmetic wraps the\n// same way on every compiler, so WebGL2 and WebGPU draw identical offsets; a\n// float hash rounds and fuses differently per compiler and drifts apart.\nuvec3 pcg3d(uvec3 v_in) {\n    uvec3 v = v_in * 1664525u + 1013904223u;\n    v.x = v.x + v.y * v.z;\n    v.y = v.y + v.z * v.x;\n    v.z = v.z + v.x * v.y;\n    v = v ^ (v >> uvec3(16u));\n    v.x = v.x + v.y * v.z;\n    v.y = v.y + v.z * v.x;\n    v.z = v.z + v.x * v.y;\n    return v;\n}\n\nfloat lum(vec3 c) { return dot(c, vec3(0.2126, 0.7152, 0.0722)); }\n\n// Sobel gradient of luminance; used by anisotropic mode to find the local\n// edge direction (perpendicular to the gradient = along the edge).\nvec2 lumGradient(vec2 uv) {\n    vec2 px = 1.0 / resolution;\n    float tl = lum(texture(inputTex, uv + px * vec2(-1.0,  1.0)).rgb);\n    float  l = lum(texture(inputTex, uv + px * vec2(-1.0,  0.0)).rgb);\n    float bl = lum(texture(inputTex, uv + px * vec2(-1.0, -1.0)).rgb);\n    float tr = lum(texture(inputTex, uv + px * vec2( 1.0,  1.0)).rgb);\n    float  r = lum(texture(inputTex, uv + px * vec2( 1.0,  0.0)).rgb);\n    float br = lum(texture(inputTex, uv + px * vec2( 1.0, -1.0)).rgb);\n    float  t = lum(texture(inputTex, uv + px * vec2( 0.0,  1.0)).rgb);\n    float  b = lum(texture(inputTex, uv + px * vec2( 0.0, -1.0)).rgb);\n    return vec2(tr + 2.0 * r + br - tl - 2.0 * l - bl,\n                tl + 2.0 * t + tr - bl - 2.0 * b - br);\n}\n\nvoid main() {\n    vec2 uv = gl_FragCoord.xy / resolution;\n    ivec2 texel = ivec2(gl_FragCoord.xy);\n    ivec2 texSize = textureSize(inputTex, 0);\n\n    // Seed with the global (tile-aware) coordinate, not gl_FragCoord.xy\n    // alone, so the scatter field is continuous across CLI render tiles\n    // instead of restarting at each tile's local origin.\n    vec2 globalCoord = gl_FragCoord.xy + tileOffset;\n\n    // Clumped mode: quantize the hash coordinate to 3px blocks BEFORE\n    // hashing so every pixel in a block shares the same random offset.\n    vec2 hashCoord = globalCoord;\n    #if MODE == 4\n        hashCoord = floor(globalCoord / 3.0) * 3.0;\n    #endif\n\n    uvec3 h = pcg3d(uvec3(uvec2(ivec2(floor(hashCoord))), uint(seed)));\n\n    // Offset in 1/256 px steps, in [-radius, radius) on each axis: the top 16\n    // hash bits scale the span 2 * radius * 256 in integers. radius * 256 is\n    // exact; the 128 px cap (far above the 25 px slider maximum) keeps the\n    // product within 32 bits.\n    uint r256 = uint(min(abs(radius), 128.0) * 256.0);\n    uvec2 steps = ((h.xy >> uvec2(16u)) * (2u * r256)) >> uvec2(16u);\n    vec2 offset = vec2(ivec2(steps) - int(r256)) / 256.0;\n\n    #if MODE == 3\n        // Anisotropic: project the offset onto the direction perpendicular\n        // to the local luminance gradient (edge-following smear).\n        vec2 grad = lumGradient(uv);\n        float gradLen = length(grad);\n        if (gradLen > 1e-5) {\n            vec2 perp = vec2(-grad.y, grad.x) / gradLen;\n            offset = dot(offset, perp) * perp;\n        }\n        // else: gradient ~zero (flat region) -- fall back to raw offset.\n    #endif\n\n    // Read the texel nearest the offset sample position, clamped to the edge.\n    // Outside anisotropic mode the offset is a multiple of 1/256, so\n    // offset + 0.5 and its floor are exact on both backends.\n    ivec2 sampleTexel = clamp(texel + ivec2(floor(offset + 0.5)), ivec2(0), texSize - 1);\n\n    vec4 src = texelFetch(inputTex, texel, 0);\n    vec4 samp = texelFetch(inputTex, sampleTexel, 0);\n\n    vec4 result = samp;\n    #if MODE == 1\n        result = min(src, samp);\n    #elif MODE == 2\n        result = max(src, samp);\n    #endif\n\n    fragColor = result;\n}\n",
    },
    # filter/craquelure, filter/stipple, and filter/feedback's hash/hue
    # programs changed at upstream 1faed961 (stipple and craquelure hash in
    # integers, feedback takes hue-shift steps in exact rounded division);
    # the locked CDN build predates all three.
    ("filter/craquelure", "craquelure"): {
        "locked_sha256": "4a4e45337334727178f889fe11cc59cf03b9830a6f8a9cf13689de900cd38219",
        "locked": '/*\n * Craquelure - cracked-plaster groove network with carved relief over the\n * image.\n *\n * Crack field: Voronoi\'s jittered-grid Voronoi cell (see voronoiCell in e.g.\n * filter/stipple.glsl) is extended here to voronoiF1F2, which tracks the\n * nearest (F1) AND second-nearest (F2) seed distances instead of just the\n * nearest cell id. (F2 - F1) is the standard "distance to the Voronoi\n * border" proxy: it is exactly 0 ON a cell border (where two seeds are\n * equidistant) and grows the further a point sits from any border, so\n * \\`k = 1 - smoothstep(0, edge, (F2-F1)*spacing)\\` is a ridge function that\n * peaks at 1 exactly on cell borders and falls to 0 within \\`edge\\` pixels\n * - i.e. the crack groove cross-section. \\`edge = 1.5 + depth/100*2\\` is\n * the groove\'s half-width in px, so \\`depth\\` widens the crack band.\n *\n * Voronoi jitter is fixed at 1.0 (the maximum value Voronoi\'s 3x3-neighbor\n * search window supports - see voronoiF1F2\'s docstring: the search is\n * exact for F1 at this jitter, with F2 only rarely under-counted near a\n * cell\'s corner) for maximally irregular, organic plate shapes, matching\n * real crazed plaster/glaze.\n *\n * Border wobble: before the Voronoi search, the sample position is\n * perturbed by two INDEPENDENT noise taps, one per axis -\n * \\`vec2(vnoise(gc/6), vnoise(gc/6 + vec2(37.7, 91.3))) * 2\\` px (same 2px\n * amplitude as a single-scalar wobble; the additive offset decorrelates\n * the second tap from the first). A single scalar broadcast to both axes\n * only displaces the sample along the (1,1) diagonal, leaving\n * diagonal-tangent border segments unperturbed - a visible blind spot.\n * Independent per-axis taps wobble the crack path in every direction, so\n * borders weave organically regardless of their local tangent angle.\n *\n * Wall shading: the crack mask k is re-evaluated at 4 neighboring\n * (gc +/- 1px on each axis) positions to build a true central-difference\n * gradient of k (5 bounded Voronoi evaluations total). A cheaper\n * forward-difference, as filter/relief\'s rlShade.glsl\n * uses for its cheap-to-sample blurred-luminance height field, would\n * bias the bevel normal off-axis for a feature this narrow, since k\'s\n * transition width can be as little as 1.5px). The height fed to filter/relief\'s\n * reliefShade (see filter/relief) is -k, NOT +k: a crack is a carved\n * groove (a dip), not a raised ridge, so height must FALL toward the\n * crack center. This is implemented by negating hC/hR/hT (hC = -kC, hR\n * = hC - centralGradX, hT = hC - centralGradY) so reliefShade\'s internal\n * forward-difference subtraction reproduces the true central-difference\n * gradient of -k exactly - equivalently, this flips the sign of the\n * gradient/normal reliefShade sees versus feeding +k directly, which is\n * what puts the lit wall on the correct (concave-groove) side of the\n * crack. Light angle is fixed at 135 degrees (filter/relief\'s default\n * convention - upper-left; craquelure exposes no\n * lightAngle param). reliefShade\'s flat-gradient (grad=0) baseline is\n * dot((0,0,1), normalize(vec3(cos135, sin135, 0.75))) = 0.75/1.25 = 0.6\n * EXACTLY, not 0.5 - the shade term is remapped from reliefShade\'s 0..1\n * output to a subtle \\`1 +/- 0.25*depth/100\\` multiplier band centered on\n * shade==0.6 (not 0.5), and additionally gated by \\`wallMask =\n * smoothstep(0, 0.02, gradMagK)\\` (gradMagK = length of the same\n * central-diff gradient of k used above) so the multiplier is pinned to\n * EXACTLY 1.0 on flat ground regardless of depth or any future light-\n * vector change, instead of leaking a small global brightening\n * everywhere (the old unmasked, 0.5-centered version leaked because\n * reliefShade\'s true flat baseline is 0.6). This multiplier is applied\n * on top of the crack darkening - matching filter/relief\'s notePaper\n * mode precedent of multiplying a shade term onto color (\\`sheet *\n * mix(0.6, 1.4, shade)\\`).\n *\n * Output: \\`c * mix(1, 0.35 + brightness/100*0.5, k)\\` darkens the image\n * inside cracks (brightness raises the floor, i.e. higher brightness =\n * shallower/paler cracks), then the wall-shade multiplier is applied on\n * top - matching filter/relief\'s notePaper mode precedent of multiplying\n * a shade term onto color (\\`sheet * mix(0.6, 1.4, shade)\\`).\n *\n * Single pass, evaluated on global (tile-aware) pixel coordinates so the\n * crack network is continuous across CLI render tiles.\n */\n\n#ifdef GL_ES\nprecision highp float;\n#endif\n\nuniform sampler2D inputTex;\nuniform vec2 resolution;\nuniform vec2 tileOffset;\nuniform float spacing;\nuniform float depth;\nuniform float brightness;\nuniform int seed;\n\nout vec4 fragColor;\n\n// hash - hash / jitter.\nfloat hash12(vec2 p) {\n    vec3 p3 = fract(vec3(p.xyx) * 0.1031);\n    p3 += dot(p3, p3.yzx + 33.33);\n    return fract((p3.x + p3.y) * p3.z);\n}\n\nvec2 hash22(vec2 p) {\n    vec3 p3 = fract(vec3(p.xyx) * vec3(0.1031, 0.1030, 0.0973));\n    p3 += dot(p3, p3.yzx + 33.33);\n    return fract((p3.xx + p3.yz) * p3.zy);\n}\n\n// value noise - value noise (fBm not needed here).\nfloat vnoise(vec2 p) {\n    vec2 i = floor(p);\n    vec2 f = fract(p);\n    vec2 u = f * f * (3.0 - 2.0 * f);\n    return mix(mix(hash12(i), hash12(i + vec2(1.0, 0.0)), u.x),\n               mix(hash12(i + vec2(0.0, 1.0)), hash12(i + vec2(1.0, 1.0)), u.x), u.y);\n}\n\n// Voronoi extended - jittered-grid Voronoi F1/F2: returns x = nearest seed\n// distance (F1), y = second-nearest seed distance (F2), in the same\n// cell-space units as \\`p\\`. Squared distances are compared internally\n// (cheaper); sqrt is taken only for the two winners since the crack\n// metric (F2-F1) needs true (not squared) distances to stay in\n// consistent px-proportional units once multiplied by \\`spacing\\`. Search\n// radius is one ring of neighbor cells, so jitter must stay within\n// [0, 1] to keep both candidates in-window; this is an EXACT guarantee\n// for F1 (the true nearest neighbor cannot be more than one cell away\n// at this jitter), but F2 (the second-nearest) can rarely be\n// under-counted near a cell\'s corner at jitter\'s [0, 1] maximum, where\n// the true second-nearest seed can sit just outside the 1-ring window -\n// a minor, infrequent error in the crack metric, not a hard guarantee.\nvec2 voronoiF1F2(vec2 p, float jitter, float seedVal) {\n    vec2 g = floor(p);\n    vec2 f = p - g;\n    float best = 1e9;\n    float second = 1e9;\n    for (int y = -1; y <= 1; y++) {\n        for (int x = -1; x <= 1; x++) {\n            vec2 cell = vec2(float(x), float(y));\n            vec2 pt = cell + 0.5 + (hash22(g + cell + seedVal * 101.7) - 0.5) * jitter;\n            float d = dot(pt - f, pt - f);\n            if (d < best) {\n                second = best;\n                best = d;\n            } else if (d < second) {\n                second = d;\n            }\n        }\n    }\n    return vec2(sqrt(best), sqrt(second));\n}\n\n// Directional relief shading from height.\nfloat reliefShade(float hC, float hR, float hT, float strength, float lightAngleDeg) {\n    vec2 grad = vec2(hR - hC, hT - hC) * strength;\n    vec3 n = normalize(vec3(-grad, 1.0));\n    float a = radians(lightAngleDeg);\n    vec3 L = normalize(vec3(cos(a), sin(a), 0.75));\n    return clamp(dot(n, L), 0.0, 1.0);\n}\n\n// Crack mask k at global pixel position gc: 1 on a cell border, falling\n// to 0 within \\`edge\\` px (see file header for the F2-F1 derivation).\nfloat crackMask(vec2 gc, float spacingPx, float depthPct, float seedVal) {\n    vec2 wob = vec2(vnoise(gc / 6.0), vnoise(gc / 6.0 + vec2(37.7, 91.3))) * 2.0;\n    vec2 p = (gc + wob) / spacingPx;\n    vec2 f1f2 = voronoiF1F2(p, 1.0, seedVal);\n    float d = (f1f2.y - f1f2.x) * spacingPx;\n    float edge = 1.5 + depthPct / 100.0 * 2.0;\n    return 1.0 - smoothstep(0.0, edge, d);\n}\n\nvoid main() {\n    vec2 globalCoord = gl_FragCoord.xy + tileOffset;\n    vec2 uv = gl_FragCoord.xy / resolution;\n    vec4 src = texture(inputTex, uv);\n    float seedF = float(seed);\n\n    float kC = crackMask(globalCoord, spacing, depth, seedF);\n    float kR = crackMask(globalCoord + vec2(1.0, 0.0), spacing, depth, seedF);\n    float kL = crackMask(globalCoord - vec2(1.0, 0.0), spacing, depth, seedF);\n    float kT = crackMask(globalCoord + vec2(0.0, 1.0), spacing, depth, seedF);\n    float kB = crackMask(globalCoord - vec2(0.0, 1.0), spacing, depth, seedF);\n\n    // Central-difference gradient of k; feeds both reliefShade\'s synthetic\n    // height samples below and wallMask\'s locality gate.\n    vec2 gradK = vec2((kR - kL) * 0.5, (kT - kB) * 0.5);\n\n    // Height fed to reliefShade is -k: a crack is a carved groove (a dip),\n    // not a raised ridge, so height must fall toward the crack center.\n    // Negating hC/hR/hT flips the sign of the gradient/normal reliefShade\n    // sees, which flips which groove wall catches the light (see header).\n    float hC = -kC;\n    float hR = hC - gradK.x;\n    float hT = hC - gradK.y;\n    float shadeStrength = 6.0;\n    float shade = reliefShade(hC, hR, hT, shadeStrength, 135.0);\n\n    // reliefShade\'s flat-gradient baseline is 0.6, not 0.5 (see header) -\n    // recenter on it, and gate by wallMask so flat ground away from any\n    // crack gets EXACTLY shadeMul == 1.0 (gradK saturates to exactly 0\n    // there by smoothstep\'s clamped range).\n    float gradMagK = length(gradK);\n    float wallMask = smoothstep(0.0, 0.02, gradMagK);\n    float shadeMul = 1.0 + (shade - 0.6) * 2.0 * (0.25 * depth / 100.0) * wallMask;\n\n    vec3 darkened = src.rgb * mix(1.0, 0.35 + brightness / 100.0 * 0.5, kC);\n    vec3 result = clamp(darkened * shadeMul, 0.0, 1.0);\n\n    fragColor = vec4(result, src.a);\n}',
        "source": '/*\n * Craquelure - cracked-plaster groove network with carved relief over the\n * image.\n *\n * Crack field: Voronoi\'s jittered-grid Voronoi cell (see voronoiCell in e.g.\n * filter/stipple.glsl) is extended here to voronoiF1F2, which tracks the\n * nearest (F1) AND second-nearest (F2) seed distances instead of just the\n * nearest cell id. (F2 - F1) is the standard "distance to the Voronoi\n * border" proxy: it is exactly 0 ON a cell border (where two seeds are\n * equidistant) and grows the further a point sits from any border, so\n * `k = 1 - smoothstep(0, edge, (F2-F1)*spacing)` is a ridge function that\n * peaks at 1 exactly on cell borders and falls to 0 within `edge` pixels\n * - i.e. the crack groove cross-section. `edge = 1.5 + depth/100*2` is\n * the groove\'s half-width in px, so `depth` widens the crack band.\n *\n * Voronoi jitter is fixed at 1.0 (the maximum value Voronoi\'s 3x3-neighbor\n * search window supports - see voronoiF1F2\'s docstring: the search is\n * exact for F1 at this jitter, with F2 only rarely under-counted near a\n * cell\'s corner) for maximally irregular, organic plate shapes, matching\n * real crazed plaster/glaze.\n *\n * Hashes: the Voronoi seed jitter and the value-noise lattice values come\n * from an integer hash (PCG3D) of the integer cell or lattice coordinate\n * (and `seed` for the jitter), so WebGL2 and WebGPU draw identical crack\n * networks.\n *\n * Border wobble: before the Voronoi search, the sample position is\n * perturbed by two INDEPENDENT noise taps, one per axis -\n * `vec2(vnoise(gc/6), vnoise(gc/6 + vec2(37.7, 91.3))) * 2` px (same 2px\n * amplitude as a single-scalar wobble; the additive offset decorrelates\n * the second tap from the first). A single scalar broadcast to both axes\n * only displaces the sample along the (1,1) diagonal, leaving\n * diagonal-tangent border segments unperturbed - a visible blind spot.\n * Independent per-axis taps wobble the crack path in every direction, so\n * borders weave organically regardless of their local tangent angle.\n *\n * Wall shading: the crack mask k is re-evaluated at 4 neighboring\n * (gc +/- 1px on each axis) positions to build a true central-difference\n * gradient of k (5 bounded Voronoi evaluations total). A cheaper\n * forward-difference, as filter/relief\'s rlShade.glsl\n * uses for its cheap-to-sample blurred-luminance height field, would\n * bias the bevel normal off-axis for a feature this narrow, since k\'s\n * transition width can be as little as 1.5px). The height fed to filter/relief\'s\n * reliefShade (see filter/relief) is -k, NOT +k: a crack is a carved\n * groove (a dip), not a raised ridge, so height must FALL toward the\n * crack center. This is implemented by negating hC/hR/hT (hC = -kC, hR\n * = hC - centralGradX, hT = hC - centralGradY) so reliefShade\'s internal\n * forward-difference subtraction reproduces the true central-difference\n * gradient of -k exactly - equivalently, this flips the sign of the\n * gradient/normal reliefShade sees versus feeding +k directly, which is\n * what puts the lit wall on the correct (concave-groove) side of the\n * crack. Light angle is fixed at 135 degrees (filter/relief\'s default\n * convention - upper-left; craquelure exposes no\n * lightAngle param). reliefShade\'s flat-gradient (grad=0) baseline is\n * dot((0,0,1), normalize(vec3(cos135, sin135, 0.75))) = 0.75/1.25 = 0.6\n * EXACTLY, not 0.5 - the shade term is remapped from reliefShade\'s 0..1\n * output to a subtle `1 +/- 0.25*depth/100` multiplier band centered on\n * shade==0.6 (not 0.5), and additionally gated by `wallMask =\n * smoothstep(0, 0.02, gradMagK)` (gradMagK = length of the same\n * central-diff gradient of k used above) so the multiplier is pinned to\n * EXACTLY 1.0 on flat ground regardless of depth or any future light-\n * vector change, instead of leaking a small global brightening\n * everywhere (the old unmasked, 0.5-centered version leaked because\n * reliefShade\'s true flat baseline is 0.6). This multiplier is applied\n * on top of the crack darkening - matching filter/relief\'s notePaper\n * mode precedent of multiplying a shade term onto color (`sheet *\n * mix(0.6, 1.4, shade)`).\n *\n * Output: `c * mix(1, 0.35 + brightness/100*0.5, k)` darkens the image\n * inside cracks (brightness raises the floor, i.e. higher brightness =\n * shallower/paler cracks), then the wall-shade multiplier is applied on\n * top - matching filter/relief\'s notePaper mode precedent of multiplying\n * a shade term onto color (`sheet * mix(0.6, 1.4, shade)`).\n *\n * Single pass, evaluated on global (tile-aware) pixel coordinates so the\n * crack network is continuous across CLI render tiles.\n */\n\n#ifdef GL_ES\nprecision highp float;\nprecision highp int;\n#endif\n\nuniform sampler2D inputTex;\nuniform vec2 resolution;\nuniform vec2 tileOffset;\nuniform float spacing;\nuniform float depth;\nuniform float brightness;\nuniform int seed;\n\nout vec4 fragColor;\n\n// PCG3D integer hash (Jarzynski & Olano 2020). Unsigned arithmetic wraps the\n// same way on every compiler, so WebGL2 and WebGPU draw identical values; a\n// float hash rounds and fuses differently per compiler and drifts apart.\nuvec3 pcg3d(uvec3 v_in) {\n    uvec3 v = v_in * 1664525u + 1013904223u;\n    v.x = v.x + v.y * v.z;\n    v.y = v.y + v.z * v.x;\n    v.z = v.z + v.x * v.y;\n    v = v ^ (v >> uvec3(16u));\n    v.x = v.x + v.y * v.z;\n    v.y = v.y + v.z * v.x;\n    v.z = v.z + v.x * v.y;\n    return v;\n}\n\n// Value-noise lattice value in [0, 1) at integer lattice point p. The top\n// 24 hash bits convert to float exactly.\nfloat hash12(ivec2 p) {\n    return float(pcg3d(uvec3(uvec2(p), 0u)).x >> 8u) / 16777216.0;\n}\n\n// Voronoi seed jitter in [0, 1)^2 for integer cell p and seed.\nvec2 hash22(ivec2 p, int seedVal) {\n    uvec2 h = pcg3d(uvec3(uvec2(p), uint(seedVal))).xy >> uvec2(8u);\n    return vec2(h) / 16777216.0;\n}\n\n// value noise - value noise (fBm not needed here).\nfloat vnoise(vec2 p) {\n    ivec2 i = ivec2(floor(p));\n    vec2 f = fract(p);\n    vec2 u = f * f * (3.0 - 2.0 * f);\n    return mix(mix(hash12(i), hash12(i + ivec2(1, 0)), u.x),\n               mix(hash12(i + ivec2(0, 1)), hash12(i + ivec2(1, 1)), u.x), u.y);\n}\n\n// Voronoi extended - jittered-grid Voronoi F1/F2: returns x = nearest seed\n// distance (F1), y = second-nearest seed distance (F2), in the same\n// cell-space units as `p`. Squared distances are compared internally\n// (cheaper); sqrt is taken only for the two winners since the crack\n// metric (F2-F1) needs true (not squared) distances to stay in\n// consistent px-proportional units once multiplied by `spacing`. Search\n// radius is one ring of neighbor cells, so jitter must stay within\n// [0, 1] to keep both candidates in-window; this is an EXACT guarantee\n// for F1 (the true nearest neighbor cannot be more than one cell away\n// at this jitter), but F2 (the second-nearest) can rarely be\n// under-counted near a cell\'s corner at jitter\'s [0, 1] maximum, where\n// the true second-nearest seed can sit just outside the 1-ring window -\n// a minor, infrequent error in the crack metric, not a hard guarantee.\nvec2 voronoiF1F2(vec2 p, float jitter, int seedVal) {\n    vec2 g = floor(p);\n    vec2 f = p - g;\n    ivec2 gi = ivec2(g);\n    float best = 1e9;\n    float second = 1e9;\n    for (int y = -1; y <= 1; y++) {\n        for (int x = -1; x <= 1; x++) {\n            vec2 cell = vec2(float(x), float(y));\n            vec2 pt = cell + 0.5 + (hash22(gi + ivec2(x, y), seedVal) - 0.5) * jitter;\n            float d = dot(pt - f, pt - f);\n            if (d < best) {\n                second = best;\n                best = d;\n            } else if (d < second) {\n                second = d;\n            }\n        }\n    }\n    return vec2(sqrt(best), sqrt(second));\n}\n\n// Directional relief shading from height.\nfloat reliefShade(float hC, float hR, float hT, float strength, float lightAngleDeg) {\n    vec2 grad = vec2(hR - hC, hT - hC) * strength;\n    vec3 n = normalize(vec3(-grad, 1.0));\n    float a = radians(lightAngleDeg);\n    vec3 L = normalize(vec3(cos(a), sin(a), 0.75));\n    return clamp(dot(n, L), 0.0, 1.0);\n}\n\n// Crack mask k at global pixel position gc: 1 on a cell border, falling\n// to 0 within `edge` px (see file header for the F2-F1 derivation).\nfloat crackMask(vec2 gc, float spacingPx, float depthPct, int seedVal) {\n    vec2 wob = vec2(vnoise(gc / 6.0), vnoise(gc / 6.0 + vec2(37.7, 91.3))) * 2.0;\n    vec2 p = (gc + wob) / spacingPx;\n    vec2 f1f2 = voronoiF1F2(p, 1.0, seedVal);\n    float d = (f1f2.y - f1f2.x) * spacingPx;\n    float edge = 1.5 + depthPct / 100.0 * 2.0;\n    return 1.0 - smoothstep(0.0, edge, d);\n}\n\nvoid main() {\n    vec2 globalCoord = gl_FragCoord.xy + tileOffset;\n    vec2 uv = gl_FragCoord.xy / resolution;\n    vec4 src = texture(inputTex, uv);\n\n    float kC = crackMask(globalCoord, spacing, depth, seed);\n    float kR = crackMask(globalCoord + vec2(1.0, 0.0), spacing, depth, seed);\n    float kL = crackMask(globalCoord - vec2(1.0, 0.0), spacing, depth, seed);\n    float kT = crackMask(globalCoord + vec2(0.0, 1.0), spacing, depth, seed);\n    float kB = crackMask(globalCoord - vec2(0.0, 1.0), spacing, depth, seed);\n\n    // Central-difference gradient of k; feeds both reliefShade\'s synthetic\n    // height samples below and wallMask\'s locality gate.\n    vec2 gradK = vec2((kR - kL) * 0.5, (kT - kB) * 0.5);\n\n    // Height fed to reliefShade is -k: a crack is a carved groove (a dip),\n    // not a raised ridge, so height must fall toward the crack center.\n    // Negating hC/hR/hT flips the sign of the gradient/normal reliefShade\n    // sees, which flips which groove wall catches the light (see header).\n    float hC = -kC;\n    float hR = hC - gradK.x;\n    float hT = hC - gradK.y;\n    float shadeStrength = 6.0;\n    float shade = reliefShade(hC, hR, hT, shadeStrength, 135.0);\n\n    // reliefShade\'s flat-gradient baseline is 0.6, not 0.5 (see header) -\n    // recenter on it, and gate by wallMask so flat ground away from any\n    // crack gets EXACTLY shadeMul == 1.0 (gradK saturates to exactly 0\n    // there by smoothstep\'s clamped range).\n    float gradMagK = length(gradK);\n    float wallMask = smoothstep(0.0, 0.02, gradMagK);\n    float shadeMul = 1.0 + (shade - 0.6) * 2.0 * (0.25 * depth / 100.0) * wallMask;\n\n    vec3 darkened = src.rgb * mix(1.0, 0.35 + brightness / 100.0 * 0.5, kC);\n    vec3 result = clamp(darkened * shadeMul, 0.0, 1.0);\n\n    fragColor = vec4(result, src.a);\n}',
    },
    ("filter/stipple", "stipple"): {
        "locked_sha256": "39cf37ee3bc53445d6795599a93d11e098b4a92eb6555613651cc350bc7b8949",
        "locked": '/*\n * Stipple - discrete random marks reproducing image tone. Covers three\n * filters via \\`mode\\`:\n *\n *   pointillize (0)  - Colored dots on a paper\n *                       background, one dot per jittered-grid Voronoi\n *                       cell (Voronoi), sized by that cell\'s own darkness.\n *                       Inside the dot the color is the image sampled at\n *                       the cell\'s seed point (flat per dot, like real\n *                       pointillism); outside is paperColor.\n *   mezzoDots/Lines/Strokes (1/2/3) - Mezzotint dots/lines/\n *                       strokes conversion types: each RGB channel is\n *                       independently hard-thresholded against a shaped\n *                       value-noise field, producing the harsh per-\n *                       channel black/white/primary speckle real\n *                       mezzotint conversion has. No AA is applied to the\n *                       threshold; mezzotint is a hard binary process, and\n *                       softening it would blur the per-\n *                       channel color separation that makes the effect\n *                       read as mezzotint rather than an ordered dither.\n *   reticulation (4) - A two-tone ink/paper tonemap driven by fBm "clump" noise\n *                       whose amplitude is modulated by local luminance,\n *                       so shadows fill in with dense broad clumps and\n *                       highlights break up into fine grain.\n *\n * Single pass on global (tile-aware) pixel coordinates so every pattern\n * (Voronoi grid, noise field) is continuous across CLI render tiles.\n *\n * \\`density\\` biases the ink/paper balance in BOTH the mezzo branch (its\n * threshold n) and the reticulation branch (its threshold clumpNoise)\n * with the identical (density-50)/100 term. Density acts as reticulation\n * balance / mezzo bias, and clumpNoise-vs-lum is\n * structurally the same threshold-vs-value pairing as mezzo\'s n-vs-\n * channel, so the same bias mechanism was extended there for a\n * consistent, non-dead control across every mode that enables it.\n *\n * mezzoStrokes rotates the sampling position 45 degrees before shaping\n * the anisotropic (line) noise. That rotation is applied to\n * position-derived geometry (the fragment\'s own global coordinate), using\n * the mat2(c,-s,s,c) rotation form shared with filter/halftone.\n * The rotation can push the noise-lookup position negative even though\n * globalCoord itself never is; every noise/hash function below is built\n * from \\`floor\\`/\\`fract\\`, which are floor-based (not truncated) in GLSL\n * for negative inputs, so no separate floored-mod wrap is needed here\n * (same reasoning as filter/halftone\'s rotated cell math).\n */\n\n#ifdef GL_ES\nprecision highp float;\n#endif\n\n// MODE is a compile-time define injected by the runtime (see definition.js\n// \\`globals.mode.define\\`). Wrapping the 5-way variant dispatch in #if blocks\n// instead of a runtime int dispatch lets the compiler drop the unreachable\n// mode arms instead of inlining all 5 at the single call site.\n#ifndef MODE\n#define MODE 0\n#endif\n\nuniform sampler2D inputTex;\nuniform vec2 resolution;\nuniform vec2 tileOffset;\nuniform float cellSize;\nuniform float grainSize;\nuniform float density;\nuniform vec3 paperColor;\nuniform int seed;\n\nout vec4 fragColor;\n\n// hash - hash / jitter.\nfloat hash12(vec2 p) {\n    vec3 p3 = fract(vec3(p.xyx) * 0.1031);\n    p3 += dot(p3, p3.yzx + 33.33);\n    return fract((p3.x + p3.y) * p3.z);\n}\n\nvec2 hash22(vec2 p) {\n    vec3 p3 = fract(vec3(p.xyx) * vec3(0.1031, 0.1030, 0.0973));\n    p3 += dot(p3, p3.yzx + 33.33);\n    return fract((p3.xx + p3.yz) * p3.zy);\n}\n\n// luminance - luminance.\nfloat lum(vec3 c) {\n    return dot(c, vec3(0.2126, 0.7152, 0.0722));\n}\n\n// value noise - value noise + fBm.\nfloat vnoise(vec2 p) {\n    vec2 i = floor(p);\n    vec2 f = fract(p);\n    vec2 u = f * f * (3.0 - 2.0 * f);\n    return mix(mix(hash12(i), hash12(i + vec2(1.0, 0.0)), u.x),\n               mix(hash12(i + vec2(0.0, 1.0)), hash12(i + vec2(1.0, 1.0)), u.x), u.y);\n}\n\nfloat fbm(vec2 p) {\n    float v = 0.0;\n    float a = 0.5;\n    for (int i = 0; i < 5; i++) {\n        v += a * vnoise(p);\n        p *= 2.03;\n        a *= 0.5;\n    }\n    return v;\n}\n\n// Voronoi - jittered-grid Voronoi cell: returns xy = seed point in the same\n// cell-space units as \\`p\\`, zw = integer cell id. Search radius is one\n// ring of neighbor cells, so jitter must stay within [0, 1] for the\n// nearest seed to always be found within the search window.\nvec4 voronoiCell(vec2 p, float jitter, float seedVal) {\n    vec2 g = floor(p);\n    vec2 f = p - g;\n    float best = 1e9;\n    vec4 res = vec4(0.0);\n    for (int y = -1; y <= 1; y++) {\n        for (int x = -1; x <= 1; x++) {\n            vec2 cell = vec2(float(x), float(y));\n            vec2 pt = cell + 0.5 + (hash22(g + cell + seedVal * 101.7) - 0.5) * jitter;\n            float d = dot(pt - f, pt - f);\n            if (d < best) {\n                best = d;\n                res = vec4(g + pt, g + cell);\n            }\n        }\n    }\n    return res;\n}\n\n// ink/paper tonemapping - ink/paper tonemap.\nvec3 tonemap2(float t, vec3 ink, vec3 paper) {\n    return mix(ink, paper, clamp(t, 0.0, 1.0));\n}\n\n// Rotates a position-derived (global pixel space) vector by angleDeg.\n// GLSL mat2(c,-s,s,c) rotation for the global pixel coordinate.\nvec2 rotate2D(vec2 v, float angleDeg) {\n    float a = radians(angleDeg);\n    float co = cos(a);\n    float si = sin(a);\n    return mat2(co, -si, si, co) * v;\n}\n\nvoid main() {\n    vec2 globalCoord = gl_FragCoord.xy + tileOffset;\n    vec2 uv = gl_FragCoord.xy / resolution;\n    float alpha = texture(inputTex, uv).a;\n    vec3 result;\n\n#if MODE == 0\n    // Pointillize: one dot per jittered Voronoi cell (cellSize px),\n    // colored and sized from the image at that cell\'s own seed\n    // point; darker seed colors get bigger dots. Background is\n    // paperColor. fwidth-based AA on the dot edge.\n    vec2 p = globalCoord / cellSize;\n    vec4 cell = voronoiCell(p, 0.9, float(seed));\n    vec2 seedGc = cell.xy * cellSize;\n    vec2 seedUV = clamp((seedGc - tileOffset) / resolution, 0.0, 1.0);\n    vec3 seedColor = texture(inputTex, seedUV).rgb;\n    float radius = 0.35 + 0.4 * (1.0 - lum(seedColor));\n    float d = length(p - cell.xy);\n    float aa = max(fwidth(d) * 1.5, 0.00001);\n    float inside = 1.0 - smoothstep(radius - aa, radius + aa, d);\n    result = mix(paperColor, seedColor, inside);\n#elif MODE == 1 || MODE == 2 || MODE == 3\n    // Mezzotint dots/lines/strokes: per-channel hard threshold\n    // against shaped value noise. density biases the threshold (n)\n    // directly, so higher density raises n and lowers the fraction\n    // of channel values that clear it - i.e. more ink.\n    vec2 gc = globalCoord;\n#if MODE == 3\n    gc = rotate2D(gc, 45.0);\n#endif\n    vec2 noiseP;\n#if MODE == 1\n    noiseP = gc / grainSize;\n#else\n    // Anisotropic (line) noise: the Y component keeps the coarse\n    // (grainSize*8) scale and X keeps the fine (grainSize) scale,\n    // so the field is coherent/slowly-varying down each column\n    // and decorrelates quickly across a row - i.e. streaks\n    // elongated along Y (vertical). Swapped from a\n    // literal x-coarse/y-fine reading of the spec, which was\n    // verified (lag-1 luma autocorrelation on a solid-color\n    // source region: 0.94 along X vs 0.49 along Y before this\n    // swap) to render HORIZONTAL streaks instead.\n    noiseP = gc * vec2(1.0 / grainSize, 1.0 / (grainSize * 8.0));\n#endif\n    float n = vnoise(noiseP + float(seed) * 101.7);\n    n += (density - 50.0) / 100.0;\n    vec3 src = texture(inputTex, uv).rgb;\n    result = vec3(step(n, src.r), step(n, src.g), step(n, src.b));\n#else\n    // Reticulation: two-tone ink/paper tonemap against clumped fBm\n    // noise; the noise amplitude is luminance-modulated so shadows\n    // fill in with broad dense clumps and highlights break into\n    // fine grain. density biases the ink/paper balance using the\n    // exact same (density-50)/100 term the mezzo branch applies to\n    // its threshold, since clumpNoise vs l is structurally the same\n    // threshold-vs-value pairing as mezzo\'s n vs channel.\n    vec3 src = texture(inputTex, uv).rgb;\n    float l = lum(src);\n    float clumpNoise = fbm(globalCoord / (grainSize * 4.0) + float(seed) * 101.7) * mix(1.2, 0.6, l);\n    clumpNoise += (density - 50.0) / 100.0;\n    result = tonemap2(step(clumpNoise, l), vec3(0.05), vec3(0.97));\n#endif\n\n    fragColor = vec4(result, alpha);\n}',
        "source": '/*\n * Stipple - discrete random marks reproducing image tone. Covers three\n * filters via `mode`:\n *\n *   pointillize (0)  - Colored dots on a paper\n *                       background, one dot per jittered-grid Voronoi\n *                       cell (Voronoi), sized by that cell\'s own darkness.\n *                       Inside the dot the color is the image sampled at\n *                       the cell\'s seed point (flat per dot, like real\n *                       pointillism); outside is paperColor.\n *   mezzoDots/Lines/Strokes (1/2/3) - Mezzotint dots/lines/\n *                       strokes conversion types: each RGB channel is\n *                       independently hard-thresholded against a shaped\n *                       value-noise field, producing the harsh per-\n *                       channel black/white/primary speckle real\n *                       mezzotint conversion has. No AA is applied to the\n *                       threshold; mezzotint is a hard binary process, and\n *                       softening it would blur the per-\n *                       channel color separation that makes the effect\n *                       read as mezzotint rather than an ordered dither.\n *   reticulation (4) - A two-tone ink/paper tonemap driven by fBm "clump" noise\n *                       whose amplitude is modulated by local luminance,\n *                       so shadows fill in with dense broad clumps and\n *                       highlights break up into fine grain.\n *\n * Single pass on global (tile-aware) pixel coordinates so every pattern\n * (Voronoi grid, noise field) is continuous across CLI render tiles.\n *\n * `density` biases the ink/paper balance in BOTH the mezzo branch (its\n * threshold n) and the reticulation branch (its threshold clumpNoise)\n * with the identical (density-50)/100 term. Density acts as reticulation\n * balance / mezzo bias, and clumpNoise-vs-lum is\n * structurally the same threshold-vs-value pairing as mezzo\'s n-vs-\n * channel, so the same bias mechanism was extended there for a\n * consistent, non-dead control across every mode that enables it.\n *\n * Every hash, noise, distance and blend runs in unsigned integer fixed\n * point (12-bit fractions, 16-bit values) from the integer pixel\n * coordinate, with a PCG3D hash of the lattice cell and seed, and reads\n * texels with texelFetch. Float hashes and thresholds round and fuse\n * differently in the WebGL2 and WebGPU compilers; integers give both\n * backends the same bytes.\n *\n * mezzoStrokes rotates the sampling position 45 degrees before shaping\n * the anisotropic (line) noise, in the mat2(c,-s,s,c) rotation form\n * shared with filter/halftone. The rotated y is offset by 2^20 px so the\n * unsigned position stays positive.\n */\n\n#ifdef GL_ES\nprecision highp float;\nprecision highp int;\n#endif\n\n// MODE is a compile-time define injected by the runtime (see definition.js\n// `globals.mode.define`). Wrapping the 5-way variant dispatch in #if blocks\n// instead of a runtime int dispatch lets the compiler drop the unreachable\n// mode arms instead of inlining all 5 at the single call site.\n#ifndef MODE\n#define MODE 0\n#endif\n\nuniform sampler2D inputTex;\nuniform vec2 resolution;\nuniform vec2 tileOffset;\nuniform float cellSize;\nuniform float grainSize;\nuniform float density;\nuniform vec3 paperColor;\nuniform int seed;\n\nout vec4 fragColor;\n\n// hash - PCG3D integer hash (Jarzynski & Olano 2020).\nuvec3 pcg3d(uvec3 v_in) {\n    uvec3 v = v_in * 1664525u + 1013904223u;\n    v.x = v.x + v.y * v.z;\n    v.y = v.y + v.z * v.x;\n    v.z = v.z + v.x * v.y;\n    v = v ^ (v >> uvec3(16u));\n    v.x = v.x + v.y * v.z;\n    v.y = v.y + v.z * v.x;\n    v.z = v.z + v.x * v.y;\n    return v;\n}\n\n// 16-bit hash of a lattice cell and seed.\nuint hash16(uvec2 cell, uint s) {\n    return pcg3d(uvec3(cell, s)).x >> 16u;\n}\n\n// Channel value as 16-bit unorm. Scaling by 65536 is exact, so the floor is too.\nuint unorm16(float x) {\n    return min(uint(clamp(x, 0.0, 1.0) * 65536.0), 65535u);\n}\n\n// luminance - Rec. 709 luminance, 16-bit, weights summing to 65536.\nuint lum16(vec3 c) {\n    return (unorm16(c.r) * 13933u + unorm16(c.g) * 46872u + unorm16(c.b) * 4731u) >> 16u;\n}\n\n// Smoothstep weight t * t * (3 - 2t) of a 12-bit fraction.\nuint smooth12(uint t) {\n    return (((t * t) >> 12u) * (12288u - 2u * t)) >> 12u;\n}\n\n// value noise - value noise at position n / d in lattice cells, 16-bit.\nuint vnoise(uvec2 n, uvec2 d, uint s) {\n    uvec2 i = n / d;\n    uvec2 f = ((n - i * d) << uvec2(12u)) / d;\n    uint ux = smooth12(f.x);\n    uint uy = smooth12(f.y);\n    uint ab = (hash16(i, s) * (4096u - ux) + hash16(i + uvec2(1u, 0u), s) * ux) >> 12u;\n    uint cd = (hash16(i + uvec2(0u, 1u), s) * (4096u - ux) + hash16(i + uvec2(1u, 1u), s) * ux) >> 12u;\n    return (ab * (4096u - uy) + cd * uy) >> 12u;\n}\n\n// fBm - 5 octaves of value noise on a lattice of 4 * grain, each at 2.03x\n// the frequency and half the amplitude: octave k\'s lattice is\n// 4 * grain * M[k] / 65536, with M[k] = 65536 / 2.03^k.\nuint fbm(uvec2 n, uint grain, uint s) {\n    const uint M[5] = uint[5](65536u, 32284u, 15903u, 7834u, 3859u);\n    uint v = 0u;\n    for (int k = 0; k < 5; k++) {\n        uint dk = max((grain * M[k] + 8192u) >> 14u, 1u);\n        v += vnoise(n, uvec2(dk), s) >> uint(k + 1);\n    }\n    return v;\n}\n\n// Floor of the integer square root: a float estimate, corrected in integers.\nuint isqrt(uint x) {\n    uint r = uint(sqrt(float(x)));\n    if (r * r > x) r--;\n    if (r * r > x) r--;\n    if ((r + 1u) * (r + 1u) <= x) r++;\n    if ((r + 1u) * (r + 1u) <= x) r++;\n    return r;\n}\n\n// Mezzo and reticulation threshold step(edge + (density - 50) / 100, value)\n// on 16-bit values, density in 1/256 units, multiplied through by 25.\nfloat inkStep(uint edge, uint value, int d256) {\n    return 25 * int(value) + 819200 >= 25 * int(edge) + 64 * d256 ? 1.0 : 0.0;\n}\n\nvoid main() {\n    ivec2 texel = ivec2(gl_FragCoord.xy);\n    ivec2 texSize = textureSize(inputTex, 0);\n    // Global (tile-aware) pixel. Positions are pixel centers in 1/256 px,\n    // (2 * px + 1) * 128, over sizes in 1/256 px.\n    uvec2 px = uvec2(texel + ivec2(tileOffset));\n    uvec2 center = (2u * px + 1u) * 128u;\n    vec4 src = texelFetch(inputTex, texel, 0);\n    uint s = uint(seed);\n    int d256 = int(floor(density * 256.0));\n    uint g256 = clamp(uint(max(grainSize, 0.0) * 256.0), 1u, 32768u);\n    vec3 result;\n\n#if MODE == 0\n    // Pointillize: one dot per jittered Voronoi cell (cellSize px),\n    // colored and sized from the image at that cell\'s own seed\n    // point; darker seed colors get bigger dots. Background is\n    // paperColor. The dot edge blends over 2 px on each side, close to\n    // the 1.5 * fwidth(d) it used before.\n    uint c256 = clamp(uint(max(cellSize, 0.0) * 256.0), 1u, 65535u);\n    uvec2 g = center / c256;\n    ivec2 f = ivec2(((center - g * c256) << uvec2(12u)) / c256);\n    // Jittered-grid Voronoi in 12-bit cell units: seed point = cell + 0.5 +\n    // (hash - 0.5) * 0.9. Search radius is one ring of neighbor cells, so\n    // the jitter stays within [0, 1] for the nearest seed to be in the window.\n    int best = 0x7fffffff;\n    ivec2 bestPt = ivec2(0);\n    for (int y = -1; y <= 1; y++) {\n        for (int x = -1; x <= 1; x++) {\n            ivec2 cell = ivec2(x, y);\n            uvec2 h = pcg3d(uvec3(uvec2(ivec2(g) + cell), s)).xy >> uvec2(16u);\n            ivec2 pt = cell * 4096 + 205 + ivec2(((h * 9u) / 10u) >> uvec2(4u));\n            ivec2 dv = pt - f;\n            int dd = dv.x * dv.x + dv.y * dv.y;\n            if (dd < best) {\n                best = dd;\n                bestPt = pt;\n            }\n        }\n    }\n    // Seed point in 1/256 px, measured from the cell to the lower left so\n    // the offset stays positive; the dot\'s color is the texel under it.\n    ivec2 seed256 = (ivec2(g) - 1) * int(c256) + ivec2((uvec2(bestPt + 4096) * c256) >> uvec2(12u));\n    ivec2 seedTexel = clamp((max(seed256, ivec2(0)) >> 8) - ivec2(tileOffset), ivec2(0), texSize - 1);\n    vec3 seedColor = texelFetch(inputTex, seedTexel, 0).rgb;\n    int radius = 1434 + int((1638u * (65535u - lum16(seedColor))) >> 16u);\n    int d = int(isqrt(uint(best)));\n    int aa = int(2097152u / c256);\n    uint t = d <= radius - aa ? 0u : (d >= radius + aa ? 4096u : (uint(d - radius + aa) << 12u) / uint(2 * aa));\n    uint inside = 4096u - smooth12(t);\n    uvec3 paper = uvec3(unorm16(paperColor.r), unorm16(paperColor.g), unorm16(paperColor.b));\n    uvec3 ink = uvec3(unorm16(seedColor.r), unorm16(seedColor.g), unorm16(seedColor.b));\n    result = vec3((paper * (4096u - inside) + ink * inside) >> uvec3(12u)) / 65536.0;\n#elif MODE == 1 || MODE == 2 || MODE == 3\n    // Mezzotint dots/lines/strokes: per-channel hard threshold\n    // against shaped value noise. density biases the threshold (n)\n    // directly, so higher density raises n and lowers the fraction\n    // of channel values that clear it - i.e. more ink.\n    uvec2 pos = center;\n    uint grain = g256;\n#if MODE == 3\n    // Rotate 45 degrees: x\' = (x + y) / sqrt2, y\' = (y - x) / sqrt2. The\n    // 1 / sqrt2 moves into the grain size (92682 = sqrt2 * 65536).\n    pos = uvec2((px.x + px.y + 1u) * 256u, (px.y + 1048576u - px.x) * 256u);\n    grain = (g256 * 92682u + 32768u) >> 16u;\n#endif\n    uvec2 lattice;\n#if MODE == 1\n    lattice = uvec2(grain);\n#else\n    // Anisotropic (line) noise: the Y component keeps the coarse\n    // (grainSize*8) scale and X keeps the fine (grainSize) scale,\n    // so the field is coherent/slowly-varying down each column\n    // and decorrelates quickly across a row - i.e. streaks\n    // elongated along Y (vertical). Swapped from a\n    // literal x-coarse/y-fine reading of the spec, which was\n    // verified (lag-1 luma autocorrelation on a solid-color\n    // source region: 0.94 along X vs 0.49 along Y before this\n    // swap) to render HORIZONTAL streaks instead.\n    lattice = uvec2(grain, grain * 8u);\n#endif\n    uint n = vnoise(pos, lattice, s);\n    result = vec3(inkStep(n, unorm16(src.r), d256), inkStep(n, unorm16(src.g), d256), inkStep(n, unorm16(src.b), d256));\n#else\n    // Reticulation: two-tone ink/paper tonemap against clumped fBm\n    // noise; the noise amplitude is luminance-modulated so shadows\n    // fill in with broad dense clumps and highlights break into\n    // fine grain. density biases the ink/paper balance using the\n    // exact same (density-50)/100 term the mezzo branch applies to\n    // its threshold, since clumpNoise vs l is structurally the same\n    // threshold-vs-value pairing as mezzo\'s n vs channel.\n    uint l = lum16(src.rgb);\n    // Amplitude mix(1.2, 0.6, l) in 1/65536 units.\n    uint amp = 78643u - ((39322u * l) >> 16u);\n    uint clumpNoise = (fbm(center, g256, s) * (amp >> 2u)) >> 14u;\n    result = inkStep(clumpNoise, l, d256) > 0.5 ? vec3(0.97) : vec3(0.05);\n#endif\n\n    fragColor = vec4(result, src.a);\n}',
    },
    ("filter/feedback", "feedback"): {
        "locked_sha256": "32eba8fb704242bf36574c4e89e518ad11485a12d71dd72c4029a09692d1fffc",
        "locked": '/*\n * Feedback post-processing shader.\n * Offers blend modes alongside hue, distortion, and brightness controls for the accumulated feedback buffer.\n * Mix factors are normalized to avoid runaway amplification when combining the live input with the recirculated image.\n */\n\n#ifdef GL_ES\nprecision highp float;\nprecision highp int;\n#endif\n\nuniform sampler2D inputTex;   // Live input from previous effect\nuniform sampler2D selfTex;    // Feedback buffer (previous frame output)\nuniform vec2 resolution;\nuniform float time;\nuniform int seed;\n\n// Transform uniforms\nuniform float scaleAmt;\nuniform float rotation;\n\n// Feedback uniforms  \nuniform int blendMode;\nuniform float mixAmt;\n\n// Color uniforms\nuniform float hueRotation;\nuniform float intensity;\n\n// Lens uniforms\nuniform float distortion;\nuniform float aberration;\n\n// Refraction uniforms\nuniform float refractAAmt;\nuniform float refractBAmt;\nuniform float refractADir;\nuniform float refractBDir;\nuniform bool resetState;\n\nout vec4 fragColor;\n\n#define PI 3.14159265359\n#define TAU 6.28318530718\n#define aspectRatio (resolution.x / resolution.y)\n\nfloat map(float value, float inMin, float inMax, float outMin, float outMax) {\n    return outMin + (outMax - outMin) * (value - inMin) / (inMax - inMin);\n}\n\nfloat blendOverlay(float a, float b) {\n    return a < 0.5 ? (2.0 * a * b) : (1.0 - 2.0 * (1.0 - a) * (1.0 - b));\n}\n\nfloat blendSoftLight(float base, float blend) {\n    return (blend < 0.5) \n        ? (2.0 * base * blend + base * base * (1.0 - 2.0 * blend)) \n        : (sqrt(base) * (2.0 * blend - 1.0) + 2.0 * base * (1.0 - blend));\n}\n\nvec4 cloak(vec2 st) {\n    float m = map(mixAmt, 0.0, 100.0, 0.0, 1.0);\n    float ra = map(refractAAmt, 0.0, 100.0, 0.0, 0.125);\n    float rb = map(refractBAmt, 0.0, 100.0, 0.0, 0.125);\n\n    vec4 leftColor = texture(inputTex, st);\n    vec4 rightColor = texture(selfTex, st);\n\n    // When the mixer is all the way to the left, we see left refracted by right\n    vec2 leftUV = vec2(st);\n    float rightLen = length(rightColor.rgb);\n    leftUV.x += cos(rightLen * TAU) * ra;\n    leftUV.y += sin(rightLen * TAU) * ra;\n\n    vec4 leftRefracted = texture(inputTex, fract(leftUV));\n\n    // When the mixer is all the way to the right, we see right refracted by left\n    vec2 rightUV = vec2(st);\n    float leftLen = length(leftColor.rgb);\n    rightUV.x += cos(leftLen * TAU) * rb;\n    rightUV.y += sin(leftLen * TAU) * rb;\n\n    vec4 rightRefracted = texture(selfTex, fract(rightUV));\n\n    // As the mixer approaches midpoint, mix the two refracted outputs using the same\n    // logic as the "reflect" mode in coalesce.\n    vec4 leftReflected = min(rightRefracted * rightColor / (1.0 - leftRefracted * leftColor), vec4(1.0));\n    vec4 rightReflected = min(leftRefracted * leftColor / (1.0 - rightRefracted * rightColor), vec4(1.0));\n\n    vec4 left = vec4(1.0);\n    vec4 right = vec4(1.0);\n    if (mixAmt < 50.0) {\n        left = mix(leftRefracted, leftReflected, map(mixAmt, 0.0, 50.0, 0.0, 1.0));\n        right = rightReflected;\n    } else {\n        left = leftReflected;\n        right = mix(rightReflected, rightRefracted, map(mixAmt, 50.0, 100.0, 0.0, 1.0));\n    }\n\n    return mix(left, right, m);\n}\n\nvec4 blend(vec4 color1, vec4 color2, int mode, float factor) {\n    vec4 color;\n    vec4 middle;\n\n    float amt = map(mixAmt, 0.0, 100.0, 0.0, 1.0);\n\n    if (mode == 0) {\n        // add\n        middle = min(color1 + color2, 1.0);\n    } else if (mode == 2) {\n        // color burn\n        middle = (color2 == vec4(0.0)) ? color2 : max((1.0 - ((1.0 - color1) / color2)), vec4(0.0));\n    } else if (mode == 3) {\n        // color dodge\n        middle = (color2 == vec4(1.0)) ? color2 : min(color1 / (1.0 - color2), vec4(1.0));\n    } else if (mode == 4) {\n        // darken\n        middle = min(color1, color2);\n    } else if (mode == 5) {\n        // difference\n        middle = abs(color1 - color2);\n        middle.a = max(color1.a, color2.a);\n    } else if (mode == 6) {\n        // exclusion\n        middle = color1 + color2 - 2.0 * color1 * color2;\n        middle.a = max(color1.a, color2.a);\n    } else if (mode == 7) {\n        // glow\n        middle = (color2 == vec4(1.0)) ? color2 : min(color1 * color1 / (1.0 - color2), vec4(1.0));\n    } else if (mode == 8) {\n        // hard light\n        middle = vec4(blendOverlay(color2.r, color1.r), blendOverlay(color2.g, color1.g), blendOverlay(color2.b, color1.b), mix(color1.a, color2.a, 0.5));\n    } else if (mode == 9) {\n        // lighten\n        middle = max(color1, color2);\n    } else if (mode == 10) {\n        // mix\n        middle = mix(color1, color2, 0.5);\n    } else if (mode == 11) {\n        // multiply\n        middle = color1 * color2;\n    } else if (mode == 12) {\n        // negation\n        middle = vec4(1.0) - abs(vec4(1.0) - color1 - color2);\n        middle.a = max(color1.a, color2.a);\n    } else if (mode == 13) {\n        // overlay\n        middle = vec4(blendOverlay(color1.r, color2.r), blendOverlay(color1.g, color2.g), blendOverlay(color1.b, color2.b), mix(color1.a, color2.a, 0.5));\n    } else if (mode == 14) {\n        // phoenix\n        middle = min(color1, color2) - max(color1, color2) + vec4(1.0);\n    } else if (mode == 15) {\n        // reflect\n        middle = (color1 == vec4(1.0)) ? color1 : min(color2 * color2 / (1.0 - color1), vec4(1.0));\n    } else if (mode == 16) {\n        // screen\n        middle = 1.0 - ((1.0 - color1) * (1.0 - color2));\n    } else if (mode == 17) {\n        // soft light\n        middle = vec4(blendSoftLight(color1.r, color2.r), blendSoftLight(color1.g, color2.g), blendSoftLight(color1.b, color2.b), mix(color1.a, color2.a, 0.5));\n    } else if (mode == 18) {\n        // subtract\n        middle = max(color1 + color2 - 1.0, 0.0);\n    } else {\n        // fallback to mix\n        middle = mix(color1, color2, 0.5);\n    }\n\n    if (factor == 0.5) {\n        color = middle;\n    } else if (factor < 0.5) {\n        factor = map(amt, 0.0, 0.5, 0.0, 1.0);\n        color = mix(color1, middle, factor);\n    } else if (factor > 0.5) {\n        factor = map(amt, 0.5, 1.0, 0.0, 1.0);\n        color = mix(middle, color2, factor);\n    }\n\n    return color;\n}\n\nvec3 brightnessContrast(vec3 color) {\n    float bright = map(intensity * 0.1, -100.0, 100.0, -0.5, 0.5);\n    float cont = map(intensity * 0.1, -100.0, 100.0, 0.5, 1.5);\n    color = (color - 0.5) * cont + 0.5 + bright;\n    return color;\n}\n\nvec2 rotate2D(vec2 st, float rot) {\n    st.x *= aspectRatio;\n    rot = map(rot, 0.0, 360.0, 0.0, 2.0);\n    float angle = rot * PI;\n    st -= vec2(0.5 * aspectRatio, 0.5);\n    st = mat2(cos(angle), -sin(angle), sin(angle), cos(angle)) * st;\n    st += vec2(0.5 * aspectRatio, 0.5);\n    st.x /= aspectRatio;\n    return st;\n}\n\nvec3 hsv2rgb(vec3 hsv) {\n    float h = fract(hsv.x);\n    float s = hsv.y;\n    float v = hsv.z;\n    \n    float c = v * s;\n    float x = c * (1.0 - abs(mod(h * 6.0, 2.0) - 1.0));\n    float m = v - c;\n\n    vec3 rgb;\n    if (0.0 <= h && h < 1.0/6.0) {\n        rgb = vec3(c, x, 0.0);\n    } else if (1.0/6.0 <= h && h < 2.0/6.0) {\n        rgb = vec3(x, c, 0.0);\n    } else if (2.0/6.0 <= h && h < 3.0/6.0) {\n        rgb = vec3(0.0, c, x);\n    } else if (3.0/6.0 <= h && h < 4.0/6.0) {\n        rgb = vec3(0.0, x, c);\n    } else if (4.0/6.0 <= h && h < 5.0/6.0) {\n        rgb = vec3(x, 0.0, c);\n    } else if (5.0/6.0 <= h && h < 1.0) {\n        rgb = vec3(c, 0.0, x);\n    } else {\n        rgb = vec3(0.0, 0.0, 0.0);\n    }\n\n    return rgb + vec3(m, m, m);\n}\n\nvec3 rgb2hsv(vec3 rgb) {\n    float r = rgb.r;\n    float g = rgb.g;\n    float b = rgb.b;\n    \n    float maxC = max(r, max(g, b));\n    float minC = min(r, min(g, b));\n    float delta = maxC - minC;\n\n    float h = 0.0;\n    if (delta != 0.0) {\n        if (maxC == r) {\n            h = mod((g - b) / delta, 6.0) / 6.0;\n        } else if (maxC == g) {\n            h = ((b - r) / delta + 2.0) / 6.0;\n        } else if (maxC == b) {\n            h = ((r - g) / delta + 4.0) / 6.0;\n        }\n    }\n    \n    float s = (maxC == 0.0) ? 0.0 : delta / maxC;\n    float v = maxC;\n\n    return vec3(h, s, v);\n}\n\nvec4 getImage(vec2 st) {\n    st = rotate2D(st, rotation);\n\n    // aberration and lensing\n    vec2 diff = 0.5 - st;\n    float centerDist = length(diff);\n\n    float distort = 0.0;\n    float zoom = 0.0;\n    if (distortion < 0.0) {\n        distort = map(distortion, -100.0, 0.0, -2.0, 0.0);\n        zoom = map(distortion, -100.0, 0.0, 0.04, 0.0);\n    } else {\n        distort = map(distortion, 0.0, 100.0, 0.0, 2.0);\n        zoom = map(distortion, 0.0, 100.0, 0.0, -1.0);\n    }\n\n    st = (st - diff * zoom) - diff * centerDist * centerDist * distort;\n\n    // scale\n    float scale = 100.0 / scaleAmt;\n    if (scale == 0.0) {\n        scale = 1.0;\n    }\n    st *= scale;\n    \n    // center\n    st.x -= (scale * 0.5) - (0.5 - (1.0 / resolution.x * scale));\n    st.y += (scale * 0.5) + (0.5 - (1.0 / resolution.y * scale)) - (scale);\n\n    // nudge by one pixel to avoid drift\n    st += 1.0 / resolution;\n\n    // tile\n    st = fract(st);\n\n    // chromatic aberration\n    float aberrationOffset = map(aberration, 0.0, 100.0, 0.0, 0.1) * centerDist * PI * 0.5;\n\n    // Sample selfTex directly without Y flip\n\n    float redOffset = mix(clamp(st.x + aberrationOffset, 0.0, 1.0), st.x, st.x);\n    vec4 red = texture(selfTex, vec2(redOffset, st.y));\n\n    vec4 green = texture(selfTex, st);\n\n    float blueOffset = mix(st.x, clamp(st.x - aberrationOffset, 0.0, 1.0), st.x);\n    vec4 blue = texture(selfTex, vec2(blueOffset, st.y));\n\n    vec4 tex = vec4(red.r, green.g, blue.b, 1.0);\n    tex.rgb = tex.rgb * tex.a;\n    \n    return tex;\n}\n\nvoid main() {\n    vec2 uv = gl_FragCoord.xy / resolution;\n    \n    // If resetState is true, bypass feedback and return input directly\n    if (resetState) {\n        fragColor = texture(inputTex, uv);\n        return;\n    }\n\n    vec4 color = vec4(0.0);\n\n    if (blendMode == 100) {\n        // cloak mode\n        color = cloak(uv);\n    } else {\n        float ra = map(refractAAmt, 0.0, 100.0, 0.0, 0.125);\n        float rb = map(refractBAmt, 0.0, 100.0, 0.0, 0.125);\n\n        vec4 leftColor = texture(inputTex, uv);\n        vec4 rightColor = texture(selfTex, uv);\n\n        // refract a->b\n        vec2 leftUV = vec2(uv);\n        float rightLen = length(rightColor.rgb) + refractADir / 360.0;\n        leftUV.x += cos(rightLen * TAU) * ra;\n        leftUV.y += sin(rightLen * TAU) * ra;\n\n        // refract b->a\n        vec2 rightUV = vec2(uv);\n        float leftLen = length(leftColor.rgb) + refractBDir / 360.0;\n        rightUV.x += cos(leftLen * TAU) * rb;\n        rightUV.y += sin(leftLen * TAU) * rb;\n\n        color = blend(texture(inputTex, leftUV), getImage(rightUV), blendMode, mixAmt * 0.01);\n    }\n\n    // hue rotation\n    vec3 hsv = rgb2hsv(color.rgb);\n    hsv[0] = mod(hsv[0] + map(hueRotation, -180.0, 180.0, -0.05, 0.05), 1.0);\n    color.rgb = hsv2rgb(hsv);\n\n    // brightness/contrast\n    color.rgb = brightnessContrast(color.rgb);\n\n    fragColor = color;\n}',
        "source": '/*\n * Feedback post-processing shader.\n * Offers blend modes alongside hue, distortion, and brightness controls for the accumulated feedback buffer.\n * Mix factors are normalized to avoid runaway amplification when combining the live input with the recirculated image.\n */\n\n#ifdef GL_ES\nprecision highp float;\nprecision highp int;\n#endif\n\nuniform sampler2D inputTex;   // Live input from previous effect\nuniform sampler2D selfTex;    // Feedback buffer (previous frame output)\nuniform vec2 resolution;\nuniform float time;\nuniform int seed;\n\n// Transform uniforms\nuniform float scaleAmt;\nuniform float rotation;\n\n// Feedback uniforms  \nuniform int blendMode;\nuniform float mixAmt;\n\n// Color uniforms\nuniform float hueRotation;\nuniform float intensity;\n\n// Lens uniforms\nuniform float distortion;\nuniform float aberration;\n\n// Refraction uniforms\nuniform float refractAAmt;\nuniform float refractBAmt;\nuniform float refractADir;\nuniform float refractBDir;\nuniform bool resetState;\n\nout vec4 fragColor;\n\n// The min/max clamp keeps the value it wraps from being rearranged or fused\n// into the next operation. Its bound comes from the resolution uniform (at\n// least one pixel), so it is value-exact for every value this shader computes,\n// and the compiler cannot prove it away.\nfloat pin(float x) {\n    float bound = 1e30 * resolution.x;\n    return min(max(x, -bound), bound);\n}\n\n// Error of the product a * b against its rounded value p (Dekker). The clamps\n// keep the splitting exact.\nfloat productError(float a, float b, float p) {\n    float sa = pin(4097.0 * a);\n    float ah = pin(sa - pin(sa - a));\n    float al = a - ah;\n    float sb = pin(4097.0 * b);\n    float bh = pin(sb - pin(sb - b));\n    float bl = b - bh;\n    return pin(pin(pin(pin(ah * bh) - p) + pin(ah * bl)) + pin(al * bh)) + pin(al * bl);\n}\n\n// a / b with correct rounding, computed in the same steps as the WGSL shader.\nfloat divRound(float a, float b) {\n    float q = pin(a / b);\n    float p = pin(q * b);\n    float r = pin(pin(a - p) - productError(q, b, p));\n    return pin(q + pin(r / b));\n}\n\n#define PI 3.14159265359\n#define TAU 6.28318530718\n#define aspectRatio (resolution.x / resolution.y)\n\nfloat map(float value, float inMin, float inMax, float outMin, float outMax) {\n    return outMin + (outMax - outMin) * (value - inMin) / (inMax - inMin);\n}\n\nfloat blendOverlay(float a, float b) {\n    return a < 0.5 ? (2.0 * a * b) : (1.0 - 2.0 * (1.0 - a) * (1.0 - b));\n}\n\nfloat blendSoftLight(float base, float blend) {\n    return (blend < 0.5) \n        ? (2.0 * base * blend + base * base * (1.0 - 2.0 * blend)) \n        : (sqrt(base) * (2.0 * blend - 1.0) + 2.0 * base * (1.0 - blend));\n}\n\nvec4 cloak(vec2 st) {\n    float m = map(mixAmt, 0.0, 100.0, 0.0, 1.0);\n    float ra = map(refractAAmt, 0.0, 100.0, 0.0, 0.125);\n    float rb = map(refractBAmt, 0.0, 100.0, 0.0, 0.125);\n\n    vec4 leftColor = texture(inputTex, st);\n    vec4 rightColor = texture(selfTex, st);\n\n    // When the mixer is all the way to the left, we see left refracted by right\n    vec2 leftUV = vec2(st);\n    float rightLen = length(rightColor.rgb);\n    leftUV.x += cos(rightLen * TAU) * ra;\n    leftUV.y += sin(rightLen * TAU) * ra;\n\n    vec4 leftRefracted = texture(inputTex, fract(leftUV));\n\n    // When the mixer is all the way to the right, we see right refracted by left\n    vec2 rightUV = vec2(st);\n    float leftLen = length(leftColor.rgb);\n    rightUV.x += cos(leftLen * TAU) * rb;\n    rightUV.y += sin(leftLen * TAU) * rb;\n\n    vec4 rightRefracted = texture(selfTex, fract(rightUV));\n\n    // As the mixer approaches midpoint, mix the two refracted outputs using the same\n    // logic as the "reflect" mode in coalesce.\n    vec4 leftReflected = min(rightRefracted * rightColor / (1.0 - leftRefracted * leftColor), vec4(1.0));\n    vec4 rightReflected = min(leftRefracted * leftColor / (1.0 - rightRefracted * rightColor), vec4(1.0));\n\n    vec4 left = vec4(1.0);\n    vec4 right = vec4(1.0);\n    if (mixAmt < 50.0) {\n        left = mix(leftRefracted, leftReflected, map(mixAmt, 0.0, 50.0, 0.0, 1.0));\n        right = rightReflected;\n    } else {\n        left = leftReflected;\n        right = mix(rightReflected, rightRefracted, map(mixAmt, 50.0, 100.0, 0.0, 1.0));\n    }\n\n    return mix(left, right, m);\n}\n\nvec4 blend(vec4 color1, vec4 color2, int mode, float factor) {\n    vec4 color;\n    vec4 middle;\n\n    float amt = map(mixAmt, 0.0, 100.0, 0.0, 1.0);\n\n    if (mode == 0) {\n        // add\n        middle = min(color1 + color2, 1.0);\n    } else if (mode == 2) {\n        // color burn\n        middle = (color2 == vec4(0.0)) ? color2 : max((1.0 - ((1.0 - color1) / color2)), vec4(0.0));\n    } else if (mode == 3) {\n        // color dodge\n        middle = (color2 == vec4(1.0)) ? color2 : min(color1 / (1.0 - color2), vec4(1.0));\n    } else if (mode == 4) {\n        // darken\n        middle = min(color1, color2);\n    } else if (mode == 5) {\n        // difference\n        middle = abs(color1 - color2);\n        middle.a = max(color1.a, color2.a);\n    } else if (mode == 6) {\n        // exclusion\n        middle = color1 + color2 - 2.0 * color1 * color2;\n        middle.a = max(color1.a, color2.a);\n    } else if (mode == 7) {\n        // glow\n        middle = (color2 == vec4(1.0)) ? color2 : min(color1 * color1 / (1.0 - color2), vec4(1.0));\n    } else if (mode == 8) {\n        // hard light\n        middle = vec4(blendOverlay(color2.r, color1.r), blendOverlay(color2.g, color1.g), blendOverlay(color2.b, color1.b), mix(color1.a, color2.a, 0.5));\n    } else if (mode == 9) {\n        // lighten\n        middle = max(color1, color2);\n    } else if (mode == 10) {\n        // mix\n        middle = mix(color1, color2, 0.5);\n    } else if (mode == 11) {\n        // multiply\n        middle = color1 * color2;\n    } else if (mode == 12) {\n        // negation\n        middle = vec4(1.0) - abs(vec4(1.0) - color1 - color2);\n        middle.a = max(color1.a, color2.a);\n    } else if (mode == 13) {\n        // overlay\n        middle = vec4(blendOverlay(color1.r, color2.r), blendOverlay(color1.g, color2.g), blendOverlay(color1.b, color2.b), mix(color1.a, color2.a, 0.5));\n    } else if (mode == 14) {\n        // phoenix\n        middle = min(color1, color2) - max(color1, color2) + vec4(1.0);\n    } else if (mode == 15) {\n        // reflect\n        middle = (color1 == vec4(1.0)) ? color1 : min(color2 * color2 / (1.0 - color1), vec4(1.0));\n    } else if (mode == 16) {\n        // screen\n        middle = 1.0 - ((1.0 - color1) * (1.0 - color2));\n    } else if (mode == 17) {\n        // soft light\n        middle = vec4(blendSoftLight(color1.r, color2.r), blendSoftLight(color1.g, color2.g), blendSoftLight(color1.b, color2.b), mix(color1.a, color2.a, 0.5));\n    } else if (mode == 18) {\n        // subtract\n        middle = max(color1 + color2 - 1.0, 0.0);\n    } else {\n        // fallback to mix\n        middle = mix(color1, color2, 0.5);\n    }\n\n    if (factor == 0.5) {\n        color = middle;\n    } else if (factor < 0.5) {\n        factor = map(amt, 0.0, 0.5, 0.0, 1.0);\n        color = mix(color1, middle, factor);\n    } else if (factor > 0.5) {\n        factor = map(amt, 0.5, 1.0, 0.0, 1.0);\n        color = mix(middle, color2, factor);\n    }\n\n    return color;\n}\n\nvec3 brightnessContrast(vec3 color) {\n    float bright = map(intensity * 0.1, -100.0, 100.0, -0.5, 0.5);\n    float cont = map(intensity * 0.1, -100.0, 100.0, 0.5, 1.5);\n    color = (color - 0.5) * cont + 0.5 + bright;\n    return color;\n}\n\nvec2 rotate2D(vec2 st, float rot) {\n    st.x *= aspectRatio;\n    rot = map(rot, 0.0, 360.0, 0.0, 2.0);\n    float angle = rot * PI;\n    st -= vec2(0.5 * aspectRatio, 0.5);\n    st = mat2(cos(angle), -sin(angle), sin(angle), cos(angle)) * st;\n    st += vec2(0.5 * aspectRatio, 0.5);\n    st.x /= aspectRatio;\n    return st;\n}\n\nvec3 hsv2rgb(vec3 hsv) {\n    float h = fract(hsv.x);\n    float s = hsv.y;\n    float v = hsv.z;\n    \n    float c = v * s;\n    float x = c * (1.0 - abs(mod(h * 6.0, 2.0) - 1.0));\n    float m = v - c;\n\n    vec3 rgb;\n    if (0.0 <= h && h < 1.0/6.0) {\n        rgb = vec3(c, x, 0.0);\n    } else if (1.0/6.0 <= h && h < 2.0/6.0) {\n        rgb = vec3(x, c, 0.0);\n    } else if (2.0/6.0 <= h && h < 3.0/6.0) {\n        rgb = vec3(0.0, c, x);\n    } else if (3.0/6.0 <= h && h < 4.0/6.0) {\n        rgb = vec3(0.0, x, c);\n    } else if (4.0/6.0 <= h && h < 5.0/6.0) {\n        rgb = vec3(x, 0.0, c);\n    } else if (5.0/6.0 <= h && h < 1.0) {\n        rgb = vec3(c, 0.0, x);\n    } else {\n        rgb = vec3(0.0, 0.0, 0.0);\n    }\n\n    return rgb + vec3(m, m, m);\n}\n\nvec3 rgb2hsv(vec3 rgb) {\n    float r = rgb.r;\n    float g = rgb.g;\n    float b = rgb.b;\n    \n    float maxC = max(r, max(g, b));\n    float minC = min(r, min(g, b));\n    float delta = maxC - minC;\n\n    float h = 0.0;\n    if (delta != 0.0) {\n        if (maxC == r) {\n            h = mod((g - b) / delta, 6.0) / 6.0;\n        } else if (maxC == g) {\n            h = ((b - r) / delta + 2.0) / 6.0;\n        } else if (maxC == b) {\n            h = ((r - g) / delta + 4.0) / 6.0;\n        }\n    }\n    \n    float s = (maxC == 0.0) ? 0.0 : delta / maxC;\n    float v = maxC;\n\n    return vec3(h, s, v);\n}\n\nvec4 getImage(vec2 st) {\n    st = rotate2D(st, rotation);\n\n    // aberration and lensing\n    vec2 diff = 0.5 - st;\n    float centerDist = length(diff);\n\n    float distort = 0.0;\n    float zoom = 0.0;\n    if (distortion < 0.0) {\n        distort = map(distortion, -100.0, 0.0, -2.0, 0.0);\n        zoom = map(distortion, -100.0, 0.0, 0.04, 0.0);\n    } else {\n        distort = map(distortion, 0.0, 100.0, 0.0, 2.0);\n        zoom = map(distortion, 0.0, 100.0, 0.0, -1.0);\n    }\n\n    st = (st - diff * zoom) - diff * centerDist * centerDist * distort;\n\n    // scale\n    float scale = 100.0 / scaleAmt;\n    if (scale == 0.0) {\n        scale = 1.0;\n    }\n    st *= scale;\n    \n    // center\n    st.x -= (scale * 0.5) - (0.5 - (1.0 / resolution.x * scale));\n    st.y += (scale * 0.5) + (0.5 - (1.0 / resolution.y * scale)) - (scale);\n\n    // nudge by one pixel to avoid drift\n    st += 1.0 / resolution;\n\n    // tile\n    st = fract(st);\n\n    // chromatic aberration\n    float aberrationOffset = map(aberration, 0.0, 100.0, 0.0, 0.1) * centerDist * PI * 0.5;\n\n    // Sample selfTex directly without Y flip\n\n    float redOffset = mix(clamp(st.x + aberrationOffset, 0.0, 1.0), st.x, st.x);\n    vec4 red = texture(selfTex, vec2(redOffset, st.y));\n\n    vec4 green = texture(selfTex, st);\n\n    float blueOffset = mix(st.x, clamp(st.x - aberrationOffset, 0.0, 1.0), st.x);\n    vec4 blue = texture(selfTex, vec2(blueOffset, st.y));\n\n    vec4 tex = vec4(red.r, green.g, blue.b, 1.0);\n    tex.rgb = tex.rgb * tex.a;\n    \n    return tex;\n}\n\nvoid main() {\n    vec2 uv = gl_FragCoord.xy / resolution;\n    \n    // If resetState is true, bypass feedback and return input directly\n    if (resetState) {\n        fragColor = texture(inputTex, uv);\n        return;\n    }\n\n    vec4 color = vec4(0.0);\n\n    if (blendMode == 100) {\n        // cloak mode\n        color = cloak(uv);\n    } else {\n        float ra = map(refractAAmt, 0.0, 100.0, 0.0, 0.125);\n        float rb = map(refractBAmt, 0.0, 100.0, 0.0, 0.125);\n\n        vec4 leftColor = texture(inputTex, uv);\n        vec4 rightColor = texture(selfTex, uv);\n\n        // refract a->b\n        vec2 leftUV = vec2(uv);\n        float rightLen = length(rightColor.rgb) + refractADir / 360.0;\n        leftUV.x += cos(rightLen * TAU) * ra;\n        leftUV.y += sin(rightLen * TAU) * ra;\n\n        // refract b->a\n        vec2 rightUV = vec2(uv);\n        float leftLen = length(leftColor.rgb) + refractBDir / 360.0;\n        rightUV.x += cos(leftLen * TAU) * rb;\n        rightUV.y += sin(leftLen * TAU) * rb;\n\n        color = blend(texture(inputTex, leftUV), getImage(rightUV), blendMode, mixAmt * 0.01);\n    }\n\n    // hue rotation\n    vec3 hsv = rgb2hsv(color.rgb);\n    // Compute the shift on its own, in the same steps as the WGSL shader, so\n    // both backends add the same correctly rounded value to the hue.\n    float hueShift = pin(-0.05 + divRound(pin(0.1 * (hueRotation + 180.0)), 360.0));\n    hsv[0] = fract(hsv[0] + hueShift);\n    color.rgb = hsv2rgb(hsv);\n\n    // brightness/contrast\n    color.rgb = brightnessContrast(color.rgb);\n\n    fragColor = color;\n}',
    },
}
_LOCKED_BUILD_PROGRAM_SOURCES.update(PARTICLE_TEXTURE_INPUT_SOURCES)

_HSV2RGB_LAST_SECTOR_WRAP_KEYS = frozenset(
    {
        "classicNoisedeck/bitEffects:bitEffects",
        "classicNoisedeck/caustic:caustic",
        "classicNoisedeck/cellNoise:cellNoise",
        "classicNoisedeck/cellRefract:cellRefract",
        "classicNoisedeck/coalesce:coalesce",
        "classicNoisedeck/colorLab:colorLab",
        "classicNoisedeck/composite:composite",
        "classicNoisedeck/effects:effects",
        "classicNoisedeck/fractal:fractal",
        "classicNoisedeck/kaleido:kaleido",
        "classicNoisedeck/lensDistortion:lensDistortion",
        "classicNoisedeck/moodscape:moodscape",
        "classicNoisedeck/noise:noise",
        "classicNoisedeck/noise3d:noise3d",
        "classicNoisedeck/shapeMixer:shapeMixer",
        "classicNoisedeck/shapes:shapes",
        "classicNoisedeck/shapes3d:shapes3d",
        "filter/feedback:feedback",
        "filter/prismaticAberration:prismaticAberration",
    }
)
_HSV2RGB_LAST_SECTOR_OLD = (
    "    } else if (5.0/6.0 <= h && h < 1.0) {\n"
    "        rgb = vec3(c, 0.0, x);\n"
    "    } else {\n"
    "        rgb = vec3(0.0, 0.0, 0.0);\n"
    "    }"
)
_HSV2RGB_LAST_SECTOR_NEW = (
    "    } else {\n"
    "        rgb = vec3(c, 0.0, x);\n"
    "    }"
)


def _adapt_source(effect_id: str, program: str, source: str) -> str:
    # Programs the locked CDN build predates. bundle-lock.json pins 1.0.286,
    # whose program sources lack behavior that upstream Noisemaker b71a896a
    # (published engine 1.0.302) ships natively: synth/media:mediaInput maps
    # the fragment coordinate and the position adjustments through the tile
    # offset and the full image resolution, and
    # synth3d/cellularAutomata3d:simulate carries the packed-state behavior.
    # The transpiler substitutes the 1.0.302 program source verbatim, so the
    # shipped kernels keep the behavior the CPU authority's canonical kernels
    # encode while the lock keeps the published fetch pin. Each entry fires
    # only when the incoming source is the locked build's program text, so a
    # lock advance to a source that already carries the behavior reaches the
    # per-effect patches below unchanged.
    replacement = _LOCKED_BUILD_PROGRAM_SOURCES.get((effect_id, program))
    if replacement is not None and source.strip() == replacement["locked"]:
        # The locked build's program text: substitute the newer source
        # verbatim. Any other text reaches the per-effect patches below
        # unchanged, so a lock advance to a source that already carries the
        # behavior is untouched. Fall through to the shared tail passes:
        # the substituted source needs the same matrix-temp and vector-read
        # preservation as every other program, and skipping them changes
        # the emitted kernel.
        source = replacement["source"]

    # Upstream Noisemaker 6f98d26a wraps the hue through hsv2rgb's last sector
    # in the effects listed below (plus filter/feedback at 8395d1da): the
    # chain's final `else if (h < 1.0)` arm and its black vec3(0) fallback
    # become one unconditional else branch, so a compiler that folds hsv2rgb's
    # own fract() into the caller's renders raw h = 1.0 as the colour of
    # h = 0.0 instead of black. The locked CDN build predates both revisions.
    # filter/adjust's chain is written that way natively and stays untouched.
    if f"{effect_id}:{program}" in _HSV2RGB_LAST_SECTOR_WRAP_KEYS:
        if source.count(_HSV2RGB_LAST_SECTOR_OLD) != 1:
            raise ValueError(f"{effect_id}:{program} hsv2rgb last-sector source changed")
        source = source.replace(_HSV2RGB_LAST_SECTOR_OLD, _HSV2RGB_LAST_SECTOR_NEW)

    # Upstream Noisemaker d0ed94ae selects the prng() sign fold with a boolean
    # mix instead of three float ternaries ("Select prng() sign folds with a
    # boolean mix so software rasterizers build them promptly"). The locked CDN
    # build in bundle-lock.json predates that revision, so the transpiler
    # substitutes the d0ed94ae text verbatim; every prng() effect's shared
    # prelude carries the identical three ternary lines.
    source = source.replace(
        "    p.x = p.x >= 0.0 ? p.x * 2.0 : -p.x * 2.0 + 1.0;\n"
        "    p.y = p.y >= 0.0 ? p.y * 2.0 : -p.y * 2.0 + 1.0;\n"
        "    p.z = p.z >= 0.0 ? p.z * 2.0 : -p.z * 2.0 + 1.0;\n",
        "    // Select per component, like the WGSL select(): a software rasterizer\n"
        "    // builds each float ternary as a branch, and loops of them build for minutes.\n"
        "    p = mix(-p * 2.0 + 1.0, p * 2.0, greaterThanEqual(p, vec3(0.0)));\n",
    )
    source = source.replace(
        "return fract((p3.x + p3.y) * p3.z);",
        "return fract(float(float(p3.x + p3.y) * p3.z));",
    ).replace(
        "return fract((p3.xx + p3.yz) * p3.zy);",
        "return fract(vec2(float(float(p3.x + p3.y) * p3.z), float(float(p3.x + p3.z) * p3.y)));",
    )
    source = re.sub(
        r"\bmod\(\s*([A-Za-z_]\w*(?:\.[xyzw]{1,4})?)\s*\+\s*1\.0\s*,\s*2\.0\s*\)\s*-\s*1\.0\b",
        r"(\1 - 2.0 * floor((\1 + 1.0) * 0.5))",
        source,
    )
    if effect_id == "synth/navierStokes" and program == "nsSplat":
        old = "return fract(sin(x * 12.9898) * 43758.5453);"
        if source.count(old) != 1:
            raise ValueError("navierStokes hash11 source changed")
        source = source.replace(old, "return fract(float(float(sin(float(float(x) * 12.9898))) * 43758.5453));")
    if effect_id == "filter/extrude":
        replacements = [
            ("float s = 1.0 + h * (depth / 100.0) * 0.4;", "float s = float(1.0 + h * (depth / 100.0) * 0.4);"),
            (
                "bool topHit = all(lessThanEqual(abs(P - faceCenter), faceHalf));",
                "bool topHit = all(lessThanEqual(abs((P - imgCenter) - (cellC - imgCenter) * s), faceHalf));",
            ),
        ]
        for old, new in replacements:
            if source.count(old) != 1:
                raise ValueError("extrude block face source changed")
            source = source.replace(old, new)
    if effect_id == "synth3d/noise3d" and program == "precompute":
        replacements = [
            (
                "float hash4(vec4 p) {\n    vec4 ps = p + float(seed) * 0.1;",
                "float hash4(vec4 p, vec4 k) {\n"
                "    float cpuSeedOffset = float(float(seed) * 0.1);\n"
                "    vec4 cpuLatticeOffset = k + cpuSeedOffset;\n"
                "    vec4 ps = p + cpuLatticeOffset;",
            ),
            (
                "vec4 grad4(vec4 p) {\n    float h1 = hash4(p);\n    float h2 = hash4(p + 127.1);\n"
                "    float h3 = hash4(p + 269.5);\n    float h4 = hash4(p + 419.2);",
                "vec4 grad4(vec4 p, vec4 k) {\n    float h1 = hash4(p, k);\n    float h2 = hash4(p, k + 127.1);\n"
                "    float h3 = hash4(p, k + 269.5);\n    float h4 = hash4(p, k + 419.2);",
            ),
        ]
        for old, new in replacements:
            if source.count(old) != 1:
                raise ValueError("noise3d seeded lattice source changed")
            source = source.replace(old, new)
        source, corners = re.subn(
            r"grad4\(vec4\(i\.xyz, (iw[01])\) \+ (vec4\([01],[01],[01],0\))\)", r"grad4(vec4(i.xyz, \1), \2)", source
        )
        if corners != 16:
            raise ValueError(f"noise3d expected 16 corner hashes, found {corners}")
    if effect_id == "synth/perlin" and program == "perlin":
        replacements = [
            (
                "float hash3(vec3 p) {\n    // Add seed to input to vary the noise pattern\n"
                "    p = p + float(seed) * 0.1;",
                "float hash3(vec3 p, vec3 k) {\n"
                "    float cpuSeedOffset = float(float(seed) * 0.1);\n"
                "    vec2 cpuLatticeOffset = k.xy + cpuSeedOffset;\n"
                "    p = vec3(p.x + cpuLatticeOffset.x, p.y + cpuLatticeOffset.y,"
                " float(p.z + cpuSeedOffset) + k.z);",
            ),
            (
                "vec3 grad3(vec3 p) {\n    // Generate 3 independent random values\n"
                "    float h1 = hash3(p);\n    float h2 = hash3(p + 127.1);\n"
                "    float h3 = hash3(p + 269.5);",
                "vec3 grad3(vec3 p, vec3 k) {\n    float h1 = hash3(p, k);\n"
                "    float h2 = hash3(p, k + 127.1);\n    float h3 = hash3(p, k + 269.5);",
            ),
        ]
        for old, new in replacements:
            if source.count(old) != 1:
                raise ValueError("perlin seeded lattice source changed")
            source = source.replace(old, new)
        source, corners = re.subn(
            r"grad3\(vec3\(i\.xy, (iz[01])\) \+ (vec3\([01],[01],0\))\)",
            r"grad3(vec3(i.xy, \1), \2)",
            source,
        )
        if corners != 8:
            raise ValueError(f"perlin expected 8 corner hashes, found {corners}")
    if effect_id in {"synth3d/reactionDiffusion3d", "synth3d/cellularAutomata3d"} and program == "simulate":
        old = (
            "float hash3(vec3 p) {\n"
            "    p = p + float(seed) * 0.1;\n"
            "    p = fract(p * vec3(0.1031, 0.1030, 0.0973));\n"
            "    p += dot(p, p.yxz + 33.33);\n"
            "    return fract((p.x + p.y) * p.z);\n}"
        )
        if source.count(old) != 1:
            raise ValueError(f"{effect_id} seeding hash source changed")
        source = source.replace(
            old,
            "float hash3(vec3 p) {\n"
            "    p = p + float(float(seed) * 0.1);\n"
            "    p = fract(p * vec3(0.1031, 0.1030, 0.0973));\n"
            "    float cpuHashDot = dot(p, p.yxz + 33.33);\n"
            "    return fract(float(float(float(p.x + p.y) + float(cpuHashDot + cpu"
            "HashDot)) * float(p.z + cpuHashDot)));\n}",
        )
    if effect_id == "synth3d/cellularAutomata3d" and program == "simulate":
        if "uniform int colorMode;" not in source:
            replacements = [
                ("uniform float weight;", "uniform float weight;\nuniform int colorMode;"),
                (
                    "int countMooreNeighbors(ivec3 voxel, int volSize) {",
                    "vec4 packState(float alive, float age) {\n"
                    "    if (colorMode == 1) return vec4(alive, age, 0.0, 1.0);\n"
                    "    return vec4(alive, alive, alive, 1.0);\n}\n\n"
                    "int countMooreNeighbors(ivec3 voxel, int volSize) {",
                ),
                ("fragColor = vec4(alive, alive, alive, 1.0);", "fragColor = packState(alive, age);"),
                (
                    "fragColor = vec4(finalAlive, finalAlive, finalAlive, 1.0);",
                    "fragColor = packState(finalAlive, finalAge);",
                ),
            ]
            for old, new in replacements:
                if source.count(old) != 1:
                    raise ValueError("cellularAutomata3d state source changed")
                source = source.replace(old, new)
    if effect_id == "synth3d/cell3d" and program == "precompute":
        old = "vec3 hash3(vec3 p) {\n    p = p + float(seed) * 0.1;"
        if source.count(old) != 1 or source.count("vec3 randomOffset = hash3(cellPos);") != 1:
            raise ValueError("cell3d seeded lattice source changed")
        source = source.replace(
            old,
            "vec3 hash3(vec3 base, vec3 neighbor) {\n"
            "    float cpuSeedOffset = float(float(seed) * 0.1);\n"
            "    vec3 cpuCellPos = base + neighbor;\n"
            "    vec3 p = vec3(base.x + float(neighbor.x + cpuSeedOffset),"
            " cpuCellPos.y + cpuSeedOffset, cpuCellPos.z + cpuSeedOffset);",
        )
        source = source.replace("vec3 randomOffset = hash3(cellPos);", "vec3 randomOffset = hash3(i, neighbor);")
    if effect_id == "filter/strokes" and program == "stkSmear":
        # The canonical typed-array product rounds before accumulation.
        pigment = "pigmentSum += srcSample(centerUV).rgb * mark;"
        if source.count(pigment) != 1:
            raise ValueError("strokes canonical pigment pattern changed")
        source = source.replace(pigment, "pigmentSum += vec3(srcSample(centerUV).rgb * mark);")
    if effect_id == "classicNoisedeck/glitch" and program == "glitch":
        # Upstream Noisemaker a1a3fa2a quantizes the glitch result's rgb
        # channels to 8-bit color before the scanlines/snow stages. The
        # locked CDN build in bundle-lock.json predates that revision, so
        # the transpiler applies the same statement here.
        glitch_call = "color = glitch(uv);"
        quantize = "color.rgb = floor(clamp(color.rgb, 0.0, 1.0) * 255.0 + 0.5) / 255.0;"
        if source.count(glitch_call) != 1:
            raise ValueError("glitch canonical call pattern changed")
        source = source.replace(glitch_call, glitch_call + "\n    " + quantize)
    if effect_id == "synth/testPattern" and program == "testPattern":
        # Mirror the sibling's compile-glsl.js restoreIntegerDivision addition
        # (GAP-035): testPattern's numbered checkerboard divides an int digit
        # accumulator in place. Raw JS `/=` leaves a fractional digit and
        # drops glyph-table lookups; the lowered form truncates. Same exact
        # source guards as the sibling's pass.
        digit_decl = "int temp = number;"
        digit_step = "temp /= 10;"
        if digit_decl not in source or digit_step not in source:
            raise ValueError("testPattern digit division source changed")
        source = source.replace(digit_step, "temp = int(temp / 10.0);", 1)
    if effect_id == "filter/crt" and program == "crt":
        # Upstream a1a3fa2a quantizes the foreground color to 8-bit before
        # blending it with base_color; same locked-build constraint as
        # classicNoisedeck/glitch above.
        crt_mix = "color = mix(base_color, color, alphaVal);"
        if source.count(crt_mix) != 1:
            raise ValueError("crt canonical mix pattern changed")
        source = source.replace(
            crt_mix,
            "vec3 effectColor8 = floor(clamp(color, 0.0, 1.0) * 255.0 + 0.5) / 255.0;\n"
            "    color = mix(base_color, effectColor8, alphaVal);",
        )
    if effect_id == "classicNoisedeck/effects" and program == "effects":
        # Upstream Noisemaker 6cb1a3c3 makes the classicNoisedeck effect stack
        # tile-aware: the block grids (pixellate, checkerboard dither, stripe
        # mask) anchor to fullResolution, one convolution step measures one
        # full-image texel, input taps map through the tile mapping
        # ((st * fullResolution - tileOffset) / textureSize), the radial zoom
        # clamps each tap to a 256 px budget under tiling, and the checker
        # phase advances by tileOffset. Untiled the two resolutions are equal
        # and tileOffset is zero, so untiled output is unchanged. The locked
        # CDN build in bundle-lock.json predates that revision, so the
        # transpiler applies the same statements here.
        tile_rules = [
            # pixellate: the block grid anchors to the full image
            ("float dx = size * (1.0 / resolution.x);",
             "float dx = size * (1.0 / fullResolution.x);", 1),
            ("float dy = size * (1.0 / resolution.y);",
             "float dy = size * (1.0 / fullResolution.y);", 1),
            ("return texture(inputTex, coord).rgb;",
             "return texture(inputTex, (coord * fullResolution - tileOffset)"
             " / vec2(textureSize(inputTex, 0))).rgb;", 1),
            # convolve: one kernel step is one full-image pixel
            ("vec2 steps = 1.0 / resolution;",
             "vec2 steps = 1.0 / fullResolution;", 1),
            # dither: the block count uses the full resolution and the snapped
            # block center is a full-image coordinate
            ("float amount = resolution.x / size;",
             "float amount = fullResolution.x / size;", 1),
            ("vec4 base = texture( inputTex, vec2( sx, sy ) );",
             "vec4 base = texture( inputTex, (vec2( sx, sy ) * fullResolution"
             " - tileOffset) / vec2(textureSize(inputTex, 0)) );", 1),
            # checker phase anchored to the full image
            ("mod( gl_FragCoord.x, dSize )",
             "mod( gl_FragCoord.x + tileOffset.x, dSize )", 1),
            ("mod( gl_FragCoord.y, dSize )",
             "mod( gl_FragCoord.y + tileOffset.y, dSize )", 2),
            # stripes anchored to full-image pixels
            ("st *= resolution;",
             "st *= fullResolution;", 1),
            # bloom: every tap maps through the tile mapping
            ("vec3 orig = texture(inputTex, st).rgb;",
             "vec3 orig = texture(inputTex, (st * fullResolution - tileOffset)"
             " / vec2(textureSize(inputTex, 0))).rgb;", 1),
            ("sum += texture(inputTex, st + vec2(j, i) * 0.004).rgb * strength;",
             "sum += texture(inputTex, ((st + vec2(j, i) * 0.004)"
             " * fullResolution - tileOffset) / vec2(textureSize(inputTex, 0)))"
             ".rgb * strength;", 1),
            # radial zoom: clamp each tap to a 256 px budget under tiling
            ("vec4 tex = texture(inputTex, st + tapB);",
             "if (tileOffset.x != 0.0 || tileOffset.y != 0.0) {\n"
             "            vec2 tapBudget = vec2(256.0) * invFullResolution;\n"
             "            tapB = min(max(tapB, -tapBudget), tapBudget);\n"
             "        }\n"
             "        vec4 tex = texture(inputTex, ((st + tapB)"
             " * fullResolution - tileOffset) / vec2(textureSize(inputTex, 0)));", 1),
            # the zoom center anchors to the full image
            ("vec2 imageSize = resolution;",
             "vec2 imageSize = fullResolution;", 1),
        ]
        for old, new, count in tile_rules:
            if source.count(old) != count:
                raise ValueError(
                    f"classicNoisedeck/effects tile-awareness source changed: {old!r}"
                )
            source = source.replace(old, new)
    if effect_id == "filter/glyphMap" and program == "glyphMap":
        # Upstream Noisemaker 6cb1a3c3 detects tiling from the full-image size
        # differing from the local render size instead of from tileOffset:
        # the origin tile's offset is (0, 0), the same value the runtime
        # writes when not tiling. Untiled the two resolutions are equal, so
        # output is unchanged. Same locked-build constraint as
        # classicNoisedeck/effects above.
        is_tile = "bool isTileRendering = length(tileOffset) > 0.0;"
        if source.count(is_tile) != 1:
            raise ValueError("glyphMap tiling detection source changed")
        source = source.replace(
            is_tile,
            "bool isTileRendering = any(notEqual(fullResolution, resolution));",
        )
    if effect_id == "synth/polygon" and program == "shape":
        # Upstream Noisemaker 6cb1a3c3 special-cases the degenerate
        # smoothing=0 edge: GLSL smoothstep is undefined when edge0 == edge1.
        # babf6b2d refines that case: the kernel branches on smoothing > 0.0
        # and the hard edge picks foreground by d < radius, so a pixel exactly
        # on the radius boundary renders background. Same locked-build
        # constraint as classicNoisedeck/effects above.
        degenerate = "float m = smoothstep(radius, radius - smoothing, d);"
        if source.count(degenerate) != 1:
            raise ValueError("polygon degenerate smoothing source changed")
        source = source.replace(
            degenerate,
            "float m = smoothing > 0.0 ? smoothstep(radius, radius - smoothing, d)"
            " : float(d < radius);",
        )
    # The sibling's adaptCanonicalSource also temps matrix self-assignments
    # (`v = matN(...) * v;`) before the transpiler sees them, so the multiply
    # reads the pre-assignment vector.
    source = preserve_matrix_self_assignments(source)
    # The sibling's adaptCanonicalSource ends with preserveVectorAssignmentReads:
    # a single-line `v = vecN(...);` whose arguments swizzle-read `v` compiles
    # from a temporary, so the assignment is atomic. Multi-line constructor
    # statements escape that pass and keep the glsl-transpiler's component-wise
    # in-place expansion, where later components read the already-stored earlier
    # ones (mandelbrot's derivative, shapeMask's hexagram SDF).
    return preserve_vector_assignment_reads(source)


_VECTOR_ASSIGNMENT = re.compile(
    r"^(\s*)([A-Za-z_]\w*)\s*=\s*((?:[biu]?vec[234])\s*\([^;\n]*\)[^;\n]*)\s*;$",
    re.M,
)


_MATRIX_SELF_ASSIGNMENT = re.compile(
    r"^(\s*)([A-Za-z_]\w*)\s*=\s*(mat([234])\s*\([^;\n]*\)\s*\*\s*\2)\s*;$",
    re.M,
)


def preserve_matrix_self_assignments(source: str) -> str:
    counter = 0

    def replace(match: re.Match) -> str:
        nonlocal counter
        indent, target, expression, width = match.groups()
        temporary = f"cpu_matrix_assignment_{counter}"
        counter += 1
        return (
            f"{indent}vec{width} {temporary} = {expression};\n"
            f"{indent}{target} = {temporary};"
        )

    return _MATRIX_SELF_ASSIGNMENT.sub(replace, source)


def preserve_vector_assignment_reads(source: str) -> str:
    counter = 0

    def replace(match: re.Match) -> str:
        nonlocal counter
        indent, target, expression = match.groups()
        if not re.search(rf"\b{target}\.[xyzwrgba]", expression):
            return match.group(0)
        declared = re.match(r"^([biu]?vec[234])\s*\(", expression)
        if not declared:
            return match.group(0)
        temporary = f"cpu_vector_assignment_{counter}"
        counter += 1
        return (
            f"{indent}{declared.group(1)} {temporary} = {expression};\n"
            f"{indent}{target} = {temporary};"
        )

    return _VECTOR_ASSIGNMENT.sub(replace, source)


def runtime_defines(params: dict) -> dict:
    out = {}
    for spec in params.values():
        if isinstance(spec, dict) and spec.get("define"):
            out[spec["define"]] = "float" if spec.get("type") == "float" else "int"
    return out


def infer_kind(namespace: str, passes: list[dict], textures: dict) -> str:
    if namespace in {"synth", "synth3d"}:
        return "generator"
    if namespace == "filter3d":
        return "filter"
    if namespace == "mixer":
        return "mixer"
    if namespace in {"points", "render"}:
        return "filter"
    has_inputs = False
    external = False
    for render_pass in passes:
        for value in (render_pass.get("inputs") or {}).values():
            has_inputs = True
            if not isinstance(value, str):
                continue
            if value in {"inputTex", "outputTex", "selfTex", "feedback"}:
                continue
            if value.startswith(("_", "global_")):
                continue
            texture = textures.get(value)
            if (
                texture
                and isinstance(texture.get("width"), (int, float))
                and isinstance(texture.get("height"), (int, float))
            ):
                continue
            external = True
    if not has_inputs:
        return "generator"
    return "mixer" if external else "filter"


def infer_domain(effect_id: str) -> str:
    namespace = effect_id.split("/", 1)[0]
    if effect_id == "render/loopBegin":
        return "loop-begin"
    if effect_id == "render/loopEnd":
        return "loop-end"
    if namespace == "synth3d":
        return "volume-generator"
    if namespace == "filter3d":
        return "volume-filter"
    if effect_id.startswith("render/render"):
        return "volume-renderer"
    return "image"


def _key(eid, program):
    return f"{eid}:{program}"


def _file(key):
    return key.replace("/", "__").replace(":", "__") + ".py"


_PASS_EXECUTION_KEYS = (
    "uniforms",
    "repeat",
    "blend",
    "clear",
    "drawMode",
    "count",
    "countUniform",
    "type",
    "entryPoint",
    "drawBuffers",
    "conditions",
    "viewport",
    "defines",
)


def _pass_metadata(render_pass: dict, key: str | None) -> dict:
    outputs = {
        ("fragColor" if render_pass.get("drawBuffers", 0) >= 2 and name == "color" else name): texture
        for name, texture in (render_pass.get("outputs") or {}).items()
    }
    metadata = {
        "name": render_pass["name"],
        "program": render_pass["program"],
        "key": key,
        "inputs": render_pass.get("inputs") or {},
        "outputs": outputs,
    }
    for field in _PASS_EXECUTION_KEYS:
        if field in render_pass:
            metadata[field] = render_pass[field]
    return metadata


def _validate_artifacts(bundle: dict, hashes: dict, kernel_dir: str) -> None:
    pass_keys = {
        render_pass["key"]
        for effect in bundle["effects"].values()
        for render_pass in effect["passes"]
        if render_pass["key"] is not None
    }
    kernel_files = set(os.listdir(kernel_dir))
    expected_files = {_file(key) for key in pass_keys}
    if set(hashes) != pass_keys or kernel_files != expected_files:
        raise RuntimeError(
            f"bundle artifact mismatch: metadata={len(pass_keys)}, hashes={len(hashes)}, kernels={len(kernel_files)}"
        )


def _publish_bundle(staged_dir: str, out_dir: str) -> None:
    parent = os.path.dirname(out_dir)
    backup_dir = None
    if os.path.lexists(out_dir):
        backup_dir = tempfile.mkdtemp(prefix=f".{os.path.basename(out_dir)}.backup-", dir=parent)
        os.rmdir(backup_dir)
        os.replace(out_dir, backup_dir)
    try:
        os.replace(staged_dir, out_dir)
    except BaseException:
        if backup_dir is not None:
            os.replace(backup_dir, out_dir)
        raise
    if backup_dir is not None:
        shutil.rmtree(backup_dir, ignore_errors=True)


def build(ids, out_dir=BUNDLE, update_lock=False):
    ids = list(ids)
    out_dir = os.path.abspath(os.fspath(out_dir))
    parent = os.path.dirname(out_dir)
    os.makedirs(parent, exist_ok=True)
    lock_path = os.path.join(out_dir, "bundle-lock.json")
    if os.path.exists(lock_path):
        with open(lock_path) as f:
            old = json.load(f)
    else:
        old = {"hashes": {}}
    staged_dir = tempfile.mkdtemp(prefix=f".{os.path.basename(out_dir)}.build-", dir=parent)
    kdir = os.path.join(staged_dir, "kernels", "python")
    os.makedirs(kdir)
    old_hashes = old.get("hashes", {})
    hashes = {}
    drift = []
    failures = []
    bundle = {
        "provenance": {"source": "shaders.noisedeck.app CDN", "version": CDN_VERSION, "base": CDN_BASE},
        "effects": {},
    }
    n_ok = 0
    try:
        for eid in ids:
            try:
                eff = fetch_effect(eid)
            except Exception as e:
                failures.append(f"{eid}: cdn: {type(e).__name__}: {str(e)[:80]}")
                continue
            _resolve_shared_enums(eff["params"])
            defines = runtime_defines(eff["params"])
            # Pass-level defines (reference 0ed489ec's `.flatMap()` per-viewMode/
            # blendMode/blurLayer pass-cloning pattern): each clone bakes a
            # different literal into e.g. VIEW_MODE at the reference's compile
            # time, but since this transpiler lowers every `define:` name to a
            # runtime-branch uniform (see runtime_defines/normalize above), all
            # clones of the same program share one kernel -- the clone-specific
            # value differs only in which uniform binding renderer.py supplies
            # per pass-instance (_pass_metadata below). Union every pass.defines
            # key across the whole effect so the shared kernel declares the
            # uniform regardless of which clone's iteration transpiles first.
            for p in eff["passes"]:
                for name in (p.get("defines") or {}):
                    defines.setdefault(name, "int")
            passes = []
            for p in eff["passes"]:
                glsl = eff["programs"].get(p["program"])
                if glsl is None:
                    # A pass without GLSL is a CPU-only draw op (e.g. wormhole's
                    # point-scatter deposit). Keep it so the renderer can run its
                    # native adapter; it has no transpiled kernel key.
                    if p.get("drawMode"):
                        passes.append(_pass_metadata(p, None))
                    else:
                        failures.append(f"{_key(eid, p['program'])}: missing GLSL program")
                    continue
                key = _key(eid, p["program"])
                h = hashlib.sha256(glsl.strip().encode("utf-8")).hexdigest()
                try:
                    norm = normalize(_adapt_source(eid, p["program"], glsl), defines)
                    ast = parse(norm["source"])
                    py = emit_python(
                        ast,
                        norm.get("outputs"),
                        norm.get("varyings"),
                        js_vector_storage=key in _JS_VECTOR_STORAGE_KEYS,
                        atomic_compound=key in _ATOMIC_COMPOUND_KEYS,
                        effect_id=eid,
                        constant_divisors=defines,
                    )
                except Exception as e:
                    failures.append(f"{key}: {type(e).__name__}: {str(e)[:80]}")
                    continue
                with open(os.path.join(kdir, _file(key)), "w") as f:
                    f.write(py)
                if old_hashes.get(key) and old_hashes[key] != h:
                    drift.append(key)
                hashes[key] = h
                n_ok += 1
                passes.append(_pass_metadata(p, key))
            if not passes:
                if not any(message.startswith(f"{eid}:") for message in failures):
                    failures.append(f"{eid}: no executable passes")
                continue
            bundle["effects"][eid] = {
                "namespace": eff["namespace"],
                "func": eff["func"],
                "kind": infer_kind(eff["namespace"], eff["passes"], eff.get("textures", {})),
                "domain": eff.get("domain", infer_domain(eid)),
                "params": eff["params"],
                "textures": eff.get("textures", {}),
                "passes": passes,
            }
            if eff["params"].get("iterationCount", {}).get("cpuOnly"):
                bundle["effects"][eid]["iterated"] = True
            for field in ("outputTex", "outputTex3d", "outputGeo", "loopRole"):
                if eff.get(field) is not None:
                    bundle["effects"][eid][field] = eff[field]
            if eff.get("externalTexture"):
                bundle["effects"][eid]["externalTexture"] = eff["externalTexture"]
        if failures:
            raise RuntimeError(f"bundle build failed ({len(failures)} failure(s)):\n" + "\n".join(failures))
        if set(bundle["effects"]) != set(ids):
            raise RuntimeError("bundle effect inventory does not match requested effect ids")
        if drift and not update_lock:
            print(
                f"\nSHADER DRIFT vs bundle-lock.json ({len(drift)}): {drift[:8]}\nRe-run with --update-lock to accept.",
                file=sys.stderr,
            )
            raise SystemExit(1)
        with open(os.path.join(staged_dir, "metadata.json"), "w") as f:
            json.dump(bundle, f, indent=2)
        with open(os.path.join(staged_dir, "bundle-lock.json"), "w") as f:
            json.dump({"source": CDN_BASE, "version": CDN_VERSION, "hashes": hashes}, f, indent=2)
        _validate_artifacts(bundle, hashes, kdir)
        _publish_bundle(staged_dir, out_dir)
        staged_dir = None
    finally:
        if staged_dir is not None and os.path.exists(staged_dir):
            shutil.rmtree(staged_dir)
    print(f"wrote {len(bundle['effects'])} effect(s) ({n_ok} programs, 0 skipped) from CDN {CDN_VERSION}")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--all" in argv:
        ids = eligible_ids()
    elif "--only" in argv:
        ids = argv[argv.index("--only") + 1].split(",")
    else:
        ids = ["synth/solid", "filter/invert"]
    build(ids, update_lock="--update-lock" in argv)


if __name__ == "__main__":
    main()
