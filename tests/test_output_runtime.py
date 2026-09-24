from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pytest

import noisemaker_cpu
from noisemaker_cpu.frame_export import CpuFrameExportAdapter, FrameExportQueue
from noisemaker_cpu.renderer import CpuRenderer
from noisemaker_cpu.sink import SinkManager
from noisemaker_cpu.surface import Surface


class RecordingSink:
    def __init__(self, submit_result=True):
        self.events = []
        self.submit_result = submit_result

    def configure(self, descriptor):
        self.events.append(("configure", dict(descriptor)))

    def submit(self, frame, timestamp):
        self.events.append(("submit", frame, timestamp))
        if isinstance(self.submit_result, Exception):
            raise self.submit_result
        return self.submit_result

    def close(self, options=None):
        self.events.append(("close", options))


class FakeAdapter:
    def __init__(self):
        self.slots = []
        self.destroy_error = None

    def create_slot(self, index, descriptor):
        slot = SimpleNamespace(index=index, descriptor=descriptor, ready=False, value=None, destroys=0)
        self.slots.append(slot)
        return slot

    def begin(self, slot, value, timestamp):
        slot.ready = False
        slot.value = value

    def poll(self, slot):
        return slot.ready

    def read(self, slot):
        return slot.value

    def destroy_slot(self, slot):
        slot.destroys += 1
        if self.destroy_error == slot.index:
            raise RuntimeError(f"destroy {slot.index} failed")


def export_bytes(surface, alpha_mode):
    queue = FrameExportQueue(CpuFrameExportAdapter(), slots=2)
    received = []
    queue.configure(
        {
            "width": surface.width,
            "height": surface.height,
            "format": "rgba8unorm",
            "colorSpace": "srgb",
            "alphaMode": alpha_mode,
            "fps": 60,
        }
    )
    assert queue.enqueue(surface, 42, lambda frame, _timestamp, _context: received.append(bytes(frame.data)))
    queue.poll()
    queue.close()
    return received[0]


def test_public_api_exports_output_runtime():
    assert noisemaker_cpu.CpuFrameExportAdapter is CpuFrameExportAdapter
    assert noisemaker_cpu.CpuRenderer is CpuRenderer
    assert noisemaker_cpu.FrameExportQueue is FrameExportQueue
    assert noisemaker_cpu.SinkManager is SinkManager


def test_sink_manager_configures_current_and_later_sinks():
    first = RecordingSink()
    later = RecordingSink()
    manager = SinkManager()
    descriptor = {"width": 2, "height": 3}

    manager.add(first)
    manager.configure(descriptor)
    manager.add(later)

    assert first.events == [("configure", descriptor)]
    assert later.events == [("configure", descriptor)]


def test_sink_manager_counts_outcomes_and_isolates_sink_and_reporter_failures():
    reported = []
    accepted = RecordingSink(True)
    dropped = RecordingSink(False)
    failed = RecordingSink(RuntimeError("sink failed"))
    later = RecordingSink(True)

    def report(error, sink):
        reported.append((str(error), sink))
        raise RuntimeError("reporter failed")

    manager = SinkManager(on_error=report)
    for sink in (accepted, dropped, failed, later):
        manager.add(sink)

    manager.submit(Surface(1, 1), 10)

    assert manager.stats.get(accepted) == {"accepted": 1, "dropped": 0, "failed": 0}
    assert manager.stats.get(dropped) == {"accepted": 0, "dropped": 1, "failed": 0}
    assert manager.stats.get(failed) == {"accepted": 0, "dropped": 0, "failed": 1}
    assert manager.stats.get(later) == {"accepted": 1, "dropped": 0, "failed": 0}
    assert reported == [("sink failed", failed)]


def test_sink_manager_removal_during_submission_does_not_skip_later_sink():
    manager = SinkManager()
    events = []

    class SelfRemovingSink(RecordingSink):
        def submit(self, frame, timestamp):
            manager.remove(self)
            return True

        def close(self, options=None):
            events.append("self close")

    self_removing = SelfRemovingSink()
    later = RecordingSink()
    manager.add(self_removing)
    manager.add(later)

    manager.submit(Surface(1, 1), 20)

    assert events == ["self close"]
    assert [event[0] for event in later.events] == ["submit"]
    assert self_removing not in manager.stats


