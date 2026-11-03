"""Zoomed sheet of chosen font codes, one cell each with its label, for checking look-alike glyphs.

    python -X utf8 tools/font_cells.py ROM OUT.png 139 4A8 14A 4EC ... [--zoom 8] [--cols 8]
"""
import argparse

from PIL import Image, ImageDraw

from font_sheet import glyph


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom')
    ap.add_argument('out')
    ap.add_argument('codes', nargs='+')
    ap.add_argument('--base', type=lambda s: int(s, 0), default=0xA8000)
    ap.add_argument('--zoom', type=int, default=8)
    ap.add_argument('--cols', type=int, default=8)
    a = ap.parse_args()
    rom = open(a.rom, 'rb').read()
    z = a.zoom
    cw, ch = 14 * z, 14 * z + 12
    codes = [int(c, 16) for c in a.codes]
    rows = (len(codes) + a.cols - 1) // a.cols
    im = Image.new('RGB', (a.cols * cw, rows * ch), 'white')
    dr = ImageDraw.Draw(im)
    for i, code in enumerate(codes):
        x0, y0 = (i % a.cols) * cw, (i // a.cols) * ch
        dr.text((x0 + 2, y0), '%03X' % code, fill=(200, 0, 0))
        for y, row in enumerate(glyph(rom, a.base, code)):
            for x, p in enumerate(row):
                if p:
                    dr.rectangle([x0 + z + x * z, y0 + 12 + y * z, x0 + z + x * z + z - 2, y0 + 12 + y * z + z - 2],
                                 fill=(0, 0, 0))
    im.save(a.out)
    print(a.out)


if __name__ == '__main__':
    main()
