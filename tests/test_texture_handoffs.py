"""Chain texture publication, storage lifetimes and particle tick routing."""

import numpy as np
import pytest

from noisemaker_cpu import renderer


def pixel(program, target="outputTex", **inputs):
    return {"name": program, "program": program, "key": program, "outputs": {"color": target}, "inputs": inputs}


def fill(target, value, *, storage=False):
    render_pass = pixel("fill", target)
    render_pass["uniforms"] = {"value": value}
    if storage:
        render_pass["storageTextures"] = render_pass.pop("outputs")
    return render_pass


def effect(*passes, kind="filter", iterated=False, **fields):
    params = {"iterationCount": {"type": "int", "default": 2}} if iterated else {}
    return {"namespace": "probe", "kind": kind, "params": params, "iterated": iterated, "passes": passes, **fields}


def render_probes(monkeypatch, definitions, **kernels):
    effects = {"probe/" + name: spec for name, spec in definitions.items()}

    def fill_pixel(ctx, out):
        out[:] = [ctx.uniforms["value"]] * 4

    def copy_pixel(ctx, out):
        out[:] = ctx.textures["src"].data[:4]

    programs = {"fill": fill_pixel, "copy": copy_pixel, **kernels}
    monkeypatch.setattr(renderer, "_meta", lambda: {"effects": effects})
    monkeypatch.setattr(renderer, "_kernel_for", programs.__getitem__)

    def render(chain):
        return renderer.render_dsl(f"search probe\n{chain}.write(o0)\nrender(o0)", width=2, height=2)

    return render


@pytest.mark.parametrize("iterated", [False, True])
def test_published_channels_survive_an_image_filter(monkeypatch, iterated):
    producer = effect(
        fill("color", 0.125),
        fill("positions", 0.25),
        fill("speed", 0.5),
        fill("tint", 0.75),
        kind="generator",
        iterated=iterated,
        textures={"outputTex": {"width": 1, "height": 1}},
        outputTex="color",
        outputXyz="positions",
        outputVel="speed",
        outputRgba="tint",
    )
    reader = pixel("pack", image="inputTex", x="inputXyz", v="inputVel", r="inputRgba")

    def pack(ctx, out):
        out[:] = [ctx.textures[name].data[0] for name in ("image", "x", "v", "r")]

    render = render_probes(
        monkeypatch,
        {
            "producer": producer,
            "copy": effect(pixel("copy", src="inputTex")),
            "reader": effect(reader, iterated=iterated),
        },
        pack=pack,
    )
    assert render("producer().copy().reader()").to_rgba8() == bytes([32, 64, 128, 191]) * 4


def test_written_outputs_override_configured_fallbacks(monkeypatch):
    source = effect(
        fill("work", 0.25),
        fill("outputTex", 0.5),
        fill("outputXyz", 0.75),
        kind="generator",
        outputTex="work",
        outputXyz="work",
    )

    def read(ctx, out):
        out[:] = [ctx.textures["image"].data[0], ctx.textures["xyz"].data[0], 0.0, 1.0]

    render = render_probes(
        monkeypatch,
        {
            "source": source,
            "readState": effect(pixel("read", image="inputTex", xyz="inputXyz")),
        },
        read=read,
    )
    assert render("source().readState()").to_rgba8() == bytes([128, 191, 0, 255]) * 4


@pytest.mark.parametrize("target", ["coordinates", "global_xyz"])
def test_image_and_agent_alias_follow_ping_pong_writes(monkeypatch, target):
    source = effect(
        fill(target, 0.25),
        kind="generator",
        iterated=target == "global_xyz",
        textures={target: {"width": 1, "height": 1, "format": "rgba8"}},
        outputTex=target,
        outputXyz=target,
    )
    edit = effect(fill("inputXyz", 0.5), pixel("copy", src="inputTex"), textures={"outputTex": {"format": "rgba32f"}})
    render = render_probes(monkeypatch, {"source": source, "edit": edit})
    assert np.all(render("source().edit()").data == np.float32(128 / 255))


