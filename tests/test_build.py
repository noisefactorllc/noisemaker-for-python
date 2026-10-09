import json
from collections import Counter
from pathlib import Path

import pytest

from transpiler import build as build_module


def _simple_effect(effect_id="synth/test"):
    namespace, func = effect_id.split("/", 1)
    return {
        "id": effect_id,
        "namespace": namespace,
        "func": func,
        "params": {},
        "textures": {},
        "passes": [
            {
                "name": "main",
                "program": "main",
                "inputs": {},
                "outputs": {"fragColor": "outputTex"},
            }
        ],
        "programs": {"main": "out vec4 fragColor; void main() { fragColor = vec4(1.0); }"},
    }


def _tree_snapshot(root):
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in root.rglob("*") if path.is_file()}


def test_bundled_catalog_preserves_scientific_notation_enum_value():
    metadata = json.loads((Path(build_module.BUNDLE) / "metadata.json").read_text())

    choices = metadata["effects"]["classicNoisedeck/coalesce"]["params"]["blendMode"]["choices"]

    assert choices["hueAB"] == 1000


def test_bundled_catalog_has_complete_cpu_domain_partition():
    effects = json.loads((Path(build_module.BUNDLE) / "metadata.json").read_text())["effects"]

    assert len(effects) == 210
    assert Counter(definition["domain"] for definition in effects.values()) == {
        "image": 193,
        "loop-begin": 1,
        "loop-end": 1,
        "volume-filter": 2,
        "volume-generator": 8,
        "volume-renderer": 5,
    }


def test_bundled_degauss_kernel_carries_tile_awareness():
    kernel = (
        Path(build_module.BUNDLE) / "kernels" / "python" / "filter__degauss__degauss.py"
    ).read_text()

    # The offset scales by the full-resolution dims (width/height of
    # warped_channel_value), not the tile-local resolution uniform...
    assert 'displacement, 2, "float"), rt.array([width, height]), 2, "float")' in kernel
    assert (
        'rt.array([rt.swizzle(_u_resolution, "x"), rt.swizzle(_u_resolution, "y")]), 2, "float")'
        not in kernel
    )
    # ...and the displacement clamp is tile-aware.
    assert (
        'maxAllowedDisplacement = (rt.binary("/", maxOffsetPixels, '
        'rt.component_wise("max", width_f, height_f, width=1), 1, "float") if isTiling else'
    ) in kernel


def test_bundled_degauss_kernel_matches_tiled_oracle_render():
    """Node-free regression pin for the 48d25116 tile-awareness delta, against
    committed oracle bytes. With a 32x32 destination inside a 64x64 full
    resolution (renderScale 2 > 1.01), the pre-48d25116 kernel's tile-local
    offset diverges from the oracle by up to 238 rgba8 levels; the committed
    kernel must reproduce the oracle's rgba8 bytes exactly. Oracle surface
    captured from noisemaker-for-cpu 181bff8bfa74 by running
    bindCanonicalKernel(canonicalKernelFactories['filter/degauss:degauss'])
    with resolution 32x32, fullResolution 64x64, tileOffset [0,0],
    displacement 0.25, direction 30, speed 1, seed 1, time 0.25 over a
    procedural input texture."""
    import numpy as np

    from noisemaker_cpu.kernel_loader import load_kernel
    from noisemaker_cpu.pass_runner import Ctx, run_pass
    from noisemaker_cpu.runtime import Runtime
    from noisemaker_cpu.surface import Surface

    width = height = 32
    full_resolution = 64
    fixture = Path(__file__).parent / "data" / "degauss-tile-oracle" / "degauss-tile-64.f32"
    oracle = np.fromfile(fixture, dtype=np.float32)
    assert oracle.shape == (width * height * 4,)

    input_tex = Surface(width, height)
    xs = np.arange(width * height) % width
    ys = np.arange(width * height) // width
    input_tex.data[0::4] = (((xs * 3 + ys * 5) % 256) / 255).astype(np.float32)
    input_tex.data[1::4] = (((xs * 11 + ys * 7) % 256) / 255).astype(np.float32)
    input_tex.data[2::4] = (((xs * 17 + ys * 23) % 256) / 255).astype(np.float32)
    input_tex.data[3::4] = 1

    f32 = np.float32
    uniforms = {
        "renderScale": f32(1.0),
        "speed": f32(1),
        "seed": 1,
        "centerLoX": 0,
        "centerLoY": 0,
        "size": np.zeros(4, dtype=f32),
        "motion": np.zeros(4, dtype=f32),
        "displacement": f32(0.25),
        "direction": f32(30),
        "resolution": np.array([width, height], dtype=f32),
        "fullResolution": np.array([full_resolution, full_resolution], dtype=f32),
        "tileOffset": np.zeros(2, dtype=f32),
        "aspectRatio": f32(width / height),
        "aspect": f32(width / height),
        "time": f32(0.25),
        "globalTime": f32(0.25),
        "deltaTime": f32(0.0),
        "frame": 0,
    }
    kernel_path = Path(build_module.BUNDLE) / "kernels" / "python" / "filter__degauss__degauss.py"
    kernel = load_kernel(kernel_path.read_text(encoding="utf-8"))
    ctx = Ctx(
        Runtime(),
        uniforms=uniforms,
        textures={"inputTex": input_tex},
        resolution=np.array([width, height], dtype=f32),
        time=0.25,
        seed=1,
    )
    surface = run_pass(kernel, ctx, width, height)

    oracle_rgba8 = Surface(width, height, oracle).to_rgba8()
    assert surface.to_rgba8() == oracle_rgba8


