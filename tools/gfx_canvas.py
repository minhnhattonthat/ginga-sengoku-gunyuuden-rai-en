"""Tile canvas (data/gfx.tsv `tAA.BB/CC.DD`) of a screen rect: which tiles of one block draw it, in screen order.

    python -X utf8 tools/gfx_canvas.py work/gfx/jp/<scene> BLOCK X Y W H [--layer N]

BLOCK names a file in work/gfx/blocks (LZ: `0E48FE`; word-RLE stream decoded to `R168000.bin`: `R168000`). The
rect is snapped to the 8x8 grid. A cell whose tile is not in the block prints `--` (the canvas then needs
another row or block). Uses the PPU dump of tools/lua/finaldump.lua, like tools/gfx_locate.py.
"""
import argparse
import re
from pathlib import Path

import gfx_locate


def canvas(scene, block, rect, layer=None, blocks='work/gfx/blocks'):
    d = Path(scene)
    p = gfx_locate.ppu(d / 'final.ppu.txt')
    vram = (d / 'final.vram.bin').read_bytes()
    data = (Path(blocks) / f'{block}.bin').read_bytes()
    mode = int(p['ppu.bgMode'])
    x0, y0, w, h = rect
    best = None
    for L in ([layer] if layer is not None else range(4)):
        bpp = gfx_locate.BPP.get(mode, (0,) * 4)[L]
        if not bpp:
            continue
        g = lambda k: p[f'ppu.layers[{L}].{k}']  # noqa: E731
        chr_, tm = int(g('chrAddress')) * 2, int(g('tilemapAddress')) * 2
        hs, vs = int(g('hscroll')), int(g('vscroll'))
        size = 8 * bpp
        rows, hits = [], 0
        for sy in range(y0 // 8 * 8, y0 + h, 8):
            row = []
            for sx in range(x0 // 8 * 8, x0 + w, 8):
                tx, ty = (sx + hs) // 8 % 32, (sy + vs) // 8 % 32
                e = tm + (ty * 32 + tx) * 2
                tile = (vram[e] | vram[e + 1] << 8) & 0x3FF
                t = vram[chr_ + tile * size:chr_ + tile * size + size]
                m = [k.start() // size for k in re.finditer(re.escape(t), data) if k.start() % size == 0]
                # prefer the block tile whose index matches the VRAM tile's low bits (block loaded at a base)
                m.sort(key=lambda i: (i - tile) % 0x100 != 0)
                row.append(f'{m[0]:02X}' if m and any(t) else '--')
                hits += bool(m and any(t))
            rows.append(row)
        if best is None or hits > best[0]:
            best = (hits, L, rows)
    return best


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('scene')
    ap.add_argument('block')
    ap.add_argument('rect', nargs=4, type=int)
    ap.add_argument('--layer', type=int)
    a = ap.parse_args()
    hits, L, rows = canvas(a.scene, a.block, a.rect, a.layer)
    print(f'BG{L + 1} {hits} cells: t' + '/'.join('.'.join(r) for r in rows))


if __name__ == '__main__':
    main()
