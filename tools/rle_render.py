"""Decode every word-RLE tilemap stream (source pointers from tools/rle_ptrs.py) and render the tile-number
grids as PNGs, so text-shaped maps (rows of consecutive glyph tiles) can be spotted.

    python -X utf8 tools/rle_render.py ROM > work/recon/rle_streams.tsv
    -> work/recon/rle/<offset>_tiles.png   (tile index as a rainbow), <offset>_hi.png (high nibble of tile)

Also prints, per stream: word count, guessed width, and the command-mode profile (literal/inc/dec/repeat runs),
which is the text signature: text rows use many short increment/decrement runs of consecutive glyph tiles.
"""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from rle import decode  # noqa: E402
from rle_ptrs import find  # noqa: E402


def ptrs(rom):
    return sorted(find(rom))


def profile(words):
    """Command-mode run profile: count runs of consecutive tile numbers of length >= 2."""
    runs = []
    i = 0
    n = len(words)
    while i < n:
        j = i + 1
        while j < n and words[j] == words[i]:
            j += 1
        if j - i >= 2:
            runs.append(('rep', j - i))
            i = j
            continue
        j = i + 1
        while j < n and words[j] == (words[j - 1] + 1) & 0xFFFF:
            j += 1
        if j - i >= 3:
            runs.append(('inc', j - i))
            i = j
            continue
        j = i + 1
        while j < n and words[j] == (words[j - 1] - 1) & 0xFFFF:
            j += 1
        if j - i >= 3:
            runs.append(('dec', j - i))
            i = j
            continue
        i += 1
    return runs


def render(words, outdir, off, width):
    tiles = [w & 0x3FF for w in words]
    rows = (len(tiles) + width - 1) // width
    im = Image.new('RGB', (width, rows))
    hi = Image.new('L', (width, rows))
    for idx, t in enumerate(tiles):
        x, y = idx % width, idx // width
        # hue by tile index, fixed value/saturation: text rows = smooth hue gradients
        import colorsys
        h = (t / 1024.0) % 1.0
        r, g, b = colorsys.hsv_to_rgb(h, 0.85, 0.9)
        im.putpixel((x, y), (int(r * 255), int(g * 255), int(b * 255)))
        hi.putpixel((x, y), ((t >> 8) & 0xF) * 17)
    im = im.resize((width * 2, rows * 2), Image.NEAREST)
    im.save(outdir / ('%06X_tiles.png' % off))
    hi.save(outdir / ('%06X_hi.png' % off))


def main():
    rom = open(sys.argv[1], 'rb').read()
    outdir = Path('work/recon/rle')
    outdir.mkdir(parents=True, exist_ok=True)
    print('off\twords\twidth\tincruns\tdecruns\trepruns\tmaxrun')
    for off in ptrs(rom):
        words, used = decode(rom, off)
        if not words:
            print('%06X\t0\t-\t-\t-\t-\t-' % off)
            continue
        runs = profile(words)
        inc = sum(1 for k, l in runs if k == 'inc')
        dec = sum(1 for k, l in runs if k == 'dec')
        rep = sum(1 for k, l in runs if k == 'rep')
        mx = max((l for k, l in runs), default=0)
        width = 32 if len(words) <= 1024 else 64
        if len(words) == 1536:
            width = 32
        print('%06X\t%d\t%d\t%d\t%d\t%d\t%d' % (off, len(words), width, inc, dec, rep, mx))
        render(words, outdir, off, width)


if __name__ == '__main__':
    main()