def test_bundled_octave_warp_kernel_matches_negative_seed_oracle_render():
    """Node-free regression pin for the 058d15dc hash21 sign-handling delta,
    against committed oracle bytes. The whole-catalog parity gate renders
    octaveWarp at seed 1, where the sign-split and abs() seed conversions agree;
    at a negative seed the pre-058d15dc kernel's wrapped negative truncation
    diverges from the oracle by full pixel levels. The committed kernel must
    reproduce the oracle's rgba8 bytes exactly. Oracle surface captured from
    noisemaker-for-cpu 21017a708983 by running
    bindCanonicalKernel(canonicalKernelFactories['filter/octaveWarp:octaveWarp'])
    with resolution 64x48, fullResolution 64x48, tileOffset [0,0], frequency 2,
    octaves 1, displacement 0.25, speed 1, wrap 0, antialias false, seed -2.5,
    time 0.25 over a procedural input texture."""
    import numpy as np

    from noisemaker_cpu.kernel_loader import load_kernel
    from noisemaker_cpu.pass_runner import Ctx, run_pass
    from noisemaker_cpu.runtime import Runtime
    from noisemaker_cpu.surface import Surface

    width, height = 64, 48
    f32 = np.float32
    fixture = Path(__file__).parent / "data" / "octave-warp-sign-oracle" / "octave-warp-negseed-64x48.f32"
    oracle = np.fromfile(fixture, dtype=np.float32)
    assert oracle.shape == (width * height * 4,)

    input_tex = Surface(width, height)
    xs = np.arange(width * height) % width
    ys = np.arange(width * height) // width
    input_tex.data[0::4] = (((xs * 3 + ys * 5) % 256) / 255).astype(np.float32)
    input_tex.data[1::4] = (((xs * 11 + ys * 7) % 256) / 255).astype(np.float32)
    input_tex.data[2::4] = (((xs * 17 + ys * 23) % 256) / 255).astype(np.float32)
    input_tex.data[3::4] = 1

    uniforms = {
        "renderScale": f32(1.0),
        "speed": f32(1),
        "seed": f32(-2.5),
        "centerLoX": 0,
        "centerLoY": 0,
        "size": np.zeros(4, dtype=f32),
        "motion": np.zeros(4, dtype=f32),
        "frequency": f32(2),
        "octaves": f32(1),
        "displacement": f32(0.25),
        "wrap": f32(0),
        "antialias": False,
        "resolution": np.array([width, height], dtype=f32),
        "fullResolution": np.array([width, height], dtype=f32),
        "tileOffset": np.zeros(2, dtype=f32),
        "aspectRatio": f32(width / height),
        "aspect": f32(width / height),
        "time": f32(0.25),
        "globalTime": f32(0.25),
        "deltaTime": f32(0.0),
        "frame": 0,
    }
    kernel_path = Path(build_module.BUNDLE) / "kernels" / "python" / "filter__octaveWarp__octaveWarp.py"
    kernel = load_kernel(kernel_path.read_text(encoding="utf-8"))
    ctx = Ctx(
        Runtime(),
        uniforms=uniforms,
        textures={"inputTex": input_tex},
        resolution=np.array([width, height], dtype=f32),
        time=0.25,
        seed=-2.5,
    )
    surface = run_pass(kernel, ctx, width, height)

    oracle_rgba8 = Surface(width, height, oracle).to_rgba8()
    assert surface.to_rgba8() == oracle_rgba8


