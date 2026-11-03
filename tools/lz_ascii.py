"""Render tiles from LZ blocks as ASCII art so text-bearing blocks can be spotted without image viewing.
For each tile, non-zero 4bpp pixels print as '#'. Prints the first N non-empty tiles per block.

    python -X utf8 tools/lz_ascii.py ROM OFFSET [N [FMT]]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lz import decompress  # noqa: E402


def tiles(raw, bpp=4):
    out = []
    for i in range(len(raw) // (8 * bpp)):
        t = raw[i * 8 * bpp:(i + 1) * 8 * bpp]
        px = [[0] * 8 for _ in range(8)]
        for y in range(8):
            for p in range(bpp):
                b = t[(p // 2) * 16 + y * 2 + (p & 1)] if (p // 2) * 16 + y * 2 + (p & 1) < len(t) else 0
                for x in range(8):
                    if b & (0x80 >> x):
                        px[y][x] |= 1 << p
        out.append(px)
    return out


def art(px):
    return '\n'.join(''.join('#' if px[y][x] else '.' for x in range(8)) for y in range(8))


def main():
    rom = open(sys.argv[1], 'rb').read()
    off = int(sys.argv[2], 16)
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    raw, _ = decompress(rom, off)
    ts = tiles(raw)
    print('block %06X  %d tiles' % (off, len(ts)))
    shown = 0
    for idx, px in enumerate(ts):
        if all(px[y][x] == 0 for y in range(8) for x in range(8)):
            continue
        print('--- tile %d ---' % idx)
        print(art(px))
        shown += 1
        if shown >= n:
            break


if __name__ == '__main__':
    main()
