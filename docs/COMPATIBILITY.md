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
Source hashes (audit evidence `evidence-audit-20260925-090206/source-hashes.json`). Authority metadata (audit evidence `evidence-audit-20260925-090206/published-authority.json`).

Served kit `0.1.7` identifies `1901b267a8b8ef29efc702cc3976b70f8aae0404`.
All 329 served files match their inventory hashes. All 324 engine files match the reviewed source.
The existing builder reproduces all 329 inventoried files. Later source changes affect only tests and audit documents.
Served verification (audit evidence `evidence-audit-20260925-090206/served-verification.json`). Reproduction (audit evidence `evidence-audit-20260925-090206/kit-reproduction.json`). Source comparison (audit evidence `evidence-audit-20260925-090206/kit-source-diff.json`).

The candidate wheel and source archive omit all bundle JSON files. Installation succeeds, but the first render fails with missing `bundle/metadata.json`.
No PyPI project exists at the checked project endpoint. The GitHub API returned no releases.
Wheel failure (audit evidence `evidence-audit-20260925-090206/wheel-first-output.json`). Archive inventory (audit evidence `evidence-audit-20260925-090206/sdist-inventory.json`). Endpoint observations (audit evidence `evidence-audit-20260925-090206/endpoint-results.json`).

Audit publication covers only these two reports. Their paths match no existing workflow.
No implementation, release, or parity checkpoint changes belong to this audit.

### Earlier review observations

