# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1 (research and recon), mostly done. Remaining before its done-when: finish the graphics-text survey (see "Next").
- **Done (phase 1):** no earlier patch exists; encoding = 16-bit LE font-cell codes, 12x12 font at 0x0A8000 (1,320 cells), full `tbl/jp.tbl` (kanji read by eye, 5 fixed from context); plain format (FFFF end) + dialogue format (`FFFF <cmd>` codes, renderer `$BA:92CD` disassembled); 16-bit in-bank pointer tables (37 found) and 24-bit event-record pointers (`$8D:8652`); text ranges mapped; LZ codec (`tools/lz.py`, tested) and 125 blocks listed; static sweep + tour list 9 graphics-text items; free space ~283 KB incl. 128 KB at 0x1E0000. Notes: `docs/re/text.md`, `docs/re/graphics.md`. Tests: `tests/test_recon.py`.
- **Next:**
  1. Finish phase 1 survey: `snes_dmalog.lua` over a wide tour (ROM-source DMAs = raw tiles), catch LZ blocks not referenced by `A2/A9` immediates, decode the word-RLE tilemaps (`$BA:82C8`) enough to find text-shaped maps. Add rows to `docs/re/graphics.md`.
  2. Phase 2 debug tool: the game is a real-time strategy map (faction select -> intro events -> map at ~frame 12000 of mash-A from boot; state `work/states/map_start_nankyourou.mss`, regenerate from `work/qa/play1` route). Needs RAM for faction, turn/year, planets owned, event flags; scenes: each faction's intro, map menus, planet data, fleet build, battle, capture/recruit, game over, each faction ending, credits.
  3. Phase 4 needs an event-script parser for bank `$8D` (and others) to list every dialogue block pointer; the blind 24-bit sweep (`tools/find_ptr24.py`) is noisy.
- **Open bugs:** none.
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not hand-tested (headless agent run); scripted input verified. Non-blocking: title logo has no known official English version, so per D5 it gets redrawn in English.
