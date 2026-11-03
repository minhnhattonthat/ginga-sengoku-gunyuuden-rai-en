# Graphics, compression, graphics-text survey

## LZ compression (verified: `tests/test_recon.py::test_lz_chain_title`, sizes match the logged DMAs)

Decoder `$00:8401` (source `$06D8-06DA`, dest `$06DB-06DD`). Block: u16 LE decompressed size, then groups of a flag
byte (MSB first) + 8 items: flag 0 = literal byte; flag 1 = `lo len`, copy `len` (0 = 256) bytes from
`dest - 0x100 + lo` (1..256 back). Stops when the output reaches the size. Codec: `tools/lz.py` (greedy
compressor; output differs from the original tool, so edited blocks need relocation or a size check).

Blocks are referenced by code immediates `A2 lo hi A9 bank` + `STX $06D8 / STA $06DA` (e.g. `$8A:9A0F`), and are
stored back to back. `tools/lz_blocks.py` finds 125 (63 referenced, the rest chained): banks 07-10, 13, 16
(`work/recon/lz_blocks.tsv`). Decompressed data goes to `$7E:8000` and is DMA'd by `$8A:9AC8`, `$8A:9B4C`, `$89:94FE`.

**Not all blocks are immediate-referenced.** Some are selected at runtime: the pointer and bank are read from a
WRAM table at `$7E:A6A3`/`$7E:A6A5` (`LDX $A6A3,y` / `LDA $A6A5,y` at `$81:00EA`, DB=$00, Y = scene id in `$08DD` × 3)
instead of an `A2/A9` immediate, so a static scan cannot enumerate them. `tools/lua/lzlog.lua` hooks the decoder
entry `$00:8401` and logs every block a run actually decompresses. A boot-to-map tour (title → faction select →
intro → map) found three extra chains the immediates miss (`work/qa/lztour/log.txt`), verified in
`tests/test_recon.py::test_lz_chains_missed_by_immediates`:

| Chain start | Bank | Blocks | Likely content |
|---|---|---|---|
| 0x0C0000 | $98 | 31 × 0x460 back to back | portrait / panel tiles |
| 0x100000 | $A0 | 0x3B20, 0x2600, then 0x800×3, 0x2C0 (joins the known 0x105339) | large art (diagonal strokes) |
| 0x160000 | $AC | 0x2000 (immediately before the known 0x1617F1) | logo art |

The full list needs a tour that reaches battle, planet data and menus (phase 2 debug tool), re-run with `lzlog.lua`.

## Word-RLE tilemap codec (verified: `tests/test_recon.py::test_rle_tilemap_streams_back_to_back`)

Decoder `$BA:82B2` (source 24-bit pointer at `$1B10/$1B12` via `LDA [$00],y`; dest WRAM `$7E:<offset>`). Command
byte `c` (0 = end): `n = c >> 2`, `mode = c & 3`:
- mode 0 (literal): copy `n` words from the stream;
- mode 1 (increment): write running+1 … running+n (consecutive tiles — the text signature);
- mode 2 (repeat): write the running word `n` times;
- mode 3 (decrement): write running-1 … running-n.

The running word carries across commands. Codec: `tools/rle.py`; source streams: `tools/rle_ptrs.py` (50 streams;
the big cluster is bank `$AD` 0x168000..0x16CC13, with scattered streams in banks $9C, $9F, $A5, $A9, $B2, $BB). `tools/rle_render.py` renders each stream's tile-number grid
(`work/recon/rle/*.png`) and profiles its runs; the increment-run count is the text signature. Text-shaped maps
(rows of ~30 consecutive glyph tiles) are: 0x0FBC32/0x0FBD5F/0x0FBF1C (bank $9F), 0x12E1EB ($A5), 0x149C44 ($A9),
0x16C04B–0x16CC13 ($AD), 0x197CF3/0x197E40 ($B2), 0x1DF423/0x1DF612 ($BB). Their glyphs are the 8×8 menu/battle
tiles in the LZ blocks, matched to text in phase 7.

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

**Raw (uncompressed) tiles: none.** `snes_dmalog.lua` over a boot-to-map tour (`work/qa/dmatest/log.txt`) shows
every VRAM DMA is sourced from WRAM `$7E:8000` (the LZ output buffer, via the NMI dispatcher `$8A:9AC8`/`$8A:9B4C`);
the only CPU-bus DMAs are OAM (`$7E:0290`, 0x220 B, `$2104`) and CGRAM (`$7E:0090`, 0x200 B, `$2122`). So all tile
graphics are LZ-compressed; there is no raw-tile region to sweep. (Confirm on battle/planet screens in phase 2.)

**Screens not toured** (need a phase-2 debug-tool warp): planet data, fleet/ship build, diplomacy, battle, game
over, each faction's ending, credits. Each of those may load more LZ blocks (log with `lzlog.lua`) and more RLE
maps; the survey above is complete only for title → faction select → intro → strategy map.

## Free space (candidates, **guess** until trap-tested)

FF runs >= 512 bytes (regex `(\xff{512,}|\x00{512,})` over the ROM; no 00 runs that long): 0x006812-0x007FB0 (6 KB, bank $80),
0x017170-0x018000, 0x01E562-0x020000, 0x0407FE-0x048000 (30 KB), 0x04ACCA-0x050000 (21 KB), 0x05322F-0x058000
(19 KB), 0x05DD10-0x060000, 0x0669CD-0x068000, 0x06ED2A-0x070000, 0x1A22F0-0x1A8000 (23 KB), 0x1D3071-0x1D8000
(20 KB), **0x1E0000-0x1FFFFF (128 KB, banks $BC-$BF, all FF)**. Total ~283 KB. Several text banks (10-19) end in
random-looking bytes after their last string (e.g. 0x12ED67-0x12FFFF): not counted as free. Expansion to 4 MB
is also open (header size byte `$7FD7`).