def test_heightgrid_top_row_negative_z_source_adaptation():
    """Upstream 6b2d5d6d flips points/heightGrid's agent Z mapping so the
    image's top row lies at -Z (a top-down view along -Y shows the image as
    authored, not mirrored). The pinned CDN snapshot predates the fix, so a
    regeneration without the adaptation silently reverts the kernel to the
    pre-6b2d5d6d behavior."""
    source = (
        "    // XZ ground plane, Y elevation. These are world coordinates, not UVs.\n"
        "    outXYZ = vec4((uv.x - 0.5) * gridScale,\n"
        "        elevation * heightScale + heightOffset,\n"
        "        (uv.y - 0.5) * gridScale, 1.0);\n"
    )

    adapted = build_module._adapt_source("points/heightGrid", "agent", source)
    assert "(0.5 - uv.y) * gridScale, 1.0);" in adapted
    assert "(uv.y - 0.5) * gridScale, 1.0);" not in adapted
    assert "    // The image's top row lies at -Z, so a view from above along -Y with\n" in adapted

    # The patterns are mandatory: a changed canonical form must fail the build
    # loudly instead of silently keeping the stale lowering.
    with pytest.raises(ValueError, match="heightGrid canonical Z pattern changed"):
        build_module._adapt_source(
            "points/heightGrid",
            "agent",
            source.replace("(uv.y - 0.5) * gridScale, 1.0);", "(0.5 - uv.y) * gridScale, 1.0);"),
        )

    # Other programs pass through unmodified.
    assert build_module._adapt_source("points/heightGrid", "passthrough", source) == source


def test_bundled_heightgrid_kernel_carries_top_row_negative_z():
    kernel = (
        Path(build_module.BUNDLE) / "kernels" / "python" / "points__heightGrid__agent.py"
    ).read_text()

    # outXYZ[2] maps uv.y to Z as (0.5 - uv.y) * gridScale, not (uv.y - 0.5).
    assert 'rt.binary("*", rt.binary("-", rt.f(0.5), rt.swizzle(uv, "y"), 1, "float"), _u_gridScale, 1, "float")' in kernel
    assert 'rt.binary("*", rt.binary("-", rt.swizzle(uv, "y"), rt.f(0.5), 1, "float"), _u_gridScale, 1, "float")' not in kernel


