"""English encoder: script text -> font-cell codes, two letters per cell (tools/font_en.py, docs/re/font.md).

Each run of text between control codes is cut into pairs from its start (an odd run ends in "x "). The pairs a
build uses get font cells at build time (Alloc): the most frequent first, from the cells no remaining Japanese
string and no code-drawn number needs. Control codes `{...}` go through the Japanese table of the string's
format unchanged ({end}, {br}, {FFFE}, {spd:...}).
"""
import re
from collections import Counter

import font_en
import text

FONT = 0x0A8000          # cell c at FONT + c * 24 (bank $95)
CELLS = 0x528            # 0x000-0x527 are font; past that is other data
SPACE = 0x3E             # the game's blank cell; also the pair "  "
RESERVED = set(range(0x0A)) | {SPACE}  # digits: numbers are drawn by code from cells 0-9
TOKEN = re.compile(r'(\{[^}]*\})')


def runs(s):
    """[(is_code, str)] in order."""
    return [(t.startswith('{'), t) for t in TOKEN.split(s) if t]


def pairs(s):
    out = []
    for is_code, t in runs(s):
        if not is_code:
            bad = sorted(set(t) - set(font_en.G))
            if bad:
                raise ValueError(f'no glyph for {bad} in {s!r}')
            t += ' ' * (len(t) % 2)
            out += [t[i:i + 2] for i in range(0, len(t), 2)]
    return out


class Alloc:
    """pair -> cell code for one build. busy: cells that must keep their Japanese glyph."""

    def __init__(self, texts, busy=()):
        count = Counter(p for s in texts for p in pairs(s))
        count.pop('  ', None)
        free = [c for c in range(CELLS) if c not in RESERVED and c not in set(busy)]
        order = sorted(count, key=lambda p: (-count[p], p))
        if len(order) > len(free):
            raise ValueError(f'{len(order)} letter pairs, {len(free)} free font cells '
                             f'(least used: {order[len(free):][-10:]})')
        self.code = dict(zip(order, free))
        self.code['  '] = SPACE

    def cells(self):
        """{code: 24-byte glyph} for every allocated pair (the space cell is the game's own)."""
        return {c: font_en.cell(p) for p, c in self.code.items() if c != SPACE}

    def encode(self, s, codec):
        tab, out = text.table(codec), bytearray()
        for is_code, t in runs(s):
            if is_code:
                out += tab.encode(t)
            else:
                for p in pairs(t):
                    out += self.code[p].to_bytes(2, 'little')
        return bytes(out)


def jp_cells(rom, entries):
    """Font cells the Japanese strings in entries use (they stay drawable while the string stays JP)."""
    used = set()
    for e in entries:
        data = rom[e['off']:e['off'] + e['len']][len(e['pre']):]
        used.update(int.from_bytes(data[i:i + 2], 'little') for i in range(0, len(data) - 1, 2))
    return {c for c in used if c < CELLS}


def selftest():
    a = Alloc(['Hello{end}', 'He said "Hi"{FFFE}'])
    assert pairs('Hello{end}') == ['He', 'll', 'o ']
    assert a.code['He'] == 0x0A  # most frequent first, from the first free cell
    enc = a.encode('He{FFFE}  {end}', 'plain')
    assert enc == bytes([0x0A, 0, 0xFE, 0xFF, SPACE, 0, 0xFF, 0xFF]), enc.hex()
    assert a.encode('Hello{br}{end}', 'msg')[-8:] == bytes.fromhex('FFFF0100FFFF0000')
    try:
        pairs('{x}é')
        raise AssertionError('accepted a character with no glyph')
    except ValueError:
        pass
    print('en selftest ok')


if __name__ == '__main__':
    selftest()