@pytest.mark.parametrize(
    "field,alias", [("outputXyz", "inputXyz"), ("outputVel", "inputVel"), ("outputRgba", "inputRgba")]
)
def test_handed_on_particle_reader_accumulates_every_tick(monkeypatch, field, alias):
    source = effect(
        pixel("tick", "state"),
        fill("outputTex", 0),
        kind="generator",
        iterated=True,
        textures={"global_xyz": {"width": 1, "height": 1}},
        **{field: "state"},
    )

    def tick(ctx, out):
        out[:] = [(ctx.uniforms["frame"] + 1) / 4] * 4

    def accumulate(ctx, out):
        out[:] = ctx.textures["state"].data[:4] + ctx.textures["prior"].data[:4]

    render = render_probes(
        monkeypatch,
        {
            "source": source,
            "sum": effect(pixel("accumulate", state=alias, prior="selfTex")),
        },
        tick=tick,
        accumulate=accumulate,
    )
    assert render("source().sum()").to_rgba8() == bytes([191]) * 16


def test_another_emitter_clears_inherited_channels(monkeypatch):
    emitter = {"iterated": True, "textures": {"global_xyz": {"width": 1, "height": 1}}}
    render = render_probes(
        monkeypatch,
        {
            "first": effect(fill("vel", 1), fill("outputTex", 0), kind="generator", outputVel="vel", **emitter),
            "next": effect(fill("global_xyz", 1), fill("outputTex", 0), outputXyz="global_xyz", **emitter),
            "readVel": effect(pixel("copy", src="inputVel")),
        },
    )
    with pytest.raises(ValueError, match='requires texture "inputVel"'):
        render("first().next().readVel()")


@pytest.mark.parametrize("iterated_writer", [False, True])
def test_storage_published_and_overwritten_by_another_effect(monkeypatch, iterated_writer):
    writer = effect(
        fill("global_work", 0.25, storage=True),
        kind="generator",
        iterated=iterated_writer,
        textures={"global_work": {"width": 1, "height": 1, "format": "rgba8"}},
        outputTex="global_work",
    )
    editor = effect(
        fill("global_work", 0.5, storage=True),
        pixel("read", src="inputTex"),
        iterated=not iterated_writer,
        textures={"outputTex": {"format": "rgba32f"}},
    )

    def read(ctx, out):
        src = ctx.textures["src"]
        out[:] = [src.data[0], src.width, src.height, 1]

    render = render_probes(monkeypatch, {"writer": writer, "editor": editor}, read=read)
    assert list(render("writer().editor()").data[:4]) == [np.float32(128 / 255), 1, 1, 1]


def test_storage_reader_sees_only_its_chain(monkeypatch):
    writer = effect(
        fill("global_work", 0.75, storage=True),
        fill("outputTex", 0),
        kind="generator",
        textures={"global_work": {"width": 1, "height": 1}},
    )
    render = render_probes(monkeypatch, {"writer": writer, "reader": effect(pixel("copy", src="global_work"))})
    assert render("writer().reader()").to_rgba8() == bytes([191]) * 16
    with pytest.raises(ValueError, match='requires texture "global_work"'):
        render("writer().write(o1)\nread(o1).reader()")


@pytest.mark.parametrize("iterated", [False, True])
@pytest.mark.parametrize("final_viewport,size", [({"w": 1, "h": 1}, (1, 1)), ({}, (2, 2))])
def test_local_storage_sized_for_each_write(monkeypatch, iterated, final_viewport, size):
    first = fill("work", 0.25, storage=True) | {"viewport": {"w": 2, "h": 1}}
    second = fill("work", 0.75, storage=True) | {"viewport": final_viewport}
    source = effect(first, second, kind="generator", iterated=iterated, outputTex="work")
    result = render_probes(monkeypatch, {"source": source})("source()")

    assert (result.width, result.height) == size
    assert result.to_rgba8() == bytes([191]) * (4 * size[0] * size[1])