def test_flipmirror_vertical_mirror_keeps_named_half_source_adaptation():
    """Upstream f496735d keeps the named half in flipMirror's vertical mirror
    modes (warpedUV.y runs up the frame, so mode 13 keeps the top half, mode
    14 the bottom, and modes 15-18 follow the same named-half rule). The
    pinned CDN snapshot predates the fix, so a regeneration without the
    adaptation silently reverts the kernel to the pre-f496735d behavior."""
    x_flip = (
        "        if (warpedUV.x > 0.5) {\n"
        "            warpedUV.x = 1.0 - warpedUV.x;\n"
        "        }\n"
    )
    source = (
        "    } else if (flipMode == 13) {\n"
        "        // mirror up to down\n"
        "        if (warpedUV.y > 0.5) {\n"
        "            warpedUV.y = 1.0 - warpedUV.y;\n"
        "        }\n"
        "    } else if (flipMode == 14) {\n"
        "        // mirror down to up\n"
        "        if (warpedUV.y < 0.5) {\n"
        "            warpedUV.y = 1.0 - warpedUV.y;\n"
        "        }\n"
        "    } else if (flipMode == 15) {\n"
        "        // mirror left to right, up to down\n" + x_flip +
        "        if (warpedUV.y > 0.5) {\n"
        "            warpedUV.y = 1.0 - warpedUV.y;\n"
        "        }\n"
        "    } else if (flipMode == 16) {\n"
        "        // mirror left to right, down to up\n" + x_flip +
        "        if (warpedUV.y < 0.5) {\n"
        "            warpedUV.y = 1.0 - warpedUV.y;\n"
        "        }\n"
        "    } else if (flipMode == 17) {\n"
        "        // mirror right to left, up to down\n"
        "        if (warpedUV.x < 0.5) {\n"
        "            warpedUV.x = 1.0 - warpedUV.x;\n"
        "        }\n"
        "        if (warpedUV.y > 0.5) {\n"
        "            warpedUV.y = 1.0 - warpedUV.y;\n"
        "        }\n"
        "    } else if (flipMode == 18) {\n"
        "        // mirror right to left, down to up\n"
        "        if (warpedUV.x < 0.5) {\n"
        "            warpedUV.x = 1.0 - warpedUV.x;\n"
        "        }\n"
        "        if (warpedUV.y < 0.5) {\n"
        "            warpedUV.y = 1.0 - warpedUV.y;\n"
        "        }\n"
        "    }\n"
    )

    adapted = build_module._adapt_source("filter/flipMirror", "flipMirror", source)

    # Mode 13 keeps the top half; the comment explains the named-half rule.
    assert "        // mirror up to down. warpedUV.y runs up the frame, so the top half\n" in adapted
    assert (
        "        // is warpedUV.y > 0.5 and the bottom half samples its reflection.\n"
        "        if (warpedUV.y < 0.5) {\n"
    ) in adapted
    # Mode 14 keeps the bottom half.
    assert "        // mirror down to up\n        if (warpedUV.y > 0.5) {" in adapted
    # Modes 15-18 keep the named half on y.
    assert (
        "        // mirror left to right, up to down\n" + x_flip +
        "        if (warpedUV.y < 0.5) {\n"
    ) in adapted
    assert (
        "        // mirror left to right, down to up\n" + x_flip +
        "        if (warpedUV.y > 0.5) {\n"
    ) in adapted
    assert (
        "        // mirror right to left, up to down\n"
        "        if (warpedUV.x < 0.5) {\n"
        "            warpedUV.x = 1.0 - warpedUV.x;\n"
        "        }\n"
        "        if (warpedUV.y < 0.5) {\n"
    ) in adapted
    assert (
        "        // mirror right to left, down to up\n"
        "        if (warpedUV.x < 0.5) {\n"
        "            warpedUV.x = 1.0 - warpedUV.x;\n"
        "        }\n"
        "        if (warpedUV.y > 0.5) {\n"
    ) in adapted

    # The patterns are mandatory: a changed canonical form must fail the build
    # loudly instead of silently keeping the stale lowering.
    with pytest.raises(ValueError, match="flipMirror canonical vertical mirror pattern changed"):
        build_module._adapt_source(
            "filter/flipMirror",
            "flipMirror",
            source.replace("        if (warpedUV.y > 0.5) {", "        if (warpedUV.y >= 0.5) {", 1),
        )

    # Other programs pass through unmodified.
    assert build_module._adapt_source("filter/flipMirror", "passthrough", source) == source


def test_bundled_flipmirror_kernel_keeps_named_vertical_half():
    kernel = (
        Path(build_module.BUNDLE) / "kernels" / "python" / "filter__flipMirror__flipMirror.py"
    ).read_text()

    # Mode 13 (mirror up to down) mirrors the bottom half onto the top: the
    # condition is warpedUV.y < 0.5, not > 0.5.
    mode13 = kernel[kernel.index('rt.i(13)'):]
    assert 'rt.binary("<", rt.swizzle(warpedUV, "y"), rt.f(0.5))' in mode13[:mode13.index('rt.i(14)')]
    # Mode 14 (mirror down to up) mirrors the top half onto the bottom.
    mode14 = kernel[mode13.index('rt.i(14)'):]
    assert 'rt.binary(">", rt.swizzle(warpedUV, "y"), rt.f(0.5))' in mode14[:mode14.index('rt.i(15)')]


def test_glyphmap_glyph_rows_draw_upright_source_adaptation():
    """Upstream c5d26740 draws glyphMap's glyphs upright: the bitmaps store
    row 0 as the top row while localPos.y runs up the cell, so the row index
    is mirrored (6 - clamp(...)) instead of clamped only. The pinned CDN
    snapshot predates the fix, so a regeneration without the adaptation
    silently reverts the kernel to the pre-c5d26740 behavior."""
    source = (
        "    vec2 localPos = fract(pixelCoord / csf);\n"
        "    int gx = int(floor(localPos.x * 5.0));\n"
        "    int gy = int(floor(localPos.y * 7.0));\n"
        "    gx = clamp(gx, 0, 4);\n"
        "    gy = clamp(gy, 0, 6);\n"
    )

    adapted = build_module._adapt_source("filter/glyphMap", "glyphMap", source)
    assert "    // Glyph row 0 is the top row, while localPos.y runs up the cell.\n" in adapted
    assert "    int gy = 6 - clamp(int(floor(localPos.y * 7.0)), 0, 6);\n" in adapted
    assert "    int gy = int(floor(localPos.y * 7.0));\n" not in adapted
    assert "    gy = clamp(gy, 0, 6);\n" not in adapted

    # The patterns are mandatory: a changed canonical form must fail the build
    # loudly instead of silently keeping the stale lowering.
    with pytest.raises(ValueError, match="glyphMap canonical glyph row pattern changed"):
        build_module._adapt_source(
            "filter/glyphMap",
            "glyphMap",
            source.replace("int gy = int(floor(localPos.y * 7.0));", "int gy = int(floor(localPos.y * 6.0));"),
        )

    # Other programs pass through unmodified.
    assert build_module._adapt_source("filter/glyphMap", "passthrough", source) == source


