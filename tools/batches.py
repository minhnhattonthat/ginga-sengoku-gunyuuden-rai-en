"""Translation batches (phase 6): split the script, wrap authored English to its box, check, merge.

    python -X utf8 tools/batches.py split [--size 3500] [--skip 148000]   new work/tl/bNNN.tsv (id, box, limit, jp)
    python -X utf8 tools/batches.py check bNNN [bNNN..]   wrap + validate work/tl/bNNN.en.tsv; exit 1 on errors
    python -X utf8 tools/batches.py merge bNNN [bNNN..]   check, then write en into script/*.json
    python -X utf8 tools/batches.py fit ID "text"          print the wrapped lines of one string
    python -X utf8 tools/batches.py set bNNN ID "text" ..  replace lines of bNNN.en.tsv by id, then check

English input (bNNN.en.tsv): `id<TAB>text`, written with the file-write tool. Text without {br}/{n}/{skip} is
wrapped to the string's box (data/boxes.tsv): br boxes get {br} lines; dialogue continues each line under the
opening quote ({br}{skip:0K00} + a space, K = cells of the speaker prefix up to the first {c5}); pad boxes get
{n}; page boxes {br}. Text that already has breaks is kept as written. {end} is appended when the JP has it.
A space right after a code moves before it when the run before the code is odd (no half-cell gap mid-line).
Checks: id set, codes {end} {FFFD} {FFFE} as in the JP ({FFFE} spacing may drop in names/labels), {c5}/{c6}
alternating with the JP's first and last (typewriter on/off: an English line may merge pairs),
glyphs, box lines/letters, fixed-field cells, page cells. Glossary misses are warnings.
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import en  # noqa: E402
import extract  # noqa: E402
import lint  # noqa: E402
import text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TL = ROOT / 'work' / 'tl'
GLOSSARY = ROOT / 'glossary.md'
KEPT = ('{end}', '{c5}', '{c6}', '{FFFD}', '{FFFE}')
FFFE_SPACING = ('vertical_name', 'label', 'officer_name', 'full_name')  # {FFFE} = a blank cell there (docs/re/font.md)
BREAKS = re.compile(r'\{(br|n|skip:[0-9A-Fa-f]+)\}')
SPEAKER = re.compile(r'([A-Z][A-Za-z\- ]*?) ?(\{c5\})?(?=")')


def entries():
    """{id: (entry, block start, box name)} in ROM order."""
    rom = extract.ORIG.read_bytes()
    _, owner = lint.load_boxes()
    out = {}
    for b in extract.blocks(rom):
        for e in b['entries']:
            out[f'{e["off"]:06X}'] = (e, b['start'], lint.box_of(e['off'], b['start'], owner))
    return out


TYPE = ('{c5}', '{c6}')  # typewriter on / off ($1E bit 0): pairs may be merged, the on/off pattern kept


def typing(t):
    """(first, last) of the {c5}/{c6} codes (a repeated code changes nothing: the flag is set or clear)."""
    seq = [c for c in en.TOKEN.findall(t) if c in TYPE]
    return (seq[0], seq[-1]) if seq else ()


def width(t, wrap='one'):
    return max(lint.lines_of(t, wrap))


def jp_lines(jp):
    """Cells per {br} line of a JP string (one cell per character; codes take none)."""
    return [len(en.TOKEN.sub('', p)) for p in jp.replace('{end}', '').split('{br}')]


def own_budget(box, jp):
    """battle_cmd is not measured (docs/status.md): hold each string to its own JP lines (cells, count)."""
    if box and box['name'] == 'battle_cmd' and '{br}' in jp + '{br}':
        return dict(box, letters=2 * max(jp_lines(jp)), lines=len(jp_lines(jp)))
    return box


def wrap(text, jp, box):
    """Authored English -> box text with breaks and {end}."""
    box = own_budget(box, jp)
    t = text[:-5] if jp.endswith('{end}') and text.endswith('{end}') else text
    if box and box['wrap'] != 'one' and not BREAKS.search(t):
        brk = '{n}' if box['wrap'] == 'pad' else '{br}'
        lead, cont = '', ''
        m = SPEAKER.match(t) if box['name'] == 'dialogue' else None
        if m:  # 'Name{c5}"text' or 'Name "text': next lines start under the text after the quote
            name, c5, t = m.group(1), m.group(2) or '', t[m.end():]
            if c5 and len(name) % 2:  # odd name: its half-cell pad is the space before the quote
                lead, at = name + c5, len(name) + 2
            else:  # the quote joins the name's run
                lead, t, at = name + ' "' + c5, t[1:], len(name) + 2
            cont = f'{{skip:0{at // 2:X}00}}' + ' ' * (at % 2)
        # talk: the box wraps by itself after 14 cells, so a full line + {br} could leave a blank line
        limit = box['letters'] - 2 if box['name'] == 'talk' else box['letters']
        lines, cur = [], lead
        for w in t.split(' '):
            cand = (cur + ' ' + w) if cur not in ('', lead, cont) else cur + w
            if width(cand) > limit and cur not in (lead, cont):
                lines.append(cur)
                cur = cont + w
            else:
                cur = cand
        lines.append(cur)
        t = brk.join(lines)
    t = no_gap(t)
    if jp.endswith('{end}'):
        t += '{end}'
    return t


def no_gap(t):
    """Move a space from after a code to before it when the run before is odd: keeps words a letter apart."""
    toks = [s for s in en.TOKEN.split(t) if s]
    for i, s in enumerate(toks):
        if s.startswith('{') or not s.startswith(' ') or not i or not toks[i - 1].startswith('{'):
            continue
        j = i - 1  # the text run before the codes (not across a line break)
        while j >= 0 and toks[j].startswith('{') and not BREAKS.fullmatch(toks[j]):
            j -= 1
        k = i + 1  # the text run after this one's codes, if s is a lone space
        while k < len(toks) and toks[k].startswith('{') and not BREAKS.fullmatch(toks[k]):
            k += 1
        if j >= 0 and not toks[j].startswith('{') and len(toks[j]) % 2:
            toks[j], toks[i] = toks[j] + ' ', s[1:]  # fills the half-cell the odd run leaves
        elif s == ' ' and k < len(toks) and not toks[k].startswith('{'):
            toks[i], toks[k] = '', ' ' + toks[k]  # a lone space would take a whole cell
    return ''.join(toks)


def gaps(t):
    """Odd runs followed by a code mid-line (a 6-px gap shows there)."""
    out = []
    toks = [s for s in en.TOKEN.split(t) if s]
    for i, s in enumerate(toks[:-1]):
        nxt = ''.join(toks[i + 1:])
        follow = re.match(r'(\{[^}]*\})+([^{]?)', nxt)
        if (not s.startswith('{') and len(s) % 2 and s[-1] != ' ' and follow and not BREAKS.match(nxt)
                and follow.group(2) not in ('', ' ', '"')):
            out.append(s[-6:])
    return out


def glossary():
    """[(jp, [en forms])] from glossary.md tables (EN column; alternatives split by ' / ')."""
    rows = []
    for line in GLOSSARY.read_text(encoding='utf-8').splitlines():
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        if len(c) >= 2 and line.startswith('|') and c[0] not in ('JP', '') and not set(c[0]) <= set('-'):
            rows.append((c[0], [x.strip() for x in c[1].split(' / ') if x.strip()]))
    return sorted(rows, key=lambda r: -len(r[0]))


def check(name, E=None, quiet=False):
    """-> ({id: final en}, errors, warnings)"""
    E = E or entries()
    boxes, _ = lint.load_boxes()
    ids = [ln.split('\t')[0] for ln in (TL / f'{name}.tsv').read_text(encoding='utf-8').splitlines() if ln]
    path = TL / f'{name}.en.tsv'
    got, errs, warns = {}, [], []
    for n, ln in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not ln.strip():
            continue
        if '\t' not in ln:
            errs.append(f'{name}.en.tsv:{n}: no tab')
            continue
        i, t = ln.split('\t', 1)
        if i in got:
            errs.append(f'{i}: duplicate')
        got[i] = t
    for i in sorted(set(ids) - set(got)):
        errs.append(f'{i}: missing')
    for i in sorted(set(got) - set(ids)):
        errs.append(f'{i}: not in this batch')
    gl = glossary()
    out = {}
    for i in [x for x in ids if x in got]:
        e, _, bname = E[i]
        box = own_budget(boxes.get(bname), e['jp'])
        raw = got[i]
        if '\t' in raw or re.search(r'\\u[0-9a-fA-F]{4}|\\n', raw):
            errs.append(f'{i}: tab or escape in text')
            continue
        t = wrap(raw, e['jp'], box)
        out[i] = t
        want = Counter(c for c in en.TOKEN.findall(e['jp']) if c in KEPT and c not in TYPE)
        have = Counter(c for c in en.TOKEN.findall(t) if c in KEPT and c not in TYPE)
        tw, th = typing(e['jp']), typing(t)
        if tw != th:
            errs.append(f'{i}: {{c5}}/{{c6}} pattern {th} != JP {tw} (alternate, same first and last)')
        if bname in FFFE_SPACING:
            want.pop('{FFFE}', None)
            have.pop('{FFFE}', None)
        if want != have:
            errs.append(f'{i}: codes {dict(have)} != JP {dict(want)}')
        try:
            en.pairs(t)
        except ValueError as x:
            errs.append(f'{i}: {x}')
            continue
        if not box:
            errs.append(f'{i}: no box variant')
            continue
        ls = lint.lines_of(t, box['wrap'])
        if len(ls) > box['lines']:
            errs.append(f'{i}: {len(ls)} lines > {box["lines"]} ({bname}): {t}')
        for k, w in enumerate(ls):
            if w > box['letters']:
                errs.append(f'{i}: line {k + 1} is {w} letters > {box["letters"]} ({bname}): {t}')
        if box['wrap'] == 'pad' and re.search(r'\{FFF[DE]\}.*\{n\}', t):
            errs.append(f'{i}: a name before {{n}} (pad box): put the name on the last line: {t}')
        if box['wrap'] == 'page' and len(en.pairs(t)) > lint.PAGE_CELLS:
            errs.append(f'{i}: {len(en.pairs(t))} cells > {lint.PAGE_CELLS} ({bname})')
        codec, _, fixed = extract.parse_fmt(e['fmt'])
        tx = t
        if box['wrap'] == 'pad':
            try:
                tx = lint.expand_n(t, box['letters'])
            except ValueError:
                pass  # reported above as a long line
        tx = tx.replace('{n}', '')
        size = 2 * len(en.pairs(tx)) + sum(len(text.table(codec).encode(c)) for c in en.TOKEN.findall(tx))
        if fixed and size > fixed:
            errs.append(f'{i}: {size} bytes > fixed field {fixed}')
        for g in gaps(t):
            warns.append(f'{i}: half-cell gap after "{g}"')
        jp = e['jp']
        for term, forms in gl:
            if term in jp:
                jp = jp.replace(term, '\0')
                if forms and not any(f.lower() in raw.lower() for f in forms):
                    warns.append(f'{i}: glossary {term} -> {" / ".join(forms)} not in "{raw}"')
    if not quiet:
        for w in warns:
            print('warning:', w)
        for x in errs:
            print('error:', x)
        print(f'{name}: {len(out)} strings, {len(errs)} errors, {len(warns)} warnings')
    return out, errs, warns


def merge(names):
    E = entries()
    allout = {}
    for n in names:
        out, errs, _ = check(n, E)
        if errs:
            print(f'{n}: not merged ({len(errs)} errors)')
            return 1
        allout.update(out)
    for p in sorted(extract.SCRIPT.glob('*.json')):
        d = json.loads(p.read_text(encoding='utf-8'))
        hit = [e for e in d['entries'] if e['id'] in allout]
        if hit:
            for e in hit:
                e['en'] = allout[e['id']]
            p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    print(f'merged {len(allout)} strings')
    return 0


def split(size, skip):
    TL.mkdir(parents=True, exist_ok=True)
    boxes, _ = lint.load_boxes()
    done = {ln.split('\t')[0] for p in TL.glob('b[0-9][0-9][0-9].tsv')
            for ln in p.read_text(encoding='utf-8').splitlines() if ln}
    num = 1 + max([int(p.stem[1:]) for p in TL.glob('b[0-9][0-9][0-9].tsv')] or [0])
    cur, chars, last = [], 0, None
    batches = []
    for i, (e, start, bname) in entries().items():
        if i in done or f'{start:06X}' in skip or not e['jp'].replace('{end}', '').strip():
            continue
        box = boxes.get(bname, {})
        if cur and (chars + len(e['jp']) > size or (len(cur) >= 150) or
                    (last != start and chars > size * 0.6)):
            batches.append(cur)
            cur, chars = [], 0
        cur.append(f'{i}\t{bname}\t{box.get("letters")}x{box.get("lines")} {box.get("wrap")}'
                   f'{" fixed:" + str(extract.parse_fmt(e["fmt"])[2]) if extract.parse_fmt(e["fmt"])[2] else ""}'
                   f'\t{e["jp"]}')
        chars += len(e['jp'])
        last = start
    if cur:
        batches.append(cur)
    for b in batches:
        p = TL / f'b{num:03d}.tsv'
        assert not p.exists(), p
        p.write_text('\n'.join(b) + '\n', encoding='utf-8', newline='\n')
        print(p.name, len(b))
        num += 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['split', 'check', 'merge', 'fit', 'set'])
    ap.add_argument('args', nargs='*')
    ap.add_argument('--size', type=int, default=3500)
    ap.add_argument('--skip', default='148000')
    a = ap.parse_args()
    if a.cmd == 'split':
        return split(a.size, a.skip.split(','))
    if a.cmd == 'set':  # set bNNN ID TEXT [ID TEXT..]: replace whole lines of bNNN.en.tsv by id
        p = TL / f'{a.args[0]}.en.tsv'
        new = dict(zip(a.args[1::2], a.args[2::2]))
        lines = p.read_text(encoding='utf-8').splitlines()
        hit = {ln.split('\t')[0] for ln in lines} & set(new)
        assert hit == set(new), f'not in {p.name}: {set(new) - hit}'
        p.write_text('\n'.join(f'{ln.split(chr(9))[0]}\t{new[ln.split(chr(9))[0]]}' if ln.split('\t')[0] in new
                               else ln for ln in lines) + '\n', encoding='utf-8', newline='\n')
        return check(a.args[0], quiet=False)[1] and 1 or 0
    if a.cmd == 'fit':
        E = entries()
        e, _, bname = E[a.args[0]]
        t = wrap(a.args[1], e['jp'], lint.load_boxes()[0].get(bname))
        print(bname, lint.lines_of(t, lint.load_boxes()[0][bname]['wrap']))
        print(t)
        return 0
    if a.cmd == 'check':
        E = entries()
        return 1 if any(check(n, E)[1] for n in a.args) else 0
    return merge(a.args)


if __name__ == '__main__':
    sys.exit(main())
