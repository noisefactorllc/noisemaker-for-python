# noisemaker-python P0 — Prove the Spine — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove the GLSL→Python transpile + native runtime contract end-to-end by rendering `filter/invert` and `synth/solid` **byte-exact** against the JS oracle, through the real bundle → load → runtime-compile → render → PNG pipeline.

**Architecture:** A GLSL→Python code-gen backend (Strategy B) lives in noisemaker-cpu, reusing `glsl-tokenizer`/`glsl-parser`/`prepr` + `glsl-normalize.js`, and emits a bundle (metadata JSON + `.py` kernel source). The `noisemaker-python` package ships a runtime stdlib, a per-pixel pass runner, a kernel loader (runtime `exec` + LRU cache), a Surface, a zero-dep PNG codec, and a minimal single-effect renderer + CLI. P0 covers only the two proof effects; the full render graph, DSL, and all 167 effects are P1.

**Tech Stack:** Node ≥22 (bundler, reuses cpu's toolchain); Python ≥3.11 + numpy (runtime); Python stdlib `zlib` (PNG). JS oracle = `node bin/noisemaker-cpu.js` in noisemaker-cpu.

## Global Constraints

- Local-only: no PyPI publish, no `git push`. New port repos get local `git init`; commit checkpoints locally.
- `../noisemaker` (upstream GLSL) is READ-ONLY: never push, never run its build.
- noisemaker-cpu edits are additive under `scripts/bundle/`; do **not** touch its staged `examples/` deletion; do **not** commit cpu without explicit approval.
- Python dist name `noisemaker-cpu`, import package `noisemaker_cpu`, Python ≥ 3.11, dep `numpy`.
- Parity tolerance: **±2 bytes/channel** vs the JS oracle. Float32 fidelity via `numpy.float32`; `round` = `floor(x+0.5)` (never banker's); `dot` accumulates then truncates once; GL bottom-left origin (`fy = height-y-0.5`, integer texel-row flip in sampling).
- Golden runtime vectors (assert exactly): `filter/invert [0.2,0.4,0.8,0.5] → [0.80000001,0.60000002,0.19999999,0.5]`; texture on a 2×2 RGBA: `texelFetch([1,0],0)==[1,1,1,1]`, nearest `texture([0.5,0.5])==[0,1,0,1]`, linear `texture([0.5,0.5])==[0.5,0.5,0.5,1]`.

---

## File Structure

**noisemaker-cpu (additive bundler):**
- `scripts/bundle/backend-python.js` — GLSL AST → Python kernel source. P0 subset: `uniform` decls, `void main()`, local `vec*`/`float`/`ivec2` decls, `if/else`, arithmetic, unary minus, scalar↔vector broadcast, read+write swizzles, `texture`/`textureSize`, vector constructors, `float()`/`int()` casts, `min`/`max`/`clamp`/`mix`. Emits a `run_pixel(ctx, out)` Python function calling a passed-in `rt` runtime.
- `scripts/bundle/emit-bundle.js` — orchestrates: `assertPinnedSource` → read effect record (`inventory`) → read `glsl/*.glsl` → `normalizeCanonicalGlsl` → tokenize/parse → `backend-python` → write `bundle/metadata.json` + `bundle/kernels/python/<ns>__<func>__<program>.py`. P0: `--only synth/solid,filter/invert`.
- `scripts/bundle/README.md` — how to run; provenance.

**noisemaker-python:**
- `pyproject.toml`, `src/noisemaker_cpu/__init__.py`
- `runtime.py` — `Runtime` class: `f32`, `construct`, `swizzle_get`/`swizzle_set`, `binary`, `unary`, `component_wise` (min/max/clamp/mix/floor/fract/abs/…), `texture`, `texture_size`, `int_cast`/`float_cast`, `begin_pixel`. P0 implements only what solid+invert use; structured so P1 extends it.
- `surface.py` — `Surface(width,height,data:np.float32[w*h*4])`, `from_rgba8`, `to_rgba8` (`/255` linear).
- `sampler.py` — `sample_nearest_bottom_left`, `sample_bilinear` (y-flip on integer texel row).
- `pass_runner.py` — `run_pass(kernel, ctx, width, height) -> Surface` (per-pixel loop; `fy=height-y-0.5`, `uv`, `frag_coord`).
- `kernel_loader.py` — `load_kernel(source:str) -> callable` via `exec`; `KernelCache` (byte-bounded LRU).
- `png.py` — `encode_png(surface)->bytes`, `decode_png(bytes)->Surface` (port of cpu `png.js`; stdlib `zlib`; all 5 filters, CRC32, guards).
- `renderer.py` — `render_effect(effect_id, params, inputs, width, height, seed, time) -> Surface` (P0: single pass, generator or single-input filter).
- `cli.py` — `noisemaker-cpu effect <id> [--param k=v] [--input f] [--output f] [--width][--height]`.
- `bundle/` — vendored from the cpu bundler output.
- `tests/` — one test file per module + `test_parity.py`.

---

## Task 1: Scaffold noisemaker-python

**Files:**
- Create: `noisemaker-python/pyproject.toml`, `noisemaker-python/src/noisemaker_cpu/__init__.py`, `noisemaker-python/tests/__init__.py`, `noisemaker-python/.gitignore`

**Interfaces:**
- Produces: importable package `noisemaker_cpu` with `__version__`.

- [ ] **Step 1:** Write `pyproject.toml` (setuptools, name `noisemaker-cpu`, version `0.0.0`, `requires-python>=3.11`, dep `numpy`, `[project.scripts] noisemaker-cpu = "noisemaker_cpu.cli:main"`, package dir `src`).
- [ ] **Step 2:** Write `src/noisemaker_cpu/__init__.py` with `__version__ = "0.0.0"`.
- [ ] **Step 3:** `cd noisemaker-python && git init && python -m venv .venv && .venv/bin/pip install -e . pytest`.
- [ ] **Step 4:** Verify `python -c "import noisemaker_cpu; print(noisemaker_cpu.__version__)"` prints `0.0.0`.
- [ ] **Step 5:** Commit: `chore: scaffold noisemaker-python package`.

## Task 2: Runtime float32 truncation (`f32`)

**Interfaces:**
- Produces: `Runtime.f32(x: float) -> float` (float32 round, matching JS `Math.fround`).

- [ ] **Step 1: Failing test** `tests/test_runtime.py`:
```python
import numpy as np
from noisemaker_cpu.runtime import Runtime
def test_f32_matches_fround():
    rt = Runtime()
    assert rt.f32(0.1) == float(np.float32(0.1))
    assert rt.f32(1/3) == float(np.float32(1/3))
    assert rt.f32(4294967295) == 4294967296.0  # F32 rounds up
```
- [ ] **Step 2:** Run `pytest tests/test_runtime.py -v` → FAIL (no module).
- [ ] **Step 3:** Implement `runtime.py` with `class Runtime: def f32(self,x): return float(np.float32(x))`.
- [ ] **Step 4:** Run → PASS.
- [ ] **Step 5:** Commit: `feat: runtime f32 float32 truncation`.

## Task 3: Runtime vectors — construct, swizzle get/set, broadcast binary

**Interfaces:**
- Produces: `construct(width, *comps)->np.float32[width]`; `swizzle_get(vec, "rgb"/"xy"/…)`; `swizzle_set(vec, "rgb", value)` (returns mutated vec); `binary(op, a, b)` with scalar↔vector broadcast, float32 per-op.

- [ ] **Step 1: Failing tests** (append to `test_runtime.py`): construct splat `construct(3,0.5)==[0.5,0.5,0.5]`; nested `construct(4, construct(3,...), 1.0)`; `swizzle_get([1,2,3,4],"bgr")==[3,2,1]`; write-swizzle `swizzle_set(v,"rgb",[9,9,9])` sets first three, leaves alpha; `binary("-", 1.0, [0.2,0.4,0.8])==[0.8,0.6,0.2]` (scalar−vector); `binary("*", [1,2],[3,4])==[3,8]`.
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** Implement construct/swizzle_get/swizzle_set/binary in `runtime.py` (component index map `xyzw`/`rgba`/`stpq`; per-op `np.float32`).
- [ ] **Step 4:** Run → PASS.
- [ ] **Step 5:** Commit: `feat: runtime vectors, swizzles, broadcast ops`.

## Task 4: Surface + rgba8 conversion

**Interfaces:**
- Produces: `Surface(width,height,data)`, `Surface.from_rgba8(w,h,bytes)`, `.to_rgba8()->bytes`, `.filter` attr (`"nearest"`/`"linear"`).

- [ ] **Step 1: Failing test** `tests/test_surface.py`: round-trip `to_rgba8(from_rgba8(w,h,b)) == b` for a known 2×2 buffer; `from_rgba8` scales `/255` into float32; non-finite → 0 and clamp `[0,1]` on `to_rgba8`.
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** Implement `surface.py`.
- [ ] **Step 4:** Run → PASS.
- [ ] **Step 5:** Commit: `feat: Surface + rgba8 conversion`.

## Task 5: PNG encode

**Interfaces:**
- Produces: `encode_png(surface)->bytes` (8-bit RGBA, filter type 0 acceptable for P0, CRC32 + zlib).

- [ ] **Step 1: Failing test** `tests/test_png.py`: `encode_png` of a 2×2 surface yields bytes starting with the PNG signature `89 50 4E 47 0D 0A 1A 0A`, contains `IHDR`/`IDAT`/`IEND`, and Python's `struct`-computed CRC matches.
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** Implement `encode_png` in `png.py` (CRC32 table, chunking, `zlib.compress`).
- [ ] **Step 4:** Run → PASS.
- [ ] **Step 5:** Commit: `feat: PNG encode`.

## Task 6: PNG decode

**Interfaces:**
- Produces: `decode_png(bytes)->Surface`.

- [ ] **Step 1: Failing test** (append `test_png.py`): `decode_png(encode_png(s))` reproduces `s.to_rgba8()`; decode of a fixture PNG written by cpu (`node bin/noisemaker-cpu.js effect synth/solid --width 2 --height 2 --output /tmp/solid.png`) matches cpu's bytes.
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** Implement `decode_png` (all 5 filters incl. Paeth, `zlib.decompress`, pixel/size guards).
- [ ] **Step 4:** Run → PASS.
- [ ] **Step 5:** Commit: `feat: PNG decode`.

## Task 7: Sampler (nearest bottom-left + bilinear, y-flip)

**Interfaces:**
- Produces: `sample_nearest_bottom_left(surface, u, v)`, `sample_bilinear(surface, u, v)` → `np.float32[4]`.

- [ ] **Step 1: Failing test** `tests/test_sampler.py`: build a 2×2 surface with the test colors; assert nearest `texture([0.5,0.5])==[0,1,0,1]`, bilinear `[0.5,0.5]==[0.5,0.5,0.5,1]` (matches the golden vectors); confirm the integer texel-row flip (not `1-v`) at a boundary.
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** Implement `sampler.py` (port cpu `sampler.js`; clamp-to-edge; flip integer row `ty = height-1-iy`).
- [ ] **Step 4:** Run → PASS.
- [ ] **Step 5:** Commit: `feat: nearest+bilinear sampler with GL origin flip`.

## Task 8: Pass runner (per-pixel loop)

**Interfaces:**
- Consumes: `Runtime`, `Surface`.
- Produces: `run_pass(kernel, ctx, width, height) -> Surface`. `ctx` exposes `uv`, `frag_coord`, `resolution`, `time`, `seed`, `uniforms`, `textures`, `rt`. `kernel(ctx, out)` writes 4 floats into `out`.

- [ ] **Step 1: Failing test** `tests/test_pass_runner.py`: a trivial kernel `out[:]= [ctx.uv[0], ctx.uv[1], 0, 1]` on 2×2 → check `uv` at pixel (0,0) is bottom-left `(0.25,0.75)` given `fy=height-y-0.5` and center offset; resolution correct.
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** Implement `pass_runner.py` (`fy=height-y-0.5`; `frag_coord=(x+0.5,fy)`; `uv=frag_coord/resolution`).
- [ ] **Step 4:** Run → PASS.
- [ ] **Step 5:** Commit: `feat: per-pixel pass runner with bottom-left coords`.

## Task 9: Kernel loader (exec + LRU cache)

**Interfaces:**
- Produces: `load_kernel(source:str)->callable` (execs source defining `run_pixel`, returns it); `KernelCache(max_bytes)` with `.get(key, source_factory)` + LRU eviction.

- [ ] **Step 1: Failing test** `tests/test_kernel_loader.py`: `load_kernel("def run_pixel(ctx,out):\n out[0]=1.0")` returns a callable that sets `out[0]`; `KernelCache` evicts LRU past `max_bytes`; repeated `.get` same key compiles once (spy via a counter).
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** Implement `kernel_loader.py` (`exec(source, ns)`, return `ns["run_pixel"]`; `OrderedDict` LRU).
- [ ] **Step 4:** Run → PASS.
- [ ] **Step 5:** Commit: `feat: kernel loader with runtime exec + LRU cache`.

## Task 10: Bundler emits `synth/solid` Python; render byte-exact

**Files:**
- Create (cpu): `scripts/bundle/backend-python.js`, `scripts/bundle/emit-bundle.js`
- Create (py): `renderer.py`, vendored `bundle/kernels/python/synth__solid__main.py`, `bundle/metadata.json`

**Interfaces:**
- Consumes: Runtime, pass_runner, kernel_loader, Surface, PNG.
- Produces: `render_effect(effect_id, params, inputs, width, height, seed, time)->Surface`.

- [ ] **Step 1: Failing test** `tests/test_parity.py::test_solid`: generate the JS oracle `node ../noisemaker-cpu/bin/noisemaker-cpu.js effect synth/solid --width 16 --height 16 --param color=#4080c0 --output /tmp/js_solid.png`; render the same via `render_effect("synth/solid", {"color":"#4080c0"}, ...)`; assert every channel within ±2 of the decoded JS PNG.
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3a:** Implement `backend-python.js` (AST→Python for the solid subset: uniform reads with defaults from metadata, `construct`, `binary`, swizzle, `main` returns vec4 → `out[:]`).
- [ ] **Step 3b:** Implement `emit-bundle.js`; run `node scripts/bundle/emit-bundle.js --only synth/solid`; copy output into `noisemaker-python/bundle/`.
- [ ] **Step 3c:** Implement `render_effect` (load metadata, load kernel, build ctx with normalized params, run single pass).
- [ ] **Step 4:** Run → PASS (byte-exact expected for solid).
- [ ] **Step 5:** Commit (py repo): `feat: bundler python backend + render synth/solid at parity`.

## Task 11: Bundler emits `filter/invert`; render byte-exact

**Interfaces:**
- Consumes: everything above.
- Produces: single-input filter path in `render_effect` (binds `inputTex`).

- [ ] **Step 1: Failing test** `tests/test_parity.py::test_invert`: make a 16×16 input PNG (via cpu solid or a gradient); JS oracle `node …/noisemaker-cpu.js effect filter/invert --input /tmp/in.png --output /tmp/js_invert.png`; Python `render_effect("filter/invert", {}, {"inputTex": decode_png(in)}, …)`; assert ±2. Also unit-assert the golden `[0.2,0.4,0.8,0.5]→[0.80000001,0.60000002,0.19999999,0.5]` through the compiled kernel.
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** Extend `backend-python.js` for `textureSize`/`texture`/`if-else`/write-swizzle/`min`; re-emit bundle for `filter/invert`; add filter-input binding to `render_effect`.
- [ ] **Step 4:** Run → PASS.
- [ ] **Step 5:** Commit: `feat: render filter/invert at parity`.

## Task 12: CLI `effect` subcommand

**Interfaces:**
- Produces: `noisemaker-cpu effect <id> [--param k=v]... [--input f] [--output f] [--width N] [--height N] [--seed N] [--time T]`.

- [ ] **Step 1: Failing test** `tests/test_cli.py`: invoke `main(["effect","synth/solid","--width","8","--height","8","--output","/tmp/cli.png"])`; assert file exists, PNG signature, and matches `render_effect` output.
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** Implement `cli.py` (argparse; param parse incl. `#hex` colors; input/output PNG).
- [ ] **Step 4:** Run → PASS; manual: `noisemaker-cpu effect filter/invert --input /tmp/in.png --output /tmp/out.png`.
- [ ] **Step 5:** Commit: `feat: CLI effect subcommand`.

---

## P0 Done = spine proven
`synth/solid` and `filter/invert` render byte-exact vs JS through bundle→compile→render→PNG→CLI. The transpiler↔runtime contract, the parity harness, and the vendoring flow all work.

## P1 fan-out inventory (next plan)
Once P0 holds, P1 is parallel worker tasks, each gated by a JS-oracle parity assertion (not pre-written code — transpiler-output-driven):
1. **Runtime stdlib completion** (worker set, golden-vector tests): trig/pow/exp family; `glslMod`; `dot`/`length`/`normalize`/`reflect`/`refract`; matrices; **uint32/PCG** (`umul`,`pcg3d`,`hashUint32` — assert cpu golden vectors); **derivatives** (record/replay 2×2 quad); half-float pack/unpack.
2. **Backend completion**: `for`/`while`/`break`/`continue`, ternary, overload name-mangling, arrays, flat structs, uint-op routing through masked runtime helpers, `#define`-structural variants.
3. **Render-graph interpreter**: multi-pass, named attachments, per-pass half-float quantization, `repeat`/`blend`/`drawMode:points`, one-shot overlays.
4. **DSL**: tokenize/parse/compile → graph; `search`/`let`/`read`/`write`/`render`.
5. **Catalog/registry/definition** from `metadata.json`; `normalizeArguments`.
6. **Bundle all 167**; triage parity failures.
7. **~11 hand-ported adapters** (one worker each): fractal, julia, crt, snow, median, palette, historicPalette, pixelSort, reindex, bitEffects, wormhole+overlays.
8. **Full parity run** vs cpu goldens (166/167; crt excepted).

P2 = adapters to full parity. P3 = Perl replication (Math::Fractal::Noisemaker v1.000). P4 = compiled fast backend.
