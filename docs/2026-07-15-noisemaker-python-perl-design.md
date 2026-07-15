# noisemaker-python & noisemaker-perl — Design

**Date:** 2026-07-15
**Status:** Draft for review
**Author:** Claude (with Alex)

## 1. Goal

Produce two native ports of the `noisemaker-cpu` engine:

- **`noisemaker-python`** — a new Python package.
- **`noisemaker-perl`** — a **total replacement** of the venerable `Math::Fractal::Noisemaker` CPAN module (v0.105, 2011), keeping the namespace and bumping to **v1.000**, restructured into a proper multi-file distribution.

Both render **all 167 eligible effects** by **transpiling the upstream GLSL directly to native code** (Python source, Perl source) — an automated, re-runnable transpile, **not** three hand-maintained copies of effect logic. Everything is **local-only**: no PyPI/CPAN publish, no `git push`, no deploys.

## 2. Scope

**In scope:** the exact 167-effect eligible catalog already defined by noisemaker-cpu:
- 18 `classicNoisedeck`, 112 `filter`, 15 `mixer`, 22 `synth` (~208 fragment programs).
- Full engine: CSL/GLSL kernel execution, the **Polymorphic DSL**, multi-pass render graphs, Surface/PNG I/O, and a CLI.

**Out of scope (inherited exclusions):** the categories noisemaker-cpu already excludes — 3D (`filter3d/*`, `synth3d/*`, `render/*`), particles (`points/*`), render-loop control, and 8 stateful + 3 reactive effects (navierStokes, reactionDiffusion, mnca, cellularAutomata, feedback, motionBlur, roll/scope/spectrum, …). **This exclusion is load-bearing for tractability:** the hardest GLSL features in the corpus (MRT with up to 4 outputs, `type:"compute"` agent simulations, ping-pong state) live almost entirely in these excluded categories. Our 167 avoid them.

**Explicitly not doing:** porting noisemaker-cpu's *generated JS kernels* by hand; maintaining effect logic in three languages; building a new GLSL parser (we reuse a mature one).

## 3. Locked decisions (from Alex)

| Decision | Choice |
|---|---|
| Coverage | **All 167 eligible effects.** |
| Transpile source | **Upstream GLSL directly** (`../noisemaker/shaders/effects/**/glsl/*.glsl`, pinned rev `dc67827…`). |
| Transpiler strategy | **Fresh Python/Perl backends** on the reused `glsl-tokenizer`+`glsl-parser`+`prepr` front-end + reused `glsl-normalize.js`. (Reject fork-and-retarget of glsl-transpiler.) |
| Execution | **Runtime codegen + cache**: emit native kernel source, compile at runtime (Python `compile`/`exec`, Perl string `eval`) into callables, LRU-cache with size-bounded smart eviction. |
| Speed sequencing | **Correctness first** (byte-parity across all 167), **then** a compiled fast backend. |
| Perl identity | **Keep `Math::Fractal::Noisemaker`, bump to v1.000**, multi-file dist, `make-noise` CLI on the new engine. |
| Where the transpiler lives | **Inside noisemaker-cpu** (JS) — "provide a bundle." Alex authorized editing cpu. |

## 4. Architecture

Three parts: a **transpiler+bundler** in noisemaker-cpu, a **native runtime+engine** per target language, and a **cross-language parity harness**.

```
upstream GLSL (read-only)                 noisemaker-cpu (edit: additive)
  shaders/effects/**/glsl/*.glsl   ─┐      scripts/bundle/
  shaders/effects/**/definition.js ─┼──►   ├─ reuse: glsl-tokenizer + glsl-parser + prepr
                                    │       ├─ reuse: src/csl/glsl-normalize.js (GLSL→GLSL)
                                    │       ├─ NEW:  backend-python.js  (AST → Python source)
                                    │       ├─ NEW:  backend-perl.js    (AST → Perl source)
                                    │       └─ NEW:  emit bundle/ (metadata JSON + native kernels)
                                    │
                     ┌──────────────┴───────────────┐
                     ▼                               ▼
            noisemaker-python/                noisemaker-perl/
              runtime stdlib (numpy)            runtime stdlib (pack/unpack f32)
              kernel loader (exec+LRU)          kernel loader (eval+LRU)
              render-graph interpreter          render-graph interpreter
              DSL / catalog / Surface / PNG     DSL / catalog / Surface / PNG
              CLI  (noisemaker-cpu)             CLI  (make-noise)
              hand-ported adapters (~11)        hand-ported adapters (~11)
```

