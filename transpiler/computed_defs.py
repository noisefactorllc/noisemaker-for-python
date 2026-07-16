"""Hand-ported definitions for effects whose CDN bundle builds `globals`/`passes`
with real JavaScript (loops, spreads) rather than literals, so the static
extractor can't read them. The GLSL programs are still transpiled from the CDN;
only the definition (params/passes) is reproduced here, faithful to the JS.

- mixer/mashup: `d()` generates layer0_tex..layer7_tex surface params (max 8),
  each with a `layerN_active` colorModeUniform; `c` wires them plus `source`
  into the single render pass's inputs.
"""

from __future__ import annotations

_MASHUP_LAYERS = 8


def _mashup():
    params = {
        "source": {"type": "surface", "default": "none"},
        "layers": {"type": "int", "default": 4, "uniform": "layers"},
        "smoothness": {"type": "float", "default": 0.1, "uniform": "smoothness"},
    }
    inputs = {"source": "source"}
    for e in range(_MASHUP_LAYERS):
        params[f"layer{e}_tex"] = {"type": "surface", "default": "none",
                                   "colorModeUniform": f"layer{e}_active"}
        inputs[f"layer{e}_tex"] = f"layer{e}_tex"
    passes = [{"name": "render", "program": "mashup", "inputs": inputs,
               "outputs": {"fragColor": "outputTex"}}]
    return {"namespace": "mixer", "func": "mashup", "params": params,
            "passes": passes, "textures": {}, "externalTexture": None}


COMPUTED_DEFS = {
    "mixer/mashup": _mashup(),
}
