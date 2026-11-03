# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 3 (identity build) done. Next: phase 4 (extract to `script/`, roundtrip test, full text-range coverage).
- **Phase 3 result:** `python -X utf8 tools/build.py --repack-all` unpacks and repacks every known container and
  gives the original ROM byte for byte (`tests/test_identity.py`, in `check.py`): 162 LZ blocks
  (`data/lz_blocks.tsv`), 50 word-RLE tilemaps (`data/rle_streams.tsv`), 37 16-bit pointer tables = 37 pools,
  400 strings, 628 pointers (`data/ptr_tables.tsv`; pools = runs of back-to-back strings, `build.text_pools`).
  Both compressors now match the original tools exactly (rules in `docs/re/graphics.md`), so an edited block that
  still fits is recompressed in place; a grown one raises (relocation = phase 5/7 work). The plain build repacks
  only edited containers (`build(edits={'lz'|'rle'|'text': ...})`); every changed byte goes through `Rom.write`
  → `build/writes.log` → romdiff (fails on any unlogged change). The SNES checksum is refreshed every build.
  Edit tests prove pointers move (shortened string shifts every later pointer) and LZ/RLE edits roundtrip.
- **Phase 2 debug tool:** `tools/debug/scenes.lua` lists 50 scenes; `python -X utf8 tools/debug/regen.py --jobs 6`
  reaches every one from a cold boot, saves `work/states/<scene>.mss` and `work/qa/warp/<scene>/final.png`.
  RAM map + main loop + warp tricks: `docs/re/ram.md`. Not covered yet (add when phase 8 needs them): melee,
  attack-command target pick, winning a battle by force, unit/officer data pages, advisor tutorial pages,
  planet/fleet sub-lists, reinforcement messages, other factions' battles.
- **Phase 4 needs:**
  - an event-script parser for bank `$8D` (and others) to list every dialogue block pointer (24-bit, record +3..+5;
    messages after the first are read on from the previous one's end); the blind sweep `tools/find_ptr24.py` is
    noisy. Intro/ending script starts are logged in `scenes.lua`.
  - dialogue ranges (`docs/re/text.md` table) are not behind `data/ptr_tables.tsv`; strings reached by code
    immediates are not swept yet. Extract must cover the whole regions list and add their pointer slots to the
    build's pools.
  - text format per the skill: JSON per block, `id`/`ptr`/`jp`/`en`/`max`; dump never clobbers English.
- **Graphics text:** survey + phase-2 tour list in `docs/re/graphics.md`; phase 5 classifies the battle-UI blocks.
- **Open bugs:** none.
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not hand-tested (headless agent run);
  scripted input verified. Non-blocking: title logo has no known official English version, so per D5 it gets
  redrawn in English.