def test_sink_manager_close_is_terminal_and_closes_every_sink_after_an_error():
    closes = []

    class ClosingSink(RecordingSink):
        def __init__(self, name, error=None):
            super().__init__()
            self.name = name
            self.error = error

        def close(self, options=None):
            closes.append((self.name, options))
            if self.error:
                raise self.error

    manager = SinkManager()
    manager.add(ClosingSink("first", RuntimeError("first close failed")))
    manager.add(ClosingSink("second"))

    with pytest.raises(RuntimeError, match="first close failed"):
        manager.close({"backendLost": True})
    manager.close()

    assert closes == [("first", {"backendLost": True}), ("second", {"backendLost": True})]
    with pytest.raises(RuntimeError, match="closed"):
        manager.add(RecordingSink())


def test_sink_manager_should_defer_render_reports_sink_deferral_handles_exceptions_and_honors_unregister():
    reported = []
    manager = SinkManager(on_error=lambda error, sink: reported.append((str(error), sink)))

    defer = False

    class DeferringSink(RecordingSink):
        def defer_render(self):
            return defer

    regular_sink = RecordingSink()

    class ThrowingSink(RecordingSink):
        def defer_render(self):
            raise RuntimeError("defer failed")

    deferring_sink = DeferringSink()
    throwing_sink = ThrowingSink()

    assert manager.should_defer_render() is False
    assert manager.shouldDeferRender() is False
    manager.add(regular_sink)
    assert manager.should_defer_render() is False

    unregister = manager.add(deferring_sink)
    assert manager.should_defer_render() is False

    # Non-boolean truthy values must not trigger deferral (strict boolean True required)
    defer = 1
    assert manager.should_defer_render() is False
    defer = "yes"
    assert manager.should_defer_render() is False

    defer = True
    assert manager.should_defer_render() is True
    assert manager.shouldDeferRender() is True

    defer = False
    manager.add(throwing_sink)
    # Throwing sink does not cause should_defer_render to raise or defer; reported via on_error
    assert manager.should_defer_render() is False
    assert len(reported) > 0
    assert manager.stats.get(throwing_sink)["failed"] > 0

    defer = True
    assert manager.should_defer_render() is True

    unregister()
    assert manager.should_defer_render() is False

    # CamelCase deferRender is also recognized
    camel_defer = True

    class CamelCaseSink(RecordingSink):
        def deferRender(self):
            return camel_defer

    camel_sink = CamelCaseSink()
    remove_camel = manager.add(camel_sink)
    assert manager.should_defer_render() is True
    camel_defer = False
    assert manager.should_defer_render() is False
    remove_camel()

    # Non-callable defer_render attribute falls back to callable deferRender method
    class HybridSink(RecordingSink):
        def __init__(self):
            super().__init__()
            self.defer_render = "not-callable"

        def deferRender(self):
            return True

    hybrid_sink = HybridSink()
    remove_hybrid = manager.add(hybrid_sink)
    assert manager.should_defer_render() is True
    remove_hybrid()

    manager.close()
    assert manager.should_defer_render() is False


def test_cpu_renderer_delegates_should_defer_render_to_sink_manager():
    renderer = CpuRenderer()
    assert callable(renderer.should_defer_render)
    assert callable(renderer.shouldDeferRender)
    assert renderer.should_defer_render() is False
    assert renderer.shouldDeferRender() is False

    defer = False

    class DeferringSink(RecordingSink):
        def defer_render(self):
            return defer

    deferring_sink = DeferringSink()
    remove = renderer.add_sink(deferring_sink)

    assert renderer.should_defer_render() is False
    defer = True
    assert renderer.should_defer_render() is True
    assert renderer.shouldDeferRender() is True

    remove()
    assert renderer.should_defer_render() is False


def test_frame_export_queue_validates_adapter_and_bounded_slot_count():
    with pytest.raises(TypeError, match="adapter"):
        FrameExportQueue(object())
    with pytest.raises(ValueError, match="2 through 8"):
        FrameExportQueue(FakeAdapter(), slots=1)
    with pytest.raises(ValueError, match="2 through 8"):
        FrameExportQueue(FakeAdapter(), slots=9)


def test_frame_export_queue_drops_overflow_preserves_context_and_reuses_slots():
    adapter = FakeAdapter()
    queue = FrameExportQueue(adapter, slots=2)
    completed = []
    context = {"sequence": 7}
    queue.configure({"width": 1, "height": 1})

    def callback(frame, timestamp, value):
        completed.append((frame, timestamp, value))

    assert queue.enqueue("one", 10, callback, context)
    assert queue.enqueue("two", 20, lambda *_args: None)
    assert not queue.enqueue("overflow", 30, lambda *_args: None)
    adapter.slots[0].ready = True
    queue.poll()

    assert completed == [("one", 10, context)]
    assert queue.enqueue("replacement", 40, lambda *_args: None)
    assert queue.stats == {"accepted": 3, "dropped": 1, "completed": 1, "failed": 0}