@pytest.mark.parametrize("iterated,expected", [(False, (1, 1)), (True, (3, 3))])
@pytest.mark.parametrize("name, group_format", [("global_xyz", "rgba32f"), ("global_rgba", "rgba8")])
def test_only_group_particle_storage_uses_state_size(monkeypatch, iterated, expected, name, group_format):
    write = fill(name, 0.5001, storage=True) | {"viewport": {"w": 1, "h": 1}}
    source = effect(write, kind="generator", iterated=iterated, outputTex=name)
    source["params"]["stateSize"] = {"type": "int", "default": 3}
    result = render_probes(monkeypatch, {"source": source})("source()")
    assert (result.width, result.height) == expected
    assert result.format == (group_format if iterated else "rgba16f")
    expected_value = {"rgba32f": 0.5001, "rgba8": 128 / 255, "rgba16f": 0.5}[result.format]
    assert result.data[0] == np.float32(expected_value)


def test_declared_group_particle_target_keeps_its_dimensions(monkeypatch):
    write = fill("global_xyz", 0.5, storage=True) | {"viewport": {"w": 1, "h": 1}}
    source = effect(
        write,
        kind="generator",
        iterated=True,
        outputTex="global_xyz",
        textures={"global_xyz": {"width": 3, "height": 2}},
    )
    result = render_probes(monkeypatch, {"source": source})("source()")
    assert (result.width, result.height) == (3, 2)


@pytest.mark.parametrize("later_declaration", [False, True])
def test_particle_group_uses_first_declaration_for_every_writer(monkeypatch, later_declaration):
    original = {"width": 1, "height": 2, "format": "rgba8"}
    other = {"global_vel": {"width": 2, "height": 1, "format": "rgba32f"}} if later_declaration else {}
    emit = effect(
        fill("global_vel", 0.25),
        kind="generator",
        iterated=True,
        textures={"global_xyz": {}, "global_vel": original},
        outputTex="global_vel",
    )
    write = effect(fill("global_vel", 0.5), textures=other, outputTex="global_vel")
    result = render_probes(monkeypatch, {"emit": emit, "edit": write})("emit().edit()")
    assert (result.width, result.height, result.format) == (1, 2, "rgba8")
    assert list(result.data) == [np.float32(128 / 255)] * 8


def test_first_particle_use_can_precede_declaration(monkeypatch):
    emit = effect(
        fill("global_vel", 0.5), kind="generator", iterated=True, textures={"global_xyz": {}}, outputTex="global_vel"
    )
    emit["params"]["stateSize"] = {"type": "int", "default": 2}
    reader = effect(
        pixel("inspect", src="global_vel"),
        textures={"global_vel": {"width": 1, "height": 2, "format": "rgba8"}, "outputTex": {"format": "rgba32f"}},
    )

    def inspect(ctx, out):
        src = ctx.textures["src"]
        out[:] = [src.width, src.height, src.data[0], 1]

    result = render_probes(monkeypatch, {"emit": emit, "reader": reader}, inspect=inspect)("emit().reader()")
    assert list(result.data[:4]) == [1, 2, np.float32(128 / 255), 1]


def test_writing_plain_input_uses_pass_viewport(monkeypatch):
    source = effect(fill("outputTex", 0.25), kind="generator")
    write = fill("inputTex", 0.5) | {"viewport": {"w": 1, "h": 1}}
    result = render_probes(monkeypatch, {"source": source, "edit": effect(write, outputTex="inputTex")})(
        "source().edit()"
    )
    assert (result.width, result.height) == (1, 1)


@pytest.mark.parametrize("iterated", [False, True])
def test_storage_only_mrt_hands_on_last_attachment(monkeypatch, iterated):
    render_pass = {
        "name": "split",
        "program": "split",
        "key": "split",
        "drawBuffers": 2,
        "storageTextures": {"left": "first", "right": "last"},
    }

    def split(_ctx, out):
        out[0][:] = [0.25] * 4
        out[1][:] = [0.75] * 4

    split.output_names = ("left", "right")
    render = render_probes(
        monkeypatch,
        {
            "split": effect(render_pass, kind="generator", iterated=iterated),
            "reader": effect(pixel("copy", src="inputTex")),
        },
        split=split,
    )
    assert render("split().reader()").to_rgba8() == bytes([191]) * 16