def test_bundled_glyphmap_kernel_mirrors_glyph_rows():
    kernel = (
        Path(build_module.BUNDLE) / "kernels" / "python" / "filter__glyphMap__glyphMap.py"
    ).read_text()

    # gy = 6 - clamp(int(floor(localPos.y * 7.0)), 0, 6), with the separate
    # gy clamp gone.
    assert 'rt.binary("-", rt.i(6), rt.component_wise("clamp", rt.construct(1, rt.component_wise("floor", rt.binary("*", rt.swizzle(localPos, "y"), rt.f(7.0), 1, "float"), width=1), base="int"), rt.i(0), rt.i(6), width=1), 1, "int")' in kernel
    assert 'gy = rt.component_wise("clamp", gy, rt.i(0), rt.i(6), width=1)' not in kernel


def test_render3d_right_handed_camera_source_adaptation():
    """Upstream 700ac32e builds render3d's camera right-handed (right =
    cross(forward, worldUp), up = cross(right, forward), negated orbit angle)
    and lights it from world -X so the volume is never mirrored. The pinned
    CDN snapshot predates the fix, so a regeneration without the adaptation
    silently reverts the kernel to the pre-700ac32e behavior."""
    source = (
        "    vec3 n = calcNormal(p);\n"
        "    vec3 lightDir = normalize(vec3(1.0, 1.0, -1.0));\n"
        "    float diff = max(dot(n, lightDir), 0.0);\n"
        "    float amb = 0.15;\n"
        "    vec3 lightDir = normalize(vec3(1.0, 1.0, -1.0));\n"
        "    float diff = max(dot(n, lightDir), 0.0);\n"
        "    // Camera setup - orbiting view\n"
        "    float camDist = 3.5;\n"
        "    float angle = time * TAU * float(orbitSpeed);\n"
        "    vec3 forward = normalize(lookAt - ro);\n"
        "    vec3 right = normalize(cross(vec3(0.0, 1.0, 0.0), forward));\n"
        "    vec3 up = cross(forward, right);\n"
    )

    adapted = build_module._adapt_source("render/render3d", "render3d", source)
    assert "vec3 lightDir = normalize(vec3(-1.0, 1.0, -1.0));" in adapted
    assert "vec3 lightDir = normalize(vec3(1.0, 1.0, -1.0));" not in adapted
    assert (
        "    // Camera setup - orbiting view. (right, up, -forward) is right-handed,\n"
        "    // so screen right is world +X seen from the front and the volume is\n"
        "    // never mirrored. The orbit runs toward -X, which keeps the on-screen\n"
        "    // spin of earlier releases.\n"
    ) in adapted
    assert "    float angle = -time * TAU * float(orbitSpeed);\n" in adapted
    assert "    float angle = time * TAU * float(orbitSpeed);\n" not in adapted
    assert "    vec3 right = normalize(cross(forward, vec3(0.0, 1.0, 0.0)));\n" in adapted
    assert "    vec3 up = cross(right, forward);\n" in adapted
    assert "    vec3 right = normalize(cross(vec3(0.0, 1.0, 0.0), forward));\n" not in adapted
    assert "    vec3 up = cross(forward, right);\n" not in adapted

    # The patterns are mandatory: a changed canonical form must fail the build
    # loudly instead of silently keeping the stale lowering.
    with pytest.raises(ValueError, match="render3d canonical light direction pattern changed"):
        build_module._adapt_source(
            "render/render3d",
            "render3d",
            source.replace("vec3 lightDir = normalize(vec3(1.0, 1.0, -1.0));", "vec3 lightDir = normalize(vec3(2.0, 1.0, -1.0));", 1),
        )
    with pytest.raises(ValueError, match="render3d canonical camera pattern changed"):
        build_module._adapt_source(
            "render/render3d",
            "render3d",
            source.replace("float angle = time * TAU * float(orbitSpeed);", "float angle = 2.0 * time * TAU * float(orbitSpeed);"),
        )

    # Other programs pass through unmodified.
    assert build_module._adapt_source("render/render3d", "passthrough", source) == source