def test_frame_export_queue_isolates_callback_failures_and_remains_reusable():
    errors = []
    adapter = FakeAdapter()
    queue = FrameExportQueue(adapter, slots=2, on_error=lambda error: errors.append(str(error)))
    queue.configure({"width": 1, "height": 1})

    def fail(*_args):
        raise RuntimeError("callback failed")

    queue.enqueue("one", 10, fail)
    adapter.slots[0].ready = True
    queue.poll()

    assert errors == ["callback failed"]
    assert queue.available
    assert queue.stats == {"accepted": 1, "dropped": 0, "completed": 0, "failed": 1}


def test_frame_export_queue_rolls_back_partial_configuration():
    class FailingAdapter(FakeAdapter):
        def create_slot(self, index, descriptor):
            if index == 1:
                raise RuntimeError("slot creation failed")
            return super().create_slot(index, descriptor)

    adapter = FailingAdapter()
    queue = FrameExportQueue(adapter, slots=2)

    with pytest.raises(RuntimeError, match="slot creation failed"):
        queue.configure({"width": 1, "height": 1})

    assert [slot.destroys for slot in adapter.slots] == [1]
    assert not queue.available


def test_frame_export_queue_close_destroys_every_slot_once_and_backend_loss_abandons_slots():
    adapter = FakeAdapter()
    queue = FrameExportQueue(adapter, slots=2)
    queue.configure({"width": 1, "height": 1})
    adapter.destroy_error = 0

    with pytest.raises(RuntimeError, match="destroy 0 failed"):
        queue.close()
    queue.close()

    assert [slot.destroys for slot in adapter.slots] == [1, 1]
    assert not queue.available
    assert not queue.enqueue("late", 0, lambda *_args: None)

    lost_adapter = FakeAdapter()
    lost_queue = FrameExportQueue(lost_adapter, slots=2)
    lost_queue.configure({"width": 1, "height": 1})
    lost_queue.close(backend_lost=True)
    assert [slot.destroys for slot in lost_adapter.slots] == [0, 0]


def test_cpu_frame_export_copies_top_down_rows_into_stable_reusable_storage():
    surface = Surface(1, 2, np.array([1, 0, 0.5, 1, 0, 0.25, 1, 1], dtype=np.float32))
    queue = FrameExportQueue(CpuFrameExportAdapter(), slots=2)
    frames = []
    queue.configure(
        {"width": 1, "height": 2, "format": "rgba8unorm", "colorSpace": "srgb", "alphaMode": "straight", "fps": 60}
    )

    assert queue.enqueue(surface, 42, lambda frame, *_args: frames.append((frame, bytes(frame.data))))
    surface.clear([0, 1, 0, 1])
    queue.poll()
    first_frame = frames[0][0]
    assert queue.enqueue(surface, 43, lambda frame, *_args: frames.append((frame, bytes(frame.data))))
    queue.poll()

    assert frames[0][1] == bytes([255, 0, 128, 255, 0, 64, 255, 255])
    assert frames[1][1] == bytes([0, 255, 0, 255] * 2)
    assert frames[1][0] is first_frame
    assert frames[1][0].data is first_frame.data


def test_cpu_frame_export_applies_all_alpha_modes_before_one_quantization():
    surface = Surface(1, 2, np.array([2, 0.002, 0.5, 0.25, -1, 0.5, 1.5, 0.5], dtype=np.float32))

    assert export_bytes(surface, "straight") == bytes([255, 1, 128, 64, 0, 128, 255, 128])
    assert export_bytes(surface, "opaque") == bytes([255, 1, 128, 255, 0, 128, 255, 255])
    assert export_bytes(surface, "premultiplied") == bytes([128, 0, 32, 64, 0, 64, 191, 128])


def test_cpu_frame_export_rejects_extent_mismatch_without_consuming_a_slot():
    errors = []
    queue = FrameExportQueue(CpuFrameExportAdapter(), slots=2, on_error=lambda error: errors.append(str(error)))
    queue.configure(
        {"width": 2, "height": 1, "format": "rgba8unorm", "colorSpace": "srgb", "alphaMode": "straight", "fps": 60}
    )

    assert not queue.enqueue(Surface(1, 1), 0, lambda *_args: None)

    assert errors == ["CPU frame export source extent 1x1 does not match configured extent 2x1"]
    assert queue.stats == {"accepted": 0, "dropped": 0, "completed": 0, "failed": 1}
    assert queue.available


