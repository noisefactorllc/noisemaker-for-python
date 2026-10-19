"""Parse the DSL token stream into an AST — port of noisemaker-cpu src/dsl/parser.js.

Produces the same node shapes the JS parser does: a DslProgram with search
namespaces, `let` bindings, effect chains, and an optional render surface.
Value expressions carry precedence-correct arithmetic, vectors, arrays, colors,
enum-member identifiers, and canonical `read(oN)` surface references.
"""

from __future__ import annotations

import math

from .error import DslError
from .tokenizer import tokenize_dsl


def _location(token):
    return {
        "sourceName": token["sourceName"],
        "line": token["line"],
        "column": token["column"],
        "index": token["index"],
    }


def _parse_color(lexeme):
    hexit = lexeme[1:]
    if len(hexit) == 3:
        hexit = "".join(char + char for char in hexit)
    values = [int(hexit[offset : offset + 2], 16) / 255 for offset in (0, 2, 4)]
    if len(hexit) == 8:
        values.append(int(hexit[6:8], 16) / 255)
    return values


_PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2}


class _Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def peek(self, offset=0):
        return self.tokens[min(self.current + offset, len(self.tokens) - 1)]

    def previous(self):
        return self.tokens[self.current - 1]

    def at_end(self):
        return self.peek()["type"] == "eof"

    def check(self, lexeme):
        return self.peek()["type"] != "string" and self.peek()["lexeme"] == lexeme

    def match(self, *lexemes):
        if self.peek()["type"] == "string" or self.peek()["lexeme"] not in lexemes:
            return False
        self.current += 1
        return True

    def consume(self, lexeme, message=None):
        if not self.check(lexeme):
            raise DslError(message or f'Expected "{lexeme}"', _location(self.peek()))
        token = self.tokens[self.current]
        self.current += 1
        return token

    def identifier(self, message="Expected identifier"):
        token = self.peek()
        if token["type"] != "identifier":
            raise DslError(message, _location(token))
        self.current += 1
        return token

    def parse_program(self):
        ast = {
            "kind": "DslProgram",
            "search": [],
            "bindings": [],
            "chains": [],
            "render": None,
            "loc": _location(self.peek()),
        }
        if self.match("search"):
            while True:
                namespace = self.peek()
                if namespace["type"] != "identifier" and not (
                    namespace["type"] == "keyword" and namespace["lexeme"] == "render"
                ):
                    raise DslError("Expected namespace after search", _location(namespace))
                self.current += 1
                ast["search"].append(namespace["lexeme"])
                if not self.match(","):
                    break
            self.match(";")
        while not self.at_end():
            if self.match(";"):
                continue
            if self.match("let"):
                ast["bindings"].append(self.parse_binding(self.previous()))
            elif self.match("render"):
                if ast["render"]:
                    raise DslError("Program may only declare one render surface", _location(self.previous()))
                start = self.previous()
                self.consume("(")
                ast["render"] = self.parse_surface()
                ast["render"]["loc"] = _location(start)
                self.consume(")")
                self.match(";")
            else:
                ast["chains"].append(self.parse_chain())
                self.match(";")
        return ast

    def parse_binding(self, start):
        name = self.identifier("Expected binding name after let")
        self.consume("=")
        if self.peek()["type"] == "identifier" and self.peek(1)["lexeme"] == "(":
            value = self.parse_call()
        else:
            value = self.parse_value_expression()
        self.match(";")
        return {"kind": "Binding", "name": name["lexeme"], "value": value, "loc": _location(start)}

    def parse_chain(self):
        first = self.parse_call()
        calls = [first]
        while self.match("."):
            if self.at_subchain():
                calls.append(self.parse_subchain())
            elif self.peek()["type"] == "identifier" and self.check("write3d"):
                calls.append(self.parse_write3d())
            else:
                calls.append(self.parse_call())
        return {"kind": "Chain", "calls": calls, "loc": first["loc"]}

    def is_punctuation(self, lexeme):
        return self.peek()["type"] == "punctuation" and self.check(lexeme)

    def at_subchain(self):
        return self.peek()["type"] == "keyword" and self.check("subchain")

    def parse_write3d(self):
        name = self.identifier()
        self.consume("(")

        def reference():
            token = self.peek()
            if token["type"] == "surface":
                return self.parse_surface()
            if token["type"] != "identifier":
                raise DslError("Expected surface reference", _location(token))
            self.current += 1
            return {"kind": "identifier", "name": token["lexeme"], "loc": _location(token)}

        volume = reference()
        self.consume(",")
        geometry = reference()
        self.consume(")")
        return {
            "kind": "Call",
            "name": "write3d",
            "args": [{"name": None, "value": value, "loc": value["loc"]} for value in (volume, geometry)],
            "argMode": "positional",
            "loc": _location(name),
        }

    def parse_expression_chain(self, first):
        calls = [first]
        while self.is_punctuation("."):
            self.current += 1
            if self.at_subchain():
                calls.append(self.parse_subchain())
                continue
            call = self.parse_call()
            if call["name"] in {"write", "write3d"}:
                raise DslError("Expected effect or IO function name", call["loc"])
            calls.append(call)
        return {"kind": "Chain", "calls": calls, "loc": first["loc"]}

    def parse_subchain(self):
        start = self.peek()
        self.current += 1
        self.consume("(")
        meta = {"name": None, "id": None}
        if self.peek()["type"] == "string":
            meta["name"] = self.peek()["value"]
            self.current += 1
        else:
            while self.peek()["type"] == "identifier" and self.peek(1)["lexeme"] == ":":
                key = self.identifier()["lexeme"]
                self.consume(":")
                if self.peek()["type"] != "string":
                    break
                value = self.peek()["value"]
                self.current += 1
                if key in meta:
                    meta[key] = value
                self.match(",")
        self.consume(")")
        self.consume("{")
        body = []
        while True:
            self.consume(".")
            call = self.parse_call()
            if call["name"] in {"write", "write3d"}:
                raise DslError("Expected effect or IO function name", call["loc"])
            body.append(call)
            if self.check("}"):
                break
        self.consume("}")
        return {
            "kind": "Subchain",
            "name": meta["name"] or None,
            "id": meta["id"] or None,
            "body": body,
            "loc": _location(start),
        }

    def from_call(self, call):
        if call["argMode"] != "positional" or len(call["args"]) != 2:
            return call
        namespace, target = (arg["value"] for arg in call["args"])
        inner = (
            target["calls"][0]
            if isinstance(target, dict) and target.get("kind") == "Chain" and len(target["calls"]) == 1
            else None
        )
        if (
            not isinstance(namespace, dict)
            or namespace.get("kind") != "identifier"
            or not inner
            or inner.get("kind") != "Call"
            or inner["name"] in {"read", "read3d", "write", "write3d"}
        ):
            return call
        return {**inner, "namespace": namespace["name"]}

    def parse_call(self):
        name = self.identifier("Expected effect or IO function name")
        self.consume("(")
        args = []
        mode = None
        if not self.check(")"):
            while True:
                is_named = self.peek()["type"] == "identifier" and self.peek(1)["lexeme"] == ":"
                next_mode = "named" if is_named else "positional"
                if mode and mode != next_mode and name["lexeme"] not in ("midi", "audio"):
                    raise DslError("Cannot mix positional and named arguments", _location(self.peek()))
                mode = next_mode
                arg_name = None
                if is_named:
                    arg_name = self.identifier()["lexeme"]
                    self.consume(":")
                start = self.peek()
                args.append({"name": arg_name, "value": self.parse_value_expression(), "loc": _location(start)})
                if not self.match(","):
                    break
        self.consume(")")
        call = {"kind": "Call", "name": name["lexeme"], "args": args, "argMode": mode, "loc": _location(name)}
        return self.from_call(call) if call["name"] == "from" else call

    def parse_value_expression(self, min_precedence=0):
        left = self.parse_value_unary()
        while self.peek()["type"] == "operator" and _PRECEDENCE.get(self.peek()["lexeme"], -1) >= min_precedence:
            operator = self.tokens[self.current]
            self.current += 1
            right = self.parse_value_expression(_PRECEDENCE[operator["lexeme"]] + 1)
            left = {
                "kind": "binary",
                "operator": operator["lexeme"],
                "left": left,
                "right": right,
                "loc": _location(operator),
            }
        return left

    def parse_value_unary(self):
        if self.match("-", "+"):
            operator = self.previous()
            return {
                "kind": "unary",
                "operator": operator["lexeme"],
                "argument": self.parse_value_unary(),
                "loc": _location(operator),
            }
        return self.parse_value_primary()

    def parse_value_primary(self):
        token = self.peek()
        if token["type"] == "number":
            self.current += 1
            return token["value"]
        if token["type"] == "string":
            self.current += 1
            return token["value"]
        if token["lexeme"] == "true" or token["lexeme"] == "false":
            self.current += 1
            return token["lexeme"] == "true"
        if token["type"] == "color":
            self.current += 1
            return _parse_color(token["lexeme"])
        if token["type"] == "surface":
            return self.parse_surface()
        if self.match("["):
            values = []
            if not self.check("]"):
                while True:
                    values.append(self.parse_value_expression())
                    if not self.match(","):
                        break
            self.consume("]")
            return values
        if self.match("("):
            value = self.parse_value_expression()
            self.consume(")")
            return value
        if token["type"] == "identifier":
            self.current += 1
            name = token["lexeme"]
            if (
                name == "Math"
                and self.is_punctuation(".")
                and self.peek(1)["type"] == "identifier"
                and self.peek(1)["lexeme"] == "PI"
            ):
                self.current += 2
                return math.pi
            if name == "read3d" and self.is_punctuation("("):
                self.current -= 1
                call = self.parse_call()
                if (
                    len(call["args"]) == 1
                    and isinstance(call["args"][0]["value"], dict)
                    and call["args"][0]["value"].get("kind") == "identifier"
                ):
                    return call["args"][0]["value"]
                return self.parse_expression_chain(call)
            if name == "read" and self.match("("):
                if self.peek()["type"] == "identifier" and self.peek(1)["lexeme"] == ":":
                    argument_name = self.identifier()["lexeme"]
                    if argument_name not in ("surface", "tex"):
                        raise DslError(
                            'read() surface argument must be named "surface" or "tex"',
                            _location(self.previous()),
                        )
                    self.consume(":")
                surface = self.parse_surface()
                self.consume(")")
                if self.is_punctuation("."):
                    call = {
                        "kind": "Call",
                        "name": "read",
                        "args": [{"name": None, "value": surface, "loc": surface["loc"]}],
                        "argMode": "positional",
                        "loc": _location(token),
                    }
                    return self.parse_expression_chain(call)
                return surface
            if name in ("vec2", "vec3", "vec4") and self.match("("):
                values = []
                if not self.check(")"):
                    while True:
                        values.append(self.parse_value_expression())
                        if not self.match(","):
                            break
                self.consume(")")
                return {"kind": "vector", "width": int(name[-1]), "values": values, "loc": _location(token)}
            # Parse MIDI/audio calls only to warn and omit unsupported input.
            if name in ("osc", "midi", "audio") and self.peek()["lexeme"] == "(":
                self.current -= 1
                return self.parse_call()
            if self.is_punctuation("("):
                self.current -= 1
                return self.parse_expression_chain(self.parse_call())
            path = name
            while self.match("."):
                path += f".{self.identifier('Expected enum member')['lexeme']}"
            return {"kind": "identifier", "name": path, "loc": _location(token)}
        raise DslError("Expected DSL value", _location(token))

    def parse_surface(self):
        token = self.peek()
        if token["type"] != "surface":
            raise DslError("Expected surface reference", _location(token))
        self.current += 1
        index = int(token["lexeme"][1:])
        if index < 0 or index > 7:
            raise DslError("Surface reference must be o0 through o7", _location(token))
        return {"kind": "surface", "name": token["lexeme"], "loc": _location(token)}


def parse_dsl(source, options=None):
    return _Parser(tokenize_dsl(source, options or {})).parse_program()
