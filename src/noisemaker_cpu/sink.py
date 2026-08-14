"""Output sink lifecycle and failure isolation."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from contextlib import suppress
from dataclasses import dataclass


def _validate_sink(sink) -> None:
    if sink is None or any(not callable(getattr(sink, name, None)) for name in ("configure", "submit", "close")):
        raise TypeError("Sink must implement configure, submit, and close")


class _IdentityStats(Mapping):
    def __init__(self):
        self._values = {}

    def __getitem__(self, sink):
        entry = self._values.get(id(sink))
        if entry is None or entry[0] is not sink:
            raise KeyError(sink)
        return entry[1]

    def __iter__(self) -> Iterator:
        return (entry[0] for entry in self._values.values())

    def __len__(self) -> int:
        return len(self._values)

    def add(self, sink, stats) -> None:
        self._values[id(sink)] = (sink, stats)

    def remove(self, sink) -> None:
        entry = self._values.get(id(sink))
        if entry is not None and entry[0] is sink:
            del self._values[id(sink)]

    def clear(self) -> None:
        self._values.clear()


@dataclass
class _Registration:
    sink: object | None
    stats: dict
    active: bool = True


class SinkManager:
    """Configure and submit to independent sinks without coupling their failures."""

    def __init__(self, *, on_error=None):
        self._on_error = on_error
        self._registrations = []
        self._registrations_by_id = {}
        self._stats = _IdentityStats()
        self._descriptor = {}
        self._configured = False
        self._closed = False
        self._iteration_depth = 0
        self._has_tombstones = False

    @property
    def stats(self):
        return self._stats

    def add(self, sink):
        if self._closed:
            raise RuntimeError("SinkManager is closed")
        _validate_sink(sink)
        existing = self._registrations_by_id.get(id(sink))
        if existing is not None and existing.sink is sink:
            raise RuntimeError("Sink is already registered")
        if self._configured:
            sink.configure(self._descriptor)

        stats = {"accepted": 0, "dropped": 0, "failed": 0}
        registration = _Registration(sink, stats)
        self._registrations.append(registration)
        self._registrations_by_id[id(sink)] = registration
        self._stats.add(sink, stats)
        removed = False

        def remove():
            nonlocal removed
            if removed:
                return
            removed = True
            self._remove_registration(registration)

        return remove

    def remove(self, sink) -> None:
        registration = self._registrations_by_id.get(id(sink))
        if registration is not None and registration.sink is sink:
            self._remove_registration(registration)

    def _remove_registration(self, registration) -> None:
        if registration is None or not registration.active:
            return
        sink = registration.sink
        registration.active = False
        registration.sink = None
        self._has_tombstones = True
        if self._registrations_by_id.get(id(sink)) is registration:
            del self._registrations_by_id[id(sink)]
            self._stats.remove(sink)
        try:
            sink.close()
        finally:
            if self._iteration_depth == 0:
                self._compact_registrations()

    def _compact_registrations(self) -> None:
        if self._has_tombstones:
            self._registrations = [registration for registration in self._registrations if registration.active]
            self._has_tombstones = False

    def configure(self, descriptor=None) -> None:
        if self._closed:
            return
        self._descriptor = {} if descriptor is None else descriptor
        self._configured = True
        self._iteration_depth += 1
        try:
            for registration in self._registrations:
                if not registration.active:
                    continue
                sink = registration.sink
                try:
                    sink.configure(self._descriptor)
                except Exception as error:
                    registration.stats["failed"] += 1
                    self._report(error, sink)
        finally:
            self._iteration_depth -= 1
            if self._iteration_depth == 0:
                self._compact_registrations()

    def submit(self, frame, timestamp) -> None:
        if self._closed:
            return
        self._iteration_depth += 1
        try:
            for registration in self._registrations:
                if not registration.active:
                    continue
                sink = registration.sink
                try:
                    result = sink.submit(frame, timestamp)
                except Exception as error:
                    registration.stats["failed"] += 1
                    self._report(error, sink)
                    continue
                if result is True:
                    registration.stats["accepted"] += 1
                elif result is False:
                    registration.stats["dropped"] += 1
        finally:
            self._iteration_depth -= 1
            if self._iteration_depth == 0:
                self._compact_registrations()

    def close(self, options=None) -> None:
        if self._closed:
            return
        self._closed = True
        first_error = None
        for registration in self._registrations:
            if not registration.active:
                continue
            sink = registration.sink
            registration.active = False
            registration.sink = None
            try:
                if options is None:
                    sink.close()
                else:
                    sink.close(options)
            except Exception as error:
                if first_error is None:
                    first_error = error
        self._registrations.clear()
        self._registrations_by_id.clear()
        self._stats.clear()
        self._has_tombstones = False
        if first_error is not None:
            raise first_error

    def _report(self, error, sink) -> None:
        if not callable(self._on_error):
            return
        with suppress(Exception):
            self._on_error(error, sink)