### 4.1 Transpiler + bundler (in noisemaker-cpu)

Reuse noisemaker-cpu's existing upstream pipeline (`scripts/upstream/compile-glsl.js`, `inventory.js`, `source-lock.js`, `glsl-normalize.js`) up to the AST, then branch into new backends:

1. **Pin & load** — `assertPinnedSource()` guards the upstream revision (unchanged).
2. **Normalize** — `glsl-normalize.js` (reused as-is): strips `#version`/`#ifdef GL_ES`, lowers runtime `#if`/`#define` into `if/else` on uniforms, expands object-like macros textually (249 across 77 files, **all object-like** — no function-like macros), flattens UBO blocks, rewrites `uint`/`uvec*`→`int`/`vec*` and unsigned multiply → a `cpu_umul` GLSL shim, renames shadowing locals, captures `out vec4`.
3. **Parse** — `glsl-tokenizer` + `glsl-parser` → GLSL AST (reused; no fork of glsl-transpiler).
4. **Emit** — new `backend-python.js` / `backend-perl.js` walk the AST (a ~31-node-type dispatch, reimplemented clean per target) and emit native kernel source.

**Backend responsibilities (the real work, per target):**
- **Static type inference + name-mangling** for GLSL overloading (23 sites, e.g. `mod289(vec2)`/`mod289(vec3)` → `mod289_vec2`/`mod289_vec3`). Neither target has compile-time overload resolution.
- **Write-swizzles** (185 sites, `color.rgb = …`, `x12.xy -= i1`): scatter back into the parent vector. Python: a small `Vec` class (or index assignment on numpy views); Perl: explicit setter helpers.
- **32-bit uint wraparound (THE correctness linchpin):** route *all* unsigned arithmetic through runtime helpers that mask explicitly (`umul`, `uadd`, `ushr`, `uxor`, …), never raw operators — Python int is arbitrary-precision, Perl int is 64-bit; neither wraps at 32 bits. The normalizer already redirects `cpu_umul`; the backend extends this to every uint op.
- **Matrices** (mat2/3/4: construct, mat×vec, mat×mat, `[][]` read only — **no** transpose/inverse/compMult anywhere): narrow runtime support.
- **Fixed-size arrays & flat structs** (13 structs, all flat multi-value bundles → dataclass / hash).
- **Derivatives** (`dFdx`/`dFdy`/`fwidth`): the backend marks a kernel `usesDerivatives`; execution is handled at the runtime layer (record/replay quad model — see 4.3), not inside the per-pixel function.
- **Faithful control flow**: keep hard-capped `for` + `if(n>=max) break;` idioms verbatim (GPU loop-bound workaround); don't "optimize."
- **`float(...)` casts** (689 explicit) → coercion; GLSL ES 3.00 is strict so little implicit-promotion inference is needed.

