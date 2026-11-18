#!/usr/bin/env python3
"""Convert a useful, intentionally small subset of pseudocode to Python."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import TextIO


class ConversionError(ValueError):
    """Raised when pseudocode block structure is invalid."""


_FOR_RE = re.compile(
    r"^FOR\s+([A-Za-z_]\w*)\s+FROM\s+(.+?)\s+TO\s+(.+?)(?:\s+STEP\s+(.+))?$",
    re.IGNORECASE,
)
_ASSIGNMENT_RE = re.compile(r"^(?:SET\s+)?([A-Za-z_]\w*)\s*(?:<-|←|:=|=)\s*(.+)$", re.IGNORECASE)


def _expression(expression: str) -> str:
    """Translate common pseudocode operators without changing string literals."""
    # Split around quoted strings so words inside strings (for example "AND") stay intact.
    pieces = re.split(r'("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')', expression)
    replacements = (
        (r"\bAND\b", "and"),
        (r"\bOR\b", "or"),
        (r"\bNOT\b", "not"),
        (r"\bMOD\b", "%"),
        (r"\bDIV\b", "//"),
        (r"\bTRUE\b", "True"),
        (r"\bFALSE\b", "False"),
    )
    for index in range(0, len(pieces), 2):
        part = pieces[index].replace("<>", "!=")
        for pattern, replacement in replacements:
            part = re.sub(pattern, replacement, part, flags=re.IGNORECASE)
        pieces[index] = part
    return "".join(pieces)


def convert(pseudocode: str) -> str:
    """Convert pseudocode text to Python source.

    Supported blocks: IF/ELSE/ENDIF, WHILE/ENDWHILE, FOR/ENDFOR, and
    REPEAT/UNTIL. FOR ranges include their end value, unlike Python's range.
    """
    output: list[str] = []
    # Entries are block names; ELSE changes an if entry to else.
    blocks: list[str] = []
    uses_inclusive_range = False

    def emit(source: str, depth: int | None = None) -> None:
        output.append("    " * (len(blocks) if depth is None else depth) + source)

    for line_number, original in enumerate(pseudocode.splitlines(), start=1):
        line = original.strip()
        if not line or line.startswith("#") or line.startswith("//"):
            continue
        # Accept trailing // comments, while not treating slashes in strings as comments.
        line = re.split(r'\s//(?=(?:[^"\']|"[^"]*"|\'[^\']*\')*$)', line, maxsplit=1)[0].rstrip()
        if not line:
            continue

        upper = line.upper()
        if upper in {"ENDIF", "END IF", "ENDWHILE", "END WHILE", "ENDFOR", "END FOR"}:
            expected = "if" if upper in {"ENDIF", "END IF"} else "while" if "WHILE" in upper else "for"
            if not blocks or blocks[-1] != expected:
                raise ConversionError(f"Line {line_number}: unexpected {line!r}.")
            blocks.pop()
            continue

        if upper == "ELSE":
            if not blocks or blocks[-1] != "if":
                raise ConversionError(f"Line {line_number}: ELSE without a matching IF.")
            blocks[-1] = "else"
            emit("else:")
            continue

        if upper.startswith("IF ") and upper.endswith(" THEN"):
            condition = line[3:-5].strip()
            emit(f"if {_expression(condition)}:")
            blocks.append("if")
            continue

        if upper.startswith("WHILE ") and upper.endswith(" DO"):
            condition = line[6:-3].strip()
            emit(f"while {_expression(condition)}:")
            blocks.append("while")
            continue

        match = _FOR_RE.match(line)
        if match:
            variable, start, end, step = match.groups()
            step_expr = _expression(step) if step else "1"
            emit(
                f"for {variable} in _inclusive_range({_expression(start)}, "
                f"{_expression(end)}, {step_expr}):"
            )
            blocks.append("for")
            uses_inclusive_range = True
            continue

        if upper == "REPEAT":
            emit("while True:")
            blocks.append("repeat")
            continue

        if upper.startswith("UNTIL "):
            if not blocks or blocks[-1] != "repeat":
                raise ConversionError(f"Line {line_number}: UNTIL without a matching REPEAT.")
            condition = _expression(line[6:].strip())
            emit(f"if {condition}:", depth=len(blocks))
            emit("break", depth=len(blocks) + 1)
            blocks.pop()
            continue

        if upper.startswith(("OUTPUT ", "DISPLAY ", "PRINT ")):
            expression = line.split(None, 1)[1]
            emit(f"print({_expression(expression)})")
            continue

        if upper.startswith("INPUT "):
            target = line[6:].strip()
            if not re.fullmatch(r"[A-Za-z_]\w*", target):
                raise ConversionError(
                    f"Line {line_number}: INPUT expects a variable name, got {target!r}."
                )
            emit(f"{target} = input()")
            continue

        assignment = _ASSIGNMENT_RE.match(line)
        if assignment:
            variable, value = assignment.groups()
            emit(f"{variable} = {_expression(value)}")
            continue

        # Preserve ordinary Python statements, such as function calls, as-is.
        emit(_expression(line))

    if blocks:
        raise ConversionError(f"Unclosed {blocks[-1].upper()} block at end of input.")

    if uses_inclusive_range:
        helper = [
            "def _inclusive_range(start, end, step=1):",
            "    if step == 0:",
            '        raise ValueError("FOR loop step cannot be zero")',
            "    return range(start, end + (1 if step > 0 else -1), step)",
            "",
        ]
        output = helper + output
    return "\n".join(output) + ("\n" if output else "")


def main(argv: list[str] | None = None, *, stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description="Convert common pseudocode into Python.")
    parser.add_argument("input", nargs="-", help="input pseudocode file (defaults to stdin)")
    parser.add_argument("-o", "--output", help="write Python to this file (defaults to stdout)")
    args = parser.parse_args(argv)

    try:
        source = Path(args.input).read_text(encoding="utf-8") if args.input else stdin.read()
        result = convert(source)
        if args.output:
            Path(args.output).write_text(result, encoding="utf-8")
        else:
            stdout.write(result)
    except (OSError, ConversionError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
