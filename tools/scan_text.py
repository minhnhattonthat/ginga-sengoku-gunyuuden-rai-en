"""Find strings in the game's encoding: runs of 16-bit LE font codes (< 0x528) ending in FFFF.

    python -X utf8 tools/scan_text.py ROM [--min 3] [--kana 0.3] [--tbl tbl/jp.tbl] > out.tsv

Prints offset, length in codes, decoded text. A run must have >= --min codes and a share of kana/kanji/punct
codes (0x40-0x527) of at least --kana, which drops most graphics and code. Both byte alignments are scanned.
Codes >= 0x528 other than FFFF end a run without a hit (control codes, once known, go in KNOWN_CTRL).
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tbl import Table  # noqa: E402

FONT_END = 0x528
KNOWN_CTRL = set()


def scan(rom, minlen, kana):
    hits = []
    for align in (0, 1):
        start = align
        n = 0
        good = 0
        pos = align
        while pos + 1 < len(rom):
            v = rom[pos] | rom[pos + 1] << 8
            if v == 0xFFFF:
                if n >= minlen and good >= kana * n:
                    hits.append((start, n))
                start, n, good = pos + 2, 0, 0
            elif v < FONT_END or v in KNOWN_CTRL:
                n += 1
                if 0x40 <= v < FONT_END and v not in (0x111, 0x112, 0x113, 0x114, 0x115, 0x116, 0x117):
                    good += 1
            else:
                start, n, good = pos + 2, 0, 0
            pos += 2
    return sorted(hits)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom')
    ap.add_argument('--min', type=int, default=3)
    ap.add_argument('--kana', type=float, default=0.5)
    ap.add_argument('--tbl', default=str(Path(__file__).parent.parent / 'tbl/jp.tbl'))
    a = ap.parse_args()
    rom = open(a.rom, 'rb').read()
    t = Table.load(a.tbl)
    for off, n in scan(rom, a.min, a.kana):
        text, _ = t.decode(rom, off, n * 2)
        print('%06X\t%d\t%s' % (off, n, text))


if __name__ == '__main__':
    main()
