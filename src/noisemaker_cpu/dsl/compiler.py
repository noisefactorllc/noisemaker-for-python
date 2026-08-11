"""Compile a parsed DSL program into a render plan — port of noisemaker-cpu
src/dsl/compiler.js.

Resolves each call against the effect catalog (metadata.json), merges `let`
partials, evaluates value expressions/bindings, and lowers every chain into a
flat list of read/write/effect steps. Effect steps split arguments into value
params (handed to render_effect, which coerces + fills defaults) and surface
bindings (param name -> "@current" or ("surface", oN)), applying each surface
param's own default ("inputTex"/"none") exactly as the JS engine does.
"""

from __future__ import annotations

from .error import DslError
from .parser import parse_dsl


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_surface(value):
    return isinstance(value, dict) and value.get("kind") == "surface"


def _evaluate_value(value, bindings):
    if isinstance(value, list):
        return [_evaluate_value(item, bindings) for item in value]
    if not isinstance(value, dict):
        return value
    kind = value.get("kind")
    if kind == "surface":
        return value
    if kind == "identifier":
        name = value["name"]
        if name in bindings:
            binding = bindings[name]
            if binding["kind"] == "partial":
                raise DslError(f'Effect partial "{name}" cannot be used as a value', value.get("loc"))
            return binding["value"]
        return name
    if kind == "vector":
        components = [_evaluate_value(item, bindings) for item in value["values"]]
        if len(components) != value["width"] or any(not _is_number(item) for item in components):
            raise DslError(f"vec{value['width']} requires {value['width']} numeric values", value.get("loc"))
        return components
    if kind == "unary":
        operand = _evaluate_value(value["argument"], bindings)
        if not _is_number(operand):
            raise DslError("Unary arithmetic requires a number", value.get("loc"))
        return -operand if value["operator"] == "-" else operand
    if kind == "binary":
        left = _evaluate_value(value["left"], bindings)
        right = _evaluate_value(value["right"], bindings)
        if not _is_number(left) or not _is_number(right):
            raise DslError("Arithmetic requires numeric values", value.get("loc"))
        operator = value["operator"]
        if operator == "+":
            return left + right
        if operator == "-":
            return left - right
        if operator == "*":
            return left * right
        return left / right
    raise DslError(f"Unsupported DSL value {kind}", value.get("loc"))


def _resolve_args(args, bindings):
    return [{**arg, "value": _evaluate_value(arg["value"], bindings)} for arg in args]


def _merge_partial(stored, call):
    if not stored["argMode"]:
        return {**call, "name": stored["name"]}
    if not call["argMode"]:
        return {**stored, "loc": call["loc"]}
    if stored["argMode"] != call["argMode"]:
        raise DslError("Partial and call arguments must use the same named or positional form", call["loc"])
    if stored["argMode"] == "positional":
        return {**call, "name": stored["name"], "args": [*stored["args"], *call["args"]]}
    merged = {arg["name"]: arg for arg in stored["args"]}
    for arg in call["args"]:
        merged[arg["name"]] = arg
    return {**call, "name": stored["name"], "args": list(merged.values()), "argMode": "named"}


def _resolve_effect(func, search, effects):
    for namespace in search:
        effect_id = f"{namespace}/{func}"
        if effect_id in effects:
            return effect_id
    return None


def _surface_marker(value, name, loc):
    """Lower a surface argument (or a param's own default) to an evaluator
    binding: None means leave unbound (a blank 1x1, matching JS emptySurface),
    "@current" binds the chain's current image, ("surface", oN) a named surface."""
    if value is None or value == "none":
        return None
    if value == "inputTex":
        return "@current"
    if _is_surface(value):
        return ("surface", value["name"])
    raise DslError(f'Parameter "{name}" must be a surface reference', loc)


def _normalize_effect(effect_id, spec, args):
    """Map a call's arguments onto the effect's params, splitting value params
    (handed to render_effect) from surface bindings.

    Unlike the JS EffectDefinition.normalizeArguments, this does NOT validate
    value type/range/enum-membership here; render_effect's _coerce performs the
    coercion (and fills defaults). Consequence: the Python DSL accepts a superset
    of what the JS engine rejects — e.g. an out-of-range number, a non-integer
    for an int param, or a bool for a float param will render here where JS
    throws. Byte-parity for VALID programs is unaffected (coercion matches); only
    the rejection of malformed programs is more lenient. Unknown parameter NAMES
    are still rejected (below), matching JS.
    """
    param_specs = spec["params"]
    param_names = list(param_specs.keys())
    named = len(args) > 0 and args[0]["name"] is not None
    params = {}
    surfaces = {}
    provided = set()
    for index, arg in enumerate(args):
        # No paramAliases resolution: the bundle emits none (0/167 catalog effects
        # define aliases). If aliases are ever added, build.py must emit them and
        # this lookup must mirror EffectDefinition.paramAliases like the JS engine.
        supplied = arg["name"] if named else (param_names[index] if index < len(param_names) else None)
        if not supplied or supplied not in param_specs:
            bad = supplied if supplied else f"argument {index + 1}"
            raise DslError(f'Unknown parameter "{bad}" for {effect_id}; accepted: {", ".join(param_names)}', arg["loc"])
        provided.add(supplied)
        pspec = param_specs[supplied]
        if pspec.get("type") == "surface":
            marker = _surface_marker(arg["value"], supplied, arg["loc"])
            if marker is not None:
                surfaces[supplied] = marker
        else:
            params[supplied] = arg["value"]
    for name, pspec in param_specs.items():
        if pspec.get("type") == "surface" and name not in provided and "default" in pspec:
            marker = _surface_marker(pspec["default"], name, None)
            if marker is not None:
                surfaces[name] = marker
    return params, surfaces