**df64 extended precision** (Dekker/Knuth double-float, ~13 functions in mandelbrot/julia/newton): transpiles like any other GLSL. On CPU we *also* have native float64; keep the transpiled df64 for faithfulness by default (it's what the goldens used), and treat native-float64 substitution as an optional later simplification.

### 4.2 The bundle

The bundler emits a `bundle/` directory (vendored into each port repo — copied, since local-only, so ports are self-contained):

- **`metadata.json`** — language-neutral, from `inventory.js` + `definition.js`: for each of 167 effects — `namespace/func/id/kind`, `params` (type, default, min/max/step, `uniform:` vs `define:`, enum `choices`, `paramAliases`, `ui` hints), `passes[]` (program, inputs→sampler, outputs→texture, MRT `drawBuffers`, `drawMode`, `blend`, `count`, `uniforms`), `textures{}` (name, width/height, format), and compile-time `define` sets. **This topology is not reconstructable from GLSL alone** and must ship with the kernels.
- **`kernels/python/…`** and **`kernels/perl/…`** — the transpiled native kernel source per fragment program. The normalizer lowers *runtime-selectable* `#define` choices into uniform-fed `if/else` branches, so those stay **one function per program**; only genuinely *structural* defines (e.g. array sizes like `majorRecords[REAL_COUNT]`) produce distinct kernel variants. Emit one function per `(program, structural-define-set)`, matching cpu's coverage.
- **`provenance.json`** — pinned upstream revision, bundler version, generation timestamp (passed in, not read from a clock).

Re-running the bundler regenerates everything deterministically. Ports never parse GLSL at runtime — they load native kernel source and runtime-compile it.

### 4.3 Per-language runtime stdlib

Ported once per language from `src/csl/glsl-runtime.js` (544 lines) + `src/runtime/{sampler,texture-format}.js`, validated against the golden vectors in `test/glsl-runtime.test.js`.

**Trivial (direct builtin):** radians/degrees, trig (`atan` = 1-arg or 2-arg atan2), pow/exp/log/sqrt/inversesqrt, abs/sign/floor/ceil/fract/tanh, min/max/clamp/mix/step/smoothstep, length/distance/normalize/reflect/refract, relational family, arithmetic.

**Fidelity-critical (engineer deliberately):**

| Item | Requirement | Python | Perl |
|---|---|---|---|
| float32 truncation (`Math.fround`) after ~every op | GPU float32 emulation | `numpy.float32` or `struct.pack/unpack('f')` helper | `unpack('f<',pack('f<',$x))` |
| `pcg3d`, `hashUint32`, `umul`, `uint32` | bit-exact 32-bit wrap (**#1 risk**) | mask `& 0xFFFFFFFF`, `numpy.uint32` | mask `& 0xFFFFFFFF` |
| `glslMod` | floored `x - y*floor(x/y)`; **not** native `%`/`fmod` | | |
| `round` | ties toward +∞ = `floor(x+0.5)`; **not** Python banker's `round()` | | |
| `dot` | accumulate float64, `fround` **once** at end | | |
| `normalize` | zero-magnitude → all-zero (this file is ground truth, not the spec) | | |
| matrices | column-major mat×mat / mat×vec | | |
| `floatBitsToUint`, `packHalf2x16`/`unpackHalf2x16`, half↔float | byte reinterpret + float16 codec (denormals/inf/nan) | `struct`/`numpy.view` | `pack`/`unpack` |
| **derivatives** (`dFdx`/`dFdy`/`fwidth`) | **record/replay 2×2-quad double-execution** (~70 lines): group pixels into quads, run kernel in record mode capturing call-order-indexed values, finite-difference corners, replay by call index; fallback `1/resolution`. **Largest single runtime item.** | redesign, not transliteration | redesign |
| `texture`/`texelFetch`/`textureSize` | bilinear/nearest + **y-flip** for GL bottom-left origin (flip the integer texel row, not `1-v`); external images linear, internal nearest | port `sampler.js` | port `sampler.js` |
| `textureLod` | currently ignores LOD → just `texture`; match this simplification | | |
| per-pixel pooling | JS GC idiom; ports may skip pooling but must not alias buffers across pixels | | |

**Golden vectors to assert (ground truth):** `pcg3d([1,2,3])==[4204755366,1223881804,1500469937]`; `hashUint32(0x1234abcd)==737574769`; `umul(0xffffffff,374761393)==3920205903`; `glslMod(-1,3)==2`; `uint32(-1)==4294967295`; `float(0xffffffff)==4294967296`; derivative + texture vectors per the test file; `filter/invert [0.2,0.4,0.8,0.5] → [0.80000001,0.60000002,0.19999999,0.5]`.

### 4.4 Per-language engine

Ported from `src/runtime/` + `src/dsl/` + `src/effects/{definition,registry,catalog}.js` + `src/node/png.js` + `bin/noisemaker-cpu.js`:

- **Kernel loader** — load bundled native kernel source, runtime-compile (`exec`/`eval`) into callables, LRU cache keyed by `(program, structural-define-set)` with a byte/size-bounded eviction policy (mirrors cpu's 64 MiB overlay cache idea).
- **Render-graph interpreter** (`renderer.js`, 526 lines): per-effect internal multi-pass sub-graph — named attachments, per-pass **half-float quantization**, `repeat` counts, `blend` accumulation, `drawMode:'points'` special path, one-shot CPU overlays. Sync + optional tile-yielding async.
- **Surface** (RGBA float32, top-down; `/255` linear, no sRGB), **BufferPool**, **sampler**, **pass-runner** (the `fy = height-y-0.5` bottom-left flip lives here), **texture-format** (float16 truncation LUT).
- **Polymorphic DSL** — `tokenize`/`parse`/`compile` (452 lines) → flat render graph; `search` namespace order, `let` partials, positional/named args, `read`/`write`/`render`, compile-time arithmetic/vector-literal folding.
- **Catalog / registry / definition** — built from `bundle/metadata.json`; `normalizeArguments` type-coercion (float/int/bool/color `#hex`/vec/enum/member/palette/surface/string).
- **PNG codec** — faithful port of the zero-dependency `png.js` (encode+decode, all 5 filters incl. Paeth, CRC32, zip-bomb guards). Python: stdlib `zlib`. Perl: `Compress::Zlib`. **Rationale:** keeps deps light and behavior byte-identical, and avoids the old module's heavy `Imager` dependency.
- **CLI** — subcommands `render`/`effect`/`csl`/`effects` + flags (`--width/--height/--time/--seed/--output/--input/--texture/--param/--uniform`). Perl additionally ships `make-noise` (the historical entry point) mapped onto the new engine.

### 4.5 Special hand-ported adapters (~11 per language)

These are hand-written scalar JS in cpu (not GLSL), so they can't be auto-transpiled — each is a parallel worker task, ported faithfully to match cpu bit-for-bit:
`classicNoisedeck/fractal` (Julia/Newton/Mandelbrot dispatch, no generated fallback), `synth/julia` (df64 extended-precision complex, no fallback), `filter/crt` (metalSine range-reduction — the one effect that fails GPU parity even in JS), `filter/snow`, `filter/median` (49-tap half-float quickselect), `filter/palette` + `filter/historicPalette` (cosine/5-stop tables from `canonical-adapter-data`), `filter/pixelSort` + `filter/reindex` (Oklab-lightness), `classicNoisedeck/bitEffects` (own PCG — must match runtime `pcg3d`), plus the CPU-only `filter/wormhole` point-scatter and the fibers/scratches/strayHair one-shot overlays.

### 4.6 Parity harness

Two oracles, both already in-repo:
1. **GPU goldens** — `noisemaker-cpu/parity/goldens/**` (166/167 within ±2 RGBA bytes; `filter/crt` is the known failure). Ports diff against these at the same fixed settings (8×8, time 0.25, seed 1, `oneShot:'initial'`).
2. **JS per-pixel oracle** — render any program in cpu (JS) and diff the port's output. Available for *every* effect and any size, giving a per-kernel check far denser than the 8×8 goldens.

Tolerance: **±2 bytes/channel** (matching cpu). `filter/crt` inherits the known-fail status. A port "passes" an effect when it matches the JS output within tolerance across a spread of seeds/sizes.

## 5. Phasing (correctness-first)

- **P0 — Prove the spine (Python).** Backend emits Python for the *simple* dialect subset; port the runtime stdlib core (float32, arithmetic, texture, no derivatives yet); render `filter/invert`, `synth/solid`, `filter/bc`, `filter/threshold` **byte-exact vs JS**. Establishes the transpiler↔runtime contract end-to-end.
- **P1 — Full Python engine + auto-transpiled catalog.** Complete runtime stdlib (incl. uint32/PCG, derivatives, half-float, matrices), render-graph interpreter, DSL, catalog, Surface, PNG, CLI. Transpile all 167; reach parity on the auto-transpilable majority. Pure-Python/numpy; slow is acceptable here (speed is P4).
- **P2 — Python special adapters.** Hand-port the ~11 adapters; drive Python to **full 167 parity** (crt excepted).
- **P3 — Perl port.** Replicate backend output + runtime + engine + adapters in Perl; structure as `Math::Fractal::Noisemaker` **v1.000** (`lib/Math/Fractal/Noisemaker/**`, `t/`, build tooling, `make-noise` + `noisemaker-cpu` CLIs). Full 167 parity in Perl.
- **P4 — Fast backend (speed).** Once parity holds, add a compiled hot-path: transpile kernels → C, JIT-compile + cache (Python via `cffi`/Cython; Perl via XS/Inline::C), or numpy-vectorize the data-parallel kernels. Cached with smart eviction. This is where "as fast as possible" is delivered.

## 6. Repository layout

New sibling directories under `~/platform`, each `git init`'d locally (no remote, no push):

**`noisemaker-python/`**
- `pyproject.toml` (dist name `noisemaker-cpu`, import package `noisemaker_cpu` — avoids clash with the existing TensorFlow `noisemaker` on PyPI), `src/noisemaker_cpu/**`, `bundle/**` (vendored), `tests/**`, CLI entry point `noisemaker-cpu`. Dependency: `numpy` (fidelity + P4 vectorization). Python ≥ 3.11.

**`noisemaker-perl/`**
- `Math-Fractal-Noisemaker/` dist: `lib/Math/Fractal/Noisemaker.pm` (facade, `$VERSION='1.000'`) + `lib/Math/Fractal/Noisemaker/**` (Runtime, Kernel, Renderer, Dsl, Surface, Png, Cli, Effects), `bundle/**` (vendored), `t/**`, `bin/make-noise` + `bin/noisemaker-cpu`. Build tooling: **ExtUtils::MakeMaker** (default; lightest, most portable for a replacement). Deps kept minimal: `Compress::Zlib` (PNG). No `Imager`.

**`noisemaker-cpu/` edits (additive only):**
- `scripts/bundle/**` (backends + emitter), a `bundle` npm script, and new tests. **Do not** disturb the currently-staged `examples/` deletion or other working state; coordinate before committing.

## 7. Constraints & etiquette

- `../noisemaker` (upstream GLSL) is **read-only**: never push, never run its build, per its CLAUDE.md. We only read `shaders/effects/**`.
- Nothing is committed or pushed without explicit per-instance approval. `~/platform` is not a git repo; the two ports get local `git init` only when Alex okays it.
- No absolute-home paths / localhost / machine-specific config in any committed file.

## 8. Sonnet-worker decomposition

Highly parallel once the transpiler backend + runtime contract exist:
- **Critical path (do first, low parallelism):** Python backend emitter + runtime stdlib core + P0 proof. (Claude + 1 worker.)
- **Parallel after P0:** runtime stdlib sections (uint/PCG, derivatives, half-float, matrices, texture) as independent worker tasks with golden-vector tests; the ~11 special adapters (one worker each); DSL; PNG; CLI; render-graph interpreter.
- **Batch (not per-effect labor):** the 167 kernel transpilations are a single bundler run once the backend works — parity failures get triaged, not hand-written.
- **P3 Perl** mirrors P1/P2 structure; workers replicate module-by-module against the passing Python port + JS oracle.
- Every worker task carries a **parity assertion** (golden or JS-oracle diff) as its definition of done.

## 9. Risks

1. **32-bit uint wraparound** (#1) — 3 independent sites (dialect, runtime, normalizer shim). Mitigation: route all uint ops through masked runtime helpers; assert golden vectors early.
2. **Derivatives** — record/replay quad model is the hardest runtime item; some eligible filters use `fwidth` for AA. Mitigation: port faithfully in P1 with dedicated tests; fallback path exists.
3. **Perl float32** — no native type; `pack/unpack` per-op is correct but slow. Mitigation: accept in P1 (correctness-first); solve in P4 (C/XS or PDL — a dependency decision to confirm).
4. **Overload name-mangling** — needs static type inference in the backend. Mitigation: bounded (23 sites, mostly the `mod289` idiom).
5. **df64 fidelity** vs native-float64 substitution in mandelbrot/julia/newton. Mitigation: transpile faithfully first; substitute only if parity demands.
6. **P1 performance** — pure-Python/Perl scalar kernels are slow. Accepted by the correctness-first sequencing; P4 addresses it.

## 10. Defaults to confirm at review

These are chosen with rationale above; flag any to change:
- Python: dist `noisemaker-cpu` / import `noisemaker_cpu`, dep `numpy`, Python ≥ 3.11.
- Perl: `ExtUtils::MakeMaker`, `Compress::Zlib` for PNG (no Imager), v1.000.
- PNG: faithful port of cpu's zero-dep codec (vs Pillow/Imager).
- Bundle vendored (copied) into each port for self-containment.
- P4 fast-backend target: C via cffi/Cython (Python) + XS/Inline::C (Perl); PDL for Perl deferred to P4.
- Spec + port repos committed only on explicit approval.
