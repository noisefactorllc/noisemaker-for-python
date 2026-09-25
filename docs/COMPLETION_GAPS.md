# noisemaker-for-python: completion gaps

Current compatibility matrix: [compatibility report](COMPATIBILITY.md).

## 1. Scope and source revisions

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

### Daily review, 2026-09-25

64 CLI, DSL, and output-runtime tests pass at the current source. These checks include useful PNG output but do not supply a complete reference-versus-Python pixel denominator. The served kit remains at a different source. GAP-001 remains open and current full rendered parity is unverified. [Raw evidence](/Users/alex/.codex/automations/noisemaker-port-completion-audit/review-20260925-053200/python-current-tests.json).
The review checked source changes, worker evidence, source-bound CI where present, and current served inventories. Full installed-host and platform qualification remains incomplete.

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

- Worker verification: 2026-09-25. Current evidence: Small installed and served workflows pass. The 512×512 example exceeded 180 seconds. Cancellation preserves existing files.
- Next check: Test Python 3.11, additional platforms, upgrades, and practical first-output timing after GAP-004.
- Evidence: Current worker methods in section 3. No closure.

- Status: open. Priority: P2. Category: usability.
- Affected scope: Public API, examples, supported hosts, errors, recovery, and lifecycle.
- Expected behavior: Developers can install, produce useful output, integrate it, recover from errors, and remove the package.
- Observed behavior: This pass did not exercise the complete installed workflow or supported-version matrix.
- Evidence: [README](https://github.com/noisefactorllc/noisemaker-for-python/blob/70c03da6944be1319ccc249fd9646dd9df05e86c/README.md), [official reference](https://packaging.python.org/en/latest/tutorials/packaging-projects/), and section 3.
- Next action: Install a wheel into an isolated target. Render curl, apply a filter to PNG input, run invalid DSL, recover, and remove the installation.
- Dependencies: Use an isolated consumer. Identify host, GPU, licensing, and input requirements before execution.
- Acceptance criteria: Retain artifact hashes, steps, meaningful output, error diagnostics, recovery results, and cleanup results.
- Required checks: Test minimum and current supported versions. Check cancellation and file preservation where relevant. Keep unavailable platforms explicit.
- Last verification: 2026-09-25. Source inspection does not close this gap.

### GAP-003: distribution and release qualification

- Worker verification: 2026-09-25. Current evidence: All 329 served files match and reproduce. Candidate archives fail at first render because runtime metadata is absent.
- Next check: Resolve GAP-004 before release qualification. Add complete parity enforcement through existing CI in the implementation job.
- Evidence: Current worker methods in section 3. No closure.

- Status: open. Priority: P2. Category: release.
- Affected scope: Actual artifact, dependencies, notices, version promises, and release evidence.
- Expected behavior: The delivered artifact supports its documented installation and first useful result.
- Observed behavior: Complete artifact reproduction, installation, upgrade, and removal remain unverified.
- Evidence: [Distribution instructions](https://github.com/noisefactorllc/noisemaker-for-python/blob/70c03da6944be1319ccc249fd9646dd9df05e86c/README.md), section 1, and exact-source CI in section 2.
- Next action: Build wheel and source archive in an isolated copy. Verify installed kernels, CLI entry point, dependencies, licenses, upgrade behavior, and removal.
- Dependencies: Complete GAP-002 for the candidate. Distinguish source CI from downstream publication and native rendering.
- Acceptance criteria: Match artifact bytes to their inventory. Check notices and dependencies. Pass installation, examples, upgrade, and removal.
- Required checks: Inspect exact-source CI jobs and actual render legs. Count skips and errors rather than trusting green summaries.
- Last verification: 2026-09-25. This register does not approve a release.

### GAP-004: built distributions omit required bundle metadata

- Status: open. Priority: P1. Category: release.
- Affected scope: `pyproject.toml`, wheel contents, source archive contents, and installed public entry points.
- Expected behavior: Installed distributions include every runtime input and produce the documented first image.
- Observed behavior: Both archives omit all JSON files. The wheel installs, then raises `FileNotFoundError` for `bundle/metadata.json`.
- Evidence: [Wheel failure](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/wheel-first-output.json) and [Source archive inventory](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/sdist-inventory.json).
- Next action: Include required bundle data through the existing package configuration. Build and install both formats in empty consumers.
- Dependencies: The implementation job owns the correction. Preserve source hashes and separate editable-install evidence.
- Acceptance criteria: CLI and library calls produce verified PNGs without source-directory access. Required metadata and notices exist in both archives.
- Required checks: Wheel and source-archive installation on minimum and current Python. Execute generation, filtering, invalid-input recovery, and removal.
- Last verification: 2026-09-25. The failure reproduces in a private wheel-only target.

### GAP-005: nondefault output differs from the CPU oracle

- Status: open. Priority: P1. Category: implementation.
- Affected scope: Four-component DSL colors and repeated feedback at nondefault size, seed, and time.
- Expected behavior: Supported CPU parity cases match the identified oracle under the declared numerical contract.
- Observed behavior: Solid alpha differs by 179 in every pixel. Feedback differs by one byte in five channels.
- Evidence: [Independent comparisons](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/independent-comparisons.json) and [Controlled alpha cases](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/alpha-controls.json).
- Next action: Isolate color interpretation and feedback rounding in the implementation job. Preserve the recorded programs and dimensions.
- Dependencies: Correct behavior against immutable authority inputs. Do not change goldens, tolerances, or case selection to conceal differences.
- Acceptance criteria: All recorded alpha controls and the feedback program match exactly. The full existing suites retain their complete denominators.
- Required checks: Repeat nondefault programs, parameter choices, seeds, times, non-square sizes, and stateful frames.
- Last verification: 2026-09-25. RGB and explicit alpha match. Four-component color and feedback remain failed.

## 5. Ordered next actions

1. Correct GAP-004 in `pyproject.toml` through the implementation job. Include required bundle data in wheels and source archives.
   Build both formats. Install each into an empty consumer. Require useful CLI and library output without source-directory access.
2. Resolve GAP-005 in the DSL color and rendering paths. Retain the three alpha controls and feedback program.
   Require exact output against the recorded CPU oracle. Preserve numerical contracts and current tolerances.
3. Resolve GAP-001 authority differences and landscape filtering support. Retain both valid filtering choices and all 210 effect IDs.
   Run the complete image and DSL suites. Report every skip, missing case, error, parameter choice, and authority revision.
4. Complete GAP-002 on Python 3.11 and current Python across declared platforms. Check upgrade, removal, cancellation, and practical first-output timing.
5. Complete GAP-003 through existing packaging and CI. Require exact-source tests, complete parity enforcement, and artifact verification before release qualification.

Implementation belongs to the separate job. Do not port additional effects or advance the current parity checkpoint through this register.

## 6. Pass history

2026-09-25 worker audit at `912e6a9aac32c668a5242b8d52aa4415ca3a848e`: added GAP-004 and GAP-005. No gap closed.
Default image parity, installed workflows, current authority drift, and complete served-file reproduction now have source-bound evidence.
Full parity and release readiness remain unqualified. [Run evidence](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-audit-20260925-090206/parity-results.json).

2026-09-25 daily review at `93b8b141d21a7c853a89131166147c8337109144`: source freshness and bounded evidence reviewed. Open qualification limits retained. [Retained review evidence](/Users/alex/.codex/automations/noisemaker-port-completion-audit/review-20260925-053200/python-current-tests.json). No new closure claimed.

| Date | Source SHA | Changes | Tested scope | Remaining limits |
|---|---|---|---|---|
| 2026-09-24 | `70c03da6944be1319ccc249fd9646dd9df05e86c` | Created six-section register and README link. No closures. | Initial collection failed because Click was missing. After isolated Click installation, 62 CLI, DSL, and output tests passed with 10 warnings. | Full audit, installed workflows, current rendered parity, platforms, and releases remain unqualified. |

Run ID: `20260924-remaining-gap-documents`.
[Operational evidence](/Users/alex/.codex/automations/noisemaker-port-completion-audit/evidence-20260924-remaining-gap-documents). Creating this register does not advance successful-audit timestamps or the rotation.
