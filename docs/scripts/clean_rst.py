#!/usr/bin/env python3
"""Clean .rst files: strip trailing whitespace, collapse multiple blank lines to one.

Usage: python docs/scripts/clean_rst.py
"""
import pathlib


def clean_text(text: str) -> str:
    lines = text.splitlines()
    out_lines = []
    last_blank = False
    for line in lines:
        # remove trailing whitespace but preserve leading
        line = line.rstrip()
        if line.strip() == "":
            if not last_blank:
                out_lines.append("")
            last_blank = True
        else:
            out_lines.append(line)
            last_blank = False
    # ensure file ends with a single newline
    return "\n".join(out_lines).rstrip() + "\n"


def main():
    root = pathlib.Path(__file__).resolve().parents[1] / "source"
    changed = []
    for p in sorted(root.glob("*.rst")):
        text = p.read_text(encoding="utf-8")
        new = clean_text(text)
        if new != text:
            p.write_text(new, encoding="utf-8")
            changed.append(str(p))
    if changed:
        print("Modified files:")
        for f in changed:
            print(f)
    else:
        print("No changes needed")


if __name__ == "__main__":
    main()
