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


def tiles_to_px(raw, cols=16, bpp=4):
    """Planar SNES tiles (2 or 4 bpp) -> rows of colour indices (list of bytearrays), `cols` tiles per row."""
    size = 8 * bpp
    n = len(raw) // size
    h = (n + cols - 1) // cols * 8
    img = [bytearray(cols * 8) for _ in range(h)]
    for t in range(n):
        tx, ty = t % cols * 8, t // cols * 8
        b = raw[t * size:t * size + size]
        for y in range(8):
            planes = [b[16 * (k // 2) + 2 * y + k % 2] for k in range(bpp)]
            for x in range(8):
                img[ty + y][tx + x] = sum((p >> (7 - x) & 1) << k for k, p in enumerate(planes))
    return img


def px_to_tiles(img, n, cols=16, bpp=4):
    """Inverse of tiles_to_px for the first n tiles."""
    size = 8 * bpp
    out = bytearray(size * n)
    for t in range(n):
        tx, ty = t % cols * 8, t // cols * 8
        for y in range(8):
            for k in range(bpp):
                out[t * size + 16 * (k // 2) + 2 * y + k % 2] = sum(
                    (img[ty + y][tx + x] >> k & 1) << (7 - x) for x in range(8))
    return bytes(out)


def rows_of(path=ROOT / 'data' / 'gfx.tsv'):
    """data/gfx.tsv: block, x, y, w, h, style, colours (fg,bg[,outline,shadow]), text."""
    out = []
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        if line.strip() and not line.startswith('#'):
            f = line.split('\t')
            blk, _, bpp = f[0].partition('/')  # OFFSET or OFFSET/2 for a 2bpp block
            grid = None
            if f[1].startswith('t'):  # tile canvas "tAA.BB.CC/DD.EE.FF" (rows of block tiles); rect inside it
                grid = [[int(t, 16) for t in row.split('.')] for row in f[1][1:].split('/')]
                f[1] = '0'
            out.append({'block': int(blk, 16), 'bpp': int(bpp or 4), 'grid': grid,
                        'rect': tuple(int(v) for v in f[1:5]),
                        'style': f[5],
                        'colours': [int(v, 16) for v in f[6].split(',')], 'text': f[7]})
    return out


def glyph_cols(text, condensed=False):
    """Column bitmaps (bit y = row y, rows 0-8) of text in the 5-px font, 1 px between letters."""
    import font_en
    if condensed:
        return font_en.strip(text)
    out = []
    for i, ch in enumerate(text):
        if i:
            out.append(0)
        rs = font_en.rows(ch)
        out += [sum(((r >> (font_en.WIDTH - 1 - x)) & 1) << y for y, r in enumerate(rs))
                for x in range(font_en.WIDTH)] if ch != ' ' else [0, 0, 0]
    return out


def draw(img, rect, style, colours, text):
    """Clear rect to the bg colour and draw text centred in it. plain: fg on bg. outline: fill fg, 1-px outline,
    shadow under the outline (colours fg, bg, outline, shadow). shadow: fg with a shadow 1 px down-right (fg, bg,
    shadow)."""
    x0, y0, w, h = rect
    fg, bg = colours[0], colours[1]
    pad = {'outline': 2, 'shadow': 1}.get(style, 0)
    cols = glyph_cols(text)
    if len(cols) > w - pad:
        cols = glyph_cols(text, condensed=True)
    if len(cols) + pad > w:
        raise ValueError(f'gfx: {text!r} is {len(cols)} px, rect is {w}')
    rows_used = [y for y in range(9) if any(c >> y & 1 for c in cols)]
    top = 0 if not rows_used else min(rows_used)
    gh = 7 - top if max(rows_used, default=0) <= 6 else max(rows_used) + 1 - top  # descenders count only if used
    ox, oy = x0 + (w - len(cols)) // 2, y0 + (h - gh) // 2 - top
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            img[y][x] = bg
    ink = {(ox + x, oy + y) for x, c in enumerate(cols) for y in range(9) if c >> y & 1}
    if style == 'outline':
        line, shadow = colours[2], colours[3]
        ring = {(x + dx, y + dy) for x, y in ink for dx in (-1, 0, 1) for dy in (-1, 0, 1)} - ink
        for x, y in ring:
            if x0 <= x < x0 + w and y0 <= y < y0 + h:
                img[y][x] = line
        for x, y in ring:
            if (x, y + 1) not in ink and (x, y + 1) not in ring and x0 <= x < x0 + w and y0 <= y + 1 < y0 + h:
                img[y + 1][x] = shadow
    if style == 'shadow':
        ox -= pad // 2  # keep the shadow inside the rect
        ink = {(x - pad // 2, y) for x, y in ink}
        for x, y in ink:
            if x + 1 < x0 + w and y + 1 < y0 + h:
                img[y + 1][x + 1] = colours[2]
    for x, y in ink:
        img[y][x] = fg


def edits(rom_orig, lz):
    """{block offset: new raw bytes} for every block named in data/gfx.tsv. lz: tools/lz.py module."""
    out, bpp = {}, {}
    for r in rows_of():
        b = r['block']
        bpp[b] = r['bpp']
        if b not in out:
            out[b] = (bytearray(lz.decompress(rom_orig, b)[0]), None)
        raw, img = out[b]
        img = img or tiles_to_px(raw, bpp=bpp[b])
        if r['grid']:
            cells = [(gx, gy, t) for gy, row in enumerate(r['grid']) for gx, t in enumerate(row)]
            canvas = [bytearray(8 * len(r['grid'][0])) for _ in range(8 * len(r['grid']))]
            for gx, gy, t in cells:
                for y in range(8):
                    canvas[gy * 8 + y][gx * 8:gx * 8 + 8] = img[t // 16 * 8 + y][t % 16 * 8:t % 16 * 8 + 8]
            draw(canvas, r['rect'], r['style'], r['colours'], r['text'])
            for gx, gy, t in cells:
                for y in range(8):
                    img[t // 16 * 8 + y][t % 16 * 8:t % 16 * 8 + 8] = canvas[gy * 8 + y][gx * 8:gx * 8 + 8]
        else:
            draw(img, r['rect'], r['style'], r['colours'], r['text'])
        out[b] = (raw, img)
    res = {}
    for b, (raw, img) in out.items():
        size = 8 * bpp[b]
        res[b] = px_to_tiles(img, len(raw) // size, bpp=bpp[b]) + bytes(raw[len(raw) // size * size:])
    return res


def preview(rom_orig, lz, out_dir, zoom=4):
    """work/gfx/preview/<block>.png of every edited block (before | after)."""
    from PIL import Image
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    for b, new in edits(rom_orig, lz).items():
        old = lz.decompress(rom_orig, b)[0]
        a, n = tiles_to_px(old), tiles_to_px(new)
        w, h = 128, len(a)
        im = Image.new('L', (2 * w + 4, h), 80)
        for k, img in enumerate((a, n)):
            im.paste(Image.frombytes('L', (w, h), bytes(v * 17 for row in img for v in row)), (k * (w + 4), 0))
        im.resize((im.width * zoom, h * zoom), Image.NEAREST).save(Path(out_dir) / f'{b:06X}.png')


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
