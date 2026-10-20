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

import math
import sys

from ..automation import MAX_AUTOMATION_DEPTH, is_automation_value
from .error import DslError
from .parser import parse_dsl


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_surface(value):
    return isinstance(value, dict) and value.get("kind") == "surface"


# Mirrors upstream std_enums.js oscKind (sine..noise2d; noise/noise1d alias kind 5,
# noise2d is the two-stage periodic noise).
_OSC_KINDS = {"sine": 0, "tri": 1, "saw": 2, "sawInv": 3, "square": 4, "noise": 5, "noise1d": 5, "noise2d": 6}
_OSC_PARAM_ORDER = ["type", "min", "max", "speed", "offset", "seed"]
_UNSUPPORTED_INPUT = object()
_VALUE_CALLS = {"osc", "midi", "audio"}


def _clamp01(value):
    return max(0.0, min(1.0, value))


def _compile_oscillator(call, bindings, depth, resolving=None):
    """Compiles an `osc(...)` value-position call into the automation value shape
    the runtime evaluator consumes ({type: 'Oscillator', oscType, min, max, speed,
    offset, seed}), mirroring upstream's parser transformOscInvocation plus the
    validator's compileAutomationDescriptor: positional args fill
    type/min/max/speed/offset/seed in order, kwargs select by name, every field
    defaults as upstream defaults, min/max clamp into [0,1], nested osc() fields
    are allowed, and the oscType resolves from an integer 0..6 or an oscKind name
    (bare or oscKind-qualified). Invalid programs throw DslError, as everywhere
    else in this compiler."""
    loc = call.get("loc")
    if depth > MAX_AUTOMATION_DEPTH:
        raise DslError(f"Automation nesting exceeds the maximum depth of {MAX_AUTOMATION_DEPTH}", loc)
    fields = {}
    if call["argMode"] == "named":
        for arg in call["args"]:
            if arg["name"] not in _OSC_PARAM_ORDER:
                raise DslError(
                    f"osc() unknown parameter '{arg['name']}'; valid: {', '.join(_OSC_PARAM_ORDER)}", loc
                )
            fields[arg["name"]] = arg["value"]
    else:
        for index, arg in enumerate(call["args"]):
            if index < len(_OSC_PARAM_ORDER):
                fields[_OSC_PARAM_ORDER[index]] = arg["value"]

    raw_type = (
        0
        if fields.get("type") is None
        else _evaluate_value(fields["type"], bindings, depth + 1, resolving)
    )
    if isinstance(raw_type, (int, float)) and not isinstance(raw_type, bool):
        if not (isinstance(raw_type, int) or (isinstance(raw_type, float) and raw_type.is_integer())) or not 0 <= raw_type <= 6:
            raise DslError("osc() type must resolve to a supported oscKind value (0-6)", loc)
        osc_type = int(raw_type)
    elif isinstance(raw_type, str):
        kind_name = raw_type[len("oscKind."):] if raw_type.startswith("oscKind.") else raw_type
        if kind_name not in _OSC_KINDS:
            raise DslError(f'osc() type must resolve to a supported oscKind value; got "{raw_type}"', loc)
        osc_type = _OSC_KINDS[kind_name]
    else:
        raise DslError("osc() type must resolve to a supported oscKind value", loc)

    def number_field(node, name, fallback, clamp):
        if node is None:
            return fallback
        value = _evaluate_value(node, bindings, depth + 1, resolving)
        if value is _UNSUPPORTED_INPUT:
            return fallback
        if is_automation_value(value):
            return value
        if value is True:
            return 1
        if value is False:
            return 0
        if not _is_number(value) or not math.isfinite(value):
            raise DslError(f"osc() {name} must be a number or a nested osc()", loc)
        return _clamp01(value) if clamp else value

    return {
        "type": "Oscillator",
        "oscType": osc_type,
        "min": number_field(fields.get("min"), "min", 0, True),
        "max": number_field(fields.get("max"), "max", 1, True),
        "speed": number_field(fields.get("speed"), "speed", 1, False),
        "offset": number_field(fields.get("offset"), "offset", 0, False),
        "seed": number_field(fields.get("seed"), "seed", 1, False),
    }


class _CompileScope(dict):
    def __init__(self, effects, search):
        super().__init__()
        self.effects = effects
        self.search = search
        self.pending = None
        self.inline_count = 0
        # Names of the program's lets that a later statement declares. Reading one
        # before its let reports S003, as upstream's validator does.
        self.pending_names = None

    def compile_inline_chain(self, chain):
        compiled = _compile_chain(chain, self, self.search, self.effects, inline=True)
        surface = f"inline:{self.inline_count}"
        self.inline_count += 1
        self.pending.append({"surface": surface, "chain": compiled})
        return {"kind": "surface", "name": surface, "loc": chain["loc"]}


