"""build.py: original ROM -> build/rai_en.sfc, with a write log and a romdiff check.

    python -X utf8 tools/build.py               normal build (repacks only edited containers; none yet)
    python -X utf8 tools/build.py --repack-all  identity build: unpack and repack every known container

Containers (lists in data/): LZ blocks (data/lz_blocks.tsv, tools/lz.py), word-RLE tilemaps
(data/rle_streams.tsv, tools/rle.py), and text blocks: runs of strings stored back to back, with every ref to
them (tools/extract.py, tools/refs.py; tbl/jp.tbl, tbl/msg_codes.tbl). Both codecs are byte-identical to the original tools, so --repack-all with no
edits gives the original ROM (tests/test_identity.py). Every changed byte goes through Rom.write, which logs it
to build/writes.log in romdiff.py's --writes format; romdiff then fails on any change outside the log.
"""
import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import check_rom  # noqa: E402
import en  # noqa: E402
import extract  # noqa: E402
import font_en  # noqa: E402
import lint  # noqa: E402
import lz  # noqa: E402
import patches  # noqa: E402
import rle  # noqa: E402
import text  # noqa: E402
import romdiff  # noqa: E402
from bps import snes_checksum  # noqa: E402

ORIG = ROOT / 'rom' / 'Ginga Sengoku Gunyuuden Rai (Japan).sfc'
OUT = ROOT / 'build' / 'rai_en.sfc'
DATA = ROOT / 'data'


def rows(name):
    """Rows of a data/*.tsv file as lists of ints (hex fields), skipping # comments."""
    for line in (DATA / name).read_text(encoding='utf-8').splitlines():
        if line.strip() and not line.startswith('#'):
            yield [int(f, 16) for f in line.split('\t')]


# FF runs (docs/re/graphics.md §Free space) text blocks may move into; 0x1E0000+ is the code patches' (patches.py)
FREE = [(0x006812, 0x007C00),  # 0x7C00-0x7FB0: patches.CLASS_TABS
(0x017170, 0x018000), (0x01E562, 0x020000), (0x0407FE, 0x048000),
        (0x04ACCA, 0x050000), (0x05322F, 0x058000), (0x05DD10, 0x060000), (0x0669CD, 0x068000),
        (0x06ED2A, 0x070000), (0x1A22F0, 0x1A8000), (0x1D3071, 0x1D8000)]
# Save-panel labels the code builds from cell immediates (LDY #cell / STY $1B6x, $BA:AB18-ABDB): JP Lv, 惑星数,
# 武将数 with blank cells around (checked on screen). (English, LDY operand offsets): the en build writes their
# pair cells there.
CODE_LABELS = [('Lv  ', [0x1D2B19, 0x1D2B1F]),
               (' Planets  ', [0x1D2B86, 0x1D2B8C, 0x1D2B92, 0x1D2B98, 0x1D2B9E]),
               (' Officers ', [0x1D2BC1, 0x1D2BC7, 0x1D2BCD, 0x1D2BD3, 0x1D2BD9]),
               ('Fort', [0x00DCDF, 0x00DD09])]  # LDA # (16-bit) in the fortress header patch (patches.py)
OFFICERS, NAME_TABLE = 56, 0x0010DC  # $00:90DC: word pointers (bank $00) to the officer names, block 00114C
TAG_SHORT = {'Sanrakusai': 'Sanraku', 'Ryogenkaku': 'Genkaku', 'Sho Shigen': 'Shigen', 'Rin Sokuka': 'Sokuka',
             'Kyo Shisho': 'Shisho'}  # too wide even condensed (glossary.md)
TAG_PX = 42  # speech box: the text starts 48 px after the name; keep a 6-px gap