def test_bundled_render3d_kernel_carries_right_handed_camera():
    kernel = (
        Path(build_module.BUNDLE) / "kernels" / "python" / "render__render3d__render3d.py"
    ).read_text()

    # The light comes from world -X at both shade sites.
    assert 'rt.normalize(rt.construct(3, rt.unary("-", rt.f(1.0)), rt.f(1.0), rt.unary("-", rt.f(1.0))))' in kernel
    assert 'rt.normalize(rt.construct(3, rt.f(1.0), rt.f(1.0), rt.unary("-", rt.f(1.0))))' not in kernel
    # The orbit angle is negated and the basis is right-handed.
    assert 'rt.binary("*", rt.binary("*", rt.unary("-", _u_time), g.TAU, 1, "float"), rt.construct(1, _u_orbitSpeed), 1, "float")' in kernel
    assert 'rt.normalize(rt.cross(rt.construct(3, rt.f(0.0), rt.f(1.0), rt.f(0.0)), forward))' not in kernel
    assert 'rt.normalize(rt.cross(forward, rt.construct(3, rt.f(0.0), rt.f(1.0), rt.f(0.0))))' in kernel
    assert "up = rt.cross(right, forward)" in kernel
    assert "up = rt.cross(forward, right)" not in kernel


def test_hash_returns_take_the_sibling_float_casts_in_every_effect_but_scatter():
    # The sibling's adaptCanonicalSource rounds the add and the multiply of
    # these hash returns for every effect except filter/scatter. Without it,
    # points/dla's anchor grid lands one half-float step off at 64x64.
    source = "float hash21(vec2 p) {\n    return fract((p3.x + p3.y) * p3.z);\n}\nvec2 hash22(vec2 p) {\n    return fract((p3.xx + p3.yz) * p3.zy);\n}\n"

    adapted = build_module._adapt_source("points/dla", "initGrid", source)

    assert "return fract(float(float(p3.x + p3.y) * p3.z));" in adapted
    assert "return fract(vec2(float(float(p3.x + p3.y) * p3.z), float(float(p3.x + p3.z) * p3.y)));" in adapted
    assert build_module._adapt_source("filter/scatter", "scatter", source) == source


def test_bundled_artifact_sets_match():
    bundle_dir = Path(build_module.BUNDLE)
    metadata = json.loads((bundle_dir / "metadata.json").read_text())
    lock = json.loads((bundle_dir / "bundle-lock.json").read_text())
    pass_keys = {
        render_pass["key"]
        for definition in metadata["effects"].values()
        for render_pass in definition["passes"]
        if render_pass["key"] is not None
    }
    kernel_files = {path.name for path in (bundle_dir / "kernels" / "python").iterdir()}

    assert set(lock["hashes"]) == pass_keys
    assert kernel_files == {build_module._file(key) for key in pass_keys}


def test_build_preserves_iterated_effect_and_pass_execution_metadata(tmp_path, monkeypatch):
    effect = {
        "id": "render/pointsRender",
        "namespace": "render",
        "func": "pointsRender",
        "params": {
            "iterationCount": {"type": "int", "default": 60, "cpuOnly": True},
            "iterations": {"type": "int", "default": 3, "uniform": "iterations"},
        },
        "textures": {"trail": {"width": "50%", "height": "50%", "format": "rgba32f"}},
        "passes": [
            {
                "name": "deposit",
                "program": "deposit",
                "inputs": {"trailTex": "trail"},
                "outputs": {"fragColor": "trail"},
                "uniforms": {"count": "iterations"},
                "repeat": "iterations",
                "blend": ["ONE", "ONE_MINUS_SRC_ALPHA"],
                "clear": False,
                "drawMode": "points",
                "count": "input",
                "countUniform": "iterations",
                "drawBuffers": 1,
                "conditions": {"runIf": [{"uniform": "iterations", "equals": 3}]},
            }
        ],
        "programs": {"deposit": "out vec4 fragColor; void main() { fragColor = vec4(1.0); }"},
    }
    monkeypatch.setattr(build_module, "fetch_effect", lambda _effect_id: effect)

    build_module.build([effect["id"]], out_dir=tmp_path)

    metadata = json.loads((tmp_path / "metadata.json").read_text())
    built = metadata["effects"][effect["id"]]
    assert built["kind"] == "filter"
    assert built["iterated"] is True
    assert built["textures"] == effect["textures"]
    assert built["passes"][0] == {
        **effect["passes"][0],
        "key": "render/pointsRender:deposit",
    }


