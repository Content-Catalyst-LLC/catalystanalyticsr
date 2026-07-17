#!/usr/bin/env python3
"""Lightweight lexical checks for R source when an R runtime is unavailable."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = sorted((ROOT / "R").glob("*.R")) + sorted((ROOT / "tests").rglob("*.R"))
PAIRS = {")": "(", "]": "[", "}": "{"}
OPENERS = set(PAIRS.values())
ALLOWED_ESCAPES = set("abfnrtv\\'\"`01234567xuU\n")


def check(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    stack: list[tuple[str, int, int]] = []
    quote = None
    escaped = False
    comment = False
    line = 1
    column = 0
    i = 0
    while i < len(text):
        char = text[i]
        column += 1
        if char == "\n":
            line += 1
            column = 0
            comment = False
            if quote and escaped:
                escaped = False
            i += 1
            continue
        if comment:
            i += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                if i + 1 >= len(text) or text[i + 1] not in ALLOWED_ESCAPES:
                    nxt = "<eof>" if i + 1 >= len(text) else text[i + 1]
                    raise AssertionError(f"{path}:{line}:{column}: invalid R escape \\{nxt}")
                escaped = True
            elif char == quote:
                quote = None
            i += 1
            continue
        if char == "#":
            comment = True
        elif char in ('"', "'", "`"):
            quote = char
        elif char in OPENERS:
            stack.append((char, line, column))
        elif char in PAIRS:
            if not stack or stack[-1][0] != PAIRS[char]:
                raise AssertionError(f"{path}:{line}:{column}: mismatched {char}")
            stack.pop()
        i += 1
    if quote:
        raise AssertionError(f"{path}: unclosed quote {quote}")
    if stack:
        opener, open_line, open_column = stack[-1]
        raise AssertionError(f"{path}:{open_line}:{open_column}: unclosed {opener}")


def main() -> int:
    if not FILES:
        raise AssertionError("No R source files found")
    for path in FILES:
        check(path)
    print(f"R lexical structure passed for {len(FILES)} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