def _evaluate_value(value, bindings, osc_depth=0, resolving=None):
    if resolving is None:
        resolving = []
    if isinstance(value, list):
        return [_evaluate_value(item, bindings, osc_depth, resolving) for item in value]
    if not isinstance(value, dict):
        return value
    kind = value.get("kind")
    if kind == "surface":
        return value
    if kind == "Call":
        if value["name"] in {"midi", "audio"}:
            print(f"Warning: {value['name']}() is unsupported in CPU ports; real-time input is unavailable. Ignoring this unsupported input value.", file=sys.stderr)
            return _UNSUPPORTED_INPUT
        if value["name"] == "osc":
            return _compile_oscillator(value, bindings, osc_depth, resolving)
        raise DslError(f'Unsupported DSL value {kind} "{value["name"]}"', value.get("loc"))
    if kind == "identifier":
        name = value["name"]
        if name in bindings:
            binding = bindings[name]
            if binding["kind"] == "partial":
                raise DslError(f'Effect partial "{name}" cannot be used as a value', value.get("loc"))
            if binding["kind"] == "alias":
                return binding["name"]
            # A value binding resolves lazily at its first use. Statement order
            # (upstream 9cc041d0) makes a chain see only lets declared at or before
            # its own index, so a name declared by a later let is pending here and
            # reading it reports S003, as upstream does.
            if binding["resolved"]:
                return binding["value"]
            if name in resolving:
                raise DslError(f"Automation cycle detected: {' -> '.join([*resolving, name])}", value.get("loc"))
            binding["value"] = _evaluate_value(binding["expr"], bindings, osc_depth, [*resolving, name])
            binding["resolved"] = True
            return binding["value"]
        if bindings.pending_names is not None and name in bindings.pending_names:
            raise DslError(f"Variable used before assignment: '{name}'", value.get("loc"))
        return name
    if kind == "vector":
        components = [_evaluate_value(item, bindings, 0, resolving) for item in value["values"]]
        if len(components) != value["width"] or any(not _is_number(item) for item in components):
            raise DslError(f"vec{value['width']} requires {value['width']} numeric values", value.get("loc"))
        return components
    if kind == "unary":
        operand = _evaluate_value(value["argument"], bindings, 0, resolving)
        if not _is_number(operand):
            raise DslError("Unary arithmetic requires a number", value.get("loc"))
        return -operand if value["operator"] == "-" else operand
    if kind == "binary":
        left = _evaluate_value(value["left"], bindings, 0, resolving)
        right = _evaluate_value(value["right"], bindings, 0, resolving)
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
    if kind == "Chain" and bindings.pending is not None:
        return bindings.compile_inline_chain(value)
    raise DslError(f"Unsupported DSL value {kind}", value.get("loc"))


def _resolve_args(args, bindings):
    return [{**arg, "value": _evaluate_value(arg["value"], bindings)} for arg in args]


def _merge_args(stored, call):
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


def _merge_partial(stored, call):
    merged = _merge_args(stored, call)
    namespace = call.get("namespace", stored.get("namespace"))
    if namespace:
        merged["namespace"] = namespace
    else:
        merged.pop("namespace", None)
    return merged


def _volume_references(call):
    if call["argMode"] != "positional" or len(call["args"]) != 2:
        return None
    names = []
    for arg in call["args"]:
        value = arg["value"]
        if not isinstance(value, dict) or value.get("kind") not in {"surface", "identifier"}:
            return None
        if value["kind"] == "identifier" and "." in value["name"]:
            return None
        names.append(value["name"])
    return names


def _read3d_references(call):
    if call["argMode"] == "named":
        named = {arg["name"]: arg for arg in call["args"]}
        if "tex3d" not in named or "geo" not in named:
            return None
        return _volume_references({"argMode": "positional", "args": [named["tex3d"], named["geo"]]})
    return _volume_references(call)


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
        if arg["value"] is _UNSUPPORTED_INPUT:
            continue
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


