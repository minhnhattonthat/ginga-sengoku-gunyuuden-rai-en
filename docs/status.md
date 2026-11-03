# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5 (engine spike + marker build) done except one box variant: font decided and proven, marker
  build + tour done, missed text extracted, label renderers patched, 23 of 24 box variants measured
  (`data/boxes.tsv`, notes `docs/re/boxes.md`). Not measured: **battle_cmd** (block 148000, 101 strings:
  melee deployment prompts + battle-start quotes, bank `$8E`). Phase 6 may start; translate 148000 last.
- **Font (decided, `docs/re/font.md`):** digraph cells, two 5-px letters per 12x12 cell, allocated per build
  (`tools/font_en.py`, `tools/en.py`; `Alloc` fails if pairs > 1,309 free cells). Torture line renders.
- **Build:** `tools/build.py` modes: default `en`, `--marker`, `--qa ID=TEXT` overrides, `--out`. Code patches:
  `tools/patches.py` (`docs/re/hooks.md`). `pad` boxes: `{n}` in en is padded with spaces to the box width
  (`lint.expand_n`, called by `build.english_edits`). Free space used from `$BC:8000`.
- **Lint (`tools/lint.py`, in check):** `{skip:0N00}` = N cells = 2N letters (was counted as N: fixed);
  wrap `page` = full-screen narration, at most 112 glyph cells per string (the 113th garbles the screen).
- **QA tools:** `tools/stress.py`, `tools/debug/regen.py`, warp.lua (`force` now takes `once = true`),
  `tools/lua/readpc.lua`. New scenes: `prologue` (event 4 runs before every faction intro), `save_empty` /
  `save_broken` (`$1B28` forced), `flagship_speech` (map mode `$1B` forced), `formation` (fleet bar icon 4),
  `battle_unit_data` / `battle_officer_data` now press A on the unit cursor.
- **Next:**
  1. Phase 6 (translate): translators get budgets from `data/boxes.tsv` (`python -X utf8 tools/lint.py --boxes`
     maps every string to its box). Pad boxes: write `{n}` for line breaks. Attract 0FC029: keep the JP line
     cells (row evidence). column_label 0623D8: `Unit{n}Ship` style, 4 letters each.
  2. Measure battle_cmd before translating 148000. Found: attack menu step 8 (`$81:AC98`) maps icon id `$091D`
     `$16` -> step `$15` (`$81:AFEC`: attack type `$0989` = 3) -> `$83:8000` -> `$83:CAAA` -> `$8E:8000`.
     Forcing `$0989` = 3 at `$81:ADB7`/`$81:B6AD` crashed; forcing `$091D` at `$81:ACAA` did nothing (menu never
     confirmed); poking `$0737` = `$15` + `$0901` = 5 in the invasion attack menu stalled (the attacker there
     is a fortress, probably no melee). Next try: play to a real melee (own flagship next to an enemy flagship, pick the melee icon),
     then `tools/stress.py`.
  3. Unit labels 002C91 / column labels 0623D8 are budgeted from code only; see them in phase 8 QA (fleet
     unit data window; formation sub-view). Ship vertical names 006375: not seen on screen yet.
  4. Widen the fleet-command name tag to 5 cells (10 letters) or record 8 as the officer-name limit (D4).
  5. Code-built save-slot labels ("######"): `LDY #cell / STY $1B6x` around `$BA:ABC0..AC00`; sweep and have
     the build write allocated pair codes into those immediates (phase 7 at the latest). Same kind: the fortress
     unit-data header shows `##5####` (marker `battle_unit_data`): a fortress label built from cells + a digit.
  6. Attract prologue layout script (find it to free the JP line layout), save-error panel counts
     (`$BA:AC2C`/`$AC54`, panel fits ~29 letters) - phase 7 engine work.
- **Known limits (`docs/re/font.md`):** odd-length names in composite notices leave a 12-px gap; names block
  00114C is full (English names need relocation in phase 7; strings pinned by imm16 refs).
- **Graphics text:** survey in `docs/re/graphics.md`; still Japanese (phase 7/8).
- **Open bugs:** none.
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not hand-tested (headless agent run);
  scripted input verified. Non-blocking: title logo has no known official English version, so per D5 it gets
  redrawn in English.
