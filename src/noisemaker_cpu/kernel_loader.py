"""Kernel loader + size-bounded LRU cache for runtime-compiled kernel source.

There is no direct JS file to port here: this is the Python analogue of the
`new Function(...)` + `Map` cache in noisemaker-cpu `src/csl/compiler.js`. JS
builds a callable from generated source text via `new Function` and memoizes
it in a `Map` keyed by source + options. Here we `exec` generated Python
source (a top-level ``def run_pixel(ctx, out): ...``) into a fresh namespace
to obtain the callable, and memoize it in `KernelCache`, an ``OrderedDict``-
based LRU keyed by an opaque string the caller supplies (e.g. a hash of the
transpiled source + compile options), bounded by total source byte size
rather than entry count.
"""

from __future__ import annotations

from collections import OrderedDict
from typing import Callable, NamedTuple

Kernel = Callable[..., object]
SourceFactory = Callable[[], str]


def load_kernel(source: str, name: str = "run_pixel") -> Kernel:
    """Compile ``source`` and return the top-level function named ``name``.

    ``source`` is Python text defining a module-level function, e.g.::

        def run_pixel(ctx, out):
            ...

    It is compiled with ``compile(source, f"<kernel:{name}>", "exec")`` and
    executed into a fresh namespace dict; ``ns[name]`` is returned.

    Raises ``NameError`` if ``name`` is not defined by ``source`` after
    execution, and ``TypeError`` if the binding exists but is not callable.
    """
    code = compile(source, f"<kernel:{name}>", "exec")
    namespace: dict[str, object] = {}
    exec(code, namespace)
    try:
        kernel = namespace[name]
    except KeyError as exc:
        raise NameError(f"kernel source did not define {name!r}") from exc
    if not callable(kernel):
        raise TypeError(f"kernel source defines {name!r} but it is not callable")
    return kernel


class _Entry(NamedTuple):
    kernel: Kernel
    size: int


class KernelCache:
    """Size-bounded LRU cache of compiled kernel callables.

    Keys are opaque strings supplied by the caller. On a miss, ``get`` calls
    ``source_factory()`` to obtain source text, compiles it via
    `load_kernel`, and stores it. Entries are evicted least-recently-used
    first whenever the summed UTF-8 byte size of cached sources exceeds
    ``max_bytes``; accessing a key (hit or fresh insert) marks it
    most-recently-used. A single entry larger than ``max_bytes`` is still
    cached in full — it is simply never evicted while it is the only entry,
    rather than triggering an infinite eviction loop.
    """

    def __init__(self, max_bytes: int = 64 * 1024 * 1024):
        self.max_bytes = max_bytes
        self._entries: OrderedDict[str, _Entry] = OrderedDict()
        self._bytes = 0
        self._hits = 0
        self._misses = 0

    def get(self, key: str, source_factory: SourceFactory) -> Kernel:
        entry = self._entries.get(key)
        if entry is not None:
            self._hits += 1
            self._entries.move_to_end(key)
            return entry.kernel

        self._misses += 1
        source = source_factory()
        kernel = load_kernel(source)
        size = len(source.encode("utf-8"))

        self._entries[key] = _Entry(kernel=kernel, size=size)
        self._bytes += size
        self._evict()
        return kernel

    def _evict(self) -> None:
        while self._bytes > self.max_bytes and len(self._entries) > 1:
            _, evicted = self._entries.popitem(last=False)
            self._bytes -= evicted.size

    def stats(self) -> dict:
        return {
            "entries": len(self._entries),
            "bytes": self._bytes,
            "hits": self._hits,
            "misses": self._misses,
        }

    def clear(self) -> None:
        self._entries.clear()
        self._bytes = 0
