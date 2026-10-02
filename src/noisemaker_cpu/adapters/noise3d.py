"""Version-aware JavaScript-number semantics for synth3d/noise3d.

The upstream noisemaker-for-cpu transpiler lowered the hash3/hash4 LCG
kernels to raw JavaScript operators over plain-number uvec arrays, so their
rendered output followed IEEE-754 double arithmetic up to each bitwise
coercion, and the port mirrored that with ``runtime.js_uvec_numbers``.
noisemaker-for-cpu ef26f1c88a44 ("GAP-003: restore exact GLSL uint semantics
in transpiled hash kernels") restored exact mod-2^32 uint arithmetic in
those statements via ``cpu_umul`` and ``>>> 0``, so an oracle whose
transpiled canonical kernels contain the restored lowering must be mirrored
with the runtime's exact uint path instead.
"""

from __future__ import annotations

import os
from pathlib import Path

from . import register

_RESTORED_UINT_MARKER = "restoreUnsignedIntegerArithmetic"
_SIBLING_DEFAULT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "noisemaker-for-cpu")
)
_restored_uint_semantics: bool | None = None


def _oracle_restored_uint_semantics() -> bool:
    """True when the sibling oracle's transpiler restores exact uint semantics.

    ``noisemaker-for-cpu`` scripts/upstream/compile-glsl.js grew the
    ``restoreUnsignedIntegerArithmetic`` lowering in ef26f1c88a44; pre-fix
    oracles (including the CI oracle tarball and the pinned gate authority)
    do not have it. Resolved once per process. When no oracle checkout is
    mounted the pre-fix JavaScript-number behavior is preserved unchanged.
    """
    global _restored_uint_semantics
    if _restored_uint_semantics is None:
        cpu_dir = os.environ.get("NOISEMAKER_CPU_DIR") or _SIBLING_DEFAULT
        transpiler = Path(cpu_dir) / "scripts" / "upstream" / "compile-glsl.js"
        try:
            text = transpiler.read_text(encoding="utf-8")
        except OSError:
            _restored_uint_semantics = False
        else:
            _restored_uint_semantics = _RESTORED_UINT_MARKER in text
    return _restored_uint_semantics


@register("synth3d/noise3d:precompute")
def noise3d_factory(runtime, kernel):
    runtime.js_uvec_numbers = not _oracle_restored_uint_semantics()
    return kernel
