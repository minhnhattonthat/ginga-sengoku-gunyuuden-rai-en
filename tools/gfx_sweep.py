"""Static graphics sweep: decompress every LZ block in work/recon/lz_blocks.tsv and render it as 4bpp and 2bpp
tile sheets (greyscale), with an index of what went where. Blocks that fail are printed with the reason.

    python -X utf8 tools/gfx_sweep.py ROM BLOCKS.tsv OUTDIR [--fmt snes4 snes2]

Writes OUTDIR/<offset>_<fmt>.png (32 tiles wide, 2x) and OUTDIR/index.tsv.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from lz import decompress  # noqa: E402

BPP = {'snes2': 2, 'snes4': 4}


def tile(raw, i, bpp):
    t = raw[i * 8 * bpp: (i + 1) * 8 * bpp]
    px = [[0] * 8 for _ in range(8)]
    for y in range(8):
        for p in range(bpp):
            b = t[(p // 2) * 16 + y * 2 + (p & 1)] if (p // 2) * 16 + y * 2 + (p & 1) < len(t) else 0
            for x in range(8):
                if b & (0x80 >> x):
                    px[y][x] |= 1 << p
    return px


def render(raw, bpp, cols=32, zoom=2):
    n = len(raw) // (8 * bpp)
    rows = max(1, (n + cols - 1) // cols)
    im = Image.new('L', (cols * 8, rows * 8), 0)
    scale = 255 // ((1 << bpp) - 1)
    for i in range(n):
        px = tile(raw, i, bpp)
        x0, y0 = (i % cols) * 8, (i // cols) * 8
        for y in range(8):
            for x in range(8):
                im.putpixel((x0 + x, y0 + y), px[y][x] * scale)
    return im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom')
    ap.add_argument('blocks')
    ap.add_argument('out')
    ap.add_argument('--fmt', nargs='+', default=['snes4', 'snes2'])
    a = ap.parse_args()
    rom = open(a.rom, 'rb').read()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    index = []
    for line in open(a.blocks):
        off = int(line.split('\t')[0], 16)
        try:
            raw, _ = decompress(rom, off)
        except Exception as e:  # noqa: BLE001 - report every skipped block
            print('SKIP %06X %s' % (off, e))
            continue
        for fmt in a.fmt:
            name = '%06X_%s.png' % (off, fmt)
            render(raw, BPP[fmt]).save(out / name)
            index.append('%06X\t%s\t%X\t%s' % (off, fmt, len(raw), name))
    (out / 'index.tsv').write_text('\n'.join(index) + '\n')
    pages(out, [l.split('\t')[3] for l in index])
    print('%d sheets in %s' % (len(index), out))


def pages(out, names, height=1800):
    """Stack sheets vertically with a label bar each, into page_NN.png files of at most `height` px."""
    from PIL import ImageDraw
    page, items, h = 1, [], 0

    def flush():
        nonlocal page, items, h
        if not items:
            return
        im = Image.new('RGB', (512, h), (90, 0, 90))
        dr = ImageDraw.Draw(im)
        y = 0
        for name, s in items:
            dr.text((2, y + 1), name, fill=(255, 255, 0))
            im.paste(s.convert('RGB'), (0, y + 12))
            y += s.height + 14
        im.save(out / ('page_%02d.png' % page))
        page, items, h = page + 1, [], 0

    for name in names:
        s = Image.open(out / name)
        if s.height > height - 14:
            s = s.crop((0, 0, s.width, height - 14))
        if h + s.height + 14 > height:
            flush()
        items.append((name, s))
        h += s.height + 14
    flush()


if __name__ == '__main__':
    main()