def _compile_chain(chain, bindings, search, effects, inline=False):
    steps = []
    has_image = False
    has_volume = False
    starts_with_generator = False
    open_loop = None
    calls = [
        call
        for element in chain["calls"]
        for call in (element["body"] if element.get("kind") == "Subchain" else [element])
    ]
    for index, raw_call in enumerate(calls):
        call = raw_call
        binding = bindings.get(call["name"])
        if binding is not None:
            if binding["kind"] == "alias":
                call = {**call, "name": binding["name"]}
            elif binding["kind"] == "partial":
                call = _merge_partial(binding["call"], call)
            else:
                raise DslError(f'Binding "{call["name"]}" is not callable', call["loc"])
        outer_pending = bindings.pending
        bindings.pending = []
        try:
            args = _resolve_args(call["args"], bindings)
        finally:
            inline_chains = bindings.pending
            bindings.pending = outer_pending
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
        if call["name"] == "write3d":
            if index == 0:
                raise DslError("Expected effect or IO function name", call["loc"])
            if open_loop is not None:
                raise DslError("loopBegin must be closed by loopEnd before write", call["loc"])
            references = _volume_references(call)
            if not references:
                raise DslError("Expected surface reference", call["loc"])
            steps.append({"kind": "write3d", "volume": references[0], "geometry": references[1], "loc": call["loc"]})
            continue
        references = _read3d_references(call) if call["name"] == "read3d" and index == 0 else None
        if references:
            steps.append({"kind": "read3d", "volume": references[0], "geometry": references[1], "loc": call["loc"]})
            has_volume = True
            continue
        namespaces = [call["namespace"]] if call.get("namespace") else search
        effect_id = _resolve_effect(call["name"], namespaces, effects)
        if effect_id is None:
            raise DslError(f'Unknown effect "{call["name"]}" in search namespaces {", ".join(namespaces)}', call["loc"])
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
        step = {"kind": "effect", "effect_id": effect_id, "params": params, "surfaces": surfaces, "loc": call["loc"]}
        if inline_chains:
            step["inlineChains"] = inline_chains
        steps.append(step)
    if open_loop is not None:
        raise DslError("loopBegin must be closed by loopEnd before the chain ends", open_loop)
    if not inline and starts_with_generator and (not steps or steps[-1]["kind"] not in {"write", "write3d"}):
        raise DslError("Generator chain must end with write(oN)", chain["loc"])
    return {"steps": steps, "loc": chain["loc"]}


def _alias_binding(value, bindings):
    if not isinstance(value, dict) or value.get("kind") != "identifier" or "." in value["name"]:
        return None
    bound = bindings.get(value["name"])
    if bound is not None:
        return bound if bound["kind"] in {"partial", "alias"} else None
    if _resolve_effect(value["name"], bindings.search, bindings.effects):
        return {"kind": "alias", "name": value["name"]}
    return None


def _declare_binding(binding, bindings):
    """Declares one let. Statement order (upstream 9cc041d0): a chain sees only the
    lets declared at or before its own statement index; a later `let` of the same
    name reassigns it for later statements; reading a pending name reports S003.
    A bare identifier value must name something resolvable now (an earlier
    binding, an alias, or an effect), as upstream's declareVar requires."""
    value = binding["value"]
    if isinstance(value, dict) and value.get("kind") == "Call" and value.get("name") not in _VALUE_CALLS:
        # A partial keeps its call unresolved. Its arguments resolve where it is
        # called, as upstream's validator substitutes a symbol at each use.
        bindings[binding["name"]] = {"kind": "partial", "call": value}
        return
    alias = _alias_binding(value, bindings)
    if alias is not None:
        bindings[binding["name"]] = alias
        return
    if (
        isinstance(value, dict)
        and value.get("kind") == "identifier"
        and "." not in value["name"]
        and value["name"] not in bindings
        and not _resolve_effect(value["name"], bindings.search, bindings.effects)
    ):
        raise DslError(f"Variable used before assignment: '{value['name']}'", value.get("loc"))
    bindings[binding["name"]] = {"kind": "value", "expr": value, "resolved": False, "value": None}


def compile_dsl(source, effects, options=None):
    ast = parse_dsl(source, options or {})
    if len(ast["search"]) == 0:
        raise DslError("Missing required search directive", ast["loc"])

    bindings = _CompileScope(effects, ast["search"])
    next_binding = 0

    def declare_through(chain_index):
        nonlocal next_binding
        while next_binding < len(ast["bindings"]) and getattr(ast["bindings"][next_binding], "planIndex", 0) <= chain_index:
            _declare_binding(ast["bindings"][next_binding], bindings)
            next_binding += 1

    chains = []
    for chain_index, chain in enumerate(ast["chains"]):
        declare_through(chain_index)
        # pendingNames covers the whole chain compile, including inline chains:
        # every argument position reports a pending read, as upstream does.
        bindings.pending_names = {binding["name"] for binding in ast["bindings"][next_binding:]}
        try:
            chains.append(_compile_chain(chain, bindings, ast["search"], effects))
        finally:
            bindings.pending_names = None
    declare_through(float("inf"))

    last_written = None
    for chain in chains:
        for step in chain["steps"]:
            if step["kind"] == "write":
                last_written = step["surface"]
    render_surface = ast["render"]["name"] if ast["render"] else last_written
    if not render_surface:
        raise DslError("No render surface specified and no write() found - add render(oN) or write(oN)", ast["loc"])

    return {"search": list(ast["search"]), "chains": chains, "render_surface": render_surface}
