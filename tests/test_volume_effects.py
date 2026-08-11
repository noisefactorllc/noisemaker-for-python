import numpy as np
import pytest

from noisemaker_cpu import renderer


def _volume_fixture(monkeypatch, *, bad_atlas=False):
    observed_volume_sizes = []
    atlas_height = 8 if bad_atlas else {"param": "volumeSize", "power": 2, "default": 16}
    effects = {
        "synth3d/volumeSeed": {
            "namespace": "synth3d",
            "kind": "generator",
            "domain": "volume-generator",
            "params": {"volumeSize": {"type": "int", "default": 4, "uniform": "volumeSize"}},
            "textures": {
                "volumeCache": {"width": {"param": "volumeSize"}, "height": atlas_height, "format": "rgba32f"},
                "geoBuffer": {"width": {"param": "volumeSize"}, "height": atlas_height, "format": "rgba32f"},
            },
            "passes": [
                {
                    "name": "seed",
                    "program": "seed",
                    "key": "synth3d/volumeSeed:seed",
                    "inputs": {},
                    "outputs": {"fragColor": "volumeCache", "geoOut": "geoBuffer"},
                    "drawBuffers": 2,
                }
            ],
            "outputTex3d": "volumeCache",
            "outputGeo": "geoBuffer",
        },
        "filter3d/volumeFilter": {
            "namespace": "filter3d",
            "kind": "filter",
            "domain": "volume-filter",
            "params": {"volumeSize": {"type": "int", "default": 8, "uniform": "volumeSize"}},
            "textures": {
                "volumeCache": {
                    "width": {"param": "volumeSize", "inputOverride": "inputTex3d"},
                    "height": {"param": "volumeSize", "power": 2, "inputOverride": "inputTex3d"},
                    "format": "rgba32f",
                }
            },
            "passes": [
                {
                    "name": "filter",
                    "program": "filter",
                    "key": "filter3d/volumeFilter:filter",
                    "inputs": {"source": "inputTex3d"},
                    "outputs": {"fragColor": "volumeCache"},
                }
            ],
            "outputTex3d": "volumeCache",
            "outputGeo": "inputGeo",
        },
        "render/volumeRender": {
            "namespace": "render",
            "kind": "filter",
            "domain": "volume-renderer",
            "params": {"volumeSize": {"type": "int", "default": 8, "uniform": "volumeSize"}},
            "textures": {"screenGeo": {"width": "resolution", "height": "resolution", "format": "rgba32f"}},
            "passes": [
                {
                    "name": "render",
                    "program": "render",
                    "key": "render/volumeRender:render",
                    "inputs": {"volume": "inputTex3d", "geometry": "inputGeo"},
                    "outputs": {"fragColor": "outputTex", "geoOut": "screenGeo"},
                    "drawBuffers": 2,
                }
            ],
            "outputTex3d": "inputTex3d",
            "outputGeo": "screenGeo",
        },
    }

    def seed(ctx, out):
        out[0][:] = [ctx.resolution[0] / 100, ctx.resolution[1] / 100, 0.0, 1.0]
        out[1][:] = [0.75, 0.0, 0.0, 1.0]

    seed.output_names = ("fragColor", "geoOut")

    def volume_filter(ctx, out):
        observed_volume_sizes.append(("filter", ctx.uniforms["volumeSize"]))
        source = ctx.textures["source"].data[:4]
        out[:] = [source[0], source[1], ctx.uniforms["volumeSize"] / 10, 1.0]

    def volume_render(ctx, out):
        observed_volume_sizes.append(("render", ctx.uniforms["volumeSize"]))
        volume = ctx.textures["volume"].data[:4]
        geometry = ctx.textures["geometry"].data[:4]
        out[0][:] = [volume[0], volume[1], geometry[0], 1.0]
        out[1][:] = [0.0, 0.0, 0.0, 1.0]

    volume_render.output_names = ("fragColor", "geoOut")

    kernels = {
        "synth3d/volumeSeed:seed": seed,
        "filter3d/volumeFilter:filter": volume_filter,
        "render/volumeRender:render": volume_render,
    }
    monkeypatch.setattr(renderer, "_meta", lambda: {"effects": effects})
    monkeypatch.setattr(renderer, "_kernel_for", kernels.__getitem__)
    return observed_volume_sizes


def test_volume_and_geometry_atlases_flow_through_typed_chain(monkeypatch):
    observed_volume_sizes = _volume_fixture(monkeypatch)

    surface = renderer.render_dsl(
        "search synth3d, filter3d, render\n"
        "volumeSeed(volumeSize: 4).volumeFilter(volumeSize: 8).volumeRender(volumeSize: 8).write(o0)\n"
        "render(o0)",
        width=1,
        height=1,
    )

    assert np.allclose(surface.data[:4], np.array([0.04, 0.16, 0.75, 1.0], dtype=np.float32), atol=0.0002)
    assert set(observed_volume_sizes) == {("filter", 4), ("render", 4)}


def test_volume_generator_rejects_noncanonical_atlas_dimensions(monkeypatch):
    _volume_fixture(monkeypatch, bad_atlas=True)

    with pytest.raises(ValueError, match=r"volume atlas expected 4x16, received 4x8"):
        renderer.render_dsl(
            "search synth3d, render\nvolumeSeed(volumeSize: 4).volumeRender().write(o0)\nrender(o0)",
            width=1,
            height=1,
        )