def speech_tags(rom_orig, script):
    """[(officer, tag)] for names over 7 letters (patches.TAGNAME): a short form, or the name to set condensed."""
    out = []
    for i in range(OFFICERS):
        p = int.from_bytes(rom_orig[NAME_TABLE + 2 * i:NAME_TABLE + 2 * i + 2], 'little') & 0x7FFF
        name = script.get(p, {}).get('en', '').replace('{end}', '')
        if len(name) > 7:
            t = TAG_SHORT.get(name, name)
            assert len(t) <= 7 or len(font_en.strip(t)) <= TAG_PX, f'speech tag {t!r} too wide: add to TAG_SHORT'
            out.append((i, t))
    return out


CLASS_TABLE, CLASSES, CLASS_TABS_END = 0x000CB0, 30, 0x007FB0  # $00:8CB0 ship class records; tabs end


def class_names(rom_orig, script):
    """English ship class name per class (records [layout byte][text] at CLASS_TABLE) for patches.CLASS_TABS."""
    ps = [int.from_bytes(rom_orig[CLASS_TABLE + 2 * k:CLASS_TABLE + 2 * k + 2], 'little') & 0x7FFF
          for k in range(CLASSES)]
    return [script[p]['en'].replace('{end}', '') for p in ps]


FAR = [(0x1E8000, 0x200000)]  # banks $BD-$BF (all FF): blocks reached only by 24-bit pointers
STALE_TALK =0x1D9BA4  # base of talk type 2 ($BA:9E27), a stale table landing mid-string (docs/re/text.md)


class Rom:
    def __init__(self, orig):
        self.orig = bytes(orig)
        self.buf = bytearray(orig)
        self.writes = []  # (offset, orig bytes, new bytes, writer)

    def write(self, off, data, who):
        if off + len(data) > len(self.orig):
            raise ValueError(f'{who}: write at {off:#x} runs past the ROM end')  # shortcut: no expansion yet
        old = bytes(self.buf[off:off + len(data)])
        if old != data:
            self.writes.append((off, self.orig[off:off + len(data)], bytes(data), who))
            self.buf[off:off + len(data)] = data


def repack_lz(rom, edits=None):
    """edits: {offset: new raw bytes}; None = repack every block unchanged. Packed size must not grow."""
    for off, packed_len, raw_len in rows('lz_blocks.tsv'):
        if edits is not None and off not in edits:
            continue
        raw, used = lz.decompress(rom.orig, off)
        assert (used, len(raw)) == (packed_len, raw_len), f'lz {off:06X}: list says {packed_len:#x}/{raw_len:#x}'
        packed = lz.compress(edits[off] if edits else raw)
        if len(packed) > used:
            raise ValueError(f'lz {off:06X}: repacked {len(packed):#x} > original {used:#x} (relocation needed)')
        rom.write(off, packed, f'lz:{off:06X}')


def repack_rle(rom, edits=None):
    for (off,) in rows('rle_streams.tsv'):
        if edits is not None and off not in edits:
            continue
        words, end = rle.decode(rom.orig, off)
        packed = rle.encode(edits[off] if edits else words)
        if len(packed) > end - off:
            raise ValueError(f'rle {off:06X}: repacked {len(packed)} > original {end - off} bytes')
        rom.write(off, packed, f'rle:{off:06X}')


def units(b):
    """Entry index runs that must stay together: a read_on string follows the one before it; a block with rel16
    refs (offsets from a base string) stays whole."""
    if any(r[0] == 'rel16' for e in b['entries'] for r in e['refs'] + e['tails']):
        return [list(range(len(b['entries'])))]
    out = []
    for i, e in enumerate(b['entries']):
        if out and e['read_on']:
            out[-1].append(i)
        else:
            out.append([i])
    return out


