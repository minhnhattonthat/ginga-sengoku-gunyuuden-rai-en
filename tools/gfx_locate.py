"""Which LZ block tiles draw a screen rect: BG tilemaps of a PPU dump (tools/lua/finaldump.lua) -> block, tile.

    python -X utf8 tools/gfx_locate.py work/gfx/jp/<scene> X Y W H [--blocks work/gfx/blocks]

Per enabled BG layer (mode 1: BG1/BG2 4bpp, BG3 2bpp) prints, for each non-blank 8x8 cell in the rect, the
tilemap entry (tile, palette, flips) and every block offset whose bytes match the tile (as tile index in that
block at the layer's bpp; '?' = not found: built at run time or sprite). Sprites are not covered.
"""
import argparse
import re
from pathlib import Path

BPP = {0: (2, 2, 2, 2), 1: (4, 4, 2, 0), 2: (4, 4, 0, 0), 3: (8, 4, 0, 0), 4: (8, 2, 0, 0), 5: (4, 2, 0, 0)}


def ppu(path):
    out = {}
    for line in Path(path).read_text().splitlines():
        k, _, v = line.partition('=')
        out[k] = v
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('scene')
    ap.add_argument('rect', nargs=4, type=int)
    ap.add_argument('--blocks', default='work/gfx/blocks')
    a = ap.parse_args()
    d = Path(a.scene)
    p = ppu(d / 'final.ppu.txt')
    vram = (d / 'final.vram.bin').read_bytes()
    blocks = {f.stem: f.read_bytes() for f in Path(a.blocks).glob('*.bin')}
    mode, main_layers = int(p['ppu.bgMode']), int(p['ppu.mainScreenLayers'])
    x0, y0, w, h = a.rect
    for L in range(4):
        bpp = BPP.get(mode, (0,) * 4)[L]
        if not bpp or not main_layers >> L & 1:
            continue
        g = lambda k: p[f'ppu.layers[{L}].{k}']  # noqa: E731
        chr_, tm = int(g('chrAddress')) * 2, int(g('tilemapAddress')) * 2
        hs, vs = int(g('hscroll')), int(g('vscroll'))
        dw, dh = g('doubleWidth') == 'true', g('doubleHeight') == 'true'
        size = 8 * bpp
        found = {}
        for sy in range(y0 // 8 * 8, y0 + h, 8):
            for sx in range(x0 // 8 * 8, x0 + w, 8):
                tx, ty = (sx + hs) // 8 % (64 if dw else 32), (sy + vs) // 8 % (64 if dh else 32)
                scr = (tx >= 32) + (ty >= 32) * (2 if dw else 1)
                e = tm + scr * 0x800 + ((ty % 32) * 32 + tx % 32) * 2
                ent = vram[e] | vram[e + 1] << 8
                tile = ent & 0x3FF
                data = vram[chr_ + tile * size:chr_ + tile * size + size]
                if not any(data) or tile in found:
                    continue
                hits = [f'{n}:{m.start() // size:X}' for n, b in blocks.items()
                        for m in re.finditer(re.escape(data), b) if m.start() % size == 0]
                found[tile] = hits
                print(f'BG{L + 1} {bpp}bpp ({sx},{sy}) tile {tile:03X} pal {ent >> 10 & 7} '
                      f'{"h" if ent & 0x4000 else ""}{"v" if ent & 0x8000 else ""}  {" ".join(hits[:4]) or "?"}')


if __name__ == '__main__':
    main()
