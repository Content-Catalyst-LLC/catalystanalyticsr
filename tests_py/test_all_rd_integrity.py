from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def test_no_stray_escaped_newline_tokens_in_rd_files():
    offenders = []
    for path in sorted((ROOT / "man").glob("*.Rd")):
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"\\n(?!ame\{)", text):
            offenders.append(f"{path.name}:{match.start()}")
    assert not offenders, f"Stray escaped-newline tokens found: {offenders}"


def test_rd_files_end_with_real_newline():
    offenders = []
    for path in sorted((ROOT / "man").glob("*.Rd")):
        raw = path.read_bytes()
        if not raw.endswith(b"\n"):
            offenders.append(path.name)
    assert not offenders, f"Rd files without terminal newline: {offenders}"


def test_rd_usage_blocks_are_balanced_and_multiline_when_needed():
    offenders = []
    for path in sorted((ROOT / "man").glob("*.Rd")):
        text = path.read_text(encoding="utf-8")
        start = 0
        while True:
            idx = text.find(r"\usage{", start)
            if idx < 0:
                break
            cursor = idx + len(r"\usage{")
            depth = 1
            while cursor < len(text) and depth:
                if text[cursor] == "{" and (cursor == 0 or text[cursor - 1] != "\\"):
                    depth += 1
                elif text[cursor] == "}" and (cursor == 0 or text[cursor - 1] != "\\"):
                    depth -= 1
                cursor += 1
            if depth != 0:
                offenders.append(f"{path.name}:unbalanced")
                break
            usage = text[idx:cursor]
            if r"\n" in usage:
                offenders.append(f"{path.name}:escaped-newline")
            start = cursor
    assert not offenders, f"Invalid Rd usage blocks: {offenders}"