def place(bank, size, p24, free, far, orig):
    """Room for a unit that no longer fits its block: a free range in its bank (p16 refs and imm16 operands are
    16-bit), else, when the unit is reached only by p24 (or rel16 from its own base), a far bank. -> start or None.
    Ranges are [start, end, must be FF]; the chosen one shrinks."""
    for r in [r for r in free if r[0] >> 15 == bank] + (far if p24 else []):
        a = r[0] if r[0] >> 15 == (r[0] + size - 1) >> 15 else (r[0] | 0x7FFF) + 1  # don't cross a bank
        if r[1] - a >= size:
            assert not r[2] or set(orig[a:a + size]) == {0xFF}, f'free space {a:06X} is not FF'
            r[0] = a + size
            return a
    return None


def layout(b, sizes, free, far, orig):
    """-> [(address, entry indexes)]: units in the block's own room in order while they fit, the rest each
    placed in free space. The room left over joins `free` for later blocks of the bank."""
    out, pos, us = [], b['start'], units(b)
    while us and pos + sum(sizes[i] for i in us[0]) <= b['end']:
        out.append((pos, us[0]))
        pos += sum(sizes[i] for i in us.pop(0))
    if b['end'] - pos > 0:
        free.append([pos, b['end'], False])
    for u in us:
        es = [b['entries'][i] for i in u]
        base = {e['off'] for e in es}
        p24 = all(r[0] == 'p24' or r[0] == 'rel16' and r[2] in base for e in es for r in e['refs'] + e['tails'])
        a = place(b['start'] >> 15, sum(sizes[i] for i in u), p24, free, far, orig)
        if a is None:
            raise ValueError(f'text {es[0]["off"]:06X}: {sum(sizes[i] for i in u)} bytes, no free space in '
                             f'bank {b["start"] >> 15:02X}' + ('' if p24 else ' (p16/fixed refs keep it there)'))
        out.append((a, u))
    return out


def tail_delta(e, kind, x, d, moves):
    """New offset of a tail ref into edited host e: its English tail (tail_en), 0 for the stale talk table,
    None to leave an unverified immediate alone; raises for anything else."""
    if (e['off'], d) in moves:
        return moves[e['off'], d]
    if kind == 'rel16' and x == STALE_TALK:
        return 0  # the table is stale (docs/re/text.md): any target is as wrong as the JP's mid-string one
    if kind == 'fixed' and 'verified=n' in str(x):
        return None  # probably a constant that matches by chance
    raise ValueError(f'text {e["off"]:06X}: edited string has refs into its middle (tails): give it tail_en')


