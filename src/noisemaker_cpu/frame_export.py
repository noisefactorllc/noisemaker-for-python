"""Bounded frame-export queue and synchronous CPU surface adapter."""

from __future__ import annotations

import math
from contextlib import suppress
from dataclasses import dataclass

import numpy as np

from .surface import Surface


def _validate_adapter(adapter) -> None:
    methods = ("create_slot", "begin", "poll", "read", "destroy_slot")
    if adapter is None or any(not callable(getattr(adapter, name, None)) for name in methods):
        raise TypeError("Frame export adapter must implement create_slot, begin, poll, read, and destroy_slot")


@dataclass
class _QueueSlot:
    adapter_slot: object | None = None
    created: bool = False
    pending: bool = False
    frame: object | None = None
    timestamp: object | None = None
    on_frame: object | None = None
    context: object | None = None


class FrameExportQueue:
    """A bounded, polling export queue with stable reusable adapter slots."""

    def __init__(self, adapter, *, slots=3, on_error=None):
        _validate_adapter(adapter)
        if not isinstance(slots, int) or isinstance(slots, bool) or not 2 <= slots <= 8:
            raise ValueError("Frame export slots must be an integer from 2 through 8")
        self.adapter = adapter
        self._on_error = on_error
        self._slots = [_QueueSlot() for _ in range(slots)]
        self._configured = False
        self._closed = False
        self.stats = {"accepted": 0, "dropped": 0, "completed": 0, "failed": 0}

    @property
    def available(self) -> bool:
        return self._configured and not self._closed and any(not slot.pending for slot in self._slots)

    def configure(self, descriptor) -> None:
        if self._closed:
            return
        destroy_error = self._destroy_slots()
        self._configured = False
        if destroy_error is not None:
            raise destroy_error
        try:
            for index, record in enumerate(self._slots):
                record.adapter_slot = self.adapter.create_slot(index, descriptor)
                record.created = True
        except Exception:
            cleanup_error = self._destroy_slots()
            if cleanup_error is not None:
                self._report(cleanup_error)
            raise
        self._configured = True

    def enqueue(self, frame, timestamp, on_frame, context=None) -> bool:
        if not callable(on_frame):
            raise TypeError("Frame export callback must be callable")
        if not self._configured or self._closed:
            self.stats["dropped"] += 1
            return False
        record = next((slot for slot in self._slots if not slot.pending), None)
        if record is None:
            self.stats["dropped"] += 1
            return False
        record.pending = True
        record.frame = frame
        record.timestamp = timestamp
        record.on_frame = on_frame
        record.context = context
        try:
            self.adapter.begin(record.adapter_slot, frame, timestamp)
        except Exception as error:
            self._release(record)
            self.stats["failed"] += 1
            self._report(error)
            return False
        self.stats["accepted"] += 1
        return True

    def poll(self) -> None:
        if not self._configured or self._closed:
            return
        for record in self._slots:
            if not record.pending:
                continue
            try:
                ready = self.adapter.poll(record.adapter_slot)
                if ready is False:
                    continue
                if ready is not True:
                    raise TypeError("Frame export adapter poll must return a boolean")
                frame = self.adapter.read(record.adapter_slot)
                timestamp = record.timestamp
                on_frame = record.on_frame
                context = record.context
            except Exception as error:
                self._release(record)
                self.stats["failed"] += 1
                self._report(error)
                continue
            self._release(record)
            try:
                on_frame(frame, timestamp, context)
                self.stats["completed"] += 1
            except Exception as error:
                self.stats["failed"] += 1
                self._report(error)

    def close(self, *, backend_lost=False) -> None:
        if self._closed:
            return
        self._closed = True
        self._configured = False
        if backend_lost:
            self._abandon_slots()
            destroy_error = None
        else:
            destroy_error = self._destroy_slots()
        self.adapter = None
        if destroy_error is not None:
            raise destroy_error

    @staticmethod
    def _release(record) -> None:
        record.pending = False
        record.frame = None
        record.timestamp = None
        record.on_frame = None
        record.context = None

    def _destroy_slots(self):
        first_error = None
        for record in self._slots:
            if not record.created:
                continue
            adapter_slot = record.adapter_slot
            record.created = False
            record.adapter_slot = None
            self._release(record)
            try:
                self.adapter.destroy_slot(adapter_slot)
            except Exception as error:
                if first_error is None:
                    first_error = error
        return first_error

    def _abandon_slots(self) -> None:
        for record in self._slots:
            record.created = False
            record.adapter_slot = None
            self._release(record)

    def _report(self, error) -> None:
        if not callable(self._on_error):
            return
        with suppress(Exception):
            self._on_error(error)


