"""Iteration grouping and timing for stateful and particle effects."""

from __future__ import annotations

import re

ITERATION_DELTA_TIME = 1 / 600
_PARTICLE_STATE = re.compile(r"^global_(xyz|vel|rgba|life_data)$|^global_.*_trail$")


def is_particle_state_name(name) -> bool:
    return isinstance(name, str) and _PARTICLE_STATE.fullmatch(name) is not None


def _declares_xyz(step, effects):
    definition = effects[step["effect_id"]]
    return "global_xyz" in (definition.get("textures") or {})


def _references_particle_state(step, effects):
    definition = effects[step["effect_id"]]
    for render_pass in definition.get("passes") or []:
        values = [*(render_pass.get("inputs") or {}).values(), *(render_pass.get("outputs") or {}).values()]
        if any(is_particle_state_name(value) for value in values):
            return True
    return False


def compute_iteration_groups(steps, effects):
    groups = []
    open_group = None
    open_loop = None

    def close_open_group():
        nonlocal open_group
        if open_group is not None:
            groups.append(open_group)
            open_group = None

    for step in steps:
        if open_loop is not None:
            if step["kind"] in {"read", "write"}:
                raise ValueError("Loop iteration group cannot cross a read/write boundary")
            definition = effects[step["effect_id"]]
            if definition.get("loopRole") == "begin":
                raise ValueError("Nested loop iteration groups are not supported")
            open_loop["steps"].append(step)
            if definition.get("loopRole") == "end":
                groups.append({"steps": open_loop["steps"], "iterated": True, "loop": True})
                open_loop = None
            continue
        if step["kind"] in {"read", "write"}:
            close_open_group()
            groups.append({"steps": [step], "iterated": False})
            continue
        definition = effects[step["effect_id"]]
        if definition.get("loopRole") == "end":
            raise ValueError("loopEnd has no matching loopBegin")
        if definition.get("loopRole") == "begin":
            close_open_group()
            open_loop = {"steps": [step]}
            continue
        if _declares_xyz(step, effects):
            close_open_group()
            open_group = {"steps": [step], "iterated": definition.get("iterated") is True}
            continue
        if open_group is not None and _references_particle_state(step, effects):
            open_group["steps"].append(step)
            continue
        close_open_group()
        groups.append({"steps": [step], "iterated": definition.get("iterated") is True})
    if open_loop is not None:
        raise ValueError("loopBegin has no matching loopEnd")
    close_open_group()
    return groups


def _wrap01(value):
    return value % 1


def iteration_schedule(time, count):
    count = max(0, int(count))
    return [
        {
            "frame": frame,
            "delta_time": ITERATION_DELTA_TIME,
            "time": _wrap01(time - (count - 1 - frame) * ITERATION_DELTA_TIME),
        }
        for frame in range(count)
    ]