def repack_text(rom, edits=None, tails_ok=False, loose=False, moves=None):
    """Rewrite text blocks (tools/extract.py): each block's strings back to back from its start, then every ref.
    edits: {string offset: new jp-style text, or encoded bytes}; None = repack every block unchanged. Returns the
    blocks repacked. tails_ok (marker build): a string with tails may change if its length stays the same.
    moves: {(host offset, JP tail offset): offset of its English tail in the host's new bytes} (english_edits).
    A block that outgrows its room keeps what fits and splits the rest into free space (layout: FREE, rooms
    other blocks left over, FAR banks for p24-only units).

    Refs: p16/p24 get the string's new address, rel16 the new distance from its (moved) base string, tails the
    host's new address + offset (host unchanged, else tail_delta). Fixed refs (code immediates, base + index forms)
    can't be rewritten: their strings, and every string before them in the block, must keep their offsets."""
    blocks = extract.blocks(rom.orig)
    moves = moves or {}
    if edits is not None:
        blocks = [b for b in blocks if any(b['start'] <= s < b['end'] for s in edits)]
    free = [[a + 0x10, z, True] for a, z in FREE]  # margin: a run may start with the FF end code of real data
    far = [[a, z, True] for a, z in FAR]
    for b in blocks:
        new, datas, changed = {}, [], set()
        for e in b['entries']:
            text = (edits or {}).get(e['off'])
            if isinstance(text, bytes):  # already encoded (English, marker), prefix included
                data = text
            else:
                data = extract.encode(e['jp'] if text is None else text, e['pre'], e['fmt'])
            fixed = extract.parse_fmt(e['fmt'])[2]
            if fixed and len(data) != fixed:
                raise ValueError(f'text {e["off"]:06X}: fixed field is {fixed} bytes, got {len(data)}')
            if text is not None and e['tails'] and text != e['jp'] and not (tails_ok and len(data) == e['len']):
                changed.add(e['off'])
                for kind, _, x, d in e['tails']:
                    tail_delta(e, kind, x, d, moves)
            datas.append(data)
        for a, u in layout(b, [len(d) for d in datas], free, far, rom.orig):
            rom.write(a, b''.join(datas[i] for i in u), f'text:{b["start"]:06X}')
            for i in u:
                new[b['entries'][i]['off']] = a
                a += len(datas[i])
        for e in b['entries']:
            for kind, slot, x, *delta in e['refs'] + e['tails']:
                d = delta[0] if delta else 0
                if delta and e['off'] in changed:
                    d = tail_delta(e, kind, x, d, moves)
                    if d is None:
                        continue
                t = new[e['off']] + d
                if kind == 'fixed':
                    if loose and 'verified=n' in str(x):
                        continue  # unverified immediates are probably constants (docs/re/text.md §imm16)
                    if (str(x).startswith('imm ') and 'verified=y' in str(x) and not (t ^ e['off']) & ~0x7FFF
                            and rom.orig[slot - 1] in (0xA0, 0xA2)):  # LDY/LDX #: an LDA # may be 8-bit
                        rom.write(slot, (0x8000 | t & 0x7FFF).to_bytes(2, 'little'), f'imm:{slot:06X}')
                    elif t != e['off'] + (delta[0] if delta else 0):
                        raise ValueError(f'text {e["off"]:06X}: moved, but code at {slot:06X} holds it fixed')
                elif kind != 'p24' and (t ^ (new[x] if kind == 'rel16' else b['start'])) & ~0x7FFF:
                    raise ValueError(f'text {e["off"]:06X}: string left its bank')
                elif kind == 'p16':
                    rom.write(slot, (0x8000 | t & 0x7FFF).to_bytes(2, 'little'), f'ptr:{slot:06X}')
                elif kind == 'p24':
                    rom.write(slot, bytes([t & 0xFF, 0x80 | (t >> 8) & 0x7F, rom.orig[slot + 2] & 0x80 | t >> 15]),
                              f'ptr:{slot:06X}')
                elif kind == 'rel16':
                    rom.write(slot, (t - new[x]).to_bytes(2, 'little'), f'ptr:{slot:06X}')
    return blocks


FILL = 'The quick brown fox jumps over the lazy dog. '


