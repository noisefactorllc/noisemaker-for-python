# noisemaker-cpu (Python)

A pure-Python CPU implementation of the [Noisemaker](https://noisemaker.app)
shader engine — the Python port of [`noisemaker-cpu`](https://github.com/noisefactorllc/noisemaker-cpu).

Effect kernels are **transpiled directly from the upstream GLSL** served by the
`shaders.noisedeck.app` CDN (pinned by version), not hand-maintained. A pure-Python
GLSL→Python transpiler (`transpiler/`) lexes, preprocesses, parses, and emits a
NumPy-backed kernel per shader pass; a small runtime reproduces the reference
engine's float model (float32 vectors, float64 scalar arithmetic, half-float
texture quantization, screen-space derivatives, bit-exact uint32/PCG hashing).

**165 effects** are bundled; **163 render at byte-parity** with the JavaScript
engine's `effect` CLI (8×8, seed 1). The two that don't are only untestable via
that harness (they need an external texture the CLI won't supply). Two further
effects have JS-computed definitions the static extractor can't reproduce.

## Install

```bash
pip install -e ".[dev]"      # requires Python 3.11+, numpy
```

## Render an effect

CLI:

```bash
noisemaker-cpu effect synth/curl --width 512 --height 512 --output curl.png
noisemaker-cpu effect filter/chrome --input photo.png --output chrome.png
```

Library:

```python
from noisemaker_cpu.renderer import render_effect
from noisemaker_cpu.png import encode_png

surface = render_effect("synth/curl", {"scale": 16}, width=512, height=512, seed=1)
with open("curl.png", "wb") as f:
    f.write(encode_png(surface))
```

## Regenerating the bundle

The vendored kernels + metadata under `src/noisemaker_cpu/bundle/` are generated
from the CDN. To rebuild (requires `json5`):

```bash
pip install -e ".[build]"
python -m transpiler.build --all
```

## Tests

```bash
pytest
```

Cross-language parity against the JS engine (`scripts/parity.py`) needs a sibling
`noisemaker-cpu` checkout and Node.

## License

MIT © Noise Factor LLC. See [LICENSE](LICENSE).
