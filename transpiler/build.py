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
}


# Behavior the published pin predates but upstream Noisemaker c4f7cdd7 ships
# natively (behavior-local particle texture inputs): the ten points agent
# programs sample diffuseTex through a selectedDiffuse helper gated on
# diffuseActive and read the field map from fieldTex/heightTex gated on
# fieldActive. Each substitution fires only on the locked build's exact
# program text and falls through to the shared tail passes.
_LOCKED_BUILD_PROGRAM_SOURCES.update(PARTICLE_TEXTURE_INPUT_SOURCES)


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
    if effect_id == "filter/scatter" and program == "scatterJitter":
        old = "hash22(hashCoord + float(seed) * 101.7)"
        if source.count(old) != 1:
            raise ValueError("scatter seed term source changed")
        source = source.replace(old, "hash22(hashCoord + float(float(seed) * 101.7))")
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
        # smoothing=0 edge: GLSL smoothstep is undefined when edge0 == edge1,
        # so the reference picks foreground/background by d <= radius instead
        # of the undefined smoothstep. Same locked-build constraint as
        # classicNoisedeck/effects above.
        degenerate = "float m = smoothstep(radius, radius - smoothing, d);"
        if source.count(degenerate) != 1:
            raise ValueError("polygon degenerate smoothing source changed")
        source = source.replace(
            degenerate,
            "float m = smoothing == 0.0 ? (d <= radius ? 1.0 : 0.0)"
            " : smoothstep(radius, radius - smoothing, d);",
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
