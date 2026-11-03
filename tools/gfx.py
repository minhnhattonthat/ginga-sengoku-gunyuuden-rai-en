"""Graphics text: LZ-block tile sheets as pixel images, English labels drawn into them (docs/re/graphics.md).

    python -X utf8 tools/gfx.py sheet BLOCK OUT.png [--pal X.pal.bin --pal-index N] [--zoom 4] [--cols 16]
    python -X utf8 tools/gfx.py --selftest

A block is seen as an image `cols` tiles wide (16, like the game's 16x16-character layouts); rects in
data/gfx.tsv are pixel rects in that image. sheet draws a tile grid and hex tile numbers for finding them.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def tiles_to_px(raw, cols=16):
    """4bpp planar SNES tiles -> rows of colour indices (list of bytearrays), `cols` tiles per row."""
    n = len(raw) // 32
    h = (n + cols - 1) // cols * 8
    img = [bytearray(cols * 8) for _ in range(h)]
    for t in range(n):
        tx, ty = t % cols * 8, t // cols * 8
        b = raw[t * 32:t * 32 + 32]
        for y in range(8):
            p0, p1, p2, p3 = b[2 * y], b[2 * y + 1], b[16 + 2 * y], b[17 + 2 * y]
            for x in range(8):
                s = 7 - x
                img[ty + y][tx + x] = (p0 >> s & 1) | (p1 >> s & 1) << 1 | (p2 >> s & 1) << 2 | (p3 >> s & 1) << 3
    return img


def px_to_tiles(img, n, cols=16):
    """Inverse of tiles_to_px for the first n tiles."""
    out = bytearray(32 * n)
    for t in range(n):
        tx, ty = t % cols * 8, t // cols * 8
        for y in range(8):
            p = [0, 0, 0, 0]
            for x in range(8):
                v = img[ty + y][tx + x]
                for k in range(4):
                    p[k] |= (v >> k & 1) << (7 - x)
            out[t * 32 + 2 * y], out[t * 32 + 2 * y + 1] = p[0], p[1]
            out[t * 32 + 16 + 2 * y], out[t * 32 + 17 + 2 * y] = p[2], p[3]
    return bytes(out)


def palette(path, index):
    raw = Path(path).read_bytes()[index * 32:index * 32 + 32]
    out = []
    for i in range(16):
        c = raw[2 * i] | raw[2 * i + 1] << 8
        out.append(((c & 31) << 3, (c >> 5 & 31) << 3, (c >> 10 & 31) << 3))
    return out


def sheet(block, out, pal=None, zoom=4, cols=16):
    from PIL import Image, ImageDraw
    img = tiles_to_px(Path(block).read_bytes(), cols)
    colours = pal or [(v * 17, v * 17, v * 17) for v in range(16)]
    w, h = cols * 8, len(img)
    im = Image.new('RGB', (w, h))
    im.putdata([colours[v] for row in img for v in row])
    im = im.resize((w * zoom, h * zoom), Image.NEAREST)
    d = ImageDraw.Draw(im)
    for x in range(0, w * zoom, 8 * zoom):
        d.line([(x, 0), (x, h * zoom)], fill=(255, 0, 255))
    for y in range(0, h * zoom, 8 * zoom):
        d.line([(0, y), (w * zoom, y)], fill=(255, 0, 255))
        d.text((1, y + 1), f'{y // (8 * zoom) * cols:X}', fill=(0, 255, 0))
    im.save(out)


def selftest():
    raw = bytes(range(256)) * 2
    assert px_to_tiles(tiles_to_px(raw), 16) == raw
    print('gfx selftest ok')


def main():
    if '--selftest' in sys.argv:
        return selftest()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('sheet')
    s.add_argument('block')
    s.add_argument('out')
    s.add_argument('--pal')
    s.add_argument('--pal-index', type=int, default=0)
    s.add_argument('--zoom', type=int, default=4)
    s.add_argument('--cols', type=int, default=16)
    a = ap.parse_args()
    sheet(a.block, a.out, palette(a.pal, a.pal_index) if a.pal else None, a.zoom, a.cols)


if __name__ == '__main__':
    main()
