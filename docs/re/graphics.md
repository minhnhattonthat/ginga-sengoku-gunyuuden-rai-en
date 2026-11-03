# Graphics, compression, graphics-text survey

## LZ compression (verified: `tests/test_recon.py::test_lz_chain_title`, sizes match the logged DMAs)

Decoder `$00:8401` (source `$06D8-06DA`, dest `$06DB-06DD`). Block: u16 LE decompressed size, then groups of a flag
byte (MSB first) + 8 items: flag 0 = literal byte; flag 1 = `lo len`, copy `len` (0 = 256) bytes from
`dest - 0x100 + lo` (1..256 back). Stops when the output reaches the size. Codec: `tools/lz.py` (greedy
compressor; output differs from the original tool, so edited blocks need relocation or a size check).

Blocks are referenced by code immediates `A2 lo hi A9 bank` + `STX $06D8 / STA $06DA` (e.g. `$8A:9A0F`), and are
stored back to back. `tools/lz_blocks.py` finds 125 (63 referenced, the rest chained): banks 07-10, 13, 16
(`work/recon/lz_blocks.tsv`). Decompressed data goes to `$7E:8000` and is DMA'd by `$8A:9AC8`, `$8A:9B4C`, `$89:94FE`.

A second codec, a word RLE at `$BA:82C8` (tilemaps; command byte: bit0 = copy n words, bit1 = repeat a word, 0 =
end), reads 0x06ECDD..0x12E120. Not decoded into tools yet.

## Text drawn as graphics: survey (phase 1, partial)

Static sweep: `python -X utf8 tools/gfx_sweep.py ROM work/recon/lz_blocks.tsv work/recon/sweep` (4bpp, pages
`page_NN.png`). Tour: title, faction select, intro scenes, strategy map, its A/B/X/Y/L/R/Start/Select menus.

| # | Screen | Element | Layer / source | State |
|---|---|---|---|---|
| G1 | Title | logo 銀河戦国群雄伝 ライ, subtitle | LZ 0x0F36E2 (BG) | to translate; no official English logo known (D5: keep logo only if no official English version, so redraw) |
| G2 | Title | copyright line (© ... 1996, katakana) | LZ 0x0F36E2 | translate |
| G3 | Faction select | map labels 南京楼 / 練 / 大五丈 / 南天連合 | BG1, LZ 0x0FC121 (bottom rows hold 南京楼軍 / 練軍 / 南天連合軍 / 大五丈軍 / 本陣 cells) | translate |
| G4 | Strategy map | side-panel labels 惑星 / 艦隊, faction banner frame | BG, block not yet pinned (likely 0x0F4B3D or 0x1617F1) | translate |
| G5 | Battle / fleet UI | stat labels (攻 防 射 速 ...), 新造戦艦, 旗艦 | LZ 0x08D6D3 | translate |
| G6 | Battle | big kanji labels (部隊, 戦 ...) | LZ 0x0E48FE (bottom rows) | translate |
| G7 | Event banner | レベルアップ!! | LZ 0x105339 | translate |
| G8 | Menu | 艦隊選択-like buttons | LZ 0x166080 | translate |
| G9 | Battle | TURN, EXP, digits, PAUSE, YES/NO | LZ 0x0E470C, 0x0E4814, 0x165E09, 0x07DAD4 | English already |

Font-drawn (not graphics, handled by the text pipeline): faction-select description box, map help line
(惑星データの表示), side-panel faction and general names (南京楼軍, 竜我雷), dialogue windows.

**Not yet swept** (finish before phase 1 is closed): uncompressed tile data, if any (run `snes_dmalog.lua` on a
wide tour: any VRAM DMA with a ROM source is raw tiles); the RLE tilemaps; LZ blocks referenced by other code forms
(pointer tables, `JSR $9B11` helpers) that `lz_blocks.py` misses; screens not toured (planet data, fleet/ship
build, diplomacy, battle, game over, endings, credits). Each needs a debug-tool warp (phase 2).

## Free space (candidates, **guess** until trap-tested)

FF runs >= 512 bytes (regex `(\xff{512,}|\x00{512,})` over the ROM; no 00 runs that long): 0x006812-0x007FB0 (6 KB, bank $80),
0x017170-0x018000, 0x01E562-0x020000, 0x0407FE-0x048000 (30 KB), 0x04ACCA-0x050000 (21 KB), 0x05322F-0x058000
(19 KB), 0x05DD10-0x060000, 0x0669CD-0x068000, 0x06ED2A-0x070000, 0x1A22F0-0x1A8000 (23 KB), 0x1D3071-0x1D8000
(20 KB), **0x1E0000-0x1FFFFF (128 KB, banks $BC-$BF, all FF)**. Total ~283 KB. Several text banks (10-19) end in
random-looking bytes after their last string (e.g. 0x12ED67-0x12FFFF): not counted as free. Expansion to 4 MB
is also open (header size byte `$7FD7`).
