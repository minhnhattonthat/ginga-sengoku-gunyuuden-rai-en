"""Every known reference to a text string, from all pointer forms (docs/re/text.md §Pointers).

A ref is (kind, slot, target, fmt, extra):
  p16     16-bit in-bank pointer at slot (data/ptr_tables.tsv), plain strings
  p24     24-bit LoROM pointer at slot (event message records, cmd 26 per-faction table, talk-table bases)
  rel16   16-bit offset at slot, added to a base (extra = file offset of the base string)
  fixed   code immediate or other form the build can't rewrite: the target must not move (extra = where);
          fmt None = take the format other refs give the string (plain if none)
Messages after a msg-format target are reached by reading on (no ref); text_ranges.tsv lists the extents.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import events  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / 'data'

TALK_PTRS = 0x1D1925   # $BA:9925: 16 words, pairs (cell map, talk table) per talk type (recruit, diplomacy...)
TALK_TYPES = 8
TALK_LEN = 80          # entries per talk table (one per officer)
QUOTE_BASE = 0x148050  # $A9:8050: LDX #$8050 / LDA #$A9 at $8E:9B98 and $8E:9C80
QUOTE_TABLE = 0x074EC7  # $8E:CEC7: word offsets from QUOTE_BASE, indexed by officer ($1B60)
QUOTE_LEN = 52
PROMPTS = 0x148000     # $A9:8000: 40-cell fixed field drawn by $8E:8618 (LDX #$8000 / LDA #$A9, $1AF0 = $28)
# Battle quote lists, bank $82: an index of words -> per-officer lists of [opponent id | FE][word ptr] ... FF
QUOTE_LISTS = [(0x013098, 50), (0x0132C9, 50)]  # the second index sits at an odd offset
UNIT_LABELS = 0x0118B8  # $82:98B8 (read by $8A:8833): 13 words -> [4-byte prefix][plain string] records
UNIT_LABELS_LEN = 13
# More word tables found by tools/find_refs.py (odd offsets or prefixed records, so find_ptrs.py missed them)
P16_TABLES = [(0x000CB0, 30, 'plain@1'),   # ship class names by ship type, [layout byte][text] records
              (0x005E0F, 4, 'plain'),      # faction names, vertical ($81:E4E5 renderer, FFFE = skip a cell)
              (0x005E59, 4, 'plain'),      # leader names, vertical
              (0x006339, 30, 'plain'),     # ship names by ship type, vertical
              (0x0119C6, 5, 'plain@4')]    # option-screen labels, [4-byte prefix][text] records
P24_TABLES = [(0x00241B, 7, 'plain'),      # $80:A41B: new-flagship speeches in bank $91
              (0x069243, 4, 'fixed:40')]   # $8D:9243: staff-roll leader lines, 20 cells each, no end code
# Strings the code reaches by base + index * stride or an immediate: the build keeps them in place.
# (operand offset, first string, stride, count, fmt, code)
FIXED = [(0x00E545, 0x000C60, 10, 4, 'fixed:10', '$81:E544 ADC #$8C60 (faction * 10)'),
         (0x0704ED, 0x000C88, 10, 4, 'fixed:10', '$8E:84EC ADC #$8C88 (faction * 10) and 11 more'),
         (0x00DC7F, 0x002C91, 8, 11, 'fixed:8', '$81:DC7E ADC #$AC91 (unit * 8)'),
         (0x062339, 0x0623D8, 0, 1, 'fixed:8', '$8C:A338 LDX #$A3D8 (two 2-cell column labels)')]


def rows(name):
    """Rows of a data/*.tsv file as lists of ints (hex fields), skipping # comments."""
    for line in (DATA / name).read_text(encoding='utf-8').splitlines():
        if line.strip() and not line.startswith('#'):
            yield [int(f, 16) for f in line.split('\t')]


def w(rom, o):
    return rom[o] | rom[o + 1] << 8


def lorom24(rom, p):
    return ((rom[p + 2] & 0x7F) << 15) | (w(rom, p) & 0x7FFF)


def collect(rom):
    out = []
    for off, cnt in rows('ptr_tables.tsv'):
        for k in range(cnt):
            p = off + 2 * k
            out.append(('p16', p, (p & ~0x7FFF) | (w(rom, p) & 0x7FFF), 'plain', None))
    seen = set()
    for _ev, _rec, p, t, _n in events.messages(rom):
        if p not in seen:
            seen.add(p)
            out.append(('p24', p, t, 'msg', None))
    for ev, start in events.scripts(rom).items():
        for _no, cmds in events.script(rom, start):
            for c, arg, _o in cmds:
                if c == 0x26:  # per-faction epilogue: 4 pointers at record +0D ($8D:8854)
                    for k in range(4):
                        p = events.f(arg) + 0x0D + 3 * k
                        if p not in seen:
                            seen.add(p)
                            out.append(('p24', p, lorom24(rom, p), 'msg', None))
    for k in range(TALK_TYPES):
        tab =0x1D0000 + (w(rom, TALK_PTRS + 4 * k + 2) & 0x7FFF)
        base = lorom24(rom, tab)
        out.append(('p24', tab, base, 'msg', None))
        for i in range(TALK_LEN):
            p = tab + 3 + 2 * i
            out.append(('rel16', p, base + w(rom, p), 'msg', base))
    for idx, n in QUOTE_LISTS:
        for k in range(n):
            lst = (idx & ~0x7FFF) | (w(rom, idx + 2 * k) & 0x7FFF)
            while rom[lst] != 0xFF:  # [officer id or FE = anyone][16-bit pointer] ... FF
                out.append(('p16', lst + 1, (lst & ~0x7FFF) | (w(rom, lst + 1) & 0x7FFF), 'plain', None))
                lst += 3
    for k in range(UNIT_LABELS_LEN):
        p = UNIT_LABELS + 2 * k
        out.append(('p16', p, (p & ~0x7FFF) | (w(rom, p) & 0x7FFF), 'plain@4', None))
    for tab, n, fmt in P16_TABLES:
        for k in range(n):
            p = tab + 2 * k
            out.append(('p16', p, (p & ~0x7FFF) | (w(rom, p) & 0x7FFF), fmt, None))
    for tab, n, fmt in P24_TABLES:
        for k in range(n):
            out.append(('p24', tab + 3 * k, lorom24(rom, tab + 3 * k), fmt, None))
    for op, base, stride, n, fmt, where in FIXED:
        for k in range(n):
            out.append(('fixed', op, base + stride * k, fmt, where))
    for line in (DATA / 'imm16.tsv').read_text(encoding='utf-8').splitlines():
        if line.strip() and not line.startswith('#'):
            op, t, code, ver = line.split('\t')
            out.append(('fixed', int(op, 16), int(t, 16), None, f'imm {code} verified={ver}'))
    out.append(('fixed', 0x07061C, PROMPTS, 'fixed:80', '$8E:8618'))
    out.append(('fixed', 0x071B99, QUOTE_BASE, 'msg', '$8E:9B98 + $8E:9C80'))
    for i in range(QUOTE_LEN):
        p = QUOTE_TABLE + 2 * i
        out.append(('rel16', p, QUOTE_BASE + w(rom, p), 'msg', QUOTE_BASE))
    return out
