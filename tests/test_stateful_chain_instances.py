from noisemaker_cpu.renderer import render_dsl

SIZE = 8
TIME = 0.25

PAIRS = [
    # Two reactionDiffusion instances in one chain, each with its own state
    # texture and zoom size.
    [
        "search synth, mixer\nreactionDiffusion(zoom: x4).blendMode(tex: reactionDiffusion(zoom: x16)).write(o0)\nrender(o0)\n",
        "search synth, mixer\nreactionDiffusion(zoom: x16).write(o2)\nreactionDiffusion(zoom: x4).blendMode(tex: read(o2)).write(o0)\nrender(o0)\n",
    ],
    # Two reactionDiffusion instances behind a synth, as chain arguments.
    [
        "search synth, mixer\nnoise(seed: 1).blendMode(tex: reactionDiffusion(zoom: x4)).blendMode(tex: reactionDiffusion(zoom: x16)).write(o0)\nrender(o0)\n",
        "search synth, mixer\nreactionDiffusion(zoom: x4).write(o2)\nreactionDiffusion(zoom: x16).write(o3)\nnoise(seed: 1).blendMode(tex: read(o2)).blendMode(tex: read(o3)).write(o0)\nrender(o0)\n",
    ],
    # Repeated state preserves each explicit or default zoom.
    [
        "search synth, mixer\nreactionDiffusion(zoom: x4).blendMode(tex: reactionDiffusion()).blendMode(tex: reactionDiffusion(zoom: x16)).write(o0)\nrender(o0)\n",
        "search synth, mixer\nreactionDiffusion().write(o2)\nreactionDiffusion(zoom: x16).write(o3)\nreactionDiffusion(zoom: x4).blendMode(tex: read(o2)).blendMode(tex: read(o3)).write(o0)\nrender(o0)\n",
    ],
    # Repeated stateful filters keep independent ping-pong state.
    [
        "search synth, filter\nnoise(seed: 1).watercolor().watercolor().write(o0)\nrender(o0)\n",
        "search synth, filter\nnoise(seed: 1).watercolor().write(o1)\nread(o1).watercolor().write(o0)\nrender(o0)\n",
    ],
    # Different stateful effects in one chain size from their own zoom: the
    # reactionDiffusion state keeps the chain-scoped size, the cellularAutomata
    # instance gets its own.
    [
        "search synth, mixer\nreactionDiffusion(zoom: x4).blendMode(tex: cellularAutomata(zoom: x16)).write(o0)\nrender(o0)\n",
        "search synth, mixer\ncellularAutomata(zoom: x16).write(o2)\nreactionDiffusion(zoom: x4).blendMode(tex: read(o2)).write(o0)\nrender(o0)\n",
    ],
    [
        "search synth, mixer\nnoise(seed: 1).blendMode(tex: reactionDiffusion(zoom: x4)).blendMode(tex: cellularAutomata(zoom: x16)).write(o0)\nrender(o0)\n",
        "search synth, mixer\ncellularAutomata(zoom: x16).write(o2)\nreactionDiffusion(zoom: x4).write(o3)\nnoise(seed: 1).blendMode(tex: read(o3)).blendMode(tex: read(o2)).write(o0)\nrender(o0)\n",
    ],
]

LOOP_CHAINS = [
    # Adjacent loop regions share the chain-scoped accumulator, whose content
    # equals the region input there, so each region passes the image through.
    (
        "search synth, render\nperlin(seed: 1).loopBegin().loopEnd().write(o0)\nrender(o0)\n",
        "search synth, render\nperlin(seed: 1).loopBegin().loopEnd().loopBegin().loopEnd().write(o0)\nrender(o0)\n",
    ),
]


def render_bytes(source):
    return render_dsl(source, width=SIZE, height=SIZE, seed=1, time=TIME).to_rgba8()


def test_repeated_stateful_instances_render_as_their_flattened_per_instance_programs():
    for inline, flat in PAIRS:
        assert render_bytes(inline) == render_bytes(flat), inline


def test_two_loop_regions_in_one_chain_share_the_chain_scoped_accumulator():
    for single, pair in LOOP_CHAINS:
        assert render_bytes(pair) == render_bytes(single), pair
    # A step between the two regions makes the shared feedback observable: the
    # second region reads the first region's accumulator, which still holds the
    # pre-invert image, so the chain is not the flattened fresh-per-region form.
    shared = (
        "search synth, filter, render\n"
        "perlin(seed: 1).loopBegin(alpha: 100).loopEnd().invert().loopBegin(alpha: 100).loopEnd().write(o0)\n"
        "render(o0)\n"
    )
    fresh = (
        "search synth, filter, render\n"
        "perlin(seed: 1).loopBegin(alpha: 100).loopEnd().write(o1)\n"
        "read(o1).invert().loopBegin(alpha: 100).loopEnd().write(o0)\n"
        "render(o0)\n"
    )
    assert render_bytes(shared) != render_bytes(fresh), shared


def test_repeated_mesh_renderers_keep_the_loader_mesh_and_work_with_the_loader_in_another_chain():
    repeated = "search render\nmeshLoader().meshRender().meshRender().write(o0)\nrender(o0)\n"
    flattened = "search render\nmeshLoader().meshRender().write(o1)\nread(o1).meshRender().write(o0)\nrender(o0)\n"
    assert render_bytes(repeated) == render_bytes(flattened), repeated
    assert (
        len(
            render_bytes(
                "search render\nmeshLoader().write(o0)\nread(o0).meshRender().meshRender().write(o1)\nrender(o1)\n"
            )
        )
        == SIZE * SIZE * 4
    )
