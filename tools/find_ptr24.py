"""Find 24-bit LoROM pointers (lo hi bank) to dialogue strings, the form event scripts use (docs/re/text.md).

    python -X utf8 tools/find_ptr24.py ROM > work/recon/ptr24.tsv

A target counts when it decodes cleanly (no unknown code) to {end}, is >= 8 bytes and holds kana. Prints pointer offset, target offset, the 3 bytes
before the pointer and the first decoded text.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tbl import Table  # noqa: E402


def msg_table():
    lines = [l for l in (Path(__file__).parent.parent / 'tbl/jp.tbl').read_text(encoding='utf-8').splitlines()
             if not l.startswith('FFFF=')]
    lines += ['FFFF0000={end}', 'FFFF0100={br}', 'FFFF0200={skip:2}', 'FFFF0300={spd:4}', 'FFFF0500={c5}',
              'FFFF0600={c6}', 'FFFF0700={c7}', 'FFFF0800={c8}']
    return Table(lines)


def lorom(lo, hi, bank):
    if hi < 0x80 or (bank & 0x7F) >= 0x7E:
        return None
    return ((bank & 0x7F) << 15) | (hi & 0x7F) << 8 | lo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom')
    a = ap.parse_args()
    rom = open(a.rom, 'rb').read()
    t = msg_table()
    for p in range(len(rom) - 2):
        off = lorom(rom[p], rom[p + 1], rom[p + 2])
        if off is None or off + 4 > len(rom) or rom[p + 2] < 0x80:
            continue
        try:
            text, n = t.decode(rom, off, maxlen=600)
        except ValueError:
            continue
        if '[' in text or not text.endswith('{end}') or n < 8:
            continue
        if not any('ぁ' <= c <= 'ヿ' for c in text):
            continue
        print('%06X\t%06X\t%s\t%s' % (p, off, rom[p - 3:p].hex(), text[:50]))


if __name__ == '__main__':
    main()
