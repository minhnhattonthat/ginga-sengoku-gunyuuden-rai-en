"""Sweep code banks for 16-bit immediates (LDX/LDY/LDA #$hhll) that point at text, the form the map notices,
option labels and many short system strings use (`LDX #$E41F` with DB = $80).

    python -X utf8 tools/find_imm16.py ROM [--new] > work/recon/imm16.tsv

A hit counts when $hhll, read in bank $80, $82 or the code's own bank, starts a string that decodes cleanly (no
unknown code) to an end code and holds kana or kanji. Prints operand offset, code address, target offset,
whether the target is already an extracted entry start ('entry'), inside one ('inside') or new ('new').
--new prints only new targets. Bytes of extracted text, pointer tables and not-text ranges are skipped.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import gaps  # noqa: E402
import extract  # noqa: E402
import text  # noqa: E402

CODE = [(0x000000, 0x080000), (0x1D0000, 0x1D8000)]  # banks $80-$8F and $BA
IMM = re.compile(rb'(?=[\xa0\xa2\xa9](..))', re.S)  # lookahead: overlapping matches


def is_text(s):
    return '[' not in s and s.endswith('{end}') and any('ぁ' <= c <= 'ヿ' or c >= '一' for c in s)


def hits(rom, cov):
    tabs = [text.plain_table(), text.msg_table()]
    for lo, hi in CODE:
        for m in IMM.finditer(rom, lo, hi):
            op = m.start() + 1
            if cov[op - 1] or cov[op]:
                continue
            a = m[1][0] | m[1][1] << 8
            if a < 0x8000:
                continue
            for bank in dict.fromkeys((op & ~0x7FFF, 0, 0x10000)):  # own bank first
                t = bank | (a & 0x7FFF)
                for tab in tabs:
                    try:
                        s, n = tab.decode(rom, t, maxlen=600)
                    except ValueError:
                        continue
                    if is_text(s):
                        yield op, t, s
                        break
                else:
                    continue
                break


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom')
    ap.add_argument('--new', action='store_true')
    a = ap.parse_args()
    rom = open(a.rom, 'rb').read()
    cov = gaps.covered(rom)
    starts = {e['off'] for b in extract.blocks(rom) for e in b['entries']}
    for op, t, s in hits(rom, cov):
        state = 'entry' if t in starts else 'inside' if cov[t] == 1 else 'new'
        if a.new and state != 'new':
            continue
        print(f'{op:06X}\t${0x80 | op >> 15:02X}:{0x8000 | op & 0x7FFF:04X}\t{t:06X}\t{state}\t{s[:40]}')


if __name__ == '__main__':
    main()
