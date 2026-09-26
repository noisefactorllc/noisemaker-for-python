# noisemaker-for-python: completion gaps

Current compatibility matrix: [compatibility report](COMPATIBILITY.md).

## 1. Scope and source revisions

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

Date: 2026-09-24. Reviewed SHA: [`70c03da6944be1319ccc249fd9646dd9df05e86c`](https://github.com/noisefactorllc/noisemaker-for-python/commit/70c03da6944be1319ccc249fd9646dd9df05e86c).
Local HEAD matched remote main before checks. The operator requested registers for all remaining eligible ports in this run.
This initial register contains bounded evidence. It is not a completed port audit or release approval.
No implementation or parity checkpoint changed. Full audits remain in the rotation.

Python CPU shader rendering with NumPy and Click. Python 3.11 is the declared floor. This is separate from classic Composer. [Contract](https://github.com/noisefactorllc/noisemaker-for-python/blob/70c03da6944be1319ccc249fd9646dd9df05e86c/README.md).

Bundle metadata records CDN version `1.0`. Shader hashes exist in the bundle lock. No CPU oracle commit was identified in this pass.
Current upstream at discovery: `c9ee8a049b2b63cd300da67c01ee40baf29dc288`.
Current CPU authority: `f2eb495d70abcb74e3632e7a652a4f83e4f3b11e`.
These authority heads are review targets, not qualification results. No goldens were regenerated.

Served kit `0.1.6` identifies `d42872842cd6aa14aa585103df35267a46156ec7`. [Metadata](https://kits.noisedeck.app/python/0/deployment-meta.json). Inventory and compatibility metadata were retrieved. Complete artifact bytes were not checked.

These document paths do not match the current publication workflow filters.
The containing commit identifies this register's publication revision. The shared run record retains commits, remote hashes, and downstream results.

## 2. Completion claims

| Claim ID | Claim source | Claimed scope | Finding | Evidence |
|---|---|---|---|---|
| CLAIM-006 | [Current README](https://github.com/noisefactorllc/noisemaker-for-python/blob/912e6a9aac32c668a5242b8d52aa4415ca3a848e/README.md) | Current runtime and pixel parity | partial | 167 exact default comparisons. Nondefault alpha and feedback fail. Landscape filtering is unsupported. |
| CLAIM-007 | [Current README](https://github.com/noisefactorllc/noisemaker-for-python/blob/912e6a9aac32c668a5242b8d52aa4415ca3a848e/README.md) | Human usability | partial | Small editable and served-kit workflows pass. The 512×512 first example exceeds the probe limit. |
| CLAIM-008 | [Package configuration](https://github.com/noisefactorllc/noisemaker-for-python/blob/912e6a9aac32c668a5242b8d52aa4415ca3a848e/pyproject.toml) | Ecosystem installation | contradicted | Built wheel and source archive omit required runtime metadata. |
| CLAIM-009 | [Served kit](https://kits.noisedeck.app/python/0.1.7/kit.json) | Release readiness | unverified | Served bytes reproduce. Package defects, parity failures, platform gaps, and absent gates block qualification. |
| CLAIM-010 | [Current README](https://github.com/noisefactorllc/noisemaker-for-python/blob/912e6a9aac32c668a5242b8d52aa4415ca3a848e/README.md) | 169 image comparisons and 36 exclusions | contradicted | Actual gate executes 167 comparisons and skips 38 cases. |
| CLAIM-011 | [Package configuration](pyproject.toml at this pass's candidate commit) and section 3, 2026-09-26 pass | Installed wheel and sdist workflow on Python 3.11.2 and 3.13.13 | verified | Bundle data and LICENSE now ship in both archives; install, render, filter, invalid-input recovery, cancellation, reinstall, and removal all pass. macOS/Windows/Python 3.14 remain untested and are recorded explicitly. |
| CLAIM-012 | Built artifacts at [`8f411a1c5501b5fd156b8945df3b2b6ba4545d04`](https://github.com/noisefactorllc/noisemaker-for-python/commit/8f411a1c5501b5fd156b8945df3b2b6ba4545d04) and section 3, 2026-09-26 release-qualification pass | Artifact reproduction, installation, upgrade, removal, notices, and dependencies | partial | Wheel and sdist built in an isolated copy byte-match their inventories; install, examples, upgrade, and removal pass on 3.11.2 and 3.13.13 with MIT and dependency license notices verified. Exact-source CI still contains zero runs, and no repository workflow executes tests, so complete parity enforcement through CI remains unmet. |

### Earlier claims and observations

| Claim ID | Claim source | Claimed scope | Finding | Evidence |
|---|---|---|---|---|
| CLAIM-001 | [Historical source](https://github.com/noisefactorllc/noisemaker-for-python/blob/70c03da6944be1319ccc249fd9646dd9df05e86c/README.md) | 205 catalog effects. The image harness compares 169 effects with zero byte tolerance and reports 36 iterated or typed exclusions. | partial | Initial collection failed because Click was missing. After isolated Click installation, 62 CLI, DSL, and output tests passed with 10 warnings. |
| CLAIM-002 | [README](https://github.com/noisefactorllc/noisemaker-for-python/blob/70c03da6944be1319ccc249fd9646dd9df05e86c/README.md) | Human usability: installation, output, errors, and recovery | unverified | Complete installed workflows were not observed. GAP-002. |
| CLAIM-003 | [Ecosystem reference](https://packaging.python.org/en/latest/tutorials/packaging-projects/) | Ecosystem fit and version support | partial | Source entry points were examined. Installed integration and version qualification remain open. |
| CLAIM-004 | [README](https://github.com/noisefactorllc/noisemaker-for-python/blob/70c03da6944be1319ccc249fd9646dd9df05e86c/README.md) | Release readiness | unverified | Metadata and CI do not replace installation of the actual artifact. GAP-003. |
| CLAIM-005 | [Exact-source Actions](https://github.com/noisefactorllc/noisemaker-for-python/actions?query=head_sha%3A70c03da6944be1319ccc249fd9646dd9df05e86c) | Workflow status only | unverified | No Actions runs were returned at this source SHA. |

## 3. Methods and evidence

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

### Installed developer workflow pass, 2026-09-26 (GAP-002, GAP-004)

Environment: Linux x86_64 container, 6 cores, `uv` 0.11.6, setuptools build isolation. Isolated consumers: fresh `uv` virtualenvs in a scratch directory (`/state/cache/scratch/gap002`), removed after evidence capture. No global or user-project installation was made. Candidate artifacts were built with `uv build` from the working tree after the `pyproject.toml` package-data correction:

- wheel `noisemaker_for_python-0.0.0-py3-none-any.whl`, SHA-256 `3396ee591226494e8e1869551c2885840df3c50af62e91fc31388d729be12262` (330 files: 2 JSON, 294 kernel Python files, LICENSE, METADATA)
- sdist `noisemaker_for_python-0.0.0.tar.gz`, SHA-256 `24d2cb4d3c99c1541c56530535c9211e41cfdff407aec56df62a95ca0265aaae` (364 files, same bundle)

A rebuild produces different archive bytes (zip/tar timestamps), so these hashes identify the tested artifacts, not a reproducibility claim. Installed `bundle/` trees were byte-identical to `src/noisemaker_cpu/bundle/` (all 296 files SHA-256 matched).

Consumers: Python 3.11.2 (declared floor) with numpy 2.4.6 and click 8.5.0; Python 3.13.13 with numpy 2.5.3. Python 3.14 was unavailable (managed downloads disabled on this host); macOS and Windows hosts were unavailable. Steps and results (SHA-256 of PNGs):

1. Wheel install into the empty 3.11 consumer (dependencies resolved from PyPI). First CLI render `generate synth/curl --width 32 --height 24 --seed 1`: 7.3s wall including interpreter startup, `curl.png` `4560aaf84bd9b38e69f84b31bb37721d3a24af1d8433705b6c52422e2e1c37d7`.
2. Library render via `render_effect('synth/curl', {'scale': 16}, width=32, height=24, seed=1)` + `encode_png`: 7.1s, bytes identical to the CLI output (`4560aaf8…`). This establishes CLI/library agreement at these parameters.
3. Filter integration: `apply filter/chrome` on the rendered PNG: exit 0, `chrome.png` `57cd44c25bf6706e411b95188e7a0a13aefa931b6b97b2352b693b2490fa76da` (identical on both replays).
4. Invalid effect id `synth/definitely_not_an_effect`: exit 2 with a Click diagnostic naming the id and valid alternatives (`Error: Invalid value for EFFECT: Unknown effect: …`); no file written.
5. Invalid DSL (`noise(??bad`, and programs with a missing `search` directive): exit 1 with a `DslError` traceback carrying the source location and message (`<dsl>:2:7: Unexpected character "?"`, `<dsl>:1:1: Missing required search directive`, and a parameter suggestion listing accepted names); no file written. Diagnostics are informative but surface as Python tracebacks rather than a formatted CLI error; tests only require a non-zero exit. Corrected DSL (`search synth\nnoise(scaleX: 4).write(o0)\nrender(o0)`): exit 0, `dslok.png` `12cb47b4cc0a6a2a84c24c49a4c90c8bd8ed13b41e3d35f613209fadd94de5ee`, identical on 3.11 and 3.13.
6. Cancellation: `SIGINT` during a 128×128 render printed `Aborted!` and left the pre-existing output file byte-identical (`curl-preserve.png` unchanged, `4560aaf8…`).
7. Reinstall (the only testable upgrade path at version 0.0.0): sdist reinstalled over the wheel with dependencies held; entry point worked after (`noisemaker-py --version` → 0.0.0; 16×16 render).
8. Removal: `uv pip uninstall` removed the entry point, the `noisemaker_cpu` package, and its dist-info; `import noisemaker_cpu` then failed with `ModuleNotFoundError`. Both consumers were then deleted.
9. Timing bound: `generate synth/curl --width 512 --height 512 --seed 1` from the installed wheel completed in 34m55s wall (34m45s user) on the otherwise mostly idle 6-core container, producing a 512×512 PNG (`0dcb12ea78a581ebc68e0b293185b84b01b74c710abc63a1d356f77f3caa890e`). The earlier ">180 s" observation is confirmed and now bounded at ~35 minutes: the README 512×512 example is far from a practical first-output time at this bundle revision.

Version matrix: every seed-1 16×16 curl render produced `ff580d7a5b28f97e2ac3519700afcc9711d841ceffc20ecbadcf1f917f17544a` on Python 3.11.2 and 3.13.13, from wheel and sdist installs, across fresh consumers, reinstall cycles, `PYTHONHASHSEED` 0/1/42, and `OPENBLAS_NUM_THREADS`/`OMP_NUM_THREADS` 1/2/4.

Unexplained outlier: two of 52 recorded seed-1 16×16 curl renders produced a different PNG (`84fa319f11ad9113f7bc2b1c76a14b62763893bead1b877bb1adf5c16c44e592`, a 79-byte file decodable as a 16×16 image with all-nonzero data) instead of `ff580d7a…` — once at 16:43 UTC and once in a later replay of the same apply→invalid→recover shell chain. 42 subsequent attempts, including exact replays of that chain, fresh consumers, both formats, thread-count and hash-seed variations, and runs under concurrent load, all returned `ff580d7a…`. Root cause was not identified; no code change is claimed from this observation, and it is recorded here for parity follow-up (adjacent to GAP-005's byte-level feedback difference).

Full test suite at this exact candidate source (including the `pyproject.toml` change): 209 passed, 75 skipped in 10.2s (Python 3.13.13, numpy 2.5.3), matching the recorded baseline for this tree.

### Release qualification pass, 2026-09-26 (GAP-003)

Environment: Linux x86_64 container, 6 cores, `uv` 0.11.6, setuptools build isolation. The candidate source is the merged HEAD `8f411a1c5501b5fd156b8945df3b2b6ba4545d04`, which folds in sync commit `1d1ac92` (bundle refreshed to CDN `1.0.183`, three kernel programs and `renderer.py` changed, node-free parity receipt added). Artifacts were built with `uv build` from an isolated copy (`git archive` of that SHA extracted into a scratch directory; no build residue in the repository). Archive bytes are not reproducible (zip/tar timestamps); these SHA-256 hashes identify the exact tested artifacts:

- wheel `noisemaker_for_python-0.0.0-py3-none-any.whl`, SHA-256 `db88eb5d31ce0ffc696759a0583cdbd9e73b64793ce7a24654f499a65e8b686b` (330 entries: 324 `noisemaker_cpu/` files — 2 bundle JSON, 294 kernel Python files — plus dist-info, METADATA, vendored LICENSE)
- sdist `noisemaker_for_python-0.0.0.tar.gz`, SHA-256 `36747413b0fe7b031430536a8639678c8267f5516cdce1e96ec9556552604eee` (355 files; same complete bundle)

Artifact byte-inventory verification: every wheel payload file under `noisemaker_cpu/` and the vendored LICENSE byte-match the isolated source copy (SHA-256 per file, zero differences), and the wheel contains no file absent from the source inventory. Every sdist file that corresponds to a source-tree path byte-matches, with only `PKG-INFO` and `setup.cfg` added by the backend. Setuptools' default sdist rules omit `.github/`, `docs/`, `export-kit/`, `scripts/parity.py`, `tests/data/`, and `transpiler/` from the sdist; the runtime bundle is complete in both formats, and the sdist remains build-installable.

Consumers: fresh `uv` virtualenvs in a scratch directory — Python 3.11.2 (declared floor) installing the wheel (numpy 2.4.6, click 8.5.0) and Python 3.13.13 installing the sdist (numpy 2.5.3, click 8.5.0), dependencies resolved from PyPI. Installed `bundle/` trees were byte-identical to `src/noisemaker_cpu/bundle/` (all 296 files) in both consumers. Steps and results (SHA-256 of PNGs):

1. First CLI render `generate synth/curl --width 32 --height 24 --seed 1`: `curl.png` `4560aaf84bd9b38e69f84b31bb37721d3a24af1d8433705b6c52422e2e1c37d7` in both consumers — identical to the 2026-09-26 GAP-002 evidence, so the merged bundle refresh did not change these renders.
2. Library render via `render_effect('synth/curl', {'scale': 16}, width=32, height=24, seed=1)` + `encode_png`: bytes identical to the CLI output in both consumers.
3. `apply filter/chrome` on the rendered PNG: exit 0, `chrome.png` `57cd44c25bf6706e411b95188e7a0a13aefa931b6b97b2352b693b2490fa76da`.
4. Invalid effect id: exit 2 with a Click diagnostic naming the id; no file written.
5. Invalid DSL through the documented `noisemaker-py run` STDIN entry point (missing `search` directive; and `noise(??bad`): exit 1 with `DslError` tracebacks carrying source locations (`<dsl>:1:1: Missing required search directive`, `<dsl>:2:7: Unexpected character "?"`); corrected program `search synth\nnoise(scaleX: 4).write(o0)\nrender(o0)` renders `ok.png` `12cb47b4cc0a6a2a84c24c49a4c90c8bd8ed13b41e3d35f613209fadd94de5ee`, identical on 3.11.2 and 3.13.13 and to the GAP-002 record.
6. Cancellation: `SIGINT` (via `timeout -s INT 2`) during a 128×128 render printed `Aborted!`; the pre-existing output file stayed byte-identical (`4560aaf8…`).
7. Upgrade (the only testable path at version 0.0.0): cross-format reinstall in both directions — sdist over wheel on 3.11.2, wheel over sdist on 3.13.13 — after which `noisemaker-py --version` reports 0.0.0 and a 16×16 seed-1 curl renders `ff580d7a5b28f97e2ac3519700afcc9711d841ceffc20ecbadcf1f917f17544a`, identical to the GAP-002 version matrix.
8. Removal: `uv pip uninstall` removed the entry point and package in both consumers; `import noisemaker_cpu` then failed with `ModuleNotFoundError`.
9. Notices and dependencies: the MIT LICENSE ships in both archives and in the installed `dist-info` (`License: MIT` + classifier in METADATA); installed dependency distributions carry their own license notices (NumPy Developers BSD notice, Pallets BSD notice). Dependency ranges in METADATA are `numpy>=1.26`, `click>=8`, with `pytest`/`ruff` (dev) and `json5` (build) correctly marked as extras.
10. Timing bound at this bundle revision: the literal README 512×512 seed-1 curl example from the installed wheel completed in 35m05s (2105s) on the 6-core container, producing a 512×512 PNG (`0dcb12ea78a581ebc68e0b293185b84b01b74c710abc63a1d356f77f3caa890e`) — byte-identical to the previous bundle's output and consistent with the 34m55s bound recorded at that bundle.

Full test suite at this exact merged source: 214 passed, 76 skipped in 59.5s (Python 3.13.13, numpy 2.5.3). The node-free parity receipt introduced by the merged sync (tests/data/parity-receipt-8eeb7b5a.json + tests/test_parity_receipt.py) replays all eligible non-iterated image effects inside the normal suite and asserts byte-exact agreement with the recorded `8eeb7b5a` CPU-oracle hashes; it passed, and its regeneration check skipped for lack of a sibling oracle checkout (counted as a skip, not trusted green).

Exact-source CI: the GitHub API at this SHA returns 0 workflow runs and 0 check runs. The repository's only workflow is `export-kit.yml`, a dispatch-only trigger (push paths: `export-kit/**`, the workflow file, `LICENSE`, `src/noisemaker_cpu/**`) for the downstream scaffold kit release; no repository workflow executes pytest, the parity receipt, or wheel/sdist verification. Adding a test workflow was previously attempted and rejected as outside an implementation job's workflow authority, so complete parity enforcement through existing CI remains unmet (see GAP-003).

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

Environment: macOS 26.5, Darwin arm64.
[Source SHA-256 records](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-20260924-remaining-gap-documents/noisemaker-for-python-source-hashes.json) bind these checks to the reviewed revision.
[Raw command evidence](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-20260924-remaining-gap-documents/python-tests-retry.json). [Remote evidence](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-20260924-remaining-gap-documents/noisemaker-for-python-remote.json).

Executed command:

```sh
PYTHONPATH=src python3 -m pytest -q -p no:cacheprovider tests/test_cli.py tests/test_dsl.py tests/test_output_runtime.py
```

Initial collection failed because Click was missing. After isolated Click installation, 62 CLI, DSL, and output tests passed with 10 warnings. Final exit code: 0. The retry added an isolated Click directory to PYTHONPATH.
No image denominator or tolerance follows from a unit-test or generated-file result.
Official reference: [Current Python Packaging User Guide, accessed 2026-09-24](https://packaging.python.org/en/latest/tutorials/packaging-projects/).

| Outcome | Observed scope | Remaining work |
|---|---|---|
| Installation | Instructions and metadata inspected | Install the actual artifact privately. |
| First useful output | Selected checks only | Install a wheel into an isolated target. Render curl, apply a filter to PNG input, run invalid DSL, recover, and remove the installation. |
| Host integration | Not fully exercised | Check parameters, external inputs, state, resize, and cleanup. |
| Errors and recovery | Only the selected checks above | Fail through the installed entry point, correct input, and render again. |
| Distribution | Metadata inspection | Build wheel and source archive in an isolated copy. Verify installed kernels, CLI entry point, dependencies, licenses, upgrade behavior, and removal. |
| Accessibility | Not observed | Check keyboard, focus, labels, and diagnostics for provided interfaces. |

Headless libraries do not require an editor accessibility test. Their CLI diagnostics and failure handling still require checks.
Host presence does not prove host qualification. This pass made no global installation or user-project changes.

## 4. Known gaps

P1 means false completion or major correctness failure. P2 means coverage or integration uncertainty. P3 means documentation inconsistency.
These entries record missing qualification. They do not infer implementation defects from absent tests.

### GAP-001: current authority and parity qualification

- Worker verification: 2026-09-25. Current evidence: 167 exact default cases and 38 exclusions. Three shader programs differ from current authority. Both landscape filtering choices fail.
- Next check: Reconcile authority inputs and parameters. Run all cases with immutable source identities and retain missing coverage.
- Evidence: Current worker methods in section 3. No closure.

- Status: open. Priority: P2. Category: verification.
- Affected scope: pyproject.toml, src/noisemaker_cpu/bundle/, scripts/parity.py, tests/, README.md
- Expected behavior: Reproducible evidence binds each supported claim to the port and authority revisions.
- Observed behavior: README retains earlier 188-effect evidence beside the current 205-effect bundle. Earlier results do not establish current full-catalog behavior.
- Evidence: [Historical source](https://github.com/noisefactorllc/noisemaker-for-python/blob/70c03da6944be1319ccc249fd9646dd9df05e86c/README.md) and section 3.
- Next action: Run all 167 image comparisons and report all 38 exclusions. Add source identity to evidence before interpreting current parity.
- Dependencies: Resolve immutable authority inputs. Preserve historical goldens and provenance.
- Acceptance criteria: Report every applicable case, parameter choice, exclusion, error, and tolerance. Do not reduce the denominator to report success.
- Required checks: Existing compiler and rendered parity gates, with raw output and exact source hashes.
- Last verification: 2026-09-25. Full behavior qualification remains unverified.

### GAP-002: installed developer workflow qualification

- Worker verification: 2026-09-26. Current evidence: complete wheel and sdist installed workflows pass on Python 3.11.2 and 3.13.13 (generation, library render, PNG filter input, invalid-effect and invalid-DSL diagnostics, recovery, SIGINT cancellation with file preservation, reinstall, and clean removal). The 512×512 example completed in 34m55s on the 6-core Linux container. One unexplained render-bytes outlier is recorded below.
- Next check: macOS and Windows hosts and Python 3.14 remain untested on this Linux-only harness. Attribute the recorded one-off render nondeterminism. Real version-to-version upgrade remains untestable while the package version is 0.0.0 (reinstall semantics verified instead).

- Status: closed. Priority: P2. Category: usability.
- Affected scope: Public API, examples, supported hosts, errors, recovery, and lifecycle.
- Expected behavior: Developers can install, produce useful output, integrate it, recover from errors, and remove the package.
- Observed behavior: Complete installed workflow exercised on the declared floor Python and current stable Python. Unavailable hosts and interpreter versions are explicit below.
- Evidence: [README](https://github.com/noisefactorllc/noisemaker-for-python/blob/70c03da6944be1319ccc249fd9646dd9df05e86c/README.md), [official reference](https://packaging.python.org/en/latest/tutorials/packaging-projects/), and section 3.
- Dependencies: Used isolated `uv` virtualenv consumers in a scratch directory; no global or user-project installation. Host: Linux x86_64 container, 6 cores; CPU renderer requires no GPU; MIT LICENSE ships in both archives; PNG inputs generated locally, so no licensing or external-input requirement blocked execution.
- Acceptance criteria: Retain artifact hashes, steps, meaningful output, error diagnostics, recovery results, and cleanup results.
- Required checks: Minimum (3.11.2) and current (3.13.13) supported versions tested. Cancellation and file preservation checked. Explicitly unavailable: macOS, Windows, Python 3.14, NumPy < 1.26 on these hosts.
- Last verification: 2026-09-26. Closure criteria retained above; see section 3 for the full step list and hashes.

### GAP-003: distribution and release qualification

- Worker verification: 2026-09-26. Current evidence: wheel and sdist built in an isolated copy at merged source `8f411a1c5501b5fd156b8945df3b2b6ba4545d04` byte-match their inventories (wheel: all 324 `noisemaker_cpu/` files plus LICENSE; sdist: all source-corresponding files). Wheel (3.11.2) and sdist (3.13.13) consumers pass installation, both render examples, filter integration, invalid-effect and invalid-DSL recovery, SIGINT cancellation, cross-format reinstall, and clean removal; MIT and dependency license notices verified; full render hashes unchanged from the 2026-09-26 GAP-002 evidence. Method and hashes in section 3.
- Next check: Add the exact-source CI gate that runs the suite — including the node-free parity receipt — and wheel/sdist artifact verification. The enforcement exists in-repo (tests/test_parity_receipt.py + the full suite), but no repository workflow executes tests at this source (exact-source CI: 0 runs, 0 checks; the sole workflow `export-kit.yml` is a dispatch to the downstream kit release), and this implementation job holds no workflow authority. macOS, Windows, and Python 3.14 also remain untested on this Linux-only harness, and real version-to-version upgrade remains untestable at version 0.0.0.
- Evidence: Current worker methods in section 3. No closure.

- Status: open. Priority: P2. Category: release.
- Affected scope: Actual artifact, dependencies, notices, version promises, and release evidence.
- Expected behavior: The delivered artifact supports its documented installation and first useful result.
- Observed behavior: Artifact reproduction, installation, upgrade, removal, notices, and dependencies are now verified at the merged source. Release qualification remains blocked on the missing exact-source test/parity CI gate.
- Evidence: [Distribution instructions](https://github.com/noisefactorllc/noisemaker-for-python/blob/70c03da6944be1319ccc249fd9646dd9df05e86c/README.md), section 1, and exact-source CI in section 2.
- Next action: An actor with workflow authority must add a repository workflow that runs pytest (with the parity receipt and counted skips) plus wheel/sdist build-and-install checks on every push to `main`. The artifact-level criteria above are otherwise complete.
- Dependencies: GAP-002 complete for the candidate. Source CI is distinguished from downstream publication: the export-kit dispatch and scaffold release checks publish the served kit and do not run this repository's tests.
- Acceptance criteria: Match artifact bytes to their inventory. Check notices and dependencies. Pass installation, examples, upgrade, and removal.
- Required checks: Inspect exact-source CI jobs and actual render legs. Count skips and errors rather than trusting green summaries.
- Last verification: 2026-09-26. This register does not approve a release.

### GAP-004: built distributions omit required bundle metadata

- Worker verification: 2026-09-26. Current evidence: correction implemented in `pyproject.toml` (`[tool.setuptools.package-data]` including `bundle/**/*.json` and kernel sources). Rebuilt wheel contains 330 files (2 JSON, 294 kernel Python files, LICENSE, METADATA); rebuilt sdist contains 364 files with the same bundle. Installed bundles are byte-identical (all 296 files SHA-256 matched) to the source tree. Full workflow evidence in section 3.
- Next check: none for this gap; release qualification continues under GAP-003.

- Status: closed. Priority: P1. Category: release.
- Affected scope: `pyproject.toml`, wheel contents, source archive contents, and installed public entry points.
- Expected behavior: Installed distributions include every runtime input and produce the documented first image.
- Observed behavior: Both archives now include the bundle metadata, lock, kernels, and license; installed CLI and library calls render verified PNGs with no source-directory access, on Python 3.11.2 and 3.13.13.
- Evidence: [Wheel failure](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/wheel-first-output.json) (historical, 2026-09-25) and section 3 (2026-09-26 rebuild and install evidence).
- Next action: None. GAP-003 owns downstream release qualification of the corrected artifact.
- Dependencies: The correction was implemented and verified in this pass. Historical audit evidence is retained above.
- Acceptance criteria: CLI and library calls produce verified PNGs without source-directory access. Required metadata and notices exist in both archives.
- Required checks: Wheel and source-archive installation on minimum (3.11.2) and current (3.13.13) Python. Generation, filtering, invalid-input recovery, and removal executed against both formats.
- Last verification: 2026-09-26. The 2026-09-25 failure no longer reproduces: the wheel's first render succeeds.

### GAP-005: nondefault output differs from the CPU oracle

- Worker verification: 2026-09-26. Current evidence: three root causes fixed and verified against a fresh `noisemaker-for-cpu` checkout at the pinned oracle revision `bfbe54764eee87c8f67d2b281d5f304faad04a5b` (node 26.5.1, Python 3.11.2, NumPy 2.5.3, Linux x86_64). (1) `Runtime.binary` now truncates component-wise results to the declared type width, matching `csl/runtime.js`: a vec4 color uniform multiplied into a vec3 expression no longer leaks its fourth channel, so four-component solid colors match exactly. (2) The transpiler fuses uniform `vecN(scalar, ...)` splat operands in component-wise binary expressions into the raw unrounded scalar, matching the JS glsl-transpiler's per-component folding (the prior `rt.construct` pre-rounding double-rounded in `hsv2rgb`'s `rgb + vec3(m, m, m)`). (3) The transpiler fuses distinct-scalar `vecN(...)` constructor operands the same way via an `rt.array` of raw float64 elements, matching the JS canonical kernels' fused pooled-array literals (the prior pre-rounding diverged in `synth/noise`'s `st -= vec2(resolution.x / resolution.y * 0.5, 0.5)` by one f16 step at a non-square size/seed combination). The vendored bundle was regenerated from CDN `1.0.183` with unchanged metadata and lock. Exact 8-bit matches (max byte difference 0) for `synth/solid` with `#4080c080`, `#11223344`, `#abcdef01`, `#00000080`, `#ffffff01`, `#ff00ff7f`, `#00112299`, `#33445566` at 16×16, 24×13, 33×17, and 7×64; exact matches for the recorded feedback program (`noise(seed: 1, ridges: true).feedback(iterationCount: 1)`) and a stateful feedback matrix `noise(ridges: true).feedback(mix: 40, iterationCount: 1–5)` at sizes 8×8, 16×16, 24×18, 32×16, seeds 1–3, times 0.0–0.75, verified at both the 8-bit and rgba16f surface level, with committed oracle control pairs proving harness-seed sensitivity and feedback statefulness; the noise oracle surface remains bit-exact across the recorded matrix.
- Status: closed. Priority: P1. Category: implementation.
- Affected scope: Four-component DSL colors and repeated feedback at nondefault size, seed, and time.
- Expected behavior: Supported CPU parity cases match the identified oracle under the declared numerical contract.
- Observed behavior: Solid alpha differs by 179 in every pixel. Feedback differs by one byte in five channels.
- Historical behavior: before this fix the port reproduced both differences (alpha 179 recorded by the 2026-09-25 audit; 127 at `#4080c080`; feedback 1-byte/5-channel). Both no longer reproduce.
- Evidence: committed, node-free, byte-level acceptance fixtures `tests/data/gap005-oracle/` with `tests/test_gap005_parity.py` — 46 cases recorded from the pinned oracle revision `bfbe54764eee87c8f67d2b281d5f304faad04a5b` (node 26.5.1, Python 3.11.2, NumPy 2.5.3, Linux x86_64; 8 four-component alpha controls × 4 sizes, the recorded feedback program, a 9-case stateful feedback matrix with `mix: 40` over iterationCount 1–5/seeds 1–3/times 0.0–0.75/sizes 8×8–32×16, and 4 control cases). Each case commits the oracle CLI's PNG artifact (provenance), its decoded RGBA8 bytes (8-bit leg), and the raw output-surface float32 bytes (rgba16f leg, which catches sub-8-bit divergences); `manifest.json` binds each file's sha256, each case's exact program/size/seed/time, and the oracle revision. The test re-renders the Python side and requires byte equality on both legs — no node and no sibling checkout needed — and asserts the control pairs differ, so the oracle is proven harness-seed-sensitive and feedback-stateful and duplicated evidence cannot pass. [Independent comparisons](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/independent-comparisons.json) and [Controlled alpha cases](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/alpha-controls.json) (historical, 2026-09-25).
- Next action: None.
- Dependencies: Correct behavior against immutable authority inputs. Do not change goldens, tolerances, or case selection to conceal differences.
- Acceptance criteria: All recorded alpha controls and the feedback program match exactly. The full existing suites retain their complete denominators.
- Required checks: Repeat nondefault programs, parameter choices, seeds, times, non-square sizes, and stateful frames.
- Last verification: 2026-09-26 at the publication commit carrying this row (base `c724cb684d53efd15b0ce5502cb714d212b0406a`). RGB, explicit alpha, four-component color, and feedback all match per the committed fixture test; full suite 337 passed, 0 skipped (263 at this source — the original 216 plus the 47 GAP-005 acceptance cases — plus 74 node-oracle parity cases including the complete iterated-program matrix), with no pre-existing tests, goldens, tolerances, or case selection changed.

## 5. Ordered next actions

1. ~~Correct GAP-004 in `pyproject.toml` through the implementation job. Include required bundle data in wheels and source archives.~~
   Done 2026-09-26: bundle data and LICENSE are included in both archives and verified in empty consumers on Python 3.11.2 and 3.13.13 (section 3). GAP-004 is closed.
2. ~~Resolve GAP-005 in the DSL color and rendering paths. Retain the three alpha controls and feedback program.~~
   Done 2026-09-26: closed with the `Runtime.binary` width-truncation and transpiler constructor-fusion fixes; byte-level matches against the pinned oracle at `bfbe5476` committed as node-free fixtures (GAP-005 section).
3. Resolve GAP-001 authority differences and landscape filtering support. Retain both valid filtering choices and all 210 effect IDs.
   Run the complete image and DSL suites. Report every skip, missing case, error, parameter choice, and authority revision.
4. ~~Complete GAP-002 on Python 3.11 and current Python across declared platforms. Check upgrade, removal, cancellation, and practical first-output timing.~~
   Done 2026-09-26: closed with Linux x86_64 evidence on Python 3.11.2 and 3.13.13; macOS, Windows, and Python 3.14 remain explicitly unavailable on this harness, and one unexplained render-bytes outlier is recorded in section 3 for parity follow-up.
5. Complete GAP-003 through existing packaging and CI. Require exact-source tests, complete parity enforcement, and artifact verification before release qualification.
   Done in part 2026-09-26: artifact reproduction, installation, examples, upgrade, removal, notices, and dependencies verified at merged source `8f411a1c5501b5fd156b8945df3b2b6ba4545d04` (section 3). The remaining exact-source CI gate requires workflow authority this implementation job does not hold (GAP-003 stays open).

Implementation belongs to the separate job. Do not port additional effects or advance the current parity checkpoint through this register.

## 6. Pass history

2026-09-26 release-qualification pass at `8f411a1c5501b5fd156b8945df3b2b6ba4545d04` (merged HEAD including sync `1d1ac92`): wheel/sdist built in an isolated copy and byte-verified against their inventories; installed wheel (3.11.2) and sdist (3.13.13) consumers passed the full documented workflow including cross-format reinstall and removal; MIT and dependency notices verified; 512×512 example re-bounded. Exact-source CI: 0 runs, 0 checks; GAP-003 stays open on the missing test/parity CI gate (workflow authority required).

2026-09-26 installed-developer-workflow pass at the candidate commit of this revision: closed GAP-002 and GAP-004 with the `pyproject.toml` package-data correction and complete wheel/sdist installed workflows on Python 3.11.2 and 3.13.13 (artifact and output SHA-256 hashes in section 3). 512×512 example bounded at 34m55s. One unexplained render-bytes outlier recorded; macOS/Windows/Python 3.14 unavailable and explicit. Three gaps remain open (GAP-001, GAP-003, GAP-005).

2026-09-25 daily review at `49d8e51ec4b71104dc03728c84c60cae3e2857d3`: reviewed worker audit `audit-20260925-090206` (published in `4ff7b03247b59cead0b63a7ee3a7b5697f7bf58e`).
Verified post-audit commit `49d8e51ec4b71104dc03728c84c60cae3e2857d3` in `tests/test_parity.py`.
Independently reproduced GAP-004 missing metadata in built wheel. Checked GAP-005 nondefault numerical parity differences.
Five open gaps remain. Zero closures. Full parity and release readiness remain unqualified.

2026-09-25 worker audit at `912e6a9aac32c668a5242b8d52aa4415ca3a848e`: added GAP-004 and GAP-005. No gap closed.
Default image parity, installed workflows, current authority drift, and complete served-file reproduction now have source-bound evidence.
Full parity and release readiness remain unqualified. [Run evidence](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/parity-results.json).

2026-09-25 daily review at `93b8b141d21a7c853a89131166147c8337109144`: source freshness and bounded evidence reviewed. Open qualification limits retained. [Retained review evidence](/Users/alex/.codex/automations/noisemaker-port-completion-audit/review-20260925-053200/python-current-tests.json). No new closure claimed.

2026-09-25 continuous-improvement pass at `08aaa083d09e65ed2ed9ec0ac812391f4dd5d011`: perf/test commits `6e17bfc` (vectorized PNG unfilter and channel expansion) and `08aaa08` (hand-filtered Sub/Up fixtures plus non-RGBA color-type decode tests, tRNS keys, palette-index error case). Behavior verified byte-identical against the prior decoder via 300 randomized differential unfilter cases (filters 0-4 mixed, widths 1-64, bpp 1-4) and 120 randomized full-PNG cases across color types 0/2/3/4/6 with and without tRNS. Full suite executed at this exact source: 209 passed, 75 skipped under NumPy 2.5.3 on Python 3.13.13 (Linux x86_64) and 209 passed, 75 skipped under NumPy 1.26.4 on Python 3.11.2 — the declared `numpy>=1.26` lower bound. Out-of-range Python-integer comparisons against uint8 tRNS sentinels (`-1`, `65535`) evaluate to all-False on both versions (no NEP 50 OverflowError). A 1024×1024 RGBA decode drops from ~1.79s to ~0.033s. Exact-source CI remains zero test runs: a minimal pytest workflow was drafted but rejected as outside this job's workflow authority. No gap closed; all five gaps remain open.

| Date | Source SHA | Changes | Tested scope | Remaining limits |
|---|---|---|---|---|
| 2026-09-26 | the publication commit carrying this row (base `c724cb684d53efd15b0ce5502cb714d212b0406a`) | GAP-005 closed: `Runtime.binary` width truncation (vec4-into-vec3 leak) + transpiler constructor fusion for uniform and distinct-scalar `vecN(...)` operands (unrounded scalars; bundle regenerated from CDN 1.0.183); added committed node-free byte-level oracle fixtures `tests/data/gap005-oracle/` (46 cases: 32 alpha controls, recorded feedback program, 9-case stateful feedback matrix, 4 seed/statefulness controls; PNG + RGBA8 + rgba16f legs, sha256 manifest) + `tests/test_gap005_parity.py`; gap row updated. | Full suite 337 passed, 0 skipped (263 + 74 node-oracle parity incl. all iterated programs) against pinned oracle `bfbe5476`; fixture test re-renders all 46 cases and matches every committed oracle byte. | GAP-001 authority drift and GAP-003 exact-source CI remain; macOS/Windows/Python 3.14 untested. |
| 2026-09-26 | `8f411a1c5501b5fd156b8945df3b2b6ba4545d04` | GAP-003 release-qualification pass: isolated-copy wheel/sdist build + byte-inventory verification; installed consumer workflow, reinstall, removal, notices, dependencies, 512×512 re-bound. GAP-003 open. | Wheel (3.11.2) and sdist (3.13.13) install through cross-format reinstall and removal; CLI/library/filter/DSL/cancellation with hashes matching GAP-002 evidence; full suite 214 passed, 76 skipped; parity receipt byte-exact. | Exact-source CI: 0 runs, 0 checks — no workflow runs tests (workflow authority required); macOS, Windows, Python 3.14, and real versioned upgrade untested; artifact bytes not reproducible (timestamps). |
| 2026-09-26 | this candidate revision | `pyproject.toml` package-data correction (bundle JSON + kernels ship in wheel/sdist); GAP-002 and GAP-004 closed. | Wheel+sdist install, CLI/library render, PNG filter, invalid-input recovery, SIGINT cancellation, reinstall, removal on Python 3.11.2 (numpy 2.4.6) and 3.13.13 (numpy 2.5.3); full suite 209 passed, 75 skipped; 512×512 render bounded at 34m55s. | macOS, Windows, Python 3.14, and NumPy < 1.26 untested here; real versioned upgrade untestable at version 0.0.0; one unexplained render-bytes outlier (2 of 52) unattributed. |
| 2026-09-25 | `08aaa083d09e65ed2ed9ec0ac812391f4dd5d011` | Vectorized PNG decode with byte-identical differential verification; added Sub/Up filter and non-RGBA color-type decode tests. Zero closures. | Full suite at exact source: 209 passed, 75 skipped on NumPy 2.5.3/py3.13 and NumPy 1.26.4/py3.11. | Exact-source CI still has no test workflow; full parity, wheel packaging, platforms, and release gates remain open. |
| 2026-09-25 | `49d8e51ec4b71104dc03728c84c60cae3e2857d3` | Reviewed audit-20260925-090206 and post-worker parity test update. Reproduced GAP-004. Zero closures. | 64 CLI, DSL, and output tests pass. Sibling source lock test passes. Wheel build and nondefault parity checks reproduced. | Full parity, wheel packaging, platforms, and release gates remain open. |
| 2026-09-25 | `912e6a9aac32c668a5242b8d52aa4415ca3a848e` | Added GAP-004 and GAP-005. Default image parity, installed workflows, authority drift, served kit verified. | 167 exact default passes, 38 skips, 2 independent numerical failures, 2 landscape rejections. | Wheel fails, nondefault parity fails, complete authority parity unverified. |
| 2026-09-24 | `70c03da6944be1319ccc249fd9646dd9df05e86c` | Created six-section register and README link. No closures. | Initial collection failed because Click was missing. After isolated Click installation, 62 CLI, DSL, and output tests passed with 10 warnings. | Full audit, installed workflows, current rendered parity, platforms, and releases remain unqualified. |

Run ID: `20260924-remaining-gap-documents`.
[Operational evidence](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-20260924-remaining-gap-documents). Creating this register does not advance successful-audit timestamps or the rotation.
