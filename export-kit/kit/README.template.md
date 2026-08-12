# {{NM_PROGRAM_NAME}}

Your program, exported from Noisedeck as a Python package that renders it **on the CPU**. No GPU, no
OpenGL, no compiled extension of its own: `engine/` is the whole engine, and Python executes what
would normally be shader code as numpy array math, one effect pass at a time. It fetches nothing at
runtime.

That makes this the export that drops into work you already do in Python — a notebook, a batch job,
a pipeline step — and the slow way to draw a frame. A GPU colors thousands of pixels at once; this
walks the arrays.

## Run it

You need **Python 3.11 or newer** and **numpy 1.26 or newer**. numpy is the one dependency; install
it if you have not:

```sh
python3 -m pip install 'numpy>=1.26'
```

Then unzip this folder, open a terminal in it, and start small:

```sh
python3 run.py program.dsl --width 64 --height 64 --output out.png
```

That writes a 64×64 `out.png` beside your program, which is enough to prove the export works. Then
scale up:

```sh
python3 run.py program.dsl --width 512 --height 512 --output art.png
```

Time grows with the pixel count, and how far it grows depends entirely on what your program does, so
raise the size in steps rather than jumping to a poster.

`--seed N` picks the deterministic seed and `--time N` the normalized time, for effects that animate.
`python3 run.py --help` lists everything.

## What's inside

| Path | What it is |
| --- | --- |
| `run.py` | The entry point. Puts `engine/` on the import path and renders. This is the file you run. |
| `program.dsl` | Your program's source, exactly as Noisedeck had it. |
| `engine/noisemaker_cpu/` | The engine: DSL parser, effect catalog, and the transpiled kernels. |
| `noisedeck-export.json` | What was exported, when, against which engine build. |
| `LICENSES/` | Licenses for everything shipped here. |

Nothing is installed and nothing is written outside this folder. `run.py` puts `engine/` at the front
of `sys.path` and imports `noisemaker_cpu` from there, so an unrelated `noisemaker_cpu` on the system
cannot shadow the one that shipped with your program.

## The engine

The port ships inside this export, so it runs offline as it stands. It is also a normal package —
`render_dsl(source, width=..., height=...)` from `noisemaker_cpu.renderer` and `encode_png` from
`noisemaker_cpu.png` are the two functions `run.py` calls, and you can call them the same way from
your own code. <https://github.com/noisefactorllc/noisemaker-for-python> documents the rest.

Noisedeck exported this program against Noisemaker `{{NM_ENGINE_VERSION}}`. The Python port is a
second implementation of that engine rather than the same code, so expect small differences from what
the app showed you.

## Editing it

Replace `program.dsl` with anything the Noisemaker language accepts, as long as its effects are in
the supported set below, and run the same command again. To render several variations, call `render_dsl`
in a loop of your own rather than paying process startup each time.

## Effects used by this program

{{NM_EFFECT_LIST}}

## What this port cannot render

Five effects from the upstream catalog: `synth/roll`, `synth/scope` and `synth/spectrum`, which react
to live audio, and `render/meshLoader` and `render/meshRender`, which need a mesh pipeline. Everything
else in the catalog renders here, and `engine/noisemaker_cpu/bundle/metadata.json` lists exactly what
the engine in this folder carries.

To check an edited `program.dsl` against a different build of this port, put it back into Noisedeck
and open the export dialog with Python selected: it marks any effect the port cannot render before
you export again.

## License

The Noisemaker engine and the Python port are MIT licensed; see `LICENSES/`. Your program and the
imagery it renders are yours.
