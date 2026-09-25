# noisemaker-for-python: compatibility report

## 1. Source and authority revisions

Daily review: 2026-09-25. Current inspected source: [`49d8e51ec4b71104dc03728c84c60cae3e2857d3`](https://github.com/noisefactorllc/noisemaker-for-python/commit/49d8e51ec4b71104dc03728c84c60cae3e2857d3).
Full rendered parity remains **unverified** with open nondefault parity failures. No release approval or new closure follows from this review.
Reviewed worker audit: `audit-20260925-090206` at source [`912e6a9aac32c668a5242b8d52aa4415ca3a848e`](https://github.com/noisefactorllc/noisemaker-for-python/commit/912e6a9aac32c668a5242b8d52aa4415ca3a848e), published in commit [`4ff7b03247b59cead0b63a7ee3a7b5697f7bf58e`](https://github.com/noisefactorllc/noisemaker-for-python/commit/4ff7b03247b59cead0b63a7ee3a7b5697f7bf58e).
Post-worker commit [`49d8e51ec4b71104dc03728c84c60cae3e2857d3`](https://github.com/noisefactorllc/noisemaker-for-python/commit/49d8e51ec4b71104dc03728c84c60cae3e2857d3) updated sibling source lock assertions in `tests/test_parity.py` for upstream `240740dd2d30cbd0984b179834ab24abe71c8fb2`.
Python runtime bundle and engine sources remain at the earlier snapshot with 205 effects versus 210 in published `1.0.180`.
Current upstream discovery SHA: `240740dd2d30cbd0984b179834ab24abe71c8fb2`.
Local and remote `main` match at `49d8e51ec4b71104dc03728c84c60cae3e2857d3`.
Served kit `0.1.7` identifies `1901b267a8b8ef29efc702cc3976b70f8aae0404`.

### Worker audit observations

Worker audit: 2026-09-25. Reviewed source: [`912e6a9aac32c668a5242b8d52aa4415ca3a848e`](https://github.com/noisefactorllc/noisemaker-for-python/commit/912e6a9aac32c668a5242b8d52aa4415ca3a848e).
Local and remote `main` matched before execution. Tests used regular-file snapshots with recorded source hashes.
CPU oracle: `fcb576f39a2632a6d50e79ca9f6a1bfb0daa7221`, with upstream pin `4891b9953f9fd8a61cf9ae0dda2fe747a9be82df`.
Current upstream and published `1.0.180`: `240740dd2d30cbd0984b179834ab24abe71c8fb2`.
The current manifest contains 210 effects. The Python catalog contains 205 effects.
Full parity is **failed** for tested nondefault cases and **unverified** for complete coverage. Release readiness remains **blocked**.
[Source hashes](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/source-hashes.json). [Authority metadata](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/published-authority.json).

Served kit `0.1.7` identifies `1901b267a8b8ef29efc702cc3976b70f8aae0404`.
All 329 served files match their inventory hashes. All 324 engine files match the reviewed source.
The existing builder reproduces all 329 inventoried files. Later source changes affect only tests and audit documents.
[Served verification](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/served-verification.json). [Reproduction](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/kit-reproduction.json). [Source comparison](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/kit-source-diff.json).

The candidate wheel and source archive omit all bundle JSON files. Installation succeeds, but the first render fails with missing `bundle/metadata.json`.
No PyPI project exists at the checked project endpoint. The GitHub API returned no releases.
[Wheel failure](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/wheel-first-output.json). [Archive inventory](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/sdist-inventory.json). [Endpoint observations](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/endpoint-results.json).

Audit publication covers only these two reports. Their paths match no existing workflow.
No implementation, release, or parity checkpoint changes belong to this audit.

### Earlier review observations

Daily review: 2026-09-25. Current inspected source: [`93b8b141d21a7c853a89131166147c8337109144`](https://github.com/noisefactorllc/noisemaker-for-python/commit/93b8b141d21a7c853a89131166147c8337109144).
Full rendered parity remains **unverified**. No release approval or new closure follows from this review.
Current upstream discovery: `bbdeb56c4b75cf33379766c3e87b0f5a18bcbba8`. Published Noisemaker authority: `1.0.179`, source `fca611fd8f91424661d4e531d39313d24ea21134`, 210 effect IDs.
The observations below retain their original source and authority identities. They do not qualify later updates.
Current served kit: `0.1.7`, source `1901b267a8b8ef29efc702cc3976b70f8aae0404`. [Retrieved inventory and hashes](/Users/alex/.codex/automations/noisemaker-port-completion-audit/review-20260925-053200/current-served-inventories.json). Artifact identity does not establish host qualification.

### Earlier source observations

Report date: 2026-09-24. Source inspected: [`70c03da6944be1319ccc249fd9646dd9df05e86c`](https://github.com/noisefactorllc/noisemaker-for-python/commit/70c03da6944be1319ccc249fd9646dd9df05e86c).
Full rendered parity at this SHA: **unverified**. This is not a release approval.
A later documentation-only commit does not change this tested source identity.
Any runtime, package, or authority update requires fresh evidence before this report can qualify it.

Python CPU shader rendering with NumPy and Click. Python 3.11 is the declared floor. This is separate from classic Composer. [Source contract](https://github.com/noisefactorllc/noisemaker-for-python/blob/70c03da6944be1319ccc249fd9646dd9df05e86c/README.md).

Bundle metadata records CDN version `1.0`. Shader hashes exist in the bundle lock. No CPU oracle commit was identified in this pass.
Current upstream discovery SHA: `c9ee8a049b2b63cd300da67c01ee40baf29dc288`.
Published authority: `1.0.176`, source `c9ee8a049b2b63cd300da67c01ee40baf29dc288`.
[Immutable published manifest](https://shaders.noisedeck.app/1.0.176/effects/manifest.json) contains 210 effect IDs.
Its SHA-256 is `05c4d7b7744837ae90a3bb4c89e5403ff09448a74d9d7e824abb3d719ad3314e`.
These IDs do not define complete parameter, state, input, or platform coverage.

Served kit `0.1.6` records `d42872842cd6aa14aa585103df35267a46156ec7`. [Source metadata](https://kits.noisedeck.app/python/0/deployment-meta.json).
Historical measurements remain bound to their original revisions in [completion gaps](COMPLETION_GAPS.md).

## 2. Host and distribution matrix

### Current worker measurements

| Dimension | Status | Measured scope or limit |
|---|---|---|
| Python 3.14.5, macOS arm64, NumPy CPU | verified | Small CLI and public-library rendering, filtering, three-frame H.264 output, error recovery, and cancellation. |
| Editable installation | verified | Private source installation and removal. No global installation. |
| Wheel and source archive | failed | Required bundle JSON files are absent. Wheel first render fails. GAP-004. |
| Served kit 0.1.7 | verified | All 329 file hashes, all 324 engine source hashes, rebuilt inventory, first render, invalid DSL, and recovery. |
| README 512×512 first result | blocked | Probe exceeded 180 seconds under concurrent load. Smaller output passes. |
| Minimum Python 3.11, other systems, upgrades | unverified | Runtime unavailable or workflow not executed. |
| Default image parity | verified | 167 exact 8×8 comparisons against the recorded CPU snapshot. |
| Nondefault alpha and feedback | failed | Maximum byte differences 179 and 1 respectively. GAP-005. |
| Current landscape filtering | failed | Both valid choices are rejected as unknown parameters. GAP-001. |
| Complete current-authority parity | stale | Three shader differences, missing cases, incomplete parameter matrix, and later upstream language changes. |
| Source-update parity enforcement | blocked | No current exact-source CI checks or complete parity gate. |
| Release readiness | blocked | Package defect, numerical failures, authority drift, and platform limits remain. |

[Installed evidence](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/bounded-developer-workflows.json). [Parity evidence](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/independent-comparisons.json). [Artifact evidence](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/served-verification.json).

### Earlier measured scope

Current tests and qualification limits are in [section 3](#3-parity-coverage).
The matrix below retains the earlier measured scope. A historical verified row is not a current-source or full-platform certification.

| Dimension | Status | Measured scope or limit |
|---|---|---|
| Source-level checks | verified | Initial collection failed because Click was missing. After isolated Click installation, 62 CLI, DSL, and output tests passed with 10 warnings. |
| Actual host rendering | unverified | No new complete native or browser workflow qualified by this report. |
| Minimum and current host versions | unverified | Declared requirements are not a tested version matrix. |
| Supported operating systems and backends | unverified | This pass does not establish Windows, Linux, and macOS coverage. |
| Installed package and first useful result | unverified | Complete isolated installation was not qualified for this source. |
| Parameters, external inputs, state, and chains | unverified | Full current-authority combinations remain unmeasured. |
| Invalid input and recovery | unverified | Unit checks do not establish every installed public entry point. |
| Upgrade, removal, and resource cleanup | unverified | Prior defects and missing workflows remain in the gap register. |
| Accessibility of provided controls | unverified | Keyboard, focus, labels, and diagnostics need host observations where applicable. |
| Release readiness | blocked | Full parity, installation, host, and artifact evidence remain incomplete. |

## 3. Parity coverage

### Worker audit, 2026-09-25

| Gate | Expected | Executed | Exact passes | Mismatches | Errors | Skips or missing |
|---|---|---|---|---|---|---|
| Existing default image sweep | 205 catalog effects | 167 | 167 | 0 | 0 | 38 skipped |
| Independent valid numerical programs | 3 | 3 | 1 | 2 | 0 | 0 |
| Current landscape filtering choices | 2 | 2 | 0 | 0 | 2 Python rejections | 0 |
| Current effect inventory | 210 IDs | not measured | not measured | not measured | not measured | 5 absent IDs |
| Full behavior matrix | not measured | not measured | not measured | not measured | not measured | incomplete inventory |

The default sweep uses zero byte tolerance at 8×8, seed 1, and time 0.25.
DSL tests retain their original mixture of exact and ±2-byte contracts. A tolerance pass does not establish exact equality.
Independent comparisons use 48×32, seed 17, and time 0.375. Alpha differs by 179, and feedback differs by one byte.
The one-byte result remains a strict failure. No threshold or golden changed.
[Full sweep results](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/parity-results.json). [Independent programs and channel counts](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/independent-comparisons.json).

Skipped image-gate IDs:

- `filter/convolutionFeedback`
- `filter/feedback`
- `filter/motionBlur`
- `filter/temporalAberration`
- `filter3d/flow3d`
- `filter3d/palette3d`
- `points/attractor`
- `points/buddhabrot`
- `points/dla`
- `points/flock`
- `points/flow`
- `points/hydraulic`
- `points/lenia`
- `points/life`
- `points/physarum`
- `points/physical`
- `render/loopBegin`
- `render/loopEnd`
- `render/pointsBillboardRender`
- `render/pointsEmit`
- `render/pointsRender`
- `render/render3d`
- `render/renderCubemap3d`
- `render/renderCubemapSurface`
- `render/renderLandscape3d`
- `render/renderLit3d`
- `synth/cellularAutomata`
- `synth/mnca`
- `synth/navierStokes`
- `synth/reactionDiffusion`
- `synth3d/cell3d`
- `synth3d/cellularAutomata3d`
- `synth3d/flythrough3d`
- `synth3d/fractal3d`
- `synth3d/heightmap3d`
- `synth3d/noise3d`
- `synth3d/reactionDiffusion3d`
- `synth3d/shape3d`

Missing current IDs: `render/meshLoader`, `render/meshRender`, `synth/roll`, `synth/scope`, `synth/spectrum`.
Separate DSL cases cover selected iterated and typed behavior. They do not resolve image-gate exclusions or establish the complete parameter matrix.
Current `filtering: isosurface` and `filtering: voxel` succeed in CPU and fail in Python.
Shader hashes differ for `classicNoisedeck/glitch:glitch`, `classicNoisedeck/noise:noise`, and `render/renderLandscape3d:landscape`.
[Current parameter manifests and shader hashes](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/authority-comparison-retry.json). [Filtering cases](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/landscape-valid-choices.json).

### Daily review, 2026-09-25

The daily review inspected worker audit `audit-20260925-090206` and post-worker commit `49d8e51ec4b71104dc03728c84c60cae3e2857d3`.
All 64 CLI, DSL, and output-runtime tests pass at current source `49d8e51ec4b71104dc03728c84c60cae3e2857d3`.
The sibling source lock test passes against `/workspace/repos/noisemaker-for-cpu`.
The review independently reproduced GAP-004: the built wheel contains 328 files and zero JSON files, omitting `bundle/metadata.json`.
The review checked GAP-005: four-component solid color produces alpha difference 179 against the CPU oracle, and feedback diverges by one byte.
Exact reviewed-source CI contains zero runs and zero checks.
Full installed-host and platform qualification remains incomplete.
GAP-001 remains open, and the suite leaves current full rendered parity unverified.
[Earlier raw evidence](/Users/alex/.codex/automations/noisemaker-port-completion-audit/review-20260925-053200/python-current-tests.json).

The current full case denominator remains incomplete. Missing parameters, hosts, external inputs, and stateful sequences remain qualification gaps. No skip or tolerated difference counts as exact parity.

### Earlier measurements

Full parity requires complete applicable coverage with no skips or missing cases.
Historical NEAR, CHAOS, and tolerated differences do not count as strict equality.
The existing numerical contracts remain separate from exact comparison. This report does not change tolerances or goldens.
Unknown values mean `not measured`, never zero.

| Gate | Expected cases | Executed | Strict passes | Failures | Skips | Status |
|---|---|---|---|---|---|---|
| Current full render suite | not measured | not measured | not measured | not measured | not measured | unverified |

Earlier served compatibility inventory declares 205 effect IDs. Declaration does not establish execution or parity.
IDs absent from the served declaration: `render/meshLoader`, `render/meshRender`, `synth/roll`, `synth/scope`, `synth/spectrum`.
Missing effects remain visible toward the full-parity goal. Contract exclusions do not become successful tests.

Current served declaration: 205 effect IDs. This inventory is not evidence of execution. The declaration column below reflects kit `0.1.7`.

### Effect inventory

| Effect ID | Declared in served kit | Current full parity |
|---|---|---|
| `classicNoisedeck/bitEffects` | yes | unverified |
| `classicNoisedeck/caustic` | yes | unverified |
| `classicNoisedeck/cellNoise` | yes | unverified |
| `classicNoisedeck/cellRefract` | yes | unverified |
| `classicNoisedeck/coalesce` | yes | unverified |
| `classicNoisedeck/colorLab` | yes | unverified |
| `classicNoisedeck/composite` | yes | unverified |
| `classicNoisedeck/effects` | yes | unverified |
| `classicNoisedeck/fractal` | yes | unverified |
| `classicNoisedeck/glitch` | yes | unverified |
| `classicNoisedeck/kaleido` | yes | unverified |
| `classicNoisedeck/lensDistortion` | yes | unverified |
| `classicNoisedeck/moodscape` | yes | unverified |
| `classicNoisedeck/noise` | yes | unverified |
| `classicNoisedeck/noise3d` | yes | unverified |
| `classicNoisedeck/refract` | yes | unverified |
| `classicNoisedeck/shapeMixer` | yes | unverified |
| `classicNoisedeck/shapes` | yes | unverified |
| `classicNoisedeck/shapes3d` | yes | unverified |
| `classicNoisedeck/splat` | yes | unverified |
| `filter/adjust` | yes | unverified |
| `filter/bloom` | yes | unverified |
| `filter/blur` | yes | unverified |
| `filter/bulge` | yes | unverified |
| `filter/celShading` | yes | unverified |
| `filter/channel` | yes | unverified |
| `filter/chroma` | yes | unverified |
| `filter/chromaticAberration` | yes | unverified |
| `filter/chrome` | yes | unverified |
| `filter/clouds` | yes | unverified |
| `filter/colorReplace` | yes | unverified |
| `filter/convolutionFeedback` | yes | unverified |
| `filter/corrupt` | yes | unverified |
| `filter/craquelure` | yes | unverified |
| `filter/crt` | yes | unverified |
| `filter/degauss` | yes | unverified |
| `filter/deriv` | yes | unverified |
| `filter/directionalBlur` | yes | unverified |
| `filter/dither` | yes | unverified |
| `filter/edge` | yes | unverified |
| `filter/emboss` | yes | unverified |
| `filter/extrude` | yes | unverified |
| `filter/feedback` | yes | unverified |
| `filter/fibers` | yes | unverified |
| `filter/flipMirror` | yes | unverified |
| `filter/fxaa` | yes | unverified |
| `filter/glowingEdge` | yes | unverified |
| `filter/glyphMap` | yes | unverified |
| `filter/grade` | yes | unverified |
| `filter/grain` | yes | unverified |
| `filter/grime` | yes | unverified |
| `filter/halftone` | yes | unverified |
| `filter/hatch` | yes | unverified |
| `filter/highPass` | yes | unverified |
| `filter/historicPalette` | yes | unverified |
| `filter/invert` | yes | unverified |
| `filter/lens` | yes | unverified |
| `filter/lensFlare` | yes | unverified |
| `filter/lensWarp` | yes | unverified |
| `filter/lightLeak` | yes | unverified |
| `filter/lighting` | yes | unverified |
| `filter/lowPoly` | yes | unverified |
| `filter/median` | yes | unverified |
| `filter/morphology` | yes | unverified |
| `filter/mosaicTiles` | yes | unverified |
| `filter/motionBlur` | yes | unverified |
| `filter/normalMap` | yes | unverified |
| `filter/normalize` | yes | unverified |
| `filter/octaveWarp` | yes | unverified |
| `filter/oilPaint` | yes | unverified |
| `filter/osd` | yes | unverified |
| `filter/outline` | yes | unverified |
| `filter/palette` | yes | unverified |
| `filter/parallax` | yes | unverified |
| `filter/patchwork` | yes | unverified |
| `filter/photocopy` | yes | unverified |
| `filter/pinch` | yes | unverified |
| `filter/pixelSort` | yes | unverified |
| `filter/pixels` | yes | unverified |
| `filter/plasticWrap` | yes | unverified |
| `filter/polar` | yes | unverified |
| `filter/pondRipples` | yes | unverified |
| `filter/posterize` | yes | unverified |
| `filter/prismaticAberration` | yes | unverified |
| `filter/reindex` | yes | unverified |
| `filter/relief` | yes | unverified |
| `filter/repeat` | yes | unverified |
| `filter/reverb` | yes | unverified |
| `filter/ridge` | yes | unverified |
| `filter/rotate` | yes | unverified |
| `filter/scale` | yes | unverified |
| `filter/scanlineError` | yes | unverified |
| `filter/scatter` | yes | unverified |
| `filter/scratches` | yes | unverified |
| `filter/scroll` | yes | unverified |
| `filter/seamless` | yes | unverified |
| `filter/sharpen` | yes | unverified |
| `filter/simpleAberration` | yes | unverified |
| `filter/sine` | yes | unverified |
| `filter/skew` | yes | unverified |
| `filter/smooth` | yes | unverified |
| `filter/smoothstep` | yes | unverified |
| `filter/snow` | yes | unverified |
| `filter/sobel` | yes | unverified |
| `filter/spatter` | yes | unverified |
| `filter/spinBlur` | yes | unverified |
| `filter/spiral` | yes | unverified |
| `filter/spookyTicker` | yes | unverified |
| `filter/stamp` | yes | unverified |
| `filter/step` | yes | unverified |
| `filter/stipple` | yes | unverified |
| `filter/strayHair` | yes | unverified |
| `filter/strokes` | yes | unverified |
| `filter/temporalAberration` | yes | unverified |
| `filter/tetraColorArray` | yes | unverified |
| `filter/tetraCosine` | yes | unverified |
| `filter/text` | yes | unverified |
| `filter/texture` | yes | unverified |
| `filter/threshold` | yes | unverified |
| `filter/tile` | yes | unverified |
| `filter/tint` | yes | unverified |
| `filter/translate` | yes | unverified |
| `filter/tunnel` | yes | unverified |
| `filter/unsharpMask` | yes | unverified |
| `filter/vaseline` | yes | unverified |
| `filter/vignette` | yes | unverified |
| `filter/warp` | yes | unverified |
| `filter/watercolor` | yes | unverified |
| `filter/waves` | yes | unverified |
| `filter/wind` | yes | unverified |
| `filter/wobble` | yes | unverified |
| `filter/wormhole` | yes | unverified |
| `filter/zoomBlur` | yes | unverified |
| `filter3d/flow3d` | yes | unverified |
| `filter3d/palette3d` | yes | unverified |
| `mixer/alphaMask` | yes | unverified |
| `mixer/applyMode` | yes | unverified |
| `mixer/blendMode` | yes | unverified |
| `mixer/cellSplit` | yes | unverified |
| `mixer/centerMask` | yes | unverified |
| `mixer/channelCombine` | yes | unverified |
| `mixer/distortion` | yes | unverified |
| `mixer/focusBlur` | yes | unverified |
| `mixer/mashup` | yes | unverified |
| `mixer/patternMix` | yes | unverified |
| `mixer/shadow` | yes | unverified |
| `mixer/shapeMask` | yes | unverified |
| `mixer/split` | yes | unverified |
| `mixer/thresholdMix` | yes | unverified |
| `mixer/uvRemap` | yes | unverified |
| `points/attractor` | yes | unverified |
| `points/buddhabrot` | yes | unverified |
| `points/dla` | yes | unverified |
| `points/flock` | yes | unverified |
| `points/flow` | yes | unverified |
| `points/heightGrid` | yes | unverified |
| `points/hydraulic` | yes | unverified |
| `points/lenia` | yes | unverified |
| `points/life` | yes | unverified |
| `points/physarum` | yes | unverified |
| `points/physical` | yes | unverified |
| `render/loopBegin` | yes | unverified |
| `render/loopEnd` | yes | unverified |
| `render/meshLoader` | no | unverified |
| `render/meshRender` | no | unverified |
| `render/pointsBillboardRender` | yes | unverified |
| `render/pointsEmit` | yes | unverified |
| `render/pointsRender` | yes | unverified |
| `render/render3d` | yes | unverified |
| `render/renderCubemap3d` | yes | unverified |
| `render/renderCubemapSurface` | yes | unverified |
| `render/renderLandscape3d` | yes | unverified |
| `render/renderLit3d` | yes | unverified |
| `synth/bitwise` | yes | unverified |
| `synth/cell` | yes | unverified |
| `synth/cellularAutomata` | yes | unverified |
| `synth/curl` | yes | unverified |
| `synth/gabor` | yes | unverified |
| `synth/gradient` | yes | unverified |
| `synth/julia` | yes | unverified |
| `synth/mandala` | yes | unverified |
| `synth/mandelbrot` | yes | unverified |
| `synth/media` | yes | unverified |
| `synth/mnca` | yes | unverified |
| `synth/modPattern` | yes | unverified |
| `synth/navierStokes` | yes | unverified |
| `synth/newton` | yes | unverified |
| `synth/noise` | yes | unverified |
| `synth/osc2d` | yes | unverified |
| `synth/pattern` | yes | unverified |
| `synth/perlin` | yes | unverified |
| `synth/polygon` | yes | unverified |
| `synth/reactionDiffusion` | yes | unverified |
| `synth/remap` | yes | unverified |
| `synth/roll` | no | unverified |
| `synth/sacredGeometry` | yes | unverified |
| `synth/scope` | no | unverified |
| `synth/shape` | yes | unverified |
| `synth/solid` | yes | unverified |
| `synth/spectrum` | no | unverified |
| `synth/subdivide` | yes | unverified |
| `synth/testPattern` | yes | unverified |
| `synth3d/cell3d` | yes | unverified |
| `synth3d/cellularAutomata3d` | yes | unverified |
| `synth3d/flythrough3d` | yes | unverified |
| `synth3d/fractal3d` | yes | unverified |
| `synth3d/heightmap3d` | yes | unverified |
| `synth3d/noise3d` | yes | unverified |
| `synth3d/reactionDiffusion3d` | yes | unverified |
| `synth3d/shape3d` | yes | unverified |

## 4. Evidence

### Worker audit, 2026-09-25

The environment is Python 3.14.5 on macOS arm64. NumPy supplies the actual CPU renderer.
[Runtime versions](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/runtime.json) records Python, NumPy, Node, and operating-system versions.

The unchanged image suite returns exit 0: 167/167 exact comparisons, zero mismatches, zero runtime errors, and zero oracle errors.
It skips 38 iterated or typed effects. These exclusions remain qualification gaps in this gate.
The README's 169/36 counts do not match this source's 167/38 inventory.
The suite uses 8×8 images, seed 1, time 0.25, and default parameters. Its numerical threshold is zero byte difference.
A wrapper redirects temporary PNG paths and captures local result variables. It does not change comparisons or exclusions.
[Literal command and source identities](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/parity-command.json). [Every executed and skipped ID](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/parity-results.json).

Independent public DSL probes use 48×32 images, seed 17, and time 0.375.
The noise/invert chain matches exactly across 6,144 channels.
Four-component solid color produces alpha 76 instead of CPU alpha 255 across 1,536 pixels. Maximum difference: 179.
A three-iteration feedback chain differs by one byte in five of 6,144 channels. It fails strict equality.
RGB and explicit-alpha controls match. These controls isolate the solid discrepancy to four-component color interpretation.
Both valid landscape filtering choices succeed in CPU and fail in Python with an unknown-parameter diagnostic.
[Nondefault comparisons](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/independent-comparisons.json). [Alpha controls](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/alpha-controls.json). [Valid landscape choices](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/landscape-valid-choices.json).

Current immutable shader comparison finds 291 matching program hashes and three differences among 294 compared programs.
Differences: `classicNoisedeck/glitch:glitch`, `classicNoisedeck/noise:noise`, and `render/renderLandscape3d:landscape`.
The landscape parameter manifest adds `filtering`. Palette metadata differences reflect the build-time insertion of enum choices.
These differences do not establish equivalent behavior. The upstream language implementation also changed after the CPU pin.
[Shader and parameter inventories](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/authority-comparison-retry.json). [Upstream source difference](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/upstream-diff.json).

The complete test run collected 274 cases: 267 passed, two failed, and five skipped because Python HTTPS certificate validation failed.
The 74 CPU parity tests passed: 50 exact-byte cases, 22 tolerance cases, one float32 equality case, and one source-lock check.
A targeted immutable-cache retry passed all 15 CDN and affected transpiler tests. All 274 distinct cases passed across these runs.
The initial run returned exit 1. The targeted retry returned exit 0. This is not a single clean full-suite result.
[Full command](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/pytest-command.json). [Raw output](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/pytest.log). [Retry command and output](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/network-retry.json).
[Per-case parity contracts](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/dsl-parity-contracts.json).
Verified HTTPS downloads through curl supplied immutable `1.0.180` bytes to the unchanged parser. All 13 CDN tests then passed.
The earlier malformed landscape probe used `linear`. Both renderers rejected it. It does not establish a supported-case defect.
[Initial authority probe](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/authority-comparison.json). [Pinned CDN retry](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/cdn-cached-tests.json).

The editable source installation produces a 32×24 curl image, a changed 48×32 image, filtered input, and three H.264 frames.
The public library entry point also produces a 32×24 PNG. PNG decoding and ffprobe check the outputs.
Invalid effect input returns exit 2. Corrected input returns exit 0.
SIGINT returns `Aborted!` and preserves the existing output file. Invalid input also preserves that file.
The literal README 512×512 example exceeded 180 seconds under concurrent test load. This is a bounded observation, not a performance benchmark.
The audit removed both private installation targets. Upgrade behavior, Python 3.11, other operating systems, and sustained resource use remain unverified.
[Installed commands](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/bounded-developer-workflows.json). [Output measurements](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/output-verification.json). [Animation](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/animation-verification.json).
[Cancellation](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/cancellation.json). [README timeout](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/readme-512-timeout.json). [Private removal](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/private-removal.json).

The served kit produces a 48×32 solid image. Invalid DSL fails, and corrected noise/invert DSL produces another image.
The failed wheel remains a distinct distribution defect despite successful editable and served-kit workflows.
Headless rendering has no editor controls. The audit checked CLI diagnostics and cancellation through public entry points.
[Served entry point](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/served-workflows.json). [Wheel build](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/build-command.json). [Wheel inventory](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/wheel-inventory.json).

Exact reviewed-source CI contains zero runs and zero checks. No existing workflow enforces source-update parity.
The served source's export dispatch `35963990201` passed. Downstream release `35963999103` passed 83 checks without skips and identifies that served source.
Its checks include an actual staged-kit PNG render.
Release packaging checks do not establish full port parity or current wheel correctness.
[Exact-source runs](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/source-ci.json). [Exact-source checks](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/source-checks.json). [Release log](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/kit-release.log).

Official references, accessed 2026-09-25: [Python packaging guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/) and [Python version status](https://devguide.python.org/versions/).
The packaging guide distinguishes source archives from installable wheels. This audit checked both formats and retained the declared Python 3.11 minimum.

Review CI boundary: No workflow run exists at the inspected source SHA. A passing export dispatch does not qualify rendered parity. Current complete-render enforcement remains an open verification requirement. [Exact-source responses and workflows](/Users/alex/.codex/automations/noisemaker-port-completion-audit/review-20260925-053200/noisemaker-for-python-remote-evidence.json).

[Bounded test evidence](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-20260924-remaining-gap-documents/python-tests-retry.json). [Exact-source Actions](https://github.com/noisefactorllc/noisemaker-for-python/actions?query=head_sha%3A70c03da6944be1319ccc249fd9646dd9df05e86c).
[This run evidence](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-20260924-remaining-gap-documents) retains commands, exit codes, source identities, and distribution metadata.
Official ecosystem reference: [Current Python Packaging User Guide, accessed 2026-09-24](https://packaging.python.org/en/latest/tutorials/packaging-projects/).
Source CI, export dispatch, artifact delivery, and rendered parity are separate evidence dimensions.
A successful dispatch or unit-test summary does not establish a full rendered gate.

## 5. Open compatibility limits

Current order: correct [GAP-004](COMPLETION_GAPS.md#gap-004-built-distributions-omit-required-bundle-metadata), then [GAP-005](COMPLETION_GAPS.md#gap-005-nondefault-output-differs-from-the-cpu-oracle).
Next, reconcile GAP-001 authority differences and complete GAP-002 host qualification and GAP-003 release enforcement.
Require wheel-only output, exact recorded comparisons, both valid landscape modes, and complete denominators.

Next bounded check: Install the built wheel in a fresh Python 3.11 environment and a current supported Python environment. Run the documented CLI to produce a PNG, exercise invalid DSL and recovery, then compare every declared effect against an immutable CPU oracle. Require wheel-only imports and retain skips and missing effects toward the 210-ID inventory.
See the stable entries in [completion gaps](COMPLETION_GAPS.md).

See [GAP-001 and the complete gap register](COMPLETION_GAPS.md#4-known-gaps) for evidence, dependencies, and acceptance criteria.

1. Reconcile the current authority and complete case inventory, including parameters, inputs, stateful frames, and host versions.
2. Run the existing actual-renderer suite without skip options. Record every missing, failed, refused, or timed-out case.
3. Verify installation, useful output, errors, recovery, upgrades, and removal with the actual distribution.
4. Inspect exact-source CI and retain artifact hashes. Keep unresolved qualification failed or unverified.

All eligible ports have equal priority. Full parity and zero skipped cases remain the goal.
Implementation corrections remain with the separate job. This report does not advance the parity checkpoint.

## 6. History

2026-09-25 daily review at `49d8e51ec4b71104dc03728c84c60cae3e2857d3`: reviewed worker audit `audit-20260925-090206` (published in `4ff7b03247b59cead0b63a7ee3a7b5697f7bf58e`).
Verified post-audit commit `49d8e51ec4b71104dc03728c84c60cae3e2857d3` in `tests/test_parity.py`.
Independently reproduced GAP-004 missing metadata in built wheel. Checked GAP-005 nondefault numerical parity differences.
Five open gaps remain. Zero closures. Full parity and release readiness remain unqualified.

2026-09-25 worker at `912e6a9aac32c668a5242b8d52aa4415ca3a848e`: 167 exact default comparisons, 38 image-gate exclusions, two independent numerical failures, and two landscape rejections.
Served kit hashes and reproduction pass. Candidate wheel first render fails. No full-parity or release approval follows.

2026-09-25 daily review at `93b8b141d21a7c853a89131166147c8337109144`: source freshness and bounded evidence reviewed. Open qualification limits retained. [Retained review evidence](/Users/alex/.codex/automations/noisemaker-port-completion-audit/review-20260925-053200/python-current-tests.json). No new closure claimed.

| Date | Source | Result | Change |
|---|---|---|---|
| 2026-09-25 | `49d8e51ec4b71104dc03728c84c60cae3e2857d3` | Full qualification unverified | Reviewed audit-20260925-090206 and post-worker parity test update. Reproduced GAP-004. Zero closures. |
| 2026-09-25 | `912e6a9aac32c668a5242b8d52aa4415ca3a848e` | Full qualification unverified | 167 exact default passes, 38 skips, 2 independent numerical failures, 2 landscape rejections. Wheel fails. |
| 2026-09-24 | `70c03da6944be1319ccc249fd9646dd9df05e86c` | Full qualification unverified | Created the requested maintained compatibility report. Preserved historical evidence and open gaps. |

Run: `20260924-remaining-gap-documents`. Later audits and reviews update this report with source-bound results.