def test_build_preserves_typed_effect_outputs_and_viewport(tmp_path, monkeypatch):
    effect = {
        "id": "synth3d/testVolume",
        "namespace": "synth3d",
        "func": "testVolume",
        "params": {"volumeSize": {"type": "int", "default": 4, "uniform": "volumeSize"}},
        "textures": {
            "volumeCache": {
                "width": {"param": "volumeSize", "default": 4},
                "height": {"param": "volumeSize", "power": 2, "default": 16},
            },
            "geoBuffer": {
                "width": {"param": "volumeSize", "default": 4},
                "height": {"param": "volumeSize", "power": 2, "default": 16},
            },
        },
        "passes": [
            {
                "name": "precompute",
                "program": "precompute",
                "inputs": {},
                "outputs": {"color": "volumeCache", "geoOut": "geoBuffer"},
                "drawBuffers": 2,
                "viewport": {
                    "width": {"param": "volumeSize", "default": 4},
                    "height": {"param": "volumeSize", "power": 2, "default": 16},
                },
            }
        ],
        "outputTex3d": "volumeCache",
        "outputGeo": "geoBuffer",
        "programs": {
            "precompute": (
                "layout(location = 0) out vec4 fragColor; "
                "layout(location = 1) out vec4 geoOut; "
                "void main() { fragColor = vec4(1.0); geoOut = vec4(0.0); }"
            )
        },
    }
    monkeypatch.setattr(build_module, "fetch_effect", lambda _effect_id: effect)

    build_module.build([effect["id"]], out_dir=tmp_path)

    built = json.loads((tmp_path / "metadata.json").read_text())["effects"][effect["id"]]
    assert built["kind"] == "generator"
    assert built["domain"] == "volume-generator"
    assert built["outputTex3d"] == "volumeCache"
    assert built["outputGeo"] == "geoBuffer"
    assert built["passes"][0]["viewport"] == effect["passes"][0]["viewport"]
    assert built["passes"][0]["outputs"] == {"fragColor": "volumeCache", "geoOut": "geoBuffer"}


def test_build_enables_javascript_vector_storage_for_noise3d(tmp_path, monkeypatch):
    effect = {
        "id": "synth3d/noise3d",
        "namespace": "synth3d",
        "func": "noise3d",
        "params": {},
        "textures": {},
        "passes": [
            {
                "name": "precompute",
                "program": "precompute",
                "inputs": {},
                "outputs": {"fragColor": "outputTex"},
            }
        ],
        "programs": {"precompute": "out vec4 fragColor; void main() { fragColor = vec4(1.0); }"},
    }
    calls = []
    emit_python = build_module.emit_python

    def capture_emit(*args, **kwargs):
        calls.append(kwargs)
        return emit_python(*args, **kwargs)

    monkeypatch.setattr(build_module, "fetch_effect", lambda _effect_id: effect)
    monkeypatch.setattr(build_module, "emit_python", capture_emit)

    build_module.build([effect["id"]], out_dir=tmp_path)

    assert calls == [{"js_vector_storage": True, "effect_id": "synth3d/noise3d"}]


def test_build_failure_preserves_existing_bundle(tmp_path, monkeypatch):
    out_dir = tmp_path / "bundle"
    kernel_dir = out_dir / "kernels" / "python"
    kernel_dir.mkdir(parents=True)
    (out_dir / "metadata.json").write_text("original metadata")
    (out_dir / "bundle-lock.json").write_text(json.dumps({"hashes": {"original:key": "original hash"}}))
    (kernel_dir / "original.py").write_text("original kernel")
    before = _tree_snapshot(out_dir)

    def fetch_effect(effect_id):
        if effect_id == "synth/fetchFailure":
            raise OSError("fetch failed")
        return _simple_effect(effect_id)

    monkeypatch.setattr(build_module, "fetch_effect", fetch_effect)
    monkeypatch.setattr(
        build_module, "emit_python", lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("bad kernel"))
    )

    with pytest.raises(RuntimeError) as exc_info:
        build_module.build(["synth/fetchFailure", "synth/kernelFailure"], out_dir=out_dir)

    assert "synth/fetchFailure" in str(exc_info.value)
    assert "synth/kernelFailure:main" in str(exc_info.value)
    assert _tree_snapshot(out_dir) == before


