# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 4 (extract) done. Next: phase 5 (engine spike + marker build: font/VWF decision, every string
  replaced by `[id] marker`, width gate per box variant).
- **Phase 4 result:** `python -X utf8 tools/extract.py` -> `script/` (48 block files, 1561 strings, 3579 refs).
  `tests/test_extract.py`: every string re-encodes to the original bytes, script/ matches a fresh extraction,
  every run of `data/text_scan.tsv` (scan at `--min 16`) is text / a pointer slot / a reviewed `data/not_text.tsv`
  row, nothing overlaps. Pointer forms (event scripts cmd 18/26, talk base+offset tables, quote lists, battle-quote
  offsets, 24-bit tables, fixed fields, code immediates) are in `tools/refs.py` and `docs/re/text.md`.
  `build.py` now repacks text by block from `extract.blocks()` and rewrites p16/p24/rel16 refs; edit tests cover
  a p16 pool, a p24 message chain and the rel16 talk tables (`tests/test_identity.py`).
- **Phase 5/7 needs from phase 4:**
  - `data/imm16.tsv`: 480 code-immediate refs; 41 `verified=y`, the rest may be constants. They are `fixed` refs:
    the build refuses to move their strings, which blocks relocation of bank-01 pools (e.g. 0x01676A, 0x010396).
    Verify the ones in pools that need to grow (disassemble the hit; marker build shows strings that stay JP).
  - `fixed:N` entries (faction names `$8C60`/`$8C88`, unit labels `$AC91`, column labels, deployment prompts,
    staff-roll lines) must keep their byte length: engine work (wider fields) or same-length English.
  - Tails: bank-0 officer-name tables point into the middle of names (0x0010A8 +10, 0x0010CA +10); talk type 2
    (`$BA:9E27`) is a stale table pointing mid-string into type 3. The build keeps tails only while the host
    string is unchanged; decide (repoint to a copy, or check in-game whether type 2 is ever shown).
  - Renderer-dependent `{FFFE}`/`{FFFD}` (name insert vs skip cell): see docs/re/text.md before translating.
  - Free-space candidates (FF fill, untested): 0x017172-0x018000, 0x040800-0x048000, 0x05DD10-0x060000,
    0x06ED28-0x070000, 0x1D3072-0x1D8000.
- **Phase 2 debug tool:** `tools/debug/scenes.lua` lists 50 scenes; `python -X utf8 tools/debug/regen.py --jobs 6`
  reaches every one from a cold boot. Not covered yet (add when phase 8 needs them): melee, attack-command target
  pick, winning a battle by force, unit/officer data pages, advisor tutorial pages, planet/fleet sub-lists,
  reinforcement messages, other factions' battles, recruit/diplomacy talk, new-flagship speeches, level-up notice.
- **Graphics text:** survey + phase-2 tour list in `docs/re/graphics.md`; phase 5 classifies the battle-UI blocks.
- **Open bugs:** none.
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not hand-tested (headless agent run);
  scripted input verified. Non-blocking: title logo has no known official English version, so per D5 it gets
  redrawn in English.