def test_cpu_frame_export_adapter_direct_lifecycle_and_alpha_modes():
    adapter = CpuFrameExportAdapter()
    slot = adapter.create_slot(
        0, {"width": 2, "height": 1, "format": "rgba8unorm", "colorSpace": "srgb", "alphaMode": "straight", "fps": 30}
    )
    assert slot.index == 0
    assert not slot.ready
    assert adapter.poll(slot) is False

    frame = Surface(2, 1, np.array([0.5, 0.2, 0.8, 1.0, 0.0, 1.0, 0.0, 0.5], dtype=np.float32))
    adapter.begin(slot, frame)
    assert adapter.poll(slot) is True

    read_frame = adapter.read(slot)
    assert read_frame.width == 2
    assert read_frame.height == 1
    assert list(read_frame.data) == [128, 51, 204, 255, 0, 255, 0, 128]
    assert adapter.poll(slot) is False

    opaque_slot = adapter.create_slot(
        1, {"width": 1, "height": 1, "format": "rgba8unorm", "colorSpace": "srgb", "alphaMode": "opaque", "fps": 30}
    )
    adapter.begin(opaque_slot, Surface(1, 1, np.array([0.25, 0.5, 0.75, 0.1], dtype=np.float32)))
    assert list(adapter.read(opaque_slot).data) == [64, 128, 191, 255]

    premul_slot = adapter.create_slot(
        2,
        {
            "width": 1,
            "height": 1,
            "format": "rgba8unorm",
            "colorSpace": "srgb",
            "alphaMode": "premultiplied",
            "fps": 30,
        },
    )
    adapter.begin(premul_slot, Surface(1, 1, np.array([0.5, 1.0, 0.25, 0.5], dtype=np.float32)))
    assert list(adapter.read(premul_slot).data) == [64, 128, 32, 128]

    adapter.destroy_slot(slot)
    with pytest.raises(RuntimeError, match="not usable"):
        adapter.begin(slot, frame)
    with pytest.raises(RuntimeError, match="not usable"):
        adapter.poll(slot)
    with pytest.raises(RuntimeError, match="not usable"):
        adapter.read(slot)

    adapter.destroy_slot(opaque_slot)
    with pytest.raises(RuntimeError, match="not usable"):
        adapter.poll(opaque_slot)

    adapter.destroy_slot(premul_slot)
    with pytest.raises(RuntimeError, match="not usable"):
        adapter.poll(premul_slot)


def test_cpu_renderer_configures_and_submits_successful_frames_with_explicit_timestamps():
    renderer = CpuRenderer()
    sink = RecordingSink()
    renderer.add_sink(sink)
    source = "search synth\nsolid(color: [0.2, 0.4, 0.6]).write(o0)\nrender(o0)"

    first = renderer.render(source, width=2, height=1, presentation_timestamp=100)
    second = renderer.render(source, width=2, height=1, presentation_timestamp=200)
    third = renderer.render(source, width=3, height=1, presentation_timestamp=300)

    assert [event[0] for event in sink.events] == ["configure", "submit", "submit", "configure", "submit"]
    assert sink.events[0][1] == {
        "width": 2,
        "height": 1,
        "format": "rgba8unorm",
        "colorSpace": "srgb",
        "alphaMode": "straight",
        "fps": 60,
    }
    assert sink.events[1] == ("submit", first, 100)
    assert sink.events[2] == ("submit", second, 200)
    assert sink.events[4] == ("submit", third, 300)
    assert renderer.sink_manager.stats.get(sink) == {"accepted": 3, "dropped": 0, "failed": 0}


def test_cpu_renderer_does_not_submit_failed_renders_and_dispose_is_idempotent():
    renderer = CpuRenderer()
    sink = RecordingSink()
    renderer.add_sink(sink)

    with pytest.raises(ValueError, match="has not been written"):
        renderer.render("search filter\nread(o4).invert().write(o0)\nrender(o0)", width=1, height=1)

    assert [event[0] for event in sink.events] == ["configure"]
    renderer.dispose()
    renderer.dispose()
    assert [event[0] for event in sink.events] == ["configure", "close"]
    with pytest.raises(RuntimeError, match="closed"):
        renderer.add_sink(RecordingSink())


@pytest.mark.parametrize(
    ("options", "message"),
    [
        ({"width": 0}, "width must be a positive integer"),
        ({"height": True}, "height must be a positive integer"),
        ({"seed": 1.5}, "seed must be an integer"),
        ({"time": float("nan")}, "time must be finite"),
    ],
)
def test_cpu_renderer_rejects_invalid_options_before_configuring_sinks(options, message):
    renderer = CpuRenderer()
    sink = RecordingSink()
    renderer.add_sink(sink)

    with pytest.raises((TypeError, ValueError), match=message):
        renderer.render("search synth\nsolid().write(o0)\nrender(o0)", **options)

    assert sink.events == []
