"""CPU adapter registry.

The reference engine renders a handful of effects through hand-written CPU
adapters (``canonicalAdapterFactories``) instead of the transpiled GLSL kernel.
For byte-parity we must run the same adapter. An adapter factory has the
signature ``factory(rt, base_kernel) -> kernel(ctx, out)``: it may wrap the
transpiled kernel (patching a stdlib fn) or replace it entirely.

Keys are ``"<effect_id>:<program>"`` matching the reference registry.
"""

from __future__ import annotations

CANONICAL_ADAPTERS = {}


def register(key):
    def deco(factory):
        CANONICAL_ADAPTERS[key] = factory
        return factory
    return deco


def get_adapter(effect_id, program):
    return CANONICAL_ADAPTERS.get(f"{effect_id}:{program}")


# Import adapter modules so they self-register.
from . import crt  # noqa: E402,F401
from . import palette  # noqa: E402,F401
from . import snow  # noqa: E402,F401