@dataclass
class FrameExportFrame:
    width: int
    height: int
    row_stride: int
    data: bytearray


@dataclass
class _CpuSlot:
    index: int
    width: int
    height: int
    alpha_mode: str
    data: bytearray
    frame: FrameExportFrame
    ready: bool = False
    destroyed: bool = False


def _validate_descriptor(descriptor) -> int:
    if not isinstance(descriptor, dict):
        raise TypeError("Frame export descriptor must be a dict")
    width = descriptor.get("width")
    height = descriptor.get("height")
    if not isinstance(width, int) or isinstance(width, bool) or width <= 0:
        raise ValueError("Frame export width must be a positive integer")
    if not isinstance(height, int) or isinstance(height, bool) or height <= 0:
        raise ValueError("Frame export height must be a positive integer")
    if descriptor.get("format") != "rgba8unorm":
        raise TypeError("CPU frame export format must be 'rgba8unorm'")
    if descriptor.get("colorSpace") not in {"srgb", "display-p3"}:
        raise TypeError("CPU frame export colorSpace must be 'srgb' or 'display-p3'")
    if descriptor.get("alphaMode") not in {"opaque", "straight", "premultiplied"}:
        raise TypeError("CPU frame export alphaMode must be 'opaque', 'straight', or 'premultiplied'")
    fps = descriptor.get("fps")
    if isinstance(fps, bool) or not isinstance(fps, (int, float)) or not math.isfinite(fps) or fps <= 0:
        raise ValueError("Frame export fps must be finite and positive")
    return width * height * 4


class CpuFrameExportAdapter:
    """Synchronously copy top-down float32 surfaces into reusable RGBA8 slots."""

    def create_slot(self, index, descriptor):
        byte_length = _validate_descriptor(descriptor)
        data = bytearray(byte_length)
        frame = FrameExportFrame(descriptor["width"], descriptor["height"], descriptor["width"] * 4, data)
        return _CpuSlot(index, descriptor["width"], descriptor["height"], descriptor["alphaMode"], data, frame)

    def begin(self, slot, surface, timestamp=None) -> None:
        self._assert_usable(slot)
        if slot.ready:
            raise RuntimeError("CPU frame export slot is already pending")
        if not isinstance(surface, Surface):
            raise TypeError("CPU frame export requires a Surface frame")
        if surface.width != slot.width or surface.height != slot.height:
            raise RuntimeError(
                f"CPU frame export source extent {surface.width}x{surface.height} "
                f"does not match configured extent {slot.width}x{slot.height}"
            )

        source = np.asarray(surface.data, dtype=np.float64).reshape(-1, 4)
        values = source.copy()
        alpha = source[:, 3]
        if slot.alpha_mode == "premultiplied":
            values[:, :3] *= alpha[:, None]
        if slot.alpha_mode == "opaque":
            values[:, 3] = 1.0
        finite = np.where(np.isfinite(values), values, 0.0)
        quantized = np.floor(np.clip(finite, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)
        slot.data[:] = quantized.reshape(-1).tobytes()
        slot.ready = True

    def poll(self, slot) -> bool:
        self._assert_usable(slot)
        return slot.ready

    def read(self, slot):
        self._assert_usable(slot)
        if not slot.ready:
            raise RuntimeError("CPU frame export slot is not ready")
        slot.ready = False
        return slot.frame

    @staticmethod
    def destroy_slot(slot) -> None:
        if slot is None or slot.destroyed:
            return
        slot.destroyed = True
        slot.ready = False

    @staticmethod
    def _assert_usable(slot) -> None:
        if slot is None or slot.destroyed:
            raise RuntimeError("CPU frame export slot is not usable")