def test_build_replaces_stale_bundle_artifacts(tmp_path, monkeypatch):
    out_dir = tmp_path / "bundle"
    kernel_dir = out_dir / "kernels" / "python"
    kernel_dir.mkdir(parents=True)
    (out_dir / "metadata.json").write_text("{}")
    (out_dir / "bundle-lock.json").write_text(
        json.dumps({"source": "old", "version": "old", "hashes": {"synth/stale:old": "old hash"}})
    )
    (kernel_dir / "synth__stale__old.py").write_text("stale kernel")
    effect = _simple_effect()
    monkeypatch.setattr(build_module, "fetch_effect", lambda _effect_id: effect)

    build_module.build([effect["id"]], out_dir=out_dir)

    metadata = json.loads((out_dir / "metadata.json").read_text())
    lock = json.loads((out_dir / "bundle-lock.json").read_text())
    pass_keys = {
        render_pass["key"]
        for definition in metadata["effects"].values()
        for render_pass in definition["passes"]
        if render_pass["key"] is not None
    }
    assert pass_keys == {"synth/test:main"}
    assert set(lock["hashes"]) == pass_keys
    assert {path.name for path in (out_dir / "kernels" / "python").iterdir()} == {"synth__test__main.py"}


def test_export_kit_config_is_valid_and_matches_catalog():
    root = Path(__file__).resolve().parent.parent
    config_path = root / "export-kit" / "kit.config.json"
    assert config_path.is_file(), "missing export-kit/kit.config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    assert config.get("id") == "python"
    assert config.get("compat", {}).get("mode") == "list"

    for subtree in config.get("subtrees", []):
        assert (root / subtree["from"]).exists(), f"missing subtree source {subtree['from']}"
    for license_entry in config.get("licenses", []):
        assert (root / license_entry["from"]).is_file(), f"missing license source {license_entry['from']}"

    metadata_rel = config.get("compat", {}).get("fromBundleMetadata")
    assert metadata_rel is not None, "compat.fromBundleMetadata missing"
    metadata_path = root / metadata_rel
    assert metadata_path.is_file(), f"missing {metadata_rel}"

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    effects = metadata.get("effects", {})
    assert len(effects) == 210, "expected 210 catalog effects"
    for effect_id, effect in effects.items():
        assert effect.get("func"), f"effect {effect_id} should declare non-empty func"
        assert effect.get("domain"), f"effect {effect_id} should declare non-empty domain"

    pass_keys = {
        render_pass["key"]
        for effect in effects.values()
        for render_pass in effect.get("passes", [])
        if render_pass.get("key") is not None
    }

    lock_path = metadata_path.parent / "bundle-lock.json"
    assert lock_path.is_file(), "missing bundle-lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    assert len(lock.get("hashes", {})) == 300, "expected 300 locked program hashes"
    assert set(lock.get("hashes", {}).keys()) == pass_keys


def test_package_data_config_covers_runtime_bundle(tmp_path):
    """Regression guard: wheels and sdists must ship the runtime
    bundle. ``renderer.bundle_dir()`` loads metadata.json, bundle-lock.json and
    bundle/kernels/python/*.py from the installed package directory, so the
    [tool.setuptools.package-data] globs must match those paths."""
    import tomllib

    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    patterns = data["tool"]["setuptools"]["package-data"]["noisemaker_cpu"]

    from noisemaker_cpu.renderer import bundle_dir

    bundle = Path(bundle_dir())
    runtime_files = [bundle / "metadata.json", bundle / "bundle-lock.json"]
    runtime_files += sorted((bundle / "kernels" / "python").glob("*.py"))

    assert runtime_files, "bundle runtime files missing from source tree"

    def fnmatch(python_path, pattern):
        import fnmatch as _fnmatch

        posix = python_path.relative_to(bundle.parent.parent).as_posix()
        return _fnmatch.fnmatch(posix, f"noisemaker_cpu/{pattern}")

    for runtime_file in runtime_files:
        assert any(fnmatch(runtime_file, pattern) for pattern in patterns), (
            f"{runtime_file.name} is not covered by package-data patterns {patterns}; "
            "built distributions would omit a runtime-required file"
        )
