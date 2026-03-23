#!/usr/bin/env python3
"""Fix reStructuredText section underlines to match title lengths.

This script scans .rst files under docs/source and adjusts underline
lines that consist of a single repeated punctuation character so that
their length equals the title line length.
"""
from pathlib import Path
import re


def fix_file(p: Path) -> bool:
    text = p.read_text(encoding='utf-8')
    lines = text.splitlines()
    changed = False
    out = []
    i = 0
    while i < len(lines):
        out.append(lines[i])
        # lookahead for underline-only line
        if i + 1 < len(lines):
            title = lines[i]
            underline = lines[i+1]
            if title.strip() and re.fullmatch(r'([^\w\s])\1*', underline):
                # underline is composed of repeated punctuation (one or more chars)
                # pick the first char as the underline char
                char = underline[0]
                # compute desired length as title length (including full-width chars)
                length = len(title)
                new_ul = char * length
                if new_ul != underline:
                    out.append(new_ul)
                    changed = True
                    i += 2
                    continue
        i += 1

    if changed:
        p.write_text('\n'.join(out) + '\n', encoding='utf-8')
    return changed


def main():
    root = Path(__file__).resolve().parents[1] / 'source'
    modified = []
    for p in sorted(root.glob('*.rst')):
        if fix_file(p):
            modified.append(str(p))
    if modified:
        print('Adjusted headings in:')
        for m in modified:
            print(m)
    else:
        print('No heading changes')


if __name__ == '__main__':
    main()