Daily review: 2026-09-25. Current inspected source: [`93b8b141d21a7c853a89131166147c8337109144`](https://github.com/noisefactorllc/noisemaker-for-python/commit/93b8b141d21a7c853a89131166147c8337109144).
Full rendered parity remains **unverified**. No release approval or new closure follows from this review.
Current upstream discovery: `bbdeb56c4b75cf33379766c3e87b0f5a18bcbba8`. Published Noisemaker authority: `1.0.179`, source `fca611fd8f91424661d4e531d39313d24ea21134`, 210 effect IDs.
The observations below retain their original source and authority identities. They do not qualify later updates.
Current served kit: `0.1.7`, source `1901b267a8b8ef29efc702cc3976b70f8aae0404`. Retrieved inventory and hashes (audit evidence `review-20260925-053200/current-served-inventories.json`). Artifact identity does not establish host qualification. The served kit's local artifact paths are macOS-local and are not reproducible from the repository tree; see the evidence-availability note in §6.

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
| Nondefault alpha and feedback | verified | Fixed 2026-09-26 at this source: four-component solid colors and the feedback program byte-match the pinned oracle `bfbe5476` at 8-bit and rgba16f level per the committed fixtures in `tests/data/gap005-oracle/` (with seed-sensitivity and statefulness controls). GAP-005 closed. |
| Current landscape filtering | verified | Fixed: both valid `renderLandscape3d` `filtering` choices (`isosurface`, `voxel`) render and byte-match the pinned oracle; committed as `test_landscape3d_filtering_byte_parity`. GAP-001 closed 2026-09-27. |
| Complete current-authority parity | verified | Reconciled 2026-09-27 against immutable CDN build `1.0.190`: 294/294 program GLSL hashes match the bundle lock, 0 parameter-manifest differences, 0 unmatched programs; 205/205 targeted effects have zero-tolerance oracle-matched comparisons; 5 authority IDs are documented non-targets (§3). The complete parameter matrix remains unmeasured. |
| Source-update parity enforcement | blocked | No current exact-source CI checks or complete parity gate. GAP-003. |
| Release readiness | blocked | Exact-source CI and platform limits (macOS/Windows/Python 3.14) remain. |

Installed evidence (audit evidence `evidence-audit-20260925-090206/bounded-developer-workflows.json`). Parity evidence (audit evidence `evidence-audit-20260925-090206/independent-comparisons.json`). Artifact evidence (audit evidence `evidence-audit-20260925-090206/served-verification.json`).

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

### Source-lock sync, 2026-09-30 (noisemaker-for-cpu `fd9d56c74ce7`..`5f12866e919f`)

Range audit of the sibling noisemaker-for-cpu `fd9d56c74ce7500b7eaeea90a93d3bf49375d28e..5f12866e919f76fc19e4d3e6f0670d61d10dc672` against a fresh clone (`git clone https://github.com/noisefactorllc/noisemaker-for-cpu.git`, checkout `5f12866e919f76fc19e4d3e6f0670d61d10dc672`, tree `7ce22d24a842f381bebe019404bfa6453bfc7d00`; `git merge-base --is-ancestor fd9d56c74ce7 5f12866e919f` exits 0, so the force-push-flagged delivery is contiguous over this range): seven commits beyond the previously audited `d2965d0b7880`. Six are -cpu docs commits touching only `docs/COMPLETION_GAPS.md`, `docs/CRT-PARITY.md`, and `docs/COMPATIBILITY.md` (`36872dd` accepted CRT approximation and compatibility constraints; `c58bada` records a supervisor publication 403 blocker in the GAP register pass history; `52219d9` replaces local machine paths with portable references; `65a52cb`/`7e50900`/`ce3926d` record GAP-002 bounded external-input qualifications and tie GAP-002 required checks to the exact record candidate `7e50900`); `5f12866` is the source-lock sync, bumping the upstream pin from noisemaker@`f24b52540af6a88d12daa05feba1a04ad61b22a2` to `e24c844f8dada85551ab084f41db8944fbc176c8` with a recomputed `PINNED_SOURCE_DIGEST` (`c2e0c264dc20338b19a144ee0888bd2ca39edcf325315a7d7ae1f5ced920804d`) and `PINNED_SOURCE_MANIFEST_DIGEST` (`2516724e7d886253883107b60feff6b1da6ca8bc48186b05357c8443c56f1bff`). The manifest-digest change comes from exactly four upstream `shaders/src/runtime` entries in the pinned-source manifest (`backends/diagnostics.js` 7128→8059 bytes, `backends/webgl2.js` 78150→81111, `backends/webgpu.js` 164220→164648, `pipeline.js` 123038→124928 — upstream GAP-007 backend-diagnostics and WebGL2/WebGPU validator 'input'/'resolution' dimension-keyword machinery, GPU-host files neither the -cpu CPU runtime nor this port consumes; no `diagnostics`/`webgl2`/`webgpu`/`pipeline` import exists in the -cpu `src` or `bin` tree, and `shaders/effects` is untouched, so the effect catalog is byte-identical); `git diff d2965d0..5f12866 -- shaders src/runtime src/effects catalog.js bin` is empty except `src/effects/generated/upstream-snapshot.js`, whose only change is the `UPSTREAM_REVISION` field, so the -cpu oracle's rendered output is byte-identical to the prior pin and no -python source or bundle change applies. The committed `PINNED_SOURCE_MANIFEST_DIGEST` was recomputed from the sibling's committed manifest entries with the sibling's own `sourceManifestDigest()` and matches byte-for-byte; `PINNED_SOURCE_DIGEST` is read from the sibling's committed source lock at `5f12866e919f`. Port per repo convention: `tests/test_parity.py` audited source-lock set gains the `e24c844f8da...`/`c2e0c264...` entry (added only by this audited sync whose oracle output was proven byte-identical and whose committed digest was verified as above); the node-free parity receipt and the exact-source gate's immutable oracle tarball stay pinned at `296e0138`/`b61b658399f1`, and this job holds no workflow authority to advance the `tests.yml` oracle pin. No gap closed. Raw run evidence (kept out of the repository per the current no-committed-logs policy), archived with the job in `/workspace/evidence`: `cpu-sync-fd9d56c-5f12866-range.diff` (verbatim `git log --stat` over the range, the ancestry check, the three tree SHAs, and the full `git diff d2965d0..5f12866`) and `cpu-sync-fd9d56c-5f12866-audit.json`.

Reproduction (requires network, node, and the sibling clone): `git clone https://github.com/noisefactorllc/noisemaker-for-cpu.git && git -C noisemaker-for-cpu checkout 5f12866e919f76fc19e4d3e6f0670d61d10dc672 && git -C noisemaker-for-cpu rev-parse 'HEAD^{tree}'` (expect `7ce22d24a842f381bebe019404bfa6453bfc7d00`); `git -C noisemaker-for-cpu diff --name-only d2965d0b7880cee678de11ec797155c8a65c7b66..5f12866e919f76fc19e4d3e6f0670d61d10dc672 -- shaders src/runtime src/effects catalog.js bin` (expect only `src/effects/generated/upstream-snapshot.js`); the sibling's committed source lock at that revision reads `PINNED_UPSTREAM_REVISION = 'e24c844f8dada85551ab084f41db8944fbc176c8'` / `PINNED_SOURCE_DIGEST = 'c2e0c264dc20338b19a144ee0888bd2ca39edcf325315a7d7ae1f5ced920804d'` / `PINNED_SOURCE_MANIFEST_DIGEST = '2516724e7d886253883107b60feff6b1da6ca8bc48186b05357c8443c56f1bff'`. Then `NOISEMAKER_CPU_DIR=<sibling> scripts/parity.py --json /tmp/receipt.json` and compare `byteExact` with the committed receipt (only the `cpu` provenance block may differ).

Environment: Linux x86_64 container, Python 3.11.2, NumPy 2.4.6, node 26.5.1; sibling oracle `NOISEMAKER_CPU_DIR` at `5f12866e919f76fc19e4d3e6f0670d61d10dc672`, upstream pin `e24c844f8dada85551ab084f41db8944fbc176c8`, source digest `c2e0c264dc20338b19a144ee0888bd2ca39edcf325315a7d7ae1f5ced920804d`, tree `7ce22d24a842f381bebe019404bfa6453bfc7d00`.

- `scripts/parity.py --json` — exit 0 against the fresh sibling at `5f12866e919f`: 167/167 byte-exact (zero tolerance), 0 diffs, 0 runtime errors, 0 oracle errors, 38 skipped; every non-provenance receipt field (`byteExact`, `counts`, `diffs`, `errors`, `oracleErrors`, `settings`, `skipped`, per-case SHA-256 entries) is identical to the committed `tests/data/parity-receipt-296e0138.json` — only the `cpu` provenance block moved.
- `scripts/parity-summary` (whole-catalog gate) against the fresh sibling at `5f12866e919f`: `PARITY-SUMMARY {"expected":205,"executed":205,"exact":205,"strict":0,"near":0,"defer":0,"skip":0,"fail":0,"missing":0}`, exit 0, provenance line binding portHead, cpuHead `5f12866e919f...`, cpuTree, upstreamPin `e24c844f8da...`, sourceDigest `c2e0c264...`.
- Full suite with the fresh sibling at `5f12866e919f` (`NOISEMAKER_CPU_DIR` set): 342 passed, 1 skipped, 0 failed (the skip is the gate-pinned receipt regeneration check, which requires the gate-pinned oracle checkout `296e0138`). Before the audited-entry addition the only failure was `test_cpu_upstream_source_lock_and_catalog_parity` rejecting the then-unaudited pin — red behavior of the audited-set guard verified, then fixed forward by adding the entry.
- `scripts/test` end to end (its own venv, node available): 262 passed, 81 skipped, exit 0, then the whole-catalog parity gate against the pinned authority `d2965d0b7880` (tree verified `69d2ffc4...`): `PARITY-SUMMARY {"expected":205,"executed":205,"exact":205,"strict":0,"near":0,"defer":0,"skip":0,"fail":0,"missing":0}`.

### Source-lock sync, 2026-09-29 (noisemaker-for-cpu `fd9d56c74ce7`..`d2965d0b7880`)

Range audit of the sibling noisemaker-for-cpu `fd9d56c74ce7500b7eaeea90a93d3bf49375d28e..d2965d0b7880cee678de11ec797155c8a65c7b66` against a fresh clone (`git clone https://github.com/noisefactorllc/noisemaker-for-cpu.git`, checkout `d2965d0b7880cee678de11ec797155c8a65c7b66`, tree `69d2ffc4731b23fddd472b830d3458915ede2bc4`; `git merge-base --is-ancestor fd9d56c74ce7 7863f096061b` exits 0, so the force-push-flagged delivery is contiguous over this range): ten commits. Nine are -cpu docs/audit-review commits touching only `docs/COMPLETION_GAPS.md`, `docs/CRT-PARITY.md`, and `docs/COMPATIBILITY.md` (`64539bc`..`7863f096`); `d2965d0` is the source-lock sync, bumping the upstream pin from noisemaker@`73c15be00d6888f4b5d2835d8e242ee9e840df45` to `f24b52540af6a88d12daa05feba1a04ad61b22a2` with a recomputed `PINNED_SOURCE_DIGEST` (`f11af18a15ec0220c5d41a17c70da637fa05f86597a4c1984838bd0e77246723`) and `PINNED_SOURCE_MANIFEST_DIGEST` (`143497d9db7c06955057c925c1b1f2fdb29dd8120ce9f5b2d9fa0be6fbc786a6`). The digest change comes from exactly one pinned-source manifest entry (`shaders/src/runtime/external-input.js`, 54120→67725 bytes, sha256 `824dbf38...`→`c29887aa272c02e2e695bede7a273e9010188793598ab82b1daad883071c3763`: upstream GAP-032 WebAudio multi-capture audio-input machinery in `shaders/src/runtime` plus `shaders/tests` — no `AudioInputManager`/`external-input` consumer exists in the -cpu CPU runtime or in this port); `git diff fd9d56c..d2965d0 -- shaders src/runtime src/effects catalog.js bin` is empty except `src/effects/generated/upstream-snapshot.js`, whose only change is the `UPSTREAM_REVISION` field, so the effect catalog and the -cpu oracle's rendered output are byte-identical to the prior pin and no -python source or bundle change applies. Verification of this port against the fresh sibling at `d2965d0b7880`: `scripts/parity.py --json` — 167/167 byte-exact (zero tolerance), 0 diffs, 0 runtime errors, 0 oracle errors, 38 skipped, with per-case SHA-256 entries identical to the committed `parity-receipt-296e0138.json` (only the CPU provenance fields differ); the sibling's committed source lock at `d2965d0b7880` reads `f24b5254...`/`f11af18a...`/manifest digest `143497d9...`, verified byte-for-byte. The port's source-lock assertion (`tests/test_parity.py`) now verifies the sibling's lock against the audited source-lock set (296e0138/e371a165 — the gate-pinned oracle — and f24b5254/f11af18a — the current -cpu pin), each entry added only by an audited sync whose oracle output was proven byte-identical and whose digest was verified byte-for-byte; the node-free parity receipt stays pinned at `parity-receipt-296e0138.json` because the exact-source `tests.yml` gate's immutable oracle tarball is still pinned at `b61b658399f1` and this job holds no workflow authority to advance it. This commit also adds `scripts/parity-summary`, the machine-checkable whole-catalog parity gate against the current authority: every bundled effect id must execute and match the oracle byte-exactly — plain effects through the `effect` CLI path, and the iterated/points/simulation/volume/loop effects through the DSL programs shared with `tests/test_parity.py` (now exported as the `VOLUME_DSL_CASES` table, consolidating the former volume-renderer/landscape3d/palette3d/flow3d/stateful-volume/loop test functions one-to-one into `test_volume_and_loop_dsl_byte_parity` with identical programs, sizes, and assertion; 23 rows replace 21 former parameterizations). An effect with no executable case counts as `missing`, and the entrypoint exits 0 only when `executed == expected`, `exact + strict == expected`, and `near`, `defer`, `skip`, `fail`, and `missing` are all zero — incomplete coverage fails. No gap closed.

Reproduction (requires network, node, and the sibling clone): `git clone https://github.com/noisefactorllc/noisemaker-for-cpu.git && git -C noisemaker-for-cpu checkout d2965d0b7880cee678de11ec797155c8a65c7b66 && git -C noisemaker-for-cpu rev-parse 'HEAD^{tree}'` (expect `69d2ffc4731b23fddd472b830d3458915ede2bc4`); `git -C noisemaker-for-cpu diff --name-only fd9d56c74ce7500b7eaeea90a93d3bf49375d28e..d2965d0b7880cee678de11ec797155c8a65c7b66 -- shaders src/runtime src/effects catalog.js bin` (expect only `src/effects/generated/upstream-snapshot.js`); the sibling's committed source lock at that revision reads `PINNED_UPSTREAM_REVISION = 'f24b52540af6a88d12daa05feba1a04ad61b22a2'` / `PINNED_SOURCE_DIGEST = 'f11af18a15ec0220c5d41a17c70da637fa05f86597a4c1984838bd0e77246723'` / `PINNED_SOURCE_MANIFEST_DIGEST = '143497d9db7c06955057c925c1b1f2fdb29dd8120ce9f5b2d9fa0be6fbc786a6'`. Then `NOISEMAKER_CPU_DIR=<sibling> scripts/parity.py --json /tmp/receipt.json` and compare `byteExact` with the committed receipt (only the `cpu` provenance block may differ).

Environment: Linux x86_64 container, Python 3.11.2, NumPy 2.5.3, node 26.5.1; sibling oracle `NOISEMAKER_CPU_DIR` at `d2965d0b7880cee678de11ec797155c8a65c7b66`, upstream pin `f24b52540af6a88d12daa05feba1a04ad61b22a2`, source digest `f11af18a15ec0220c5d41a17c70da637fa05f86597a4c1984838bd0e77246723`, tree `69d2ffc4731b23fddd472b830d3458915ede2bc4`. Raw run evidence (kept out of the repository per the current no-committed-logs policy), archived with the job in `/workspace/evidence`: `cpu-sync-fd9d56c-d2965d0-range.diff` — the verbatim range evidence (`git log --stat fd9d56c74ce7..d2965d0b7880`, the full `git diff fd9d56c74ce7..d2965d0b7880`, the `merge-base --is-ancestor` ancestry check, and the three tree SHAs); `cpu-sync-fd9d56c-d2965d0-audit.json`; and the parity run output below.

- `scripts/parity-summary` (whole catalog, machine-checkable gate) against the fresh sibling at `d2965d0b7880`: `PARITY-SUMMARY {"expected":205,"executed":205,"exact":205,"strict":0,"near":0,"defer":0,"skip":0,"fail":0,"missing":0}`, exit 0 — every one of the 205 bundled effect ids executed once and byte-identical to the oracle. With case-id arguments it renders and counts only those effects; an unknown or uncovered id counts as `missing` and makes the exit nonzero (verified: `scripts/parity-summary synth/solid render/loopEnd synth3d/noise3d points/life not/an-effect` → `missing:1`, exit 1). Each run prints a provenance line binding both revisions (portHead, cpuHead, cpuTree, upstreamPin, sourceDigest) before the `PARITY-SUMMARY` line. The repository test entrypoint `scripts/test` executes this gate itself when node is available: it clones the sibling at the pinned authority revision `d2965d0b7880cee678de11ec797155c8a65c7b66`, verifies its tree (`69d2ffc4731b23fddd472b830d3458915ede2bc4`), and requires exit 0 — so any supervisor run of the repository's tests records a supervisor-computed whole-catalog parity check bound to both revisions (at this candidate: 205/205 exact, exit 0).
- Full suite with the fresh sibling at `d2965d0b7880`: 342 passed, 1 skipped, 0 failed (the skip is `tests/test_parity_receipt.py:77`, which requires the gate-pinned oracle checkout `296e0138`). The source-lock assertion also passes at the gate-pinned oracle checkout `b61b658399f1`, and corrupting an audited digest in the assertion makes it fail (red behavior verified, then restored from backup). `scripts/test` end to end (pytest plus the parity gate): 262 passed, 81 skipped, then `PARITY-SUMMARY {"expected":205,"executed":205,"exact":205,"strict":0,"near":0,"defer":0,"skip":0,"fail":0,"missing":0}`, exit 0.

### Source-lock sync, 2026-09-28 (noisemaker-for-cpu `b61b658399f1`..`fd9d56c74ce7`)

Range audit of the sibling noisemaker-for-cpu `b61b658399f18b5a93abd0020c02fff3be9630f5..fd9d56c74ce7500b7eaeea90a93d3bf49375d28e` against a fresh clone (`git clone https://github.com/noisefactorllc/noisemaker-for-cpu.git`, checkout `fd9d56c74ce7500b7eaeea90a93d3bf49375d28e`, tree `406bea7cdf50f6080784bfd58ce78902697ccba1`): four commits. `f0ccebe` (GAP-007) gives the -cpu browser demo controls distinct accessible names — `examples/browser/` and its tests, machinery this port does not contain; `f290040` (GAP-008) adds golden-reference provenance reporting to the -cpu parity harness (`parity/goldens/provenance.json`, `scripts/parity/`) — no golden, tolerance, or engine change; `21d211e` is -cpu docs plus a landscape-authority comparison JSON; `fd9d56c` is the source-lock sync, bumping the upstream pin from noisemaker@`296e0138c4744ed485b2e95de3eeb466c17629ee` to `73c15be00d6888f4b5d2835d8e242ee9e840df45` with a recomputed `PINNED_SOURCE_DIGEST` (`b78f27e21703a5ae3f976273e946f71b435193eeee4006c98caba229e3eedcaa`) and `PINNED_SOURCE_MANIFEST_DIGEST` (`1cb5f2447819f6b253ea70673e03bd3dbb04486272d111f844da44e4d3ff5edb`). The digest change comes from three upstream `shaders/src` entries in the pinned-source manifest (`webgl2.js`, `compiler.js`, `pipeline.js` — upstream GPU-host machinery neither the -cpu CPU runtime nor this port consumes); `git diff b61b658..fd9d56c -- shaders src/runtime src/effects catalog.js bin` is empty except `src/effects/generated/upstream-snapshot.js`, whose only change is the `UPSTREAM_REVISION` field, so the effect catalog and the -cpu oracle's rendered output are byte-identical to the prior pin and no -python source or bundle change applies. Verification of this port against the fresh sibling at `fd9d56c74ce`: `scripts/parity.py --json` — 167/167 byte-exact (zero tolerance), 0 diffs, 0 runtime errors, 0 oracle errors, 38 skipped, with per-case SHA-256 entries identical to the committed `parity-receipt-296e0138.json` (only the CPU provenance fields differ); the sibling's committed source lock at `fd9d56c74ce` reads `73c15be0...`/`b78f27e2...`/manifest digest `1cb5f244...`, verified byte-for-byte. The port's pinned assertions and receipt were briefly advanced to `fd9d56c74ce`/`73c15be0` in commit `324f92c`, which broke the exact-source gate (run `36386480341`: all four host jobs failed) because the gate's immutable oracle tarball is pinned at `b61b658399f1` and this job holds no workflow authority to advance it. This commit restores the gate-consistent pins (`tests/test_parity.py` source-lock assertions at `296e0138...`/`e371a165...`; `tests/test_parity_receipt.py` re-pinned to `parity-receipt-296e0138.json`; the superseded `parity-receipt-73c15be0.json` removed) while keeping the sync verification evidence above. Authority limit recorded: no workflow change exists in this job; the next action is an actor with workflow authority advancing the `tests.yml` oracle pin from `b61b658399f1` to `fd9d56c74ce7500b7eaeea90a93d3bf49375d28e`, after which the port's pinned assertions and receipt re-advance to `73c15be0`/`b78f27e2` (the receipt bytes are already archived with the job). No gap closed.

Reproduction (requires network, node, and the sibling clone): `git clone https://github.com/noisefactorllc/noisemaker-for-cpu.git && git -C noisemaker-for-cpu checkout fd9d56c74ce7500b7eaeea90a93d3bf49375d28e && git -C noisemaker-for-cpu rev-parse 'HEAD^{tree}'` (expect `406bea7cdf50f6080784bfd58ce78902697ccba1`); `git -C noisemaker-for-cpu diff --name-only b61b658399f18b5a93abd0020c02fff3be9630f5..fd9d56c74ce7500b7eaeea90a93d3bf49375d28e -- shaders src/runtime src/effects catalog.js bin` (expect only `src/effects/generated/upstream-snapshot.js`); the sibling's committed source lock at that revision reads `PINNED_UPSTREAM_REVISION = '73c15be00d6888f4b5d2835d8e242ee9e840df45'` / `PINNED_SOURCE_DIGEST = 'b78f27e21703a5ae3f976273e946f71b435193eeee4006c98caba229e3eedcaa'` / `PINNED_SOURCE_MANIFEST_DIGEST = '1cb5f2447819f6b253ea70673e03bd3dbb04486272d111f844da44e4d3ff5edb'`. Then `NOISEMAKER_CPU_DIR=<sibling> scripts/parity.py --json /tmp/receipt.json` and compare `byteExact` with the committed receipt (only the `cpu` provenance block may differ).

Environment: Linux x86_64 container, Python 3.11.2, NumPy 2.5.3, node 26.5.1; sibling oracle `NOISEMAKER_CPU_DIR` at `fd9d56c74ce7500b7eaeea90a93d3bf49375d28e`, upstream pin `73c15be00d6888f4b5d2835d8e242ee9e840df45`, source digest `b78f27e21703a5ae3f976273e946f71b435193eeee4006c98caba229e3eedcaa`, tree `406bea7cdf50f6080784bfd58ce78902697ccba1`. Raw run evidence (range audit and port verification logs, kept out of the repository per the current no-committed-logs policy): archived with the job as `cpu-sync-b61b658-fd9d56c-audit.json` in `/workspace/evidence` (SHA-256 `678c7214c23e3c45e7c189487a09d0dd13a58c1b23a8e62e5c959c98f8d05a78`).

- `scripts/parity.py --json` — exit 0 against both the fresh sibling at `fd9d56c74ce` (167/167 byte-exact) and the gate-pinned oracle at `b61b658399f1`; per-case SHA-256 entries are identical across the two oracle revisions (only the `cpu` provenance fields differ).
- `tests/test_parity.py` + `tests/test_parity_receipt.py` against the gate-pinned oracle at `b61b658399f1` (tarball extraction, the workflow's exact loading procedure): 82 passed, 0 failed, including the regeneration check running against the pinned sibling.

### Source-lock sync, 2026-09-27 (noisemaker-for-cpu `dedfd07c24f8`..`b61b658399f1`)

Range audit of the sibling noisemaker-for-cpu `dedfd07c24f80d9b0adddf912a4224ce6c1d795f..b61b658399f18b5a93abd0020c02fff3be9630f5` against a fresh clone (`git clone https://github.com/noisefactorllc/noisemaker-for-cpu.git`, checkout `b61b658399f18b5a93abd0020c02fff3be9630f5`): two commits (`34a0325`, `b61b658`), each a source-lock sync. The first bumps the upstream source lock from noisemaker@`12b4d74fb4f28d5f00bb1dde107fa8673814d8b9` to `93229933b102ba82e713402be19db57207698850` and the second to `296e0138c4744ed485b2e95de3eeb466c17629ee`. The committed pinned-source manifest diff across the whole range changes only the `revision` field; `git diff dedfd07c24f8..b61b658399f1 -- shaders` is empty, so `shaders/effects` and `shaders/src` are byte-identical to the prior pin (the intervening upstream commits touch only `shaders/tests/` harness tooling and docs — machinery the -cpu port and this port do not consume), the effect catalog is byte-identical, and no -python source or bundle change applies. Port per repo convention: `tests/test_parity.py` source-lock assertions advanced to `296e0138...`/`e371a165...` (digest and manifest digest unchanged and correct); parity receipt (the node-free replay fixture) regenerated with the node oracle CLI against the sibling checkout at `b61b658399f1` (tree `41988bc079140eccf082dd08f2ec5c8a4555e787`) as `tests/data/parity-receipt-296e0138.json`, replacing `parity-receipt-12b4d74f.json`; its `byteExact` (167/167 effects, zero tolerance), settings, and counts are identical to the superseded receipt — only the CPU provenance fields moved. No gap closed.

Reproduction (requires network, node, and the sibling clone): `git clone https://github.com/noisefactorllc/noisemaker-for-cpu.git && git -C noisemaker-for-cpu checkout b61b658399f18b5a93abd0020c02fff3be9630f5 && git -C noisemaker-for-cpu rev-parse 'HEAD^{tree}'` (expect `41988bc079140eccf082dd08f2ec5c8a4555e787`); `git -C noisemaker-for-cpu diff --name-only dedfd07c24f80d9b0adddf912a4224ce6c1d795f..b61b658399f18b5a93abd0020c02fff3be9630f5 -- shaders` (expect no output); the sibling's committed source lock at that revision reads `PINNED_UPSTREAM_REVISION = '296e0138c4744ed485b2e95de3eeb466c17629ee'` / `PINNED_SOURCE_DIGEST = 'e371a1650d1ace9462a20ecf4e4f0902e5135b4772e8a9abbc8d2c037beebf59'` / `PINNED_SOURCE_MANIFEST_DIGEST = '8bb68100f40db4955c4544507eb6049b1e31a0887828196b48e67d5cd8c5f218'`. Then `NOISEMAKER_CPU_DIR=<sibling> scripts/parity.py --json /tmp/receipt.json` and compare `byteExact` with the committed receipt (only the `cpu` provenance block may differ).

Environment: Linux x86_64 container, Python 3.11.2, NumPy 2.4.6, node 26.5.1; sibling oracle `NOISEMAKER_CPU_DIR` at `b61b658399f18b5a93abd0020c02fff3be9630f5`, upstream pin `296e0138c4744ed485b2e95de3eeb466c17629ee`, source digest `e371a1650d1ace9462a20ecf4e4f0902e5135b4772e8a9abbc8d2c037beebf59`, tree `41988bc079140eccf082dd08f2ec5c8a4555e787`. Committed verbatim evidence (range audit and port verification logs, for review runtimes without a sibling checkout or network): `docs/evidence/cpu-sync-dedfd07c-b61b658-audit.json` (SHA-256 `c75740fd9cf4632f0902c073627d498df4e5c7574d5fb3a61a578a517305d617`).

- `scripts/parity.py --json` — exit 0: 167/167 byte-exact (zero tolerance), 0 diffs, 0 runtime errors, 0 oracle errors, 38 skipped; per-case SHA-256 entries identical to the superseded `parity-receipt-12b4d74f.json`, only the CPU provenance fields moved.
- `tests/test_parity_receipt.py` at the new pin: passed, including the regeneration check `test_receipt_is_current_when_the_oracle_is_available`, which runs against the live sibling at `b61b658399f1`.

### Source-lock sync, 2026-09-27 (noisemaker-for-cpu `7a824744cb56`..`dedfd07c24f8`)

Range audit of the sibling noisemaker-for-cpu `7a824744cb563f2280811f04e5a49f6792ed319d..dedfd07c24f80d9b0adddf912a4224ce6c1d795f` against a fresh clone (`git clone https://github.com/noisefactorllc/noisemaker-for-cpu.git`, checkout `dedfd07c24f80d9b0adddf912a4224ce6c1d795f`): a single commit that bumps the upstream source lock to noisemaker@`12b4d74fb4f28d5f00bb1dde107fa8673814d8b9` (digest `e371a1650d1ace9462a20ecf4e4f0902e5135b4772e8a9abbc8d2c037beebf59`, manifest digest `8bb68100f40db4955c4544507eb6049b1e31a0887828196b48e67d5cd8c5f218`). The committed pinned-source manifest diff shows the only changed upstream files are `shaders/src/runtime/pipeline.js` and a new `shaders/src/runtime/preflight.js` (static WebGL2/WebGPU authorability and device-limit prediction, plus a delegating `mrtFormatBytes`/read-only `preflight()` refactor — GPU-host machinery the -cpu port and this port do not contain); `shaders/effects` is byte-identical to the prior pin, so the ported effect catalog is byte-identical and no -python source or bundle change applies. Port per repo convention: `tests/test_parity.py` source-lock assertions advanced to `12b4d74f...`/`e371a165...`; parity receipt (the node-free replay fixture) regenerated with the node oracle CLI against the sibling checkout at `dedfd07c24f8` (tree `32960595cacf42bd89f108ffeab0580c91b96c4f`) as `tests/data/parity-receipt-12b4d74f.json`, replacing `parity-receipt-7443f6e6.json`; its `byteExact` (167/167 effects, zero tolerance), settings, and counts are identical to the superseded receipt — only the CPU provenance fields moved. No gap closed.

Reproduction (requires network, node, and the sibling clone): `git clone https://github.com/noisefactorllc/noisemaker-for-cpu.git && git -C noisemaker-for-cpu checkout dedfd07c24f80d9b0adddf912a4224ce6c1d795f && git -C noisemaker-for-cpu rev-parse 'HEAD^{tree}'` (expect `32960595cacf42bd89f108ffeab0580c91b96c4f`); `git -C noisemaker-for-cpu diff --name-only 7a824744cb563f2280811f04e5a49f6792ed319d..dedfd07c24f80d9b0adddf912a4224ce6c1d795f -- shaders/effects` (expect no output); the sibling's committed source lock at that revision reads `PINNED_UPSTREAM_REVISION = '12b4d74fb4f28d5f00bb1dde107fa8673814d8b9'` / `PINNED_SOURCE_DIGEST = 'e371a1650d1ace9462a20ecf4e4f0902e5135b4772e8a9abbc8d2c037beebf59'`. Then `NOISEMAKER_CPU_DIR=<sibling> scripts/parity.py --json /tmp/receipt.json` and compare `byteExact` with the committed receipt (only the `cpu` provenance block may differ).

Environment: Linux x86_64 container, Python 3.11.2, NumPy 2.5.3, node 26.5.1; sibling oracle `NOISEMAKER_CPU_DIR` at `dedfd07c24f80d9b0adddf912a4224ce6c1d795f`, upstream pin `12b4d74fb4f28d5f00bb1dde107fa8673814d8b9`, source digest `e371a1650d1ace9462a20ecf4e4f0902e5135b4772e8a9abbc8d2c037beebf59`, tree `32960595cacf42bd89f108ffeab0580c91b96c4f`.

- `scripts/parity.py --json` — exit 0: 167/167 byte-exact (zero tolerance), 0 diffs, 0 runtime errors, 0 oracle errors, 38 skipped; per-case SHA-256 entries identical to the superseded `parity-receipt-7443f6e6.json`, only the CPU provenance fields moved.
- `tests/test_parity_receipt.py` at the new pin: 4 passed (including the regeneration check `test_receipt_is_current_when_the_oracle_is_available`, which now runs against the live sibling at `dedfd07c24f8` instead of skipping).

### Source-lock sync, 2026-09-27 (noisemaker-for-cpu `4b590d2f7f60`..`7a824744cb56`)

Range audit of the sibling noisemaker-for-cpu `4b590d2f7f607a2788a5bc7675288ec166d0b633..7a824744cb563f2280811f04e5a49f6792ed319d` against a fresh clone (`git clone https://github.com/noisefactorllc/noisemaker-for-cpu.git`, checkout `7a824744cb563f2280811f04e5a49f6792ed319d`): 6 commits — `7145223`/`12db707`/`901bbd9`/`64d7ea4` are audit/docs records and CPU-side test characterization; `9683091` bumps the upstream source lock to noisemaker@`7443f6e6180300a45c5b97608459e5094504659d` (digest `e1ffce78499ae9a3994f3035e0f0e1fd8ca1098a9511e013fa444a5177eb523b`) with `shaders/effects` byte-identical to the prior pin (the committed pinned-source manifest diff in that repo shows the only changed upstream files are `shaders/src/lang/*` — a `predictReplacement`/preflight layer on upstream `replaceEffect` mutation APIs that neither the -cpu port nor this port contains); `7a82474` (GAP-006) is docs/packaging only (`package.json` `files`, README, audit records). No `shaders/effects` entry changed, so the ported effect catalog is byte-identical and no -python source or bundle change applies. Port per repo convention: `tests/test_parity.py` source-lock assertions advanced to `7443f6e6...`/`e1ffce78...`; node-free parity receipt regenerated against the sibling checkout at `7a824744cb56` (tree `7c68f12928719dc4e841971ac28d3f3db7e28e73`) as `tests/data/parity-receipt-7443f6e6.json`, replacing `parity-receipt-6a0af04d.json`; its `byteExact` (167/167 effects, zero tolerance), settings, and counts are identical to the superseded receipt — only the CPU provenance fields moved. No gap closed.

Environment: Linux x86_64 container, Python 3.11.2, NumPy 2.5.3, node 26.5.1; sibling oracle `NOISEMAKER_CPU_DIR` at `7a824744cb563f2280811f04e5a49f6792ed319d`, upstream pin `7443f6e6180300a45c5b97608459e5094504659d`, source digest `e1ffce78499ae9a3994f3035e0f0e1fd8ca1098a9511e013fa444a5177eb523b`, tree `7c68f12928719dc4e841971ac28d3f3db7e28e73`.

- `scripts/parity.py --json` — exit 0: 167/167 byte-exact (zero tolerance), 0 diffs, 0 runtime errors, 0 oracle errors, 38 skipped; per-case SHA-256 entries identical to the superseded `parity-receipt-6a0af04d.json`, only the CPU provenance fields moved.
- `tests/test_parity_receipt.py` at the new pin: 4 passed (including the regeneration check `test_receipt_is_current_when_the_oracle_is_available`, which now runs against the live sibling at `7a824744cb56` instead of skipping).

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
Full sweep results (audit evidence `evidence-audit-20260925-090206/parity-results.json`). Independent programs and channel counts (audit evidence `evidence-audit-20260925-090206/independent-comparisons.json`).

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
Current parameter manifests and shader hashes (audit evidence `evidence-audit-20260925-090206/authority-comparison-retry.json`). Filtering cases (audit evidence `evidence-audit-20260925-090206/landscape-valid-choices.json`).

### Parity and authority reconciliation, 2026-09-27

Environment: Linux x86_64 container, Python 3.13.13, NumPy 2.5.3, node 26.5.1. Port candidate at the publication commit carrying this row (base `77d47c583663b4b6e8f6e9297d6e906e4f3ca9cb`). Sibling oracle: noisemaker-for-cpu at `4b590d2f7f607a2788a5bc7675288ec166d0b633` (tree `3cc6f65be52ac09cc868eb1656c188f0693952f8`), upstream pin `6a0af04d3c4f345ffab5e9f8e54e532216b4cdaa`, source digest `6315004fe71950c4d687906ed81243bd85b3c3d2c2d171cd06675ac23ac2820a`.

| Gate | Expected | Executed | Exact passes | Mismatches | Errors | Skips or missing |
|---|---|---|---|---|---|---|
| Existing default image sweep | 205 catalog effects | 167 | 167 | 0 | 0 | 38 excluded from this harness's context |
| Exclusion-class DSL coverage | 38 | 38 | 38 | 0 | 0 | 0 |
| Current landscape filtering choices | 2 | 2 | 2 | 0 | 0 | 0 |
| Authority program GLSL vs bundle lock | 294 | 294 | 294 | 0 | 0 | 0 |
| Authority parameter manifests | 205 | 205 | 205 | 0 | 0 | 0 |
| Authority effect inventory | 210 IDs | 210 | 205 targeted | 0 | 0 | 5 documented non-targeted IDs |

Commands and results:

- `NOISEMAKER_CPU_DIR=<sibling checkout> PYTHONPATH=src .venv/bin/python scripts/parity.py --json parity-current.json` — exit 0: 167/167 byte-exact (zero tolerance), 0 diffs, 0 runtime errors, 0 oracle errors, 38 skipped. The regenerated JSON is equal to the committed node-free receipt `tests/data/parity-receipt-6a0af04d.json` (same counts, same per-case oracle and port SHA-256 entries).
- `NOISEMAKER_CPU_DIR=<sibling checkout> .venv/bin/python -m pytest -q -p no:cacheprovider` — exit 0: **340 passed, 0 skipped** in 16m20s (prior full-suite baseline 337 passed at the 2026-09-26 sync; the delta is the three added cases: two `renderLandscape3d` filtering choices and one `heightmap3d` volume-generator case, all node-oracle byte-parity).
- Landscape probes (both engines, 8×8, seed 1, time 0.25): `noise3d(volumeSize: 4, seed: 0).renderLandscape3d(volumeSize: 4, filtering: 0 | 1).write(o0)\nrender(o0)` — Python renders both choices and each matches the oracle's PNG at maximum absolute RGBA8 difference 0. These probes are committed as `test_landscape3d_filtering_byte_parity`; `synth3d/heightmap3d` was added to `test_volume_generator_render3d_byte_parity` (maxdiff 0).
- Authority reconciliation, immutable inputs: manifest for exact CDN build `1.0.190` has SHA-256 `05c4d7b7744837ae90a3bb4c89e5403ff09448a74d9d7e824abb3d719ad3314e` and is byte-identical to the rolling `1.0` manifest. With `NM_SHADER_VERSION=1.0.190`, fetching all 205 targeted effects from the CDN and hashing each program's GLSL (`sha256(glsl.strip())`, the same function `transpiler/build.py` records in `bundle-lock.json`) matches all 294 lock entries, finds zero lock entries without an authority program, and finds zero parameter-manifest differences (post `shared_enums` normalization, same as the builder). The formerly differing programs `classicNoisedeck/glitch:glitch`, `classicNoisedeck/noise:noise`, and `render/renderLandscape3d:landscape` now match authority.
- Denominator: 167 (image sweep) + 38 (exclusion-class DSL cases, all `_max_diff == 0`) = 205 targeted effects, each with at least one zero-tolerance oracle-matched, source-bound comparison. The 5 remaining authority IDs (`render/meshLoader`, `render/meshRender`, `synth/roll`, `synth/scope`, `synth/spectrum`) are documented non-targets in `transpiler/cdn.py`. 167 + 38 + 5 = 210 = the authority manifest inventory.
- Standing limits: the tested contexts are fixed (image sweep 8×8 at defaults; DSL chains at 2×2/8×8/16×16, volumeSize 4); the complete parameter matrix, external-input shapes, and host versions are not re-measured here; node-gated tests execute only when the sibling oracle checkout is present.

### Daily review, 2026-09-25

The daily review inspected worker audit `audit-20260925-090206` and post-worker commit `49d8e51ec4b71104dc03728c84c60cae3e2857d3`.
All 64 CLI, DSL, and output-runtime tests pass at current source `49d8e51ec4b71104dc03728c84c60cae3e2857d3`.
The sibling source lock test passes against `/workspace/repos/noisemaker-for-cpu`.
The review independently reproduced GAP-004: the built wheel contains 328 files and zero JSON files, omitting `bundle/metadata.json`.
The review checked GAP-005: four-component solid color produces alpha difference 179 against the CPU oracle, and feedback diverges by one byte.
Exact reviewed-source CI contains zero runs and zero checks.
Full installed-host and platform qualification remains incomplete.
GAP-001 remains open, and the suite leaves current full rendered parity unverified.
Earlier raw evidence (audit evidence `review-20260925-053200/python-current-tests.json`).

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
| `classicNoisedeck/bitEffects` | yes | exact default sweep (§3, 2026-09-27) |
| `classicNoisedeck/caustic` | yes | exact default sweep (§3, 2026-09-27) |
| `classicNoisedeck/cellNoise` | yes | exact default sweep (§3, 2026-09-27) |
| `classicNoisedeck/cellRefract` | yes | exact default sweep (§3, 2026-09-27) |
| `classicNoisedeck/coalesce` | yes | exact default sweep (§3, 2026-09-27) |
| `classicNoisedeck/colorLab` | yes | exact default sweep (§3, 2026-09-27) |
| `classicNoisedeck/composite` | yes | exact default sweep (§3, 2026-09-27) |
| `classicNoisedeck/effects` | yes | exact default sweep (§3, 2026-09-27) |
| `classicNoisedeck/fractal` | yes | exact default sweep (§3, 2026-09-27) |
| `classicNoisedeck/glitch` | yes | exact default sweep (§3, 2026-09-27) |
| `classicNoisedeck/kaleido` | yes | exact default sweep (§3, 2026-09-27) |
| `classicNoisedeck/lensDistortion` | yes | exact default sweep (§3, 2026-09-27) |
| `classicNoisedeck/moodscape` | yes | exact default sweep (§3, 2026-09-27) |
| `classicNoisedeck/noise` | yes | exact default sweep (§3, 2026-09-27) |
| `classicNoisedeck/noise3d` | yes | exact default sweep (§3, 2026-09-27) |
| `classicNoisedeck/refract` | yes | exact default sweep (§3, 2026-09-27) |
| `classicNoisedeck/shapeMixer` | yes | exact default sweep (§3, 2026-09-27) |
| `classicNoisedeck/shapes` | yes | exact default sweep (§3, 2026-09-27) |
| `classicNoisedeck/shapes3d` | yes | exact default sweep (§3, 2026-09-27) |
| `classicNoisedeck/splat` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/adjust` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/bloom` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/blur` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/bulge` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/celShading` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/channel` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/chroma` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/chromaticAberration` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/chrome` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/clouds` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/colorReplace` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/convolutionFeedback` | yes | exact DSL chain (§3, 2026-09-27) |
| `filter/corrupt` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/craquelure` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/crt` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/degauss` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/deriv` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/directionalBlur` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/dither` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/edge` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/emboss` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/extrude` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/feedback` | yes | exact DSL chain (§3, 2026-09-27) |
| `filter/fibers` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/flipMirror` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/fxaa` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/glowingEdge` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/glyphMap` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/grade` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/grain` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/grime` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/halftone` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/hatch` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/highPass` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/historicPalette` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/invert` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/lens` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/lensFlare` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/lensWarp` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/lightLeak` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/lighting` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/lowPoly` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/median` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/morphology` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/mosaicTiles` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/motionBlur` | yes | exact DSL chain (§3, 2026-09-27) |
| `filter/normalMap` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/normalize` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/octaveWarp` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/oilPaint` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/osd` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/outline` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/palette` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/parallax` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/patchwork` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/photocopy` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/pinch` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/pixelSort` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/pixels` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/plasticWrap` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/polar` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/pondRipples` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/posterize` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/prismaticAberration` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/reindex` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/relief` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/repeat` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/reverb` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/ridge` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/rotate` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/scale` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/scanlineError` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/scatter` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/scratches` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/scroll` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/seamless` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/sharpen` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/simpleAberration` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/sine` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/skew` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/smooth` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/smoothstep` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/snow` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/sobel` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/spatter` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/spinBlur` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/spiral` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/spookyTicker` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/stamp` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/step` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/stipple` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/strayHair` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/strokes` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/temporalAberration` | yes | exact DSL chain (§3, 2026-09-27) |
| `filter/tetraColorArray` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/tetraCosine` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/text` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/texture` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/threshold` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/tile` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/tint` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/translate` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/tunnel` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/unsharpMask` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/vaseline` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/vignette` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/warp` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/watercolor` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/waves` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/wind` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/wobble` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/wormhole` | yes | exact default sweep (§3, 2026-09-27) |
| `filter/zoomBlur` | yes | exact default sweep (§3, 2026-09-27) |
| `filter3d/flow3d` | yes | exact DSL chain (§3, 2026-09-27) |
| `filter3d/palette3d` | yes | exact DSL chain (§3, 2026-09-27) |
| `mixer/alphaMask` | yes | exact default sweep (§3, 2026-09-27) |
| `mixer/applyMode` | yes | exact default sweep (§3, 2026-09-27) |
| `mixer/blendMode` | yes | exact default sweep (§3, 2026-09-27) |
| `mixer/cellSplit` | yes | exact default sweep (§3, 2026-09-27) |
| `mixer/centerMask` | yes | exact default sweep (§3, 2026-09-27) |
| `mixer/channelCombine` | yes | exact default sweep (§3, 2026-09-27) |
| `mixer/distortion` | yes | exact default sweep (§3, 2026-09-27) |
| `mixer/focusBlur` | yes | exact default sweep (§3, 2026-09-27) |
| `mixer/mashup` | yes | exact default sweep (§3, 2026-09-27) |
| `mixer/patternMix` | yes | exact default sweep (§3, 2026-09-27) |
| `mixer/shadow` | yes | exact default sweep (§3, 2026-09-27) |
| `mixer/shapeMask` | yes | exact default sweep (§3, 2026-09-27) |
| `mixer/split` | yes | exact default sweep (§3, 2026-09-27) |
| `mixer/thresholdMix` | yes | exact default sweep (§3, 2026-09-27) |
| `mixer/uvRemap` | yes | exact default sweep (§3, 2026-09-27) |
| `points/attractor` | yes | exact DSL chain (§3, 2026-09-27) |
| `points/buddhabrot` | yes | exact DSL chain (§3, 2026-09-27) |
| `points/dla` | yes | exact DSL chain (§3, 2026-09-27) |
| `points/flock` | yes | exact DSL chain (§3, 2026-09-27) |
| `points/flow` | yes | exact DSL chain (§3, 2026-09-27) |
| `points/heightGrid` | yes | exact default sweep (§3, 2026-09-27) |
| `points/hydraulic` | yes | exact DSL chain (§3, 2026-09-27) |
| `points/lenia` | yes | exact DSL chain (§3, 2026-09-27) |
| `points/life` | yes | exact DSL chain (§3, 2026-09-27) |
| `points/physarum` | yes | exact DSL chain (§3, 2026-09-27) |
| `points/physical` | yes | exact DSL chain (§3, 2026-09-27) |
| `render/loopBegin` | yes | exact DSL chain (§3, 2026-09-27) |
| `render/loopEnd` | yes | exact DSL chain (§3, 2026-09-27) |
| `render/meshLoader` | no | not targeted (documented exclusion) |
| `render/meshRender` | no | not targeted (documented exclusion) |
| `render/pointsBillboardRender` | yes | exact DSL chain (§3, 2026-09-27) |
| `render/pointsEmit` | yes | exact DSL chain (§3, 2026-09-27) |
| `render/pointsRender` | yes | exact DSL chain (§3, 2026-09-27) |
| `render/render3d` | yes | exact DSL chain (§3, 2026-09-27) |
| `render/renderCubemap3d` | yes | exact DSL chain (§3, 2026-09-27) |
| `render/renderCubemapSurface` | yes | exact DSL chain (§3, 2026-09-27) |
| `render/renderLandscape3d` | yes | exact DSL chain (§3, 2026-09-27) |
| `render/renderLit3d` | yes | exact DSL chain (§3, 2026-09-27) |
| `synth/bitwise` | yes | exact default sweep (§3, 2026-09-27) |
| `synth/cell` | yes | exact default sweep (§3, 2026-09-27) |
| `synth/cellularAutomata` | yes | exact DSL chain (§3, 2026-09-27) |
| `synth/curl` | yes | exact default sweep (§3, 2026-09-27) |
| `synth/gabor` | yes | exact default sweep (§3, 2026-09-27) |
| `synth/gradient` | yes | exact default sweep (§3, 2026-09-27) |
| `synth/julia` | yes | exact default sweep (§3, 2026-09-27) |
| `synth/mandala` | yes | exact default sweep (§3, 2026-09-27) |
| `synth/mandelbrot` | yes | exact default sweep (§3, 2026-09-27) |
| `synth/media` | yes | exact default sweep (§3, 2026-09-27) |
| `synth/mnca` | yes | exact DSL chain (§3, 2026-09-27) |
| `synth/modPattern` | yes | exact default sweep (§3, 2026-09-27) |
| `synth/navierStokes` | yes | exact DSL chain (§3, 2026-09-27) |
| `synth/newton` | yes | exact default sweep (§3, 2026-09-27) |
| `synth/noise` | yes | exact default sweep (§3, 2026-09-27) |
| `synth/osc2d` | yes | exact default sweep (§3, 2026-09-27) |
| `synth/pattern` | yes | exact default sweep (§3, 2026-09-27) |
| `synth/perlin` | yes | exact default sweep (§3, 2026-09-27) |
| `synth/polygon` | yes | exact default sweep (§3, 2026-09-27) |
| `synth/reactionDiffusion` | yes | exact DSL chain (§3, 2026-09-27) |
| `synth/remap` | yes | exact default sweep (§3, 2026-09-27) |
| `synth/roll` | no | not targeted (documented exclusion) |
| `synth/sacredGeometry` | yes | exact default sweep (§3, 2026-09-27) |
| `synth/scope` | no | not targeted (documented exclusion) |
| `synth/shape` | yes | exact default sweep (§3, 2026-09-27) |
| `synth/solid` | yes | exact default sweep (§3, 2026-09-27) |
| `synth/spectrum` | no | not targeted (documented exclusion) |
| `synth/subdivide` | yes | exact default sweep (§3, 2026-09-27) |
| `synth/testPattern` | yes | exact default sweep (§3, 2026-09-27) |
| `synth3d/cell3d` | yes | exact DSL chain (§3, 2026-09-27) |
| `synth3d/cellularAutomata3d` | yes | exact DSL chain (§3, 2026-09-27) |
| `synth3d/flythrough3d` | yes | exact DSL chain (§3, 2026-09-27) |
| `synth3d/fractal3d` | yes | exact DSL chain (§3, 2026-09-27) |
| `synth3d/heightmap3d` | yes | exact DSL chain (§3, 2026-09-27) |
| `synth3d/noise3d` | yes | exact DSL chain (§3, 2026-09-27) |
| `synth3d/reactionDiffusion3d` | yes | exact DSL chain (§3, 2026-09-27) |
| `synth3d/shape3d` | yes | exact DSL chain (§3, 2026-09-27) |

## 4. Evidence

### Worker audit, 2026-09-25

The environment is Python 3.14.5 on macOS arm64. NumPy supplies the actual CPU renderer.
Runtime versions (audit evidence `evidence-audit-20260925-090206/runtime.json`) records Python, NumPy, Node, and operating-system versions.

The unchanged image suite returns exit 0: 167/167 exact comparisons, zero mismatches, zero runtime errors, and zero oracle errors.
It skips 38 iterated or typed effects. These exclusions remain qualification gaps in this gate.
The README's 169/36 counts do not match this source's 167/38 inventory.
The suite uses 8×8 images, seed 1, time 0.25, and default parameters. Its numerical threshold is zero byte difference.
A wrapper redirects temporary PNG paths and captures local result variables. It does not change comparisons or exclusions.
Literal command and source identities (audit evidence `evidence-audit-20260925-090206/parity-command.json`). Every executed and skipped ID (audit evidence `evidence-audit-20260925-090206/parity-results.json`).

Independent public DSL probes use 48×32 images, seed 17, and time 0.375.
The noise/invert chain matches exactly across 6,144 channels.
Four-component solid color produces alpha 76 instead of CPU alpha 255 across 1,536 pixels. Maximum difference: 179.
A three-iteration feedback chain differs by one byte in five of 6,144 channels. It fails strict equality.
RGB and explicit-alpha controls match. These controls isolate the solid discrepancy to four-component color interpretation.
Both valid landscape filtering choices succeed in CPU and fail in Python with an unknown-parameter diagnostic.
Nondefault comparisons (audit evidence `evidence-audit-20260925-090206/independent-comparisons.json`). Alpha controls (audit evidence `evidence-audit-20260925-090206/alpha-controls.json`). Valid landscape choices (audit evidence `evidence-audit-20260925-090206/landscape-valid-choices.json`).

Current immutable shader comparison finds 291 matching program hashes and three differences among 294 compared programs.
Differences: `classicNoisedeck/glitch:glitch`, `classicNoisedeck/noise:noise`, and `render/renderLandscape3d:landscape`.
The landscape parameter manifest adds `filtering`. Palette metadata differences reflect the build-time insertion of enum choices.
These differences do not establish equivalent behavior. The upstream language implementation also changed after the CPU pin.
Shader and parameter inventories (audit evidence `evidence-audit-20260925-090206/authority-comparison-retry.json`). Upstream source difference (audit evidence `evidence-audit-20260925-090206/upstream-diff.json`).

The complete test run collected 274 cases: 267 passed, two failed, and five skipped because Python HTTPS certificate validation failed.
The 74 CPU parity tests passed: 50 exact-byte cases, 22 tolerance cases, one float32 equality case, and one source-lock check.
A targeted immutable-cache retry passed all 15 CDN and affected transpiler tests. All 274 distinct cases passed across these runs.
The initial run returned exit 1. The targeted retry returned exit 0. This is not a single clean full-suite result.
Full command (audit evidence `evidence-audit-20260925-090206/pytest-command.json`). Raw output (audit evidence `evidence-audit-20260925-090206/pytest.log`). Retry command and output (audit evidence `evidence-audit-20260925-090206/network-retry.json`).
Per-case parity contracts (audit evidence `evidence-audit-20260925-090206/dsl-parity-contracts.json`).
Verified HTTPS downloads through curl supplied immutable `1.0.180` bytes to the unchanged parser. All 13 CDN tests then passed.
The earlier malformed landscape probe used `linear`. Both renderers rejected it. It does not establish a supported-case defect.
Initial authority probe (audit evidence `evidence-audit-20260925-090206/authority-comparison.json`). Pinned CDN retry (audit evidence `evidence-audit-20260925-090206/cdn-cached-tests.json`).

The editable source installation produces a 32×24 curl image, a changed 48×32 image, filtered input, and three H.264 frames.
The public library entry point also produces a 32×24 PNG. PNG decoding and ffprobe check the outputs.
Invalid effect input returns exit 2. Corrected input returns exit 0.
SIGINT returns `Aborted!` and preserves the existing output file. Invalid input also preserves that file.
The literal README 512×512 example exceeded 180 seconds under concurrent test load. This is a bounded observation, not a performance benchmark.
The audit removed both private installation targets. Upgrade behavior, Python 3.11, other operating systems, and sustained resource use remain unverified.
Installed commands (audit evidence `evidence-audit-20260925-090206/bounded-developer-workflows.json`). Output measurements (audit evidence `evidence-audit-20260925-090206/output-verification.json`). Animation (audit evidence `evidence-audit-20260925-090206/animation-verification.json`).
Cancellation (audit evidence `evidence-audit-20260925-090206/cancellation.json`). README timeout (audit evidence `evidence-audit-20260925-090206/readme-512-timeout.json`). Private removal (audit evidence `evidence-audit-20260925-090206/private-removal.json`).

The served kit produces a 48×32 solid image. Invalid DSL fails, and corrected noise/invert DSL produces another image.
The failed wheel remains a distinct distribution defect despite successful editable and served-kit workflows.
Headless rendering has no editor controls. The audit checked CLI diagnostics and cancellation through public entry points.
Served entry point (audit evidence `evidence-audit-20260925-090206/served-workflows.json`). Wheel build (audit evidence `evidence-audit-20260925-090206/build-command.json`). Wheel inventory (audit evidence `evidence-audit-20260925-090206/wheel-inventory.json`).

Exact reviewed-source CI contains zero runs and zero checks. No existing workflow enforces source-update parity.
The served source's export dispatch `35963990201` passed. Downstream release `35963999103` passed 83 checks without skips and identifies that served source.
Its checks include an actual staged-kit PNG render.
Release packaging checks do not establish full port parity or current wheel correctness.
Exact-source runs (audit evidence `evidence-audit-20260925-090206/source-ci.json`). Exact-source checks (audit evidence `evidence-audit-20260925-090206/source-checks.json`). Release log (audit evidence `evidence-audit-20260925-090206/kit-release.log`).

Official references, accessed 2026-09-25: [Python packaging guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/) and [Python version status](https://devguide.python.org/versions/).
The packaging guide distinguishes source archives from installable wheels. This audit checked both formats and retained the declared Python 3.11 minimum.

Review CI boundary: No workflow run exists at the inspected source SHA. A passing export dispatch does not qualify rendered parity. Current complete-render enforcement remains an open verification requirement. Exact-source responses and workflows (audit evidence `review-20260925-053200/noisemaker-for-python-remote-evidence.json`).

Bounded test evidence (audit evidence `evidence-20260924-remaining-gap-documents/python-tests-retry.json`). [Exact-source Actions](https://github.com/noisefactorllc/noisemaker-for-python/actions?query=head_sha%3A70c03da6944be1319ccc249fd9646dd9df05e86c).
This run evidence (audit evidence `evidence-20260924-remaining-gap-documents`) retains commands, exit codes, source identities, and distribution metadata.
Official ecosystem reference: [Current Python Packaging User Guide, accessed 2026-09-24](https://packaging.python.org/en/latest/tutorials/packaging-projects/).
Source CI, export dispatch, artifact delivery, and rendered parity are separate evidence dimensions.
A successful dispatch or unit-test summary does not establish a full rendered gate.

## 5. Open compatibility limits

Current order: [GAP-001](COMPLETION_GAPS.md#gap-001-current-authority-and-parity-qualification) closed 2026-09-27 (authority reconciled against immutable CDN `1.0.190`; 167/167 default image comparisons and all 38 exclusion-class DSL chains byte-exact against the pinned oracle; both landscape filtering choices match). Next: [GAP-003](COMPLETION_GAPS.md#gap-003-distribution-and-release-qualification) exact-source CI requires workflow authority this implementation job does not hold.
Require wheel-only output, exact recorded comparisons, and complete denominators.

Next bounded check: Add the exact-source CI gate that runs the suite — including the node-free parity receipt — and wheel/sdist artifact verification (workflow authority required). Retain skips and missing effects toward the 210-ID inventory.
See the stable entries in [completion gaps](COMPLETION_GAPS.md).

See [GAP-001 and the complete gap register](COMPLETION_GAPS.md#4-known-gaps) for evidence, dependencies, and acceptance criteria.

1. Reconcile the current authority and complete case inventory, including parameters, inputs, stateful frames, and host versions.
2. Run the existing actual-renderer suite without skip options. Record every missing, failed, refused, or timed-out case.
3. Verify installation, useful output, errors, recovery, upgrades, and removal with the actual distribution.
4. Inspect exact-source CI and retain artifact hashes. Keep unresolved qualification failed or unverified.

All eligible ports have equal priority. Full parity and zero skipped cases remain the goal.
Implementation corrections remain with the separate job. This report does not advance the parity checkpoint.

## 6. History

2026-09-27 parity and authority reconciliation at the candidate commit carrying this entry (base `77d47c583663b4b6e8f6e9297d6e906e4f3ca9cb`): GAP-001 closed — 167/167 default image comparisons byte-exact against the pinned oracle `4b590d2f7f607a2788a5bc7675288ec166d0b633`; all 38 image-harness exclusions each covered by a committed zero-byte DSL chain case (added `renderLandscape3d` filtering isosurface/voxel and `synth3d/heightmap3d`); authority reconciliation vs immutable CDN `1.0.190` shows 294/294 program GLSL hashes and 0 parameter-manifest differences; both landscape filtering choices match the oracle exactly (§3, "Parity and authority reconciliation, 2026-09-27").

2026-09-25 daily review at `49d8e51ec4b71104dc03728c84c60cae3e2857d3`: reviewed worker audit `audit-20260925-090206` (published in `4ff7b03247b59cead0b63a7ee3a7b5697f7bf58e`).
Verified post-audit commit `49d8e51ec4b71104dc03728c84c60cae3e2857d3` in `tests/test_parity.py`.
Independently reproduced GAP-004 missing metadata in built wheel. Checked GAP-005 nondefault numerical parity differences.
Five open gaps remain. Zero closures. Full parity and release readiness remain unqualified.

2026-09-25 worker at `912e6a9aac32c668a5242b8d52aa4415ca3a848e`: 167 exact default comparisons, 38 image-gate exclusions, two independent numerical failures, and two landscape rejections.
Served kit hashes and reproduction pass. Candidate wheel first render fails. No full-parity or release approval follows.

2026-09-25 daily review at `93b8b141d21a7c853a89131166147c8337109144`: source freshness and bounded evidence reviewed. Open qualification limits retained. Retained review evidence (audit evidence `review-20260925-053200/python-current-tests.json`). No new closure claimed.

| Date | Source | Result | Change |
|---|---|---|---|
| 2026-09-25 | `49d8e51ec4b71104dc03728c84c60cae3e2857d3` | Full qualification unverified | Reviewed audit-20260925-090206 and post-worker parity test update. Reproduced GAP-004. Zero closures. |
| 2026-09-25 | `912e6a9aac32c668a5242b8d52aa4415ca3a848e` | Full qualification unverified | 167 exact default passes, 38 skips, 2 independent numerical failures, 2 landscape rejections. Wheel fails. |
| 2026-09-24 | `70c03da6944be1319ccc249fd9646dd9df05e86c` | Full qualification unverified | Created the requested maintained compatibility report. Preserved historical evidence and open gaps. |

Run: `20260924-remaining-gap-documents`. Later audits and reviews update this report with source-bound results.
