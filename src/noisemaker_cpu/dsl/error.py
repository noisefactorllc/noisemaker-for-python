"""DSL diagnostic error — port of noisemaker-cpu src/dsl/error.js.

Carries a source location so tokenizer/parser/compiler failures point at the
offending line and column, formatted identically to the JS engine.
"""

from __future__ import annotations


class DslError(SyntaxError):
    def __init__(self, message: str, location: dict | None = None):
        location = location or {}
        source_name = location.get("sourceName", "<dsl>")
        line = location.get("line", 1)
        column = location.get("column", 1)
        super().__init__(f"{source_name}:{line}:{column}: {message}")
        self.source_name = source_name
        self.line = line
        self.column = column
