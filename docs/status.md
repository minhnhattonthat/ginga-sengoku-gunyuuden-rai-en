# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1 (research and recon) done. Next: phase 2 (debug tool).
- **Done (phase 1):** no earlier patch exists; encoding = 16-bit LE font-cell codes, 12x12 font at 0x0A8000
  (1,320 cells), full `tbl/jp.tbl`; plain + dialogue string formats (`$BA:92CD` renderer disassembled); 16-bit
  in-bank pointer tables (37) + 24-bit event-record pointers; text ranges mapped; LZ codec (`tools/lz.py`) and
  block list; word-RLE tilemap codec decoded (`tools/rle.py`, 50 source streams, text-shaped maps identified);
  graphics-text survey G1-G9 + RLE text maps; free space ~283 KB incl. 128 KB at 0x1E0000. Notes: `docs/re/text.md`,
  `docs/re/graphics.md`. Tests: `tests/test_recon.py`.
- **Graphics-text survey is complete for title → faction select → intro → strategy map.** Key late findings (this
  session): (1) no raw/uncompressed tile data — every VRAM DMA is sourced from the LZ output buffer in WRAM
  (`snes_dmalog.lua`); (2) `lz_blocks.py` misses blocks selected at runtime from WRAM (not `A2/A9` immediates):
  banks $98 (0x0C0000, 31 portrait/panel blocks), $A0 (0x100000 chain), $AC (0x160000) — enumerate with
  `tools/lua/lzlog.lua`; (3) the RLE tilemaps (bank $AD cluster + banks $9C/$9F/$A5/$A9/$B2/$BB) carry menu/battle
  labels as tilemaps, identifiable by increment-runs of ~30 consecutive glyph tiles.
- **Next (phase 2, debug tool):** the game is a real-time strategy map (faction select -> intro events -> map at
  ~frame 12000 of mash-A from boot; state `work/states/map_start_nankyourou.mss`, regenerate from `work/qa/play1`).
  Needs RAM for faction, turn/year, planets owned, event flags; scenes: each faction's intro, map menus, planet
  data, fleet build, battle, capture/recruit, game over, each faction ending, credits. While warping there, re-run
  `tools/lua/lzlog.lua` + `snes_dmalog.lua` to finish the block/raw-tile survey on the screens phase 1 could not
  reach.
- **Phase 4 needs** an event-script parser for bank `$8D` (and others) to list every dialogue block pointer; the
  blind 24-bit sweep (`tools/find_ptr24.py`) is noisy.
- **Open bugs:** none.
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not hand-tested (headless agent run);
  scripted input verified. Non-blocking: title logo has no known official English version, so per D5 it gets
  redrawn in English.
