<!-- repo-hero -->
<a href="https://noisemaker.app/"><img src="docs/hero.jpg" alt="Noisemaker for CPU (Python)" width="100%"></a>

<sub>Open source from <a href="https://noisefactor.io">Noise Factor</a> &middot; <a href="https://github.com/noisefactorllc">more projects</a></sub>

# noisemaker-for-python

> This package supports the "Export Shader Pipeline" feature in Noisedeck.app. The feature runs shader compositions on other platforms. Noise Factor derives this package from the upstream Noisemaker Engine project and tests it for pixel-level parity.

This is not the classic Python Noisemaker (Composer) library. This is a new
effort centered around software shader execution.

A pure-Python CPU implementation of the [Noisemaker](https://noisemaker.app)
shader engine — the Python port of [`noisemaker-for-cpu`](https://github.com/noisefactorllc/noisemaker-for-cpu).

Effect kernels are **transpiled directly from the upstream GLSL** served by the
`shaders.noisedeck.app` CDN (pinned by version), not hand-maintained. A pure-Python GLSL→Python transpiler (`transpiler/`) lexes, preprocesses, parses, and emits a NumPy-backed kernel per shader pass. A small runtime reproduces the reference engine's float model:

- Float32 vectors.
- Float64 scalar arithmetic.
- Half-float texture quantization.
- Screen-space derivatives.
- Bit-exact uint32/PCG hashing.

**The bundle contains all 210 catalog effects**, transpiled from published engine `1.0.271` (Noisemaker `5976b7a6`). `scripts/parity-summary` renders every one of them and compares it with the pinned `noisemaker-for-cpu` oracle at zero byte tolerance: 210 of 210 are byte-identical (8×8, seed 1, time 0.25). Single-frame effects render through the `effect` CLI path; iterated, typed-chain, volume and loop effects through DSL programs; and the five reactive/mesh effects (`synth/roll`, `synth/scope`, `synth/spectrum`, `render/meshLoader`, `render/meshRender`) through deterministic MIDI, audio and mesh fixtures synced from the oracle's own parity fixtures. These cases cover the catalog, not every parameter, resolution or animation.
Iterated effects default to `iterationCount: 60`. Particle pipelines share state from `pointsEmit()` through their point and render steps.

## Install

```bash
pip install -e ".[dev]"      # requires Python 3.11+, numpy, click
```

## Render an effect

CLI (modeled after the [`noisemaker`](https://github.com/noisefactorllc/noisemaker) CLI):

```bash
# Fast first render of the same effect: 48x48 with an explicit seed runs in
# well under a minute on one CPU core (~20 s measured) and writes a real image.
noisemaker-py generate synth/curl --width 48 --height 48 --seed 1 --filename curl.png

# Full-size render. Expect roughly 35-40 minutes on one CPU core for 512x512:
# the engine is single-threaded and the CLI prints nothing more until the
# finished file lands (no progress output between the effect id and completion).
noisemaker-py generate synth/curl --width 512 --height 512 --filename curl.png

# `generate random` picks a random non-iterated, input-free generator; like
# every command it takes --width/--height/--seed.

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
from the CDN at the exact engine version recorded in `bundle-lock.json`. To rebuild
them (requires `json5`):

```bash
pip install -e ".[build]"
python -m transpiler.build --all
```

To move the bundle to a newer engine release, name it and update the lock:
`NM_SHADER_VERSION=1.0.271 python -m transpiler.build --all --update-lock`.

## Tests

```bash
pytest
```

`pytest -m "not slow and not oracle"` is the quick, node-free subset that CI runs
on every push. `scripts/test` is the full gate, which CI runs weekly: it clones
`noisemaker-for-cpu` at the pinned revision, runs every test against it with
Node, and then runs `scripts/parity-summary`. A kit is released only after that
full gate passes. `tests/data/parity-receipt-<revision>.json` records the
oracle's output hashes for the single-frame and reactive/mesh effects, so the
`slow` receipt test checks byte parity without Node.

## License

MIT © Noise Factor LLC. See [LICENSE](LICENSE).
