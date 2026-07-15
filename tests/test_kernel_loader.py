import pytest

from noisemaker_cpu.kernel_loader import KernelCache, load_kernel


def test_load_kernel_returns_callable_that_sets_output():
    kernel = load_kernel("def run_pixel(ctx, out):\n    out[0] = 1.0\n")
    out = [0, 0, 0, 0]
    kernel(None, out)
    assert out[0] == 1.0


def test_load_kernel_custom_name():
    source = "def my_kernel(ctx, out):\n    out[1] = 2.0\n"
    kernel = load_kernel(source, name="my_kernel")
    out = [0, 0, 0, 0]
    kernel(None, out)
    assert out[1] == 2.0


def test_load_kernel_missing_name_raises():
    with pytest.raises(NameError):
        load_kernel("def run_pixel(ctx, out):\n    pass\n", name="not_defined")


def test_load_kernel_non_callable_binding_raises():
    with pytest.raises(TypeError):
        load_kernel("run_pixel = 42\n")


def test_cache_get_compiles_once_per_key():
    calls = {"n": 0}

    def source_factory():
        calls["n"] += 1
        return "def run_pixel(ctx, out):\n    out[0] = 1.0\n"

    cache = KernelCache()
    first = cache.get("key-a", source_factory)
    second = cache.get("key-a", source_factory)

    assert calls["n"] == 1
    assert first is second

    stats = cache.stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["entries"] == 1


def test_cache_stats_and_clear():
    cache = KernelCache()
    cache.get("a", lambda: "def run_pixel(ctx, out):\n    out[0] = 1.0\n")
    assert cache.stats()["entries"] == 1
    assert cache.stats()["bytes"] > 0

    cache.clear()
    stats = cache.stats()
    assert stats["entries"] == 0
    assert stats["bytes"] == 0


def _source_for(tag: int) -> str:
    # Single-digit tag keeps every generated source the same byte length so
    # the eviction arithmetic below is exact and deterministic.
    return f"def run_pixel(ctx, out):\n    out[0] = {tag}\n"


def test_lru_eviction_evicts_least_recently_used():
    one_entry_size = len(_source_for(0).encode("utf-8"))
    # Room for exactly two equal-sized entries.
    cache = KernelCache(max_bytes=one_entry_size * 2)

    calls = {"a": 0, "b": 0, "c": 0}

    def factory(tag, digit):
        def _factory():
            calls[tag] += 1
            return _source_for(digit)
        return _factory

    # Fill the cache with "a" then "b" -> both fit exactly.
    cache.get("a", factory("a", 0))
    cache.get("b", factory("b", 1))
    assert cache.stats()["entries"] == 2
    assert cache.stats()["bytes"] == one_entry_size * 2

    # Touch "a" so "b" becomes the least-recently-used entry.
    cache.get("a", factory("a", 0))
    assert calls["a"] == 1  # still a hit, no recompilation

    # Inserting "c" overflows max_bytes -> evicts LRU ("b"), not "a".
    cache.get("c", factory("c", 2))
    assert cache.stats()["entries"] == 2
    assert calls["c"] == 1

    # "a" survived the eviction: fetching it again is still a hit.
    cache.get("a", factory("a", 0))
    assert calls["a"] == 1

    # "b" was evicted: fetching it again must recompile (a fresh miss).
    cache.get("b", factory("b", 1))
    assert calls["b"] == 2

    final_stats = cache.stats()
    assert final_stats["entries"] == 2
    # misses: a, b, c, b again = 4. hits: touch-a, survive-a = 2.
    assert final_stats["misses"] == 4
    assert final_stats["hits"] == 2


def test_lru_single_entry_larger_than_max_bytes_is_still_cached():
    big_source = "def run_pixel(ctx, out):\n    out[0] = 1.0\n"
    tiny_max = 4  # smaller than the source itself
    cache = KernelCache(max_bytes=tiny_max)

    kernel = cache.get("only", lambda: big_source)
    assert callable(kernel)

    stats = cache.stats()
    assert stats["entries"] == 1
    assert stats["bytes"] == len(big_source.encode("utf-8"))
    assert stats["bytes"] > tiny_max  # overflow allowed for the sole entry

    # Still retrievable as a hit -- not stuck in an eviction loop.
    same_kernel = cache.get("only", lambda: big_source)
    assert same_kernel is kernel
    assert cache.stats()["hits"] == 1
