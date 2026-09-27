<!-- repo-hero -->
<a href="https://noisemaker.app/"><img src="docs/hero.jpg" alt="Noisemaker for CPU (Python)" width="100%"></a>

<sub>Open source from <a href="https://noisefactor.io">Noise Factor</a> &middot; <a href="https://github.com/noisefactorllc">more projects</a></sub>

# noisemaker-for-python

Current measured support: [compatibility report](docs/COMPATIBILITY.md).

Current qualification limits: [completion gaps](docs/COMPLETION_GAPS.md).

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

**The current bundle contains 205 CPU catalog effects.** For the current 205-effect bundle, the default image harness (8×8, seed 1, time 0.25) compares the 167 single-frame effects runnable at the harness's fixed context with zero byte tolerance (all passing; the remaining 38 effects are outside that harness's context and are each covered instead by a committed DSL chain that matches the same pinned oracle with zero byte tolerance — see `docs/COMPLETION_GAPS.md` §3, "Parity and authority reconciliation, 2026-09-27"). The image harness's 167-effect result is recorded in `docs/COMPATIBILITY.md` §6. The 5 authority-manifest effect IDs the catalog does not target (`render/meshLoader`, `render/meshRender`, `synth/roll`, `synth/scope`, `synth/spectrum`) are documented exclusions, and the tested contexts do not constitute the complete parameter matrix; no claim is made beyond the recorded cases.
Iterated effects default to `iterationCount: 60`. Particle pipelines share state from `pointsEmit()` through their point and render steps.

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
`noisemaker-for-cpu` checkout and Node. The image harness's most recent
source-bound result (2026-09-27, see `docs/COMPATIBILITY.md` §6) compared 167
effects with zero byte tolerance and reported 38 exclusions, each covered by a
committed DSL byte-parity case against the same oracle; both valid
`renderLandscape3d` filtering choices (`isosurface`, `voxel`) also match the
oracle exactly, and authority reconciliation against immutable CDN build
`1.0.190` finds 294/294 program GLSL hashes matching the bundle lock (GAP-001
closed 2026-09-27; see `docs/COMPLETION_GAPS.md`). The tested contexts do not
constitute the complete parameter matrix.

## License

MIT © Noise Factor LLC. See [LICENSE](LICENSE).
