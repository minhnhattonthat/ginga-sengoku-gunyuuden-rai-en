"""Find 16-bit pointer tables whose entries point at strings in the same LoROM bank.

    python -X utf8 tools/find_ptrs.py ROM [--run 3] > work/recon/ptrs.tsv

A string start is the first code of a scan_text.py hit (min 1 code, kana share >= 0.5). A table is a run of
>= --run consecutive words (even or odd alignment) that each point at a string start in their own bank.
Prints table offset, entry count, first/last target, and the decoded first string.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from scan_text import scan  # noqa: E402
from tbl import Table  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom')
    ap.add_argument('--run', type=int, default=3)
    a = ap.parse_args()
    rom = open(a.rom, 'rb').read()
    t = Table.load(Path(__file__).parent.parent / 'tbl/jp.tbl')
    starts = {off for off, n in scan(rom, 1, 0.5)}
    for align in (0, 1):
        pos = align
        run = []
        while pos + 1 < len(rom):
            w = rom[pos] | rom[pos + 1] << 8
            tgt = (pos & ~0x7FFF) | (w & 0x7FFF)
            if w >= 0x8000 and tgt in starts:
                run.append(tgt)
            else:
                if len(run) >= a.run:
                    first = pos - 2 * len(run)
                    text, _ = t.decode(rom, run[0])
                    print('%06X\t%d\t%06X\t%06X\t%s' % (first, len(run), min(run), max(run), text[:40]))
                run = []
            pos += 2


if __name__ == '__main__':
    main()
