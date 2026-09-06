# {{NM_PROGRAM_NAME}}

This Python package exports your Noisedeck program to render **on the CPU**. It requires no GPU, OpenGL, or compiled extension of its own. `engine/` contains the whole engine. Python executes the shader code as numpy array math, one effect pass at a time. It fetches nothing at runtime.

This export integrates with Python notebooks, batch jobs, and pipeline steps. It is a slow way to draw a frame. A GPU colors thousands of pixels at once. This renderer processes the arrays.

## Run it

You need **Python 3.11 or newer** and **numpy 1.26 or newer**. numpy is the only dependency. Install it if necessary:

```sh
python3 -m pip install 'numpy>=1.26'
```

Then unzip this folder. Open a terminal in it. Start with a small image:

```sh
python3 run.py program.dsl --width 64 --height 64 --output out.png
```

The command writes a 64×64 `out.png` beside your program. This checks that the export works. Then increase the output size:

```sh
python3 run.py program.dsl --width 512 --height 512 --output art.png
```

Rendering time increases with the pixel count. The amount of increase depends entirely on the program. Increase the size gradually.

`--seed N` selects the deterministic seed. `--time N` sets the normalized time for effects that animate.
`python3 run.py --help` lists everything.

## What's inside

| Path | What it is |
| --- | --- |
| `run.py` | The entry point. Puts `engine/` on the import path and renders. This is the file you run. |
| `program.dsl` | Your program's source, exactly as it was in Noisedeck. |
| `engine/noisemaker_cpu/` | The engine: DSL parser, effect catalog, and the transpiled kernels. |
| `noisedeck-export.json` | The exported content, export time, and engine build. |
| `LICENSES/` | Licenses for everything shipped here. |

The export installs nothing and writes nothing outside this folder. `run.py` places `engine/` first in `sys.path` and imports `noisemaker_cpu` from there. An unrelated `noisemaker_cpu` on the system cannot override the copy included with your program.

## The engine

The export includes the port and runs offline without changes. It is also a normal package. `run.py` calls two functions: `render_dsl(source, width=..., height=...)` from `noisemaker_cpu.renderer` and `encode_png` from `noisemaker_cpu.png`. You can call them the same way from your own code. <https://github.com/noisefactorllc/noisemaker-for-python> documents the rest.

Noisedeck exported this program against Noisemaker `{{NM_ENGINE_VERSION}}`. The Python port is a separate implementation of that engine. Expect small differences from the app output.

## Editing it

Replace `program.dsl` with a Noisemaker program that uses only the supported effects listed below. Run the same command again. To render several variations, call `render_dsl` in a loop in your own code. This avoids process startup for each variation.

## Effects used by this program

{{NM_EFFECT_LIST}}

## What this port cannot render

This port cannot render five effects from the upstream catalog:

- `synth/roll`, `synth/scope` and `synth/spectrum` react to live audio.
- `render/meshLoader` and `render/meshRender` need a mesh pipeline.

Everything else in the catalog renders here.
`engine/noisemaker_cpu/bundle/metadata.json` lists exactly which effects this engine contains.

To check an edited `program.dsl` against a different build of this port:

1. Import the program into Noisedeck.
2. Open the export dialog.
3. Select Python.

Before you export again, the dialog marks any effect the port cannot render.

## License

The Noisemaker engine and the Python port are MIT licensed. See `LICENSES/`. Your program and the
imagery it renders are yours.
