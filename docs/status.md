# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2 (debug tool) done. Next: phase 3 (identity build).
- **Phase 2 result:** `tools/debug/scenes.lua` lists 50 scenes; `python -X utf8 tools/debug/regen.py --jobs 6`
  reaches every one from a cold boot (no save, no playthrough), saves `work/states/<scene>.mss` and a shot in
  `work/qa/warp/<scene>/final.png`. Coverage: title (+ START…LOAD with a save), attract demo, faction select,
  4 intros, 4 maps, map system bar / fleet list / planet list / save screen, planet menu / data / sortie /
  production, fleet command bar / destination, invasion and attack notices, hex battle (move phase, attack bar,
  target overlay, enemy attack animation, battle bar, unit/officer data cursor, battle settings), battle report,
  post-battle notice, HQ screen, prisoner judge / recruit / execute / our officer captured, game save → load
  screen → continued map, game over, 4 faction endings, staff roll. RAM map + main loop: `docs/re/ram.md`.
- **Graphics survey extended** over all 50 scenes: 37 runtime LZ blocks the static scan misses
  (`work/recon/lz_runtime.tsv`, `tools/lz_runtime.py`), one raw ROM DMA (4 icon tiles), and a list of Japanese
  labels on the new screens that are not font strings (graphics or RLE tilemaps): `docs/re/graphics.md`
  "Phase-2 tour". Phase 5 classifies them.
- **Warp tricks worth knowing:** `exit_map` (patches the mode-1 jump-table entry in emulator ROM memory for one
  dispatch so the map loop returns → game over / ending checks run), `force` (write `$0973` battle outcome at
  `$8A:842B` → prisoner screens), `battle_auto` (AUTO / END on the battle bar), `cursor_to` (steer the map
  cursor by RAM feedback), `text` (wait for N glyphs from the dialogue renderer `$BA:93FB`). Every run boots with
  `work/saves/blank.srm` unless the scene names a fixture (`save_game` makes `nankyourou_start.srm`).
- **Not covered yet (add when phase 8 needs them):** melee (白兵戦) and the attack-command target pick (needs the hex
  cursor on an enemy), winning a battle by force of arms (fleet unit HP layout at `$7E5E70` unconfirmed), unit /
  officer data pages (cursor must pick a unit), advisor tutorial pages (text 0x040016), planet/fleet sub-lists
  (駐屯武将一覧 etc.), reinforcement messages, the other factions' battles. Each is one more scene entry.
- **Phase 4 needs** an event-script parser for bank `$8D` (and others) to list every dialogue block pointer; the
  blind 24-bit sweep (`tools/find_ptr24.py`) is noisy. Intro/ending script starts are logged in `scenes.lua`.
- **Open bugs:** none.
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not hand-tested (headless agent run);
  scripted input verified. Non-blocking: title logo has no known official English version, so per D5 it gets
  redrawn in English.
