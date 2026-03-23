#!/usr/bin/env python3
"""Collapse consecutive duplicate lines in .rst files under docs/source.
"""
from pathlib import Path


def dedupe_file(p: Path) -> bool:
    text = p.read_text(encoding='utf-8')
    lines = text.splitlines()
    out = []
    changed = False
    prev = None
    for l in lines:
        if l == prev:
            # skip duplicate
            changed = True
            continue
        out.append(l)
        prev = l
    if changed:
        p.write_text('\n'.join(out) + '\n', encoding='utf-8')
    return changed


def main():
    root = Path(__file__).resolve().parents[1] / 'source'
    modified = []
    for p in sorted(root.glob('*.rst')):
        if dedupe_file(p):
            modified.append(str(p))
    if modified:
        print('Deduped files:')
        for m in modified:
            print(m)
    else:
        print('No duplicates found')


if __name__ == '__main__':
    main()
