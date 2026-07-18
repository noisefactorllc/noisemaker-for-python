"""Tokenize a Polymorphic DSL program — port of noisemaker-cpu src/dsl/tokenize.js.

Emits the same token stream (numbers, colors, strings, surfaces oN, keywords,
identifiers, punctuation, operators) so the Python parser can consume it exactly
as the JS parser does. Each token is a dict with type/lexeme/value plus its
source location (sourceName/line/column/index).
"""

from __future__ import annotations

import json
import re

from .error import DslError

KEYWORDS = {"search", "let", "render", "true", "false"}
PUNCTUATION = set("()[],.:=;")
OPERATORS = set("+-*/")

_WS = re.compile(r"\s")
_HEX = re.compile(r"[0-9a-fA-F]")
_DIGIT = re.compile(r"\d")
_IDENT_START = re.compile(r"[A-Za-z_]")
_IDENT_CONT = re.compile(r"[A-Za-z0-9_]")
_SURFACE = re.compile(r"^o\d+$")


def tokenize_dsl(source, options=None):
    options = options or {}
    if not isinstance(source, str):
        raise TypeError("DSL source must be a string")
    source_name = options.get("sourceName", "<dsl>")
    tokens = []
    length = len(source)
    state = {"index": 0, "line": 1, "column": 1}

    def at(offset):
        pos = state["index"] + offset
        return source[pos] if 0 <= pos < length else ""

    def start():
        return {
            "sourceName": source_name,
            "line": state["line"],
            "column": state["column"],
            "index": state["index"],
        }

    def advance():
        char = source[state["index"]]
        state["index"] += 1
        if char == "\n":
            state["line"] += 1
            state["column"] = 1
        else:
            state["column"] += 1
        return char

    def push(ttype, lexeme, location, value=None):
        tokens.append({"type": ttype, "lexeme": lexeme, "value": value, **location})

    while state["index"] < length:
        char = source[state["index"]]
        if _WS.match(char):
            advance()
            continue
        if char == "/" and at(1) == "/":
            while state["index"] < length and source[state["index"]] != "\n":
                advance()
            continue
        if char == "/" and at(1) == "*":
            location = start()
            advance()
            advance()
            while state["index"] < length and not (source[state["index"]] == "*" and at(1) == "/"):
                advance()
            if state["index"] >= length:
                raise DslError("Unterminated block comment", location)
            advance()
            advance()
            continue

        location = start()
        if char == "#":
            lexeme = advance()
            while _HEX.match(at(0)):
                lexeme += advance()
            if len(lexeme) not in (4, 7, 9):
                raise DslError("Colors must use #RGB, #RRGGBB, or #RRGGBBAA", location)
            push("color", lexeme, location)
            continue
        if char == '"':
            advance()
            value = ""
            while state["index"] < length and source[state["index"]] != '"':
                if source[state["index"]] == "\n":
                    raise DslError("Unterminated string", location)
                if source[state["index"]] == "\\":
                    advance()
                    escaped = advance()
                    value += "\n" if escaped == "n" else "\t" if escaped == "t" else escaped
                else:
                    value += advance()
            if state["index"] >= length:
                raise DslError("Unterminated string", location)
            advance()
            push("string", value, location, value)
            continue
        if _DIGIT.match(char) or (char == "." and _DIGIT.match(at(1))):
            lexeme = ""
            while _DIGIT.match(at(0)):
                lexeme += advance()
            if at(0) == ".":
                lexeme += advance()
                while _DIGIT.match(at(0)):
                    lexeme += advance()
            if at(0) in ("e", "E"):
                lexeme += advance()
                if at(0) in ("+", "-"):
                    lexeme += advance()
                while _DIGIT.match(at(0)):
                    lexeme += advance()
            try:
                number = float(lexeme)
            except ValueError:
                # A truncated exponent like "1e" — keep every DSL failure a
                # located DslError rather than leaking a bare ValueError.
                raise DslError(f"Invalid numeric literal {json.dumps(lexeme)}", location) from None
            push("number", lexeme, location, number)
            continue
        if _IDENT_START.match(char):
            lexeme = advance()
            while _IDENT_CONT.match(at(0)):
                lexeme += advance()
            if _SURFACE.match(lexeme):
                ttype = "surface"
            elif lexeme in KEYWORDS:
                ttype = "keyword"
            else:
                ttype = "identifier"
            push(ttype, lexeme, location)
            continue
        if char in PUNCTUATION:
            advance()
            push("punctuation", char, location)
            continue
        if char in OPERATORS:
            advance()
            push("operator", char, location)
            continue
        raise DslError(f"Unexpected character {json.dumps(char)}", location)

    tokens.append(
        {
            "type": "eof",
            "lexeme": "",
            "value": None,
            "sourceName": source_name,
            "line": state["line"],
            "column": state["column"],
            "index": state["index"],
        }
    )
    return tokens
