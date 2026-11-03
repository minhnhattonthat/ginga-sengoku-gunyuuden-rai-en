"""List the game's LZ blocks: code immediates `A2 lo hi A9 bank` (LDX #ptr / LDA #bank) that start a valid
block, plus blocks chained after them (each block's end = the next one's start).

    python -X utf8 tools/lz_blocks.py ROM > work/recon/lz_blocks.tsv

Prints offset, compressed size, decompressed size, source ("ref" = referenced by code at that offset, "chain").
A block counts when it decodes without a copy before its start, its size is 0x20..0x10000 and it does not run
past its bank.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lz import decompress  # noqa: E402


def valid(rom, off):
    if off + 3 > len(rom):
        return None
    size = rom[off] | rom[off + 1] << 8
    if not 0x20 <= size <= 0x8000:
        return None
    try:
        raw, used = decompress(rom, off)
    except (ValueError, IndexError):
        return None
    if (off & 0x7FFF) + used > 0x8000 + 0x8000:  # blocks may cross into the next bank? keep generous
        return None
    if used >= size + size // 8 + 4:  # worse than all-literal: not LZ
        return None
    return raw, used


def main():
    rom = open(sys.argv[1], 'rb').read()
    blocks = {}
    for m in re.finditer(rb'\xa2(..)\xa9(.)', rom, re.S):
        lo = m[1][0] | m[1][1] << 8
        bank = m[2][0]
        if lo < 0x8000 or bank < 0x80 or bank >= 0xFE:
            continue
        off = ((bank & 0x7F) << 15) | (lo & 0x7FFF)
        if off in blocks:
            continue
        v = valid(rom, off)
        if v:
            blocks[off] = (v[1], len(v[0]), 'ref@%06X' % m.start())
    for off in sorted(blocks):
        o = off
        while True:
            o += blocks[o][0]
            if o in blocks:
                break
            v = valid(rom, o)
            if not v:
                break
            blocks[o] = (v[1], len(v[0]), 'chain')
    for off in sorted(blocks):
        print('%06X\t%X\t%X\t%s' % (off, *blocks[off]))


if __name__ == '__main__':
    main()
