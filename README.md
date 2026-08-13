# noisemaker-for-python

This is not the classic Python Noisemaker (Composer) library. This is a new
effort centered around software shader execution.

A pure-Python CPU implementation of the [Noisemaker](https://noisemaker.app)
shader engine — the Python port of [`noisemaker-cpu`](https://github.com/noisefactorllc/noisemaker-cpu).

Effect kernels are **transpiled directly from the upstream GLSL** served by the
`shaders.noisedeck.app` CDN (pinned by version), not hand-maintained. A pure-Python
GLSL→Python transpiler (`transpiler/`) lexes, preprocesses, parses, and emits a
NumPy-backed kernel per shader pass; a small runtime reproduces the reference
engine's float model (float32 vectors, float64 scalar arithmetic, half-float
texture quantization, screen-space derivatives, bit-exact uint32/PCG hashing).

**All 188 catalog effects** are bundled. The 167 single-frame effects retain
byte parity with the JavaScript engine's `effect` CLI, while the 21 stateful and
particle effects have exact JS CPU DSL parity at controlled iteration counts.
Iterated effects default to `iterationCount: 60`; particle pipelines share state
from `pointsEmit()` through their point and render steps.

## Install

```bash
pip install -e ".[dev]"      # requires Python 3.11+, numpy, click
```

## Render an effect

CLI (modeled after the [`noisemaker`](https://github.com/noisefactorllc/noisemaker) CLI):

```bash
# generate a single frame
noisemaker-py generate synth/curl --width 512 --height 512 --filename curl.png
noisemaker-py generate random --seed 42

# apply an effect to an existing image
noisemaker-py apply filter/chrome photo.png --filename chrome.png

# animate an effect over time (needs ffmpeg for .mp4; or --save-frames DIR)
noisemaker-py animate synth/curl --frame-count 60 --filename curl.mp4
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
