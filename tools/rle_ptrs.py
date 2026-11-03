"""List every word-RLE tilemap stream the code loads, by finding the `STX $1B10` / `STA $1B12` setup before each
`JSL $BA82B2` (the RLE decoder reads its 24-bit source from $1B10/$1B12 via `LDA [$00],y`).

    python -X utf8 tools/rle_ptrs.py ROM > work/recon/rle_ptrs.tsv

Columns: source file offset, ref count. The streams are back to back, so each one ends where the next begins.
"""
import sys


def lorom(bank, lo):
    return ((bank & 0x7F) << 15) | (lo & 0x7FFF)


def find(rom):
    """Return {source_file_offset: refcount} for every word-RLE stream the code loads."""
    stx = bytes([0x8E, 0x10, 0x1B])  # STX $1B10 (source pointer lo:hi)
    sites = []
    i = 0
    while True:
        j = rom.find(stx, i)
        if j < 0:
            break
        sites.append(j)
        i = j + 1
    counts = {}
    for s in sites:
        ctx = rom[max(0, s - 24):s]
        ptr = bank = None
        p = 0
        while p < len(ctx):
            b = ctx[p]
            if b == 0xA2 and p + 2 < len(ctx):
                ptr = ctx[p + 1] | ctx[p + 2] << 8
                p += 3
            elif b == 0xA9 and p + 1 < len(ctx):
                bank = ctx[p + 1]
                p += 2
            else:
                p += 1
        if ptr is not None and bank is not None and bank >= 0x80:
            counts[lorom(bank, ptr)] = counts.get(lorom(bank, ptr), 0) + 1
    return counts


def main():
    rom = open(sys.argv[1], 'rb').read()
    counts = find(rom)
    for f in sorted(counts):
        print('%06X\t%d' % (f, counts[f]))


if __name__ == '__main__':
    main()