def marker(e, codec, short=False):
    """'[id] The quick...' with the cell count of every Japanese text run kept, so the layout (box padding,
    vertical {FFFE} skips, fixed fields) and the byte length stay those of the original. short: each run at
    most 4 cells (frees room in a block for a --qa stress line)."""
    tab = text.table(codec)
    cells = lambda t: min(len(tab.encode(t)) // 2, 4 if short else 9999)  # noqa: E731
    n = 2 * sum(cells(t) for is_code, t in en.runs(e['jp']) if not is_code)
    tag = f'{e["off"]:06X}'
    tag = tag if n >= 8 else tag[-n:]
    stream = iter(tag + ' ' + FILL * (n // len(FILL) + 1))
    return ''.join(t if is_code else ''.join(next(stream) for _ in range(2 * cells(t)))
                   for is_code, t in en.runs(e['jp']))


def english_edits(rom_orig, mode='en', qa=None):
    """-> ({off: encoded bytes}, {font cell: glyph}). mode 'en': strings with an 'en' field (others stay
    Japanese and keep their cells); 'marker': every string as its marker. qa: {off: text} overrides."""
    script = extract.load_script()
    boxes, owner = lint.load_boxes()
    texts = {}
    for b in extract.blocks(rom_orig):
        short = any(len(en.pairs(qa[e['off']])) > len(en.pairs(marker(e, extract.parse_fmt(e['fmt'])[0])))
                    for e in b['entries'] if e['off'] in (qa or {}))  # a longer stress line needs room
        for e in b['entries']:
            s = script.get(e['off'], {})
            codec, _, fixed = extract.parse_fmt(e['fmt'])
            t = (qa or {}).get(e['off'])
            if t and not fixed and not t.endswith('{end}'):
                t += '{end}'
            t = t or (
                marker(e, codec, short and not fixed and not e['tails']) if mode == 'marker' else s.get('en'))
            box = boxes.get(lint.box_of(e['off'], b['start'], owner))
            if t and box and box['wrap'] == 'pad':
                t = lint.expand_n(t, box['letters'])
            if t:
                texts[e['off']] = (e, t)
    labels = [t for t, _ in CODE_LABELS] if mode == 'en' else []
    tags = speech_tags(rom_orig, script) if mode == 'en' else []
    labels += [t for _, t in tags if len(t) <= 7]
    tails = {off: {int(d): t for d, t in script[off].get('tail_en', {}).items()}
             for off in texts if mode == 'en' and off not in (qa or {}) and script.get(off, {}).get('tail_en')}
    jp_left = [e for b in extract.blocks(rom_orig) for e in b['entries'] if e['off'] not in texts]
    alloc = en.Alloc([t for _, t in texts.values()] + [t for d in tails.values() for t in d.values()] + labels,
                     en.jp_cells(rom_orig, jp_left))
    imms = {}
    for t, ops in CODE_LABELS if labels else []:
        data = alloc.encode(t, 'plain')
        assert len(data) == 2 * len(ops), t
        for k, op in enumerate(ops):
            assert rom_orig[op - 1] in (0xA0, 0xA9), f'{op:06X}: not LDY # / LDA #'
            imms[op] = data[2 * k:2 * k + 2]
    out, moves = {}, {}
    for off, (e, t) in texts.items():
        codec = extract.parse_fmt(e['fmt'])[0]
        data = e['pre'] + alloc.encode(t, codec)
        fixed = extract.parse_fmt(e['fmt'])[2]
        if fixed and len(data) < fixed:  # fixed fields: pad with blank cells
            data += en.SPACE.to_bytes(2, 'little') * ((fixed - len(data)) // 2)
        for d, tt in sorted(tails.get(off, {}).items()):  # a name tail other refs point into: its own string after
            moves[off, d] = len(data)
            data += alloc.encode(tt, codec)
        out[off] = data
    cells = alloc.cells()
    if mode == 'en':
        cells.update({c: font_en.cell(p) for c, p in en.QUOTES.items()})
        spare = iter(alloc.spare)

        def fit(t, letters):  # pairs if it fits, else condensed glyph cells (4 cells)
            if len(t) <= letters:
                return alloc.encode(t + '{end}', 'plain')
            out = b''
            for glyph in font_en.strip_cells(font_en.strip(t), 4):
                c = next(spare)
                cells[c] = glyph
                out += c.to_bytes(2, 'little')
            return out + b'\xff\xff'

        def table(addr, n, items, prefix=b''):  # word pointers (0 = none) then the strings, at CPU addr
            tab, data, seen = bytearray(2 * n), bytearray(), {}
            for i, t in items:
                if t not in seen:
                    seen[t] = addr + 2 * n + len(data)
                    data += prefix + t
                tab[2 * i:2 * i + 2] = (seen[t] & 0xFFFF).to_bytes(2, 'little')
            imms[patches.off(addr)] = bytes(tab + data)

        table(patches.TAG_TABLE, OFFICERS, [(i, fit(t, 7)) for i, t in tags])
        names = class_names(rom_orig, script)
        assert all(len(font_en.strip(t)) <= 48 for t in names if len(t) > 8), names
        table(patches.CLASS_TABS, len(names), [(i, fit(t, 8)) for i, t in enumerate(names)], b'\x02')
        assert patches.off(patches.CLASS_TABS) + 2 * len(names) + 13 * len(names) <= CLASS_TABS_END
    if mode == 'marker':  # every other cell shows '##': font text the extractor missed can't hide as Japanese
        cells.update({c: font_en.cell('##') for c in range(en.CELLS) if c not in cells and c not in en.RESERVED})
    return out, cells, moves, imms


def build(repack_all=False, edits=None, mode=None, qa=None):
    """edits: {'lz': {off: raw}, 'rle': {off: words}, 'text': {off: text}} (tests). mode: None (Japanese
    text), 'en' (script en fields) or 'marker'; qa: {off: text} single-line overrides (width gate, torture)."""
    check_rom.check()
    rom = Rom(ORIG.read_bytes())
    edits = dict(edits or {})
    if mode:
        patches.apply(rom)
        edits['text'], cells, moves, imms = english_edits(rom.orig, mode, qa)
        for c, glyph in sorted(cells.items()):
            rom.write(en.FONT + c * 24, glyph, f'font:{c:03X}')
        for op, data in sorted(imms.items()):
            rom.write(op, data, f'imm:{op:06X}')
    repack_lz(rom, None if repack_all else edits.get('lz', {}))
    repack_rle(rom, None if repack_all else edits.get('rle', {}))
    blocks = repack_text(rom, None if repack_all else edits.get('text', {}), tails_ok=mode == 'marker',
                         loose=mode == 'en' or mode == 'marker' and bool(qa), moves=moves if mode else None)
    fixed, _ = snes_checksum(rom.buf)
    for off in range(0x7FDC, 0x7FE0):
        rom.write(off, fixed[off:off + 1], 'checksum')
    return rom, blocks


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--repack-all', action='store_true')
    ap.add_argument('--marker', action='store_true', help='every string as "[id] marker text" (phase 5)')
    ap.add_argument('--jp', action='store_true', help='ignore en fields (Japanese text)')
    ap.add_argument('--qa', action='append', default=[], metavar='ID=TEXT', help='override one string')
    ap.add_argument('--out', type=Path, default=OUT)
    a = ap.parse_args()
    qa = {int(k, 16): v for k, v in (s.split('=', 1) for s in a.qa)}
    out = a.out
    out.parent.mkdir(exist_ok=True)
    out.unlink(missing_ok=True)  # a failed build must not leave a stale ROM to test
    mode = 'marker' if a.marker else None if a.jp and not qa else 'en'
    rom, blocks = build(a.repack_all, mode=mode, qa=qa)
    log = out.with_name(out.stem + '.writes.log' if out != OUT else 'writes.log')
    log.write_text(''.join(f'{o:06X} {old.hex()} {new.hex()} {who}\n' for o, old, new, who in rom.writes),
                   encoding='utf-8')
    errs, _ = romdiff.check(rom.orig, bytes(rom.buf), set(), romdiff.load_writes(log))
    if errs:
        sys.exit('romdiff:\n' + '\n'.join(errs))
    out.write_bytes(rom.buf)
    if a.repack_all:
        print(f'repacked {sum(1 for _ in rows("lz_blocks.tsv"))} LZ blocks, '
              f'{sum(1 for _ in rows("rle_streams.tsv"))} RLE streams, {len(blocks)} text blocks '
              f'({sum(len(b["entries"]) for b in blocks)} strings, '
              f'{sum(len(e["refs"]) + len(e["tails"]) for b in blocks for e in b["entries"])} refs)')
    print(f'{out}  {len(rom.writes)} writes  sha1 {hashlib.sha1(rom.buf).hexdigest()}'
          f'  {"identical to original" if rom.buf == rom.orig else "changed"}')


if __name__ == '__main__':
    main()
