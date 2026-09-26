"""Node-free GAP-005 acceptance: byte-compares the Python port against the
committed oracle fixtures.

tests/data/gap005-oracle/ holds fixtures rendered by the pinned CPU oracle
(noisemaker-for-cpu checkout at HEAD bfbe54764eee87c8f67d2b281d5f304faad04a5b,
bundle CDN 1.0.183): for every recorded case the oracle CLI's PNG artifact
(provenance), its decoded RGBA8 bytes, and the raw output-surface float32 bytes
(rgba16f leg, which catches sub-8-bit divergences), plus manifest.json binding
each file's sha256, the exact program/size/seed/time of every case, and the
oracle revision. Coverage: 8 four-component alpha controls × sizes
16×16/24×13/33×17/7×64; the gap's originally recorded feedback program
(noise(seed: 1, ridges: true).feedback(iterationCount: 1)); a feedback matrix
with mix 40 over iterationCount 1–5, seeds 1–3, times 0.0–0.75, sizes
8×8–32×16; and two control pairs asserting the oracle output is
harness-seed-sensitive and feedback-stateful (so duplicated evidence cannot
pass).

This test re-renders the Python side and requires byte equality on both legs —
no node, no sibling checkout. An auditor can likewise re-render any case with
the Python CLI and byte-compare against the committed oracle fixtures.
"""

import hashlib
import json
from pathlib import Path

import pytest

from noisemaker_cpu.png import decode_png
from noisemaker_cpu.renderer import render_dsl

FIXTURES = Path(__file__).parent / "data" / "gap005-oracle"
MANIFEST = FIXTURES / "manifest.json"
ORACLE_HEAD = "bfbe54764eee87c8f67d2b281d5f304faad04a5b"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _case_files(case: str):
    return (
        (FIXTURES / f"{case}.png").read_bytes(),
        (FIXTURES / f"{case}.rgba8").read_bytes(),
        (FIXTURES / f"{case}.f32").read_bytes(),
    )


def _py_render(case: dict):
    surface = render_dsl(
        case["program"], width=case["width"], height=case["height"],
        seed=case["seed"], time=case["time"],
    )
    return surface.to_rgba8(), surface.data.astype(surface.data.dtype, copy=False).tobytes()


def test_manifest_binds_the_pinned_oracle_revision_and_is_internally_consistent():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["oracle"]["cpuHead"] == ORACLE_HEAD
    assert manifest["oracle"]["pinnedUpstreamRevision"] == "8eeb7b5ac14eb37a8d16037f607a88ce63924cd3"
    cases = manifest["cases"]
    assert len(cases) == 46
    assert sum(key.startswith("solid-") for key in cases) == 32
    assert "fbrec-16x16-s1-t0.25-it1" in cases
    assert sum(key.startswith("fbmix-") for key in cases) == 9
    # every committed artifact matches its manifest hash, and each oracle PNG
    # decodes to exactly the committed RGBA8 bytes (provenance is load-bearing)
    for name, digest in manifest["files"].items():
        blob = (FIXTURES / name).read_bytes()
        assert _sha256(blob) == digest, name
        if name.endswith(".png"):
            oracle_png = decode_png(blob)
            rgba8 = (FIXTURES / (name[: -len(".png")] + ".rgba8")).read_bytes()
            assert oracle_png.to_rgba8() == rgba8, name
    # control pairs: the oracle must be seed-sensitive and feedback-stateful
    seed_a = (FIXTURES / "ctl-seed-a-16x16-s1-t0.25-it2.f32").read_bytes()
    seed_b = (FIXTURES / "ctl-seed-b-16x16-s2-t0.25-it2.f32").read_bytes()
    state_a = (FIXTURES / "ctl-state-a-16x16-s1-t0.25-it1.f32").read_bytes()
    state_b = (FIXTURES / "ctl-state-b-16x16-s1-t0.25-it2.f32").read_bytes()
    assert seed_a != seed_b, "oracle output must change with the harness seed"
    assert state_a != state_b, "oracle feedback output must change with iterationCount"


@pytest.mark.parametrize(
    "case",
    sorted(json.loads(MANIFEST.read_text(encoding="utf-8"))["cases"]),
)
def test_python_output_matches_the_committed_oracle_bytes(case):
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    case_spec = manifest["cases"][case]
    rgba8_fixture, f32_fixture = _case_files(case)[1:]
    rgba8_py, f32_py = _py_render(case_spec)
    assert rgba8_py == rgba8_fixture, f"8-bit RGBA mismatch for {case}"
    assert f32_py == f32_fixture, f"rgba16f surface mismatch for {case}"
