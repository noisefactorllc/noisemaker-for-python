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
    assert "displacement, 2, 'float'), rt.construct_raw(2, width, height), 2, 'float')" in kernel
    assert (
        'rt.construct_raw(2, rt.swizzle(_u_resolution, "x"), rt.swizzle(_u_resolution, "y"))'
        not in kernel
    )
    # ...and the displacement clamp is tile-aware.
    assert (
        'maxAllowedDisplacement = (rt.fdiv(maxOffsetPixels, '
        'rt.component_wise("max", width_f, height_f, width=1), 1) if isTiling else'
    ) in kernel


def test_bundled_degauss_kernel_matches_tiled_oracle_render():
    """Node-free regression pin for the 48d25116 tile-awareness delta, against
    committed oracle bytes. With a 32x32 destination inside a 64x64 full
    resolution (renderScale 2 > 1.01), the pre-48d25116 kernel's tile-local
    offset diverges from the oracle by up to 238 rgba8 levels; the committed
    kernel must reproduce the oracle's rgba8 bytes exactly. Oracle surface
    captured from noisemaker-for-cpu 2df5168abbe197eb66e64e0404efff61342b7a2d
    by running
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


def test_bundled_heightgrid_kernel_carries_top_row_negative_z():
    kernel = (
        Path(build_module.BUNDLE) / "kernels" / "python" / "points__heightGrid__agent.py"
    ).read_text()

    # outXYZ[2] maps uv.y to Z as (0.5 - uv.y) * gridScale, not (uv.y - 0.5).
    assert 'rt.binary("*", rt.binary("-", rt.f(0.5), rt.swizzle(uv, "y"), 1, "float"), _u_gridScale, 1, "float")' in kernel
    assert 'rt.binary("*", rt.binary("-", rt.swizzle(uv, "y"), rt.f(0.5), 1, "float"), _u_gridScale, 1, "float")' not in kernel


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


def test_bundled_glyphmap_kernel_mirrors_glyph_rows():
    kernel = (
        Path(build_module.BUNDLE) / "kernels" / "python" / "filter__glyphMap__glyphMap.py"
    ).read_text()

    # gy = 6 - clamp(int(floor(localPos.y * 7.0)), 0, 6), with the separate
    # gy clamp gone.
    assert 'rt.binary("-", rt.i(6), rt.component_wise("clamp", rt.construct(1, rt.component_wise("floor", rt.binary("*", rt.swizzle(localPos, "y"), rt.f(7.0), 1, "float"), width=1), base="int"), rt.i(0), rt.i(6), width=1), 1, "int")' in kernel
    assert 'gy = rt.component_wise("clamp", gy, rt.i(0), rt.i(6), width=1)' not in kernel


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


def test_hash_returns_take_the_sibling_float_casts_including_scatter():
    # The sibling's adaptCanonicalSource rounds the add and the multiply of
    # these hash returns in every effect, including filter/scatter. Without it,
    # points/dla's anchor grid lands one half-float step off at 64x64.
    source = "float hash21(vec2 p) {\n    return fract((p3.x + p3.y) * p3.z);\n}\nvec2 hash22(vec2 p) {\n    return fract((p3.xx + p3.yz) * p3.zy);\n}\n"

    adapted = build_module._adapt_source("points/dla", "initGrid", source)

    assert "return fract(float(float(p3.x + p3.y) * p3.z));" in adapted
    assert "return fract(vec2(float(float(p3.x + p3.y) * p3.z), float(float(p3.x + p3.z) * p3.y)));" in adapted
    assert build_module._adapt_source("filter/scatter", "scatter", source) == adapted


def test_transpiler_applies_the_upstream_8bit_output_quantization():
    # Upstream a1a3fa2a quantizes canonical effect output to 8-bit color in
    # classicNoisedeck/glitch (before scanlines/snow) and filter/crt (before
    # the base_color blend). The locked CDN build in bundle-lock.json predates
    # that revision, so the transpiler injects the same statements.
    glitch = build_module._adapt_source("classicNoisedeck/glitch", "glitch", "color = glitch(uv);")
    assert glitch == (
        "color = glitch(uv);\n"
        "    color.rgb = floor(clamp(color.rgb, 0.0, 1.0) * 255.0 + 0.5) / 255.0;"
    )
    crt = build_module._adapt_source("filter/crt", "crt", "color = mix(base_color, color, alphaVal);")
    assert crt == (
        "vec3 effectColor8 = floor(clamp(color, 0.0, 1.0) * 255.0 + 0.5) / 255.0;\n"
        "    color = mix(base_color, effectColor8, alphaVal);"
    )
    # Other effects and programs are untouched.
    assert build_module._adapt_source("classicNoisedeck/glitch", "scanlines", "color = glitch(uv);") == "color = glitch(uv);"
    assert build_module._adapt_source("filter/crt", "depthKeys", "color = mix(base_color, color, alphaVal);") == "color = mix(base_color, color, alphaVal);"


def test_transpiler_mirrors_the_sibling_testPattern_digit_division_fix():
    # Mirror of the sibling's compile-glsl.js restoreIntegerDivision addition:
    # testPattern's numbered checkerboard divides its int digit accumulator in
    # place. Raw JS `/=` leaves a fractional digit and drops glyph-table
    # lookups; the lowered form truncates. Same exact source guards as the
    # sibling's pass — a changed canonical source must hard-fail, not silently
    # skip the rewrite.
    source = "int temp = number;\n        digits[i] = temp % 10;\n        temp /= 10;\n"
    adapted = build_module._adapt_source("synth/testPattern", "testPattern", source)
    assert "temp = int(temp / 10.0);" in adapted
    assert "temp /= 10;" not in adapted

    # Guards: a changed canonical source raises instead of skipping.
    import pytest
    with pytest.raises(ValueError):
        build_module._adapt_source("synth/testPattern", "testPattern", "int temp = number;\ntemp = temp - 10;")
    # Other effects keep the raw form.
    assert build_module._adapt_source("synth/pattern", "pattern", source) == source


def test_transpiler_mirrors_the_sibling_tile_aware_effect_stack():
    # Upstream Noisemaker 6cb1a3c3 makes classicNoisedeck/effects tile-aware:
    # block grids anchor to fullResolution, convolution steps measure one
    # full-image texel, input taps map through the tile mapping, and the
    # radial zoom clamps its tap under tiling. The locked CDN build predates
    # that revision, so the transpiler applies the same statements here.
    source = (
        "    float dx = size * (1.0 / resolution.x);\n"
        "    float dy = size * (1.0 / resolution.y);\n"
        "    return texture(inputTex, coord).rgb;\n"
        "    vec2 steps = 1.0 / resolution;\n"
        "    float amount = resolution.x / size;\n"
        "\tvec4 base = texture( inputTex, vec2( sx, sy ) );\n"
        "    if( mod( gl_FragCoord.x, dSize ) > size ) {\n"
        "        if( mod( gl_FragCoord.y, dSize ) > size ) {\n"
        "        if( mod( gl_FragCoord.y, dSize ) > size ) {\n"
        "    st *= resolution;\n"
        "    vec3 orig = texture(inputTex, st).rgb;\n"
        "    sum += texture(inputTex, st + vec2(j, i) * 0.004).rgb * strength;\n"
        "        vec4 tex = texture(inputTex, st + tapB);\n"
        "    vec2 imageSize = resolution;\n"
    )
    adapted = build_module._adapt_source("classicNoisedeck/effects", "effects", source)
    assert "float dx = size * (1.0 / fullResolution.x);" in adapted
    assert "float dy = size * (1.0 / fullResolution.y);" in adapted
    assert (
        "return texture(inputTex, (coord * fullResolution - tileOffset)"
        " / vec2(textureSize(inputTex, 0))).rgb;" in adapted
    )
    assert "vec2 steps = 1.0 / fullResolution;" in adapted
    assert "float amount = fullResolution.x / size;" in adapted
    assert (
        "vec4 base = texture( inputTex, (vec2( sx, sy ) * fullResolution"
        " - tileOffset) / vec2(textureSize(inputTex, 0)) );" in adapted
    )
    assert "mod( gl_FragCoord.x + tileOffset.x, dSize )" in adapted
    assert adapted.count("mod( gl_FragCoord.y + tileOffset.y, dSize )") == 2
    assert "st *= fullResolution;" in adapted
    assert (
        "vec3 orig = texture(inputTex, (st * fullResolution - tileOffset)"
        " / vec2(textureSize(inputTex, 0))).rgb;" in adapted
    )
    assert (
        "sum += texture(inputTex, ((st + vec2(j, i) * 0.004) * fullResolution"
        " - tileOffset) / vec2(textureSize(inputTex, 0))).rgb * strength;" in adapted
    )
    assert (
        "if (tileOffset.x != 0.0 || tileOffset.y != 0.0) {\n"
        "            vec2 tapBudget = vec2(256.0) * invFullResolution;\n"
        "            tapB = min(max(tapB, -tapBudget), tapBudget);\n"
        "        }" in adapted
    )
    assert (
        "vec4 tex = texture(inputTex, ((st + tapB) * fullResolution"
        " - tileOffset) / vec2(textureSize(inputTex, 0)));" in adapted
    )
    assert "vec2 imageSize = fullResolution;" in adapted
    # Guards: a changed canonical source raises instead of skipping.
    import pytest
    with pytest.raises(ValueError):
        build_module._adapt_source("classicNoisedeck/effects", "effects", "st *= resolution;")
    # Other effects keep the raw form.
    assert build_module._adapt_source("synth/pattern", "pattern", source) == source


def test_transpiler_mirrors_the_sibling_glyphmap_tiling_detection():
    # Upstream Noisemaker 6cb1a3c3 detects glyphMap tiling from the
    # full-image size differing from the local render size instead of from
    # tileOffset: the origin tile's offset is (0, 0), the same value the
    # runtime writes when not tiling.
    source = "bool isTileRendering = length(tileOffset) > 0.0;\n"
    adapted = build_module._adapt_source("filter/glyphMap", "glyphMap", source)
    assert adapted == (
        "bool isTileRendering = any(notEqual(fullResolution, resolution));\n"
    )
    # Guards: a changed canonical source raises instead of skipping.
    import pytest
    with pytest.raises(ValueError):
        build_module._adapt_source("filter/glyphMap", "glyphMap", "bool isTileRendering = false;")
    # Other effects keep the raw form.
    assert build_module._adapt_source("filter/glyphMap", "preview", source) == source


def test_bundled_effects_kernel_carries_the_tile_mapping():
    kernel = (
        Path(build_module.BUNDLE) / "kernels" / "python"
        / "classicNoisedeck__effects__effects.py"
    ).read_text()
    # Every input tap maps through the tile mapping and the block grids
    # anchor to fullResolution; the radial zoom clamps its tap under tiling.
    assert (
        "rt.binary(\"-\", rt.binary(\"*\", st, _u_fullResolution, 2, 'float'),"
        " _u_tileOffset, 2, 'float')" in kernel
    )
    assert (
        "tapBudget = rt.construct(2, rt.binary(\"*\","
        " rt.construct_raw(2, rt.f(256.0)), _u_invFullResolution, 2, 'float'))" in kernel
    )
    assert "rt.swizzle(_u_fullResolution, \"x\"), size, 1, \"float\")" in kernel
    # The untiled identity is exact: the old resolution-based form is gone.
    assert "rt.binary(\"*\", st, _u_resolution, 2, \"float\")" not in kernel


def test_bundled_glyphmap_kernel_detects_tiling_from_the_full_resolution():
    kernel = (
        Path(build_module.BUNDLE) / "kernels" / "python" / "filter__glyphMap__glyphMap.py"
    ).read_text()
    # Tiling is detected from the full-image size differing from the local
    # render size; the origin tile's tileOffset is (0, 0), the same value the
    # runtime writes when not tiling.
    assert (
        "rt.component_wise(\"any\", rt.component_wise(\"notEqual\","
        " _u_fullResolution, resolution, width=2), width=2)" in kernel
    )
    assert "rt.length(_u_tileOffset)" not in kernel


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
    monkeypatch.setattr(build_module, "_adapt_source", lambda _eid, _program, source: source)

    build_module.build([effect["id"]], out_dir=tmp_path)

    assert calls == [
        {
            "js_vector_storage": True,
            "atomic_compound": False,
            "effect_id": "synth3d/noise3d",
            "constant_divisors": {},
        }
    ]


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


def test_transpiler_substitutes_the_locked_build_program_sources():
    # The bundle is built from the locked CDN build, whose program sources
    # predate behavior upstream Noisemaker b71a896a ships natively. The
    # transpiler substitutes the newer program source verbatim for exactly
    # the locked build's text, so the shipped kernels keep the behavior the
    # CPU authority's canonical kernels encode while the lock keeps the
    # published fetch pin.
    for (effect_id, program), entry in build_module._LOCKED_BUILD_PROGRAM_SOURCES.items():
        adapted = build_module._adapt_source(effect_id, program, entry["locked"])
        if (effect_id, program) == ("synth/media", "mediaInput"):
            assert "uniform vec2 tileOffset;" in adapted
            assert "gl_FragCoord.xy + tileOffset" in adapted
        if (effect_id, program) == ("synth3d/cellularAutomata3d", "simulate"):
            assert "uniform int colorMode;" in adapted
            assert "vec4 packState(float alive, float age)" in adapted
        assert adapted != entry["locked"]


def test_transpiler_mirrors_cellular_automata3d_age_state():
    source = (
        "uniform float weight;\nuniform bool resetState;\n"
        "out vec4 fragColor;\n"
        "float hash3(vec3 p) {\n"
        "    p = p + float(seed) * 0.1;\n"
        "    p = fract(p * vec3(0.1031, 0.1030, 0.0973));\n"
        "    p += dot(p, p.yxz + 33.33);\n"
        "    return fract((p.x + p.y) * p.z);\n}\n"
        "int countMooreNeighbors(ivec3 voxel, int volSize) { return 0; }\nvoid main() {\n"
        "fragColor = vec4(alive, alive, alive, 1.0);\n"
        "fragColor = vec4(finalAlive, finalAlive, finalAlive, 1.0);\n}\n"
    )
    adapted = build_module._adapt_source("synth3d/cellularAutomata3d", "simulate", source)
    assert "uniform int colorMode;" in adapted
    assert "if (colorMode == 1) return vec4(alive, age, 0.0, 1.0);" in adapted
    assert "fragColor = packState(alive, age);" in adapted
    assert "fragColor = packState(finalAlive, finalAge);" in adapted
    assert build_module._adapt_source("synth3d/cellularAutomata3d", "precompute", source) == source
    import pytest
    with pytest.raises(ValueError, match="cellularAutomata3d state source changed"):
        changed = source.replace("fragColor = vec4(alive, alive, alive, 1.0);", "fragColor = vec4(1.0);")
        build_module._adapt_source("synth3d/cellularAutomata3d", "simulate", changed)


def test_bundled_points_agent_kernels_carry_behavior_local_texture_inputs():
    """The c4f7cdd7 behavior-local particle texture inputs: every points agent
    kernel colors particles from diffuseTex through the gated selectedDiffuse
    helper, and the field-mapped behaviors read fieldTex/heightTex gated on
    fieldActive instead of plain inputTex."""
    kernel_dir = Path(build_module.BUNDLE) / "kernels" / "python"
    agents = [
        "points__attractor__agent.py",
        "points__buddhabrot__agent.py",
        "points__dla__agent.py",
        "points__flock__agent.py",
        "points__flow__agent.py",
        "points__hydraulic__agent.py",
        "points__lenia__agentField.py",
        "points__life__agent.py",
        "points__physarum__agent.py",
        "points__physical__agent.py",
    ]
    for name in agents:
        kernel = (kernel_dir / name).read_text()
        assert '_u_diffuseTex = T["diffuseTex"]' in kernel, name
        assert 'U.get("diffuseActive", rt.f(0.0))' in kernel, name
    for name in ("points__dla__agent.py", "points__flow__agent.py", "points__physarum__agent.py"):
        kernel = (kernel_dir / name).read_text()
        assert 'U.get("fieldActive", rt.f(0.0))' in kernel, name
    hydraulic = (kernel_dir / "points__hydraulic__agent.py").read_text()
    assert '_u_heightTex = T["heightTex"]' in hydraulic
    assert 'U.get("fieldActive", rt.f(0.0))' in hydraulic
    life = (kernel_dir / "points__life__agent.py").read_text()
    # The diffuse branch precedes the type-color fallback the locked source had.
    assert life.index('if rt.binary(">", _u_diffuseActive') < life.index("if _u_useTypeColor:")


def test_bundled_points_agent_kernels_carry_base_color_memory():
    """The 12751c78 per-behavior base-color memory: every base-color agent
    kernel reads baseColorTex, writes outBaseColor through keptBaseColor, and
    the dla/flow/physarum field sampler answers to the upstream heightTex
    name."""
    kernel_dir = Path(build_module.BUNDLE) / "kernels" / "python"
    for name in (
        "points__attractor__agent.py",
        "points__buddhabrot__agent.py",
        "points__dla__agent.py",
        "points__flock__agent.py",
        "points__flow__agent.py",
        "points__hydraulic__agent.py",
        "points__lenia__agentField.py",
        "points__physarum__agent.py",
        "points__physical__agent.py",
    ):
        kernel = (kernel_dir / name).read_text()
        assert '_u_baseColorTex = T["baseColorTex"]' in kernel, name
        assert "keptBaseColor__" in kernel and "baseColor__" in kernel, name
    for name in ("points__dla__agent.py", "points__flow__agent.py", "points__physarum__agent.py"):
        kernel = (kernel_dir / name).read_text()
        assert "_u_fieldTex" not in kernel and '_u_heightTex = T["heightTex"]' in kernel, name
    lenia = (kernel_dir / "points__lenia__agentField.py").read_text()
    assert '_u_fieldTex = T["fieldTex"]' in lenia
    life = (kernel_dir / "points__life__agent.py").read_text()
    assert "_u_baseColorTex" not in life


def test_bundled_points_catalog_carries_base_color_memory_contract():
    """The 12751c78 catalog contract: each base-color behavior declares its
    global_<behavior>_base_color memory (stateSize, inherit: true, rgba8),
    binds it through baseColorTex/outBaseColor, and the agent pass draws to
    four buffers."""
    effects = json.loads((Path(build_module.BUNDLE) / "metadata.json").read_text())["effects"]
    for eid in (
        "points/attractor",
        "points/buddhabrot",
        "points/dla",
        "points/flock",
        "points/flow",
        "points/hydraulic",
        "points/lenia",
        "points/physarum",
        "points/physical",
    ):
        behavior = eid.split("/")[1]
        memory = f"global_{behavior}_base_color"
        effect = effects[eid]
        assert effect["textures"][memory] == {
            "width": {"param": "stateSize", "inherit": True, "default": 256},
            "height": {"param": "stateSize", "inherit": True, "default": 256},
            "format": "rgba8",
        }, eid
        agent = next(p for p in effect["passes"] if p["program"].startswith("agent"))
        assert agent["inputs"]["baseColorTex"] == memory, eid
        assert agent["outputs"]["outBaseColor"] == memory, eid
        assert agent["drawBuffers"] == 4, eid
    life = next(
        p for p in effects["points/life"]["passes"] if p["program"] == "agent"
    )
    assert life["drawBuffers"] == 4 and "baseColorTex" not in life["inputs"]


def test_bundled_points_catalog_carries_published_texture_param_contract():
    """The published c4f7cdd7 parameter contract: the points behaviors expose
    their diffuse/field surface params with the colorModeUniform fallback, the
    field/height maps default to none (the kernel gates on fieldActive), and
    pointsEmit no longer carries its dead diffuse-map param."""
    effects = json.loads((Path(build_module.BUNDLE) / "metadata.json").read_text())["effects"]
    for eid in (
        "points/attractor",
        "points/buddhabrot",
        "points/dla",
        "points/flock",
        "points/flow",
        "points/hydraulic",
        "points/lenia",
        "points/physarum",
        "points/physical",
    ):
        spec = effects[eid]["params"]["diffuseTex"]
        assert spec["type"] == "surface" and spec["default"] == "none", eid
        assert spec["colorModeUniform"] == "diffuseActive", eid
    for eid in ("points/dla", "points/flow", "points/physarum"):
        spec = effects[eid]["params"]["heightTex"]
        assert spec["default"] == "none" and spec["colorModeUniform"] == "fieldActive", eid
        assert effects[eid]["paramAliases"] == {"fieldTex": "heightTex"}, eid
    spec = effects["points/hydraulic"]["params"]["heightTex"]
    assert spec["default"] == "none" and spec["colorModeUniform"] == "fieldActive"
    spec = effects["points/life"]["params"]["diffuseTex"]
    assert spec["default"] == "none" and spec["colorModeUniform"] == "diffuseActive"
    emit = effects["render/pointsEmit"]
    assert "diffuseTex" not in emit["params"]
    init = next(p for p in emit["passes"] if p["program"] == "init")
    assert init["inputs"]["inputTex"] == "inputTex"