@pytest.mark.parametrize("iterated", [False, True])
def test_storage_only_mrt_checks_each_declared_size(monkeypatch, iterated):
    render_pass = {
        "name": "split",
        "program": "split",
        "key": "split",
        "drawBuffers": 2,
        "storageTextures": {"a": "left", "b": "right"},
    }

    def split(_ctx, out):
        out[0][:] = out[1][:] = [1.0] * 4

    split.output_names = ("a", "b")
    source = effect(
        render_pass,
        kind="generator",
        iterated=iterated,
        textures={"left": {"width": 1, "height": 1}, "right": {"width": 2, "height": 1}},
    )
    render = render_probes(monkeypatch, {"source": source}, split=split)
    with pytest.raises(ValueError, match="MRT destinations must share dimensions"):
        render("source()")


def test_mrt_particle_memory_inherits_size_without_own_state_size_param(monkeypatch):
    emit = effect(
        fill("global_xyz", 0.25),
        fill("outputTex", 0),
        kind="generator",
        iterated=True,
        textures={"global_xyz": {"width": {"param": "stateSize"}, "height": {"param": "stateSize"}}},
    )
    emit["params"]["stateSize"] = {"type": "int", "default": 2}
    size = {"param": "stateSize", "inherit": True, "default": 3}
    write = pixel("update")
    write["outputs"] = {"xyz": "global_xyz", "saved": "global_move_base_color"}

    def update(_ctx, out):
        out[0][:] = [0.25] * 4
        out[1][:] = [0.75] * 4

    update.output_names = ("xyz", "saved")
    move = effect(write, textures={"global_move_base_color": {"width": size, "height": size}})
    render = render_probes(monkeypatch, {"emit": emit, "move": move}, update=update)
    assert render("emit().move()").to_rgba8() == bytes([191]) * 16


@pytest.mark.parametrize("iterated, seed, expected", [(False, 1, 191), (False, 2, 128), (True, 1, 0), (True, 2, 128)])
def test_conditional_output_uses_ordinary_fallback_or_persistent_target(monkeypatch, iterated, seed, expected):
    conditional = fill("outputTex", 0.5)
    conditional["conditions"] = {"runIf": [{"uniform": "seed", "equals": 2}]}
    source = effect(
        fill("work", 0.75),
        conditional,
        kind="generator",
        iterated=iterated,
        outputTex="work",
        textures={"outputTex": {}},
    )
    source["params"]["seed"] = {"type": "int", "default": 1, "uniform": "seed"}
    render = render_probes(monkeypatch, {"source": source})
    assert render(f"source(seed: {seed})").to_rgba8() == bytes([expected]) * 16


@pytest.mark.parametrize("storage", [True, False])
@pytest.mark.parametrize("declared,iterated", [(False, False), (False, True), (True, False), (True, True)])
@pytest.mark.parametrize("seed", [1, 2])
def test_local_pass_input_requires_its_conditional_write(monkeypatch, seed, storage, declared, iterated):
    write = fill("work", 0.25, storage=storage)
    write["conditions"] = {"runIf": [{"uniform": "seed", "equals": 2}]}
    source = effect(
        fill("inputImage", 0.75),
        write,
        pixel("copy", src="work"),
        kind="generator",
        iterated=iterated,
        textures={"work": {}} if declared else {},
    )
    source["params"]["seed"] = {"type": "int", "default": 1, "uniform": "seed"}
    render = render_probes(monkeypatch, {"source": source})
    if seed == 1 and not (declared and iterated):
        with pytest.raises(ValueError, match='requires texture "work"'):
            render(f"source(seed: {seed})")
    else:
        assert render(f"source(seed: {seed})").to_rgba8() == bytes([0 if seed == 1 else 64]) * 16


