"""Find 24-bit text addresses built from code immediates: a 16-bit load (LDX/LDY/LDA #$hhll) and an 8-bit
bank load (LDA #$bb) within a few bytes of each other, the form `LDX #$8050 / LDA #$A9 / STX $1CA1 / STA $1CA3`.

    python -X utf8 tools/find_imm24.py ROM [--all] > work/recon/imm24.tsv

Prints the offset of the 16-bit operand, the target file offset, the format it decodes as (msg/plain) and the
text start. Only targets that decode cleanly to an end code and hold kana are kept unless --all.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import text  # noqa: E402

PAIR = re.compile(rb'[\xa0\xa2\xa9](..)(?:.{0,6}?)\xa9([\x80-\xbf])|\xa9([\x80-\xbf])(?:.{0,6}?)[\xa0\xa2](..)', re.S)


def candidates(rom):
    for m in PAIR.finditer(rom):
        if m[1] is not None:
            lo, bank, op = m[1], m[2][0], m.start() + 1
        else:
            lo, bank, op = m[4], m[3][0], m.start(4)
        a = lo[0] | lo[1] << 8
        if a >= 0x8000:
            yield op, ((bank & 0x7F) << 15) | (a & 0x7FFF)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom')
    ap.add_argument('--all', action='store_true')
    a = ap.parse_args()
    rom = open(a.rom, 'rb').read()
    tabs = {'msg': text.msg_table(), 'plain': text.plain_table()}
    for op, t in candidates(rom):
        for fmt, tab in tabs.items():
            try:
                s, n = tab.decode(rom, t, maxlen=3000)
            except ValueError:
                continue
            if a.all or ('[' not in s and any('ぁ' <= c <= 'ヿ' or c >= '一' for c in s)):
                print(f'{op:06X}\t{t:06X}\t{fmt}\t{n}\t{s[:40]}')
                break


if __name__ == '__main__':
    main()
