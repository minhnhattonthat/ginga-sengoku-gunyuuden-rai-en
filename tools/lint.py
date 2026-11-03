"""Text lint: every English line against its box budget (data/boxes.tsv, docs/re/boxes.md).

    python -X utf8 tools/lint.py            errors (exit 1) and warnings for script/*.json en fields
    python -X utf8 tools/lint.py --boxes    every string's box (id, box, jp head) for review

data/boxes.tsv: one row per box variant: name, letters per line, lines, wrap, state, evidence, then the
strings it covers (block ids, or single string ids prefixed with '='; a single id wins over its block).
wrap: br = explicit {br} lines (dialogue); pad = the box wraps at its width, {n} in en pads to the next line
(the build fills blank cells); one = a single line; page = {br} lines on a full-screen narration page, at
most PAGE_CELLS glyph cells in all. state: measured (evidence = shot) or guess (warns).
A {skip:0N00} indent takes N cells = 2N letters of its line. Letters are 6 px (two per 12-px cell).
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import en  # noqa: E402
import extract  # noqa: E402

BOXES = Path(__file__).resolve().parents[1] / 'data' / 'boxes.tsv'
SKIP = re.compile(r'\{skip:0?([0-9A-Fa-f])00\}')
PAGE_CELLS = 112  # full-screen narration: the 113th glyph cell overwrites other tiles (work/qa/stress/e113)


def load_boxes():
    """-> ({name: row dict}, {block or string id (int): (name, single)})"""
    boxes, owner = {}, {}
    for line in BOXES.read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        name, letters, lines, wrap, state, evidence, covers = line.split('\t')
        boxes[name] = dict(name=name, letters=int(letters), lines=int(lines), wrap=wrap, state=state,
                           evidence=evidence)
        for c in covers.split():
            owner[int(c.lstrip('='), 16)] = (name, c.startswith('='))
    return boxes, owner


def box_of(sid, block, owner):
    hit = owner.get(sid)
    if hit and hit[1]:
        return hit[0]
    hit = owner.get(block)
    return hit[0] if hit and not hit[1] else None


def lines_of(t, wrap):
    body = t.replace('{end}', '')
    parts = body.split('{br}') if wrap in ('br', 'page') else body.split('{n}')
    out = []
    for p in parts:
        indent = sum(2 * int(m.group(1), 16) for m in SKIP.finditer(p))  # N cells (work/qa/stress/prol2)
        visible = ''.join(s for is_code, s in en.runs(p) if not is_code)
        out.append(indent + len(visible))
    return out


def expand_n(t, width):
    """pad box: each {n} becomes the spaces that fill its line to `width` letters (the box wraps by itself)."""
    parts = t.split('{n}')
    out = []
    for p in parts[:-1]:
        n = lines_of(p, 'pad')[0]
        if n > width:
            raise ValueError(f'line {p!r} has {n} letters > {width}')
        out.append(p + ' ' * (width - n))
    return ''.join(out) + parts[-1]


def lint(script, blocks):
    boxes, owner = load_boxes()
    errs, warns = [], []
    for b in blocks:
        for e in b['entries']:
            s = script.get(e['off'], {})
            t = s.get('en')
            if not t:
                continue
            sid = f'{e["off"]:06X}'
            name = box_of(e['off'], b['start'], owner)
            if not name:
                warns.append(f'{sid}: no box variant (data/boxes.tsv)')
                continue
            box = boxes[name]
            if box['state'] != 'measured':
                warns.append(f'{sid}: box {name} budget is a guess (measure it)')
            try:
                en.pairs(t)
            except ValueError as x:
                errs.append(f'{sid}: {x}')
                continue
            ls = lines_of(t, box['wrap'])
            if len(ls) > box['lines']:
                errs.append(f'{sid}: {len(ls)} lines > {box["lines"]} ({name})')
            for i, n in enumerate(ls):
                if n > box['letters']:
                    errs.append(f'{sid}: line {i + 1} has {n} letters > {box["letters"]} ({name})')
            if box['wrap'] == 'page' and len(en.pairs(t)) > PAGE_CELLS:
                errs.append(f'{sid}: {len(en.pairs(t))} cells > {PAGE_CELLS} per full-screen page ({name})')
            fixed = extract.parse_fmt(e['fmt'])[2]
            if fixed and len(en.pairs(t)) * 2 > fixed:
                errs.append(f'{sid}: {len(en.pairs(t))} cells > fixed field {fixed // 2}')
    return errs, warns


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--boxes', action='store_true')
    a = ap.parse_args()
    rom = extract.ORIG.read_bytes()
    blocks = extract.blocks(rom)
    script = extract.load_script()
    if a.boxes:
        _, owner = load_boxes()
        for b in blocks:
            for e in b['entries']:
                print(f'{e["off"]:06X}\t{box_of(e["off"], b["start"], owner) or "-"}\t{e["jp"][:30]}')
        return 0
    errs, warns = lint(script, blocks)
    for w in warns:
        print('warning:', w)
    for x in errs:
        print('error:', x)
    print(f'lint: {len(errs)} errors, {len(warns)} warnings')
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main())