def test_pass_input_requires_the_named_resource_even_if_sampler_is_bound(monkeypatch):
    source = effect(fill("outputTex", 0.75), kind="generator")
    read = effect(pixel("copy", src="missing"))
    read["params"]["src"] = {"type": "surface", "default": "inputTex"}
    render = render_probes(monkeypatch, {"source": source, "reader": read})
    with pytest.raises(ValueError, match='requires texture "missing"'):
        render("source().reader()")


def test_loop_first_tick_reads_cleared_accumulator_at_input_dimensions(monkeypatch):
    begin = effect(pixel("read", accum="global_accum"), iterated=True, loopRole="begin")
    begin["params"]["iterationCount"]["default"] = 1

    def read(ctx, out):
        accum = ctx.textures["accum"]
        out[:] = [accum.width / 4, accum.height / 4, accum.data[0], 1]

    render = render_probes(
        monkeypatch,
        {
            "source": effect(fill("outputTex", 0.75), kind="generator"),
            "begin": begin,
            "end": effect(pixel("copy", src="inputTex"), loopRole="end"),
        },
        read=read,
    )
    assert render("source().begin().end()").to_rgba8() == bytes([128, 128, 0, 255]) * 4


def test_unbound_surface_parameter_stays_transparent_after_another_pass(monkeypatch):
    source = effect(fill("unrelated", 0.75), pixel("copy", src="optional"), kind="generator")
    source["params"]["optional"] = {"type": "surface", "default": "none"}
    render = render_probes(monkeypatch, {"source": source})
    assert render("source()").to_rgba8() == bytes(16)


@pytest.mark.parametrize("blend, expected", [(False, 128), ([], 191)])
def test_storage_overwrite_respects_disabled_blend(monkeypatch, blend, expected):
    writer = effect(fill("global_work", 0.25, storage=True), kind="generator", outputTex="global_work")
    update = fill("global_work", 0.5, storage=True)
    update["blend"] = blend
    render = render_probes(monkeypatch, {"writer": writer, "edit": effect(update, outputTex="global_work")})
    assert render("writer().edit()").to_rgba8() == bytes([expected]) * 16


@pytest.mark.parametrize("speed_width", [1, 2])
def test_mrt_writes_each_published_channel_by_shader_output_name(monkeypatch, speed_width):
    source = effect(
        fill("positions", 0.125),
        fill("speed", 0.25),
        fill("outputTex", 0),
        kind="generator",
        outputXyz="positions",
        outputVel="speed",
        textures={"positions": {"width": 1, "height": 1}, "speed": {"width": speed_width, "height": 1}},
    )
    write = pixel("update")
    write["outputs"] = {"v": "inputVel", "x": "inputXyz"}

    def update(_ctx, out):
        out[0][:] = [0.5] * 4
        out[1][:] = [0.75] * 4

    update.output_names = ("x", "v")

    def read(ctx, out):
        x, v = ctx.textures["x"], ctx.textures["v"]
        out[:] = [x.data[0], v.data[0], x.width, v.height]

    render = render_probes(
        monkeypatch,
        {
            "source": source,
            "edit": effect(write, fill("outputTex", 0), textures={"outputXyz": {"width": 3, "height": 3}}),
            "reader": effect(pixel("read", x="inputXyz", v="inputVel")),
        },
        update=update,
        read=read,
    )
    if speed_width == 1:
        assert list(render("source().edit().reader()").data[:4]) == [0.5, 0.75, 1, 1]
    else:
        with pytest.raises(ValueError, match="MRT destinations must share dimensions"):
            render("source().edit().reader()")


def test_particle_emitter_after_named_read_starts_fresh_state(monkeypatch):
    render = render_probes(
        monkeypatch,
        {
            "first": effect(fill("outputTex", 0.125), kind="generator"),
            "emit": effect(
                fill("global_xyz", 0.75),
                fill("outputTex", 0),
                iterated=True,
                textures={"global_xyz": {"width": 1, "height": 1}},
                outputXyz="global_xyz",
            ),
            "reader": effect(pixel("copy", src="inputXyz")),
        },
    )
    assert render("first().write(o1)\nread(o1).emit().reader()").to_rgba8() == bytes([191]) * 16


