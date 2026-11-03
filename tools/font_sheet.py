"""Render the game's 12x12 1bpp font (24 bytes per glyph, 2 bytes per row, MSB = left) as a labelled sheet.

    python -X utf8 tools/font_sheet.py ROM OUT.png [--base 0xA8000] [--first 0] [--count 256] [--cols 16] [--zoom 3]

Each cell shows the glyph with its hex code above it, so readers can build or check tbl/jp.tbl by eye.
"""
import argparse

from PIL import Image, ImageDraw

GLYPH = 24


def glyph(rom, base, code):
    g = rom[base + code * GLYPH: base + code * GLYPH + GLYPH]
    return [[(int.from_bytes(g[r * 2:r * 2 + 2], 'big') >> (15 - x)) & 1 for x in range(12)] for r in range(12)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom')
    ap.add_argument('out')
    ap.add_argument('--base', type=lambda s: int(s, 0), default=0xA8000)
    ap.add_argument('--first', type=lambda s: int(s, 0), default=0)
    ap.add_argument('--count', type=lambda s: int(s, 0), default=256)
    ap.add_argument('--cols', type=int, default=16)
    ap.add_argument('--zoom', type=int, default=3)
    a = ap.parse_args()
    rom = open(a.rom, 'rb').read()
    cw, chh = 20, 22  # cell: 12 px glyph + margin, label row of 8 px
    rows = (a.count + a.cols - 1) // a.cols
    im = Image.new('RGB', (a.cols * cw, rows * chh), 'white')
    dr = ImageDraw.Draw(im)
    for i in range(a.count):
        code = a.first + i
        x0, y0 = (i % a.cols) * cw, (i // a.cols) * chh
        dr.text((x0, y0 - 2), '%03X' % code, fill=(200, 0, 0))
        for y, row in enumerate(glyph(rom, a.base, code)):
            for x, p in enumerate(row):
                if p:
                    im.putpixel((x0 + 1 + x, y0 + 9 + y), (0, 0, 0))
    im = im.resize((im.width * a.zoom, im.height * a.zoom), Image.NEAREST)
    im.save(a.out)
    print(a.out)


if __name__ == '__main__':
    main()