def _compile_chain(chain, bindings, search, effects):
    steps = []
    has_image = False
    has_volume = False
    starts_with_generator = False
    open_loop = None
    for index, raw_call in enumerate(chain["calls"]):
        call = raw_call
        binding = bindings.get(call["name"])
        if binding is not None:
            if binding["kind"] != "partial":
                raise DslError(f'Binding "{call["name"]}" is not callable', call["loc"])
            call = _merge_partial(binding["call"], call)
        args = _resolve_args(call["args"], bindings)
        if call["name"] == "read":
            if index != 0 or len(args) != 1 or not _is_surface(args[0]["value"]):
                raise DslError("read(surface) must begin a chain", call["loc"])
            steps.append({"kind": "read", "surface": args[0]["value"]["name"], "loc": call["loc"]})
            has_image = True
            continue
        if call["name"] == "write":
            if open_loop is not None:
                raise DslError("loopBegin must be closed by loopEnd before write", call["loc"])
            if not has_image or len(args) != 1 or not _is_surface(args[0]["value"]):
                raise DslError("write(surface) requires a current image", call["loc"])
            steps.append({"kind": "write", "surface": args[0]["value"]["name"], "loc": call["loc"]})
            continue
        effect_id = _resolve_effect(call["name"], search, effects)
        if effect_id is None:
            raise DslError(f'Unknown effect "{call["name"]}" in search namespaces {", ".join(search)}', call["loc"])
        spec = effects[effect_id]
        domain = spec.get("domain", "image")
        if domain == "volume-generator":
            if index != 0 and not (spec.get("iterated") and has_volume):
                raise DslError(f"Generator {effect_id} must begin a chain", call["loc"])
            if index == 0:
                starts_with_generator = True
            has_volume = True
        elif domain == "volume-filter":
            if not has_volume:
                raise DslError(f"volume filter {effect_id} requires a volume input", call["loc"])
        elif domain == "volume-renderer":
            if not has_volume:
                raise DslError(f"volume renderer {effect_id} requires a volume input", call["loc"])
            has_image = True
        elif domain == "loop-begin":
            if not has_image:
                raise DslError(f"{effect_id} requires a current image", call["loc"])
            if open_loop is not None:
                raise DslError("nested loopBegin regions are not supported", call["loc"])
            open_loop = call["loc"]
        elif domain == "loop-end":
            if open_loop is None:
                raise DslError("loopEnd has no matching loopBegin", call["loc"])
            if not has_image:
                raise DslError(f"{effect_id} requires a current image", call["loc"])
            open_loop = None
        elif spec["kind"] == "generator":
            if index != 0:
                raise DslError(f"Generator {effect_id} must begin a chain", call["loc"])
            starts_with_generator = True
            has_image = True
        elif not has_image:
            requires_input_tex = any("inputTex" in (p.get("inputs") or {}).values() for p in spec["passes"])
            if requires_input_tex:
                raise DslError(
                    f"{spec['kind']} {effect_id} requires an input; begin with a generator or read(oN)",
                    call["loc"],
                )
            has_image = True
        params, surfaces = _normalize_effect(effect_id, spec, args)
        steps.append(
            {"kind": "effect", "effect_id": effect_id, "params": params, "surfaces": surfaces, "loc": call["loc"]}
        )
    if open_loop is not None:
        raise DslError("loopBegin must be closed by loopEnd before the chain ends", open_loop)
    if starts_with_generator and (not steps or steps[-1]["kind"] != "write"):
        raise DslError("Generator chain must end with write(oN)", chain["loc"])
    return {"steps": steps, "loc": chain["loc"]}


def compile_dsl(source, effects, options=None):
    ast = parse_dsl(source, options or {})
    if len(ast["search"]) == 0:
        raise DslError("Missing required search directive", ast["loc"])

    bindings = {}
    for binding in ast["bindings"]:
        if binding["name"] in bindings:
            raise DslError(f'Duplicate binding "{binding["name"]}"', binding["loc"])
        value = binding["value"]
        if isinstance(value, dict) and value.get("kind") == "Call":
            bindings[binding["name"]] = {
                "kind": "partial",
                "call": {**value, "args": _resolve_args(value["args"], bindings)},
            }
        else:
            bindings[binding["name"]] = {"kind": "value", "value": _evaluate_value(value, bindings)}

    chains = [_compile_chain(chain, bindings, ast["search"], effects) for chain in ast["chains"]]

    last_written = None
    for chain in chains:
        for step in chain["steps"]:
            if step["kind"] == "write":
                last_written = step["surface"]
    render_surface = ast["render"]["name"] if ast["render"] else last_written
    if not render_surface:
        raise DslError("No render surface specified and no write() found - add render(oN) or write(oN)", ast["loc"])

    return {"search": list(ast["search"]), "chains": chains, "render_surface": render_surface}