@pytest.mark.parametrize("effect_id", ["filter/warp", "classicNoisedeck/glitch", "synth/media", "filter/text"])
def test_standalone_effect_with_no_source_image_renders_transparent(effect_id):
    frame = renderer.render_effect(effect_id, width=8, height=8, seed=1)
    assert frame.to_rgba8() == bytes(8 * 8 * 4)


def test_standalone_filter_uses_last_pass_when_source_image_is_absent(monkeypatch):
    render_probes(monkeypatch, {"filter": effect(fill("temp", 0.25), pixel("copy", src="inputTex"))})
    frame = renderer.render_effect("probe/filter", width=2, height=2)
    assert frame.to_rgba8() == bytes([64]) * 16


@pytest.mark.parametrize("source", ["global_xyz", "global_vel", "unbound"])
@pytest.mark.parametrize("binding", ["clear", "last-pass", "explicit-sampler", "explicit-source"])
@pytest.mark.parametrize("iterated", [False, True])
@pytest.mark.parametrize("declared", [False, True])
def test_standalone_texture_binding_order(monkeypatch, source, binding, iterated, declared):
    inputs = {}
    passes = []
    if binding != "clear":
        passes.append(fill("temp", 0.25))
    if binding == "explicit-sampler":
        inputs["src"] = renderer.Surface(4, 1)
        inputs["src"].data[:] = 0.5
    if binding == "explicit-source":
        inputs[source] = renderer.Surface(1, 4)
        inputs[source].data[:] = 0.75

    observed = set()

    def inspect_source(ctx, out):
        texture = ctx.textures["src"]
        observed.add((texture.width, texture.height, float(texture.data[0])))
        out[:] = texture.data[:4]

    passes.append(pixel("inspect", src=source))
    if declared:
        passes.append(fill(source, 0))
    probe = effect(*passes, iterated=iterated)
    if declared:
        probe["textures"] = {source: {"width": 2, "height": 4}}
    probe["params"]["stateSize"] = {"type": "int", "default": 3}
    render_probes(monkeypatch, {"filter": probe}, inspect=inspect_source)
    renderer.render_effect("probe/filter", inputs=inputs, width=2, height=2)
    expected = {
        "clear": (1, 1, 0.0) if source == "unbound" else (3, 3, 0.0),
        "last-pass": (2, 2, 0.25),
        "explicit-sampler": (4, 1, 0.5),
        "explicit-source": (1, 4, 0.75),
    }
    assert observed == {(2, 4, 0.0) if declared else expected[binding]}


@pytest.mark.parametrize("source,expected", [("work", [0.25, 0.5, 0.5, 0.5]), ("inputTex", [0.25] * 4)])
def test_standalone_inputs_and_writes_across_ticks(monkeypatch, source, expected):
    observed = []

    def inspect_source(ctx, out):
        observed.append(float(ctx.textures["src"].data[0]))
        out[:] = [0.0] * 4

    read = pixel("inspect", src=source)
    render_probes(monkeypatch, {"filter": effect(read, fill(source, 0.5), read, iterated=True)}, inspect=inspect_source)
    supplied = renderer.Surface(1, 1)
    supplied.data[:] = 0.25
    renderer.render_effect("probe/filter", inputs={source: supplied}, width=1, height=1)
    assert observed == expected


@pytest.mark.parametrize("destination", ["aux", "inputTex"])
def test_standalone_can_publish_its_original_input(monkeypatch, destination):
    render_probes(monkeypatch, {"filter": effect(fill(destination, 0.5), outputTex="inputTex")})
    supplied = renderer.Surface(2, 1)
    supplied.data[:] = 0.25
    frame = renderer.render_effect("probe/filter", inputs={"inputTex": supplied}, width=1, height=1)
    assert frame is supplied
