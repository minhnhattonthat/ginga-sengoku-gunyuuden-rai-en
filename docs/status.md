# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5 (engine spike + marker build) in progress.
- **Done in phase 5:**
  - Font decision: digraph cells (two 5-px letters per 12x12 cell), no VWF. Why + limits: `docs/re/font.md`.
    `tools/font_en.py` (94 glyphs, self-test), `tools/en.py` (pair encoder, per-build cell allocation,
    `Alloc` fails if pairs > free cells), `tests/test_en.py`.
  - `tools/build.py --marker [--out F]`: every string -> `ID The quick brown fox...` with each Japanese run's
    cell count kept (same bytes, no pointer moves); every unused cell shows `##` so font text the extractor
    missed can't hide as Japanese. `--qa ID=TEXT` overrides one string (`{end}` added unless fixed field).
    Normal build (`mode en`) encodes `en` fields and keeps untranslated strings' cells.
  - Marker build boots (smoke ok); `regen.py --rom build/rai_marker.sfc --out work/qa/marker` reaches all 50
    scenes (shots `work/qa/marker/<scene>/final.png`, JP originals in `work/qa/warp/`). `regen.py --out` added.
  - `tools/stress.py NAME SCENE ID=TEXT..` (marker build + overrides + warp + zoom; `{ruler:N}`); warp.lua
    takes `--var SETTLE=N`.
  - Torture line (all printable ASCII + `…`) renders correctly in the event window (`work/qa/stress/torture`).
- **Measured so far** (to go into `data/boxes.tsv`):
  - Event dialogue window (`$BA:92CD`, msg blocks 10EC1C..18EC39): 20 cells = 40 letters per line from the left
    margin (`{skip:n}` indent counts against it; cell 21 overflows into the next tile row), 3 lines per message
    (JP max); `work/qa/stress/dlg`.
  - Faction-select description (011A46): 20 cells = 40 letters x 2 lines (marker shot).
  - Label boxes (production / HQ / panels): a 5-cell string packs at 12 px (10 letters, `work/qa/stress/lbl`).
  - Label-layout patch done (`tools/patches.py`, `docs/re/hooks.md`, `tests/test_patches.py`): the three
    length-indexed label families now pack every name at 12 px; fleet list + production verified.
- **Marker tour review (all 50 scenes, `work/p5/rev/sheet*.png` = 2x2 pages of `work/qa/marker/*/final.png`):**
  - Fine: event dialogue, faction select, map notices (composites of name + fragment strings), help line,
    battle config, advisor box, talk window (prisoner_recruit), game over, fleet list, production.
  - **Still spread at 16 px per cell (more renderers to patch):** fleet_move officer list ("11 52"),
    fleet_command name above the icon bar ("11 4C"), prisoner/officer data screens (faction "00 0C A6  T",
    name "12 2C"), battle_enemy_attack ship names ("0C F5"). Candidates: font users `$81:E86F`, `$81:EAE0`,
    `$83:BCE1`, `$8C:E2CA`, `$8E:C772`, `$8E:C85F`, `$8E:F099`, `$8E:F197`, `$BA:896B` (search `A9 95`).
  - **Font text the extractor missed (shows `##`/random pairs):** attract demo year card (元魔三年, 4 cells),
    save/load prompts (記録してよろしいですか? / 記録が壊れています, save_screen, load_screen, save_game), save-slot
    labels ("######" next to the numbers), prisoner question line (prisoner_judge/ours: box above
    登用する/処刑する). Find where they live (code-built or an unscanned table), extract, re-tour.
  - Map side panel shows the vertical-name blocks (005E17/005E61/006375) horizontally with `{FFFE}` = skip:
    English drops the `{FFFE}`s.
- **Next:** patch the 16-px renderers; extract the missed strings; stress-measure each box variant (talk window,
  battle quotes, advisor 13 cells x 3?, map notice, help line, game over, prisoner judge, epilogue, staff roll,
  flagship speech, unit/option labels, names in lists) and fill `data/boxes.tsv` (format in `tools/lint.py`,
  new, not yet wired into check.py); odd-length runtime names (6-px gap).
- **Phase 5/7 needs from phase 4:** (unchanged)
  - `data/imm16.tsv`: 480 code-immediate refs; 41 `verified=y`, the rest may be constants. They are `fixed` refs:
    the build refuses to move their strings, which blocks relocation of bank-01 pools (e.g. 0x01676A, 0x010396).
  - `fixed:N` entries (faction names `$8C60`/`$8C88`, unit labels `$AC91`, column labels, deployment prompts,
    staff-roll lines) must keep their byte length (N/2 cells = N letters with the digraph font).
  - Tails: bank-0 officer-name tables point into the middle of names (0x0010A8 +10, 0x0010CA +10); talk type 2
    (`$BA:9E27`) is a stale table pointing mid-string into type 3. Marker build allows same-length edits.
  - Free space (FF fill, untested): 0x017172-0x018000, 0x040800-0x048000, 0x05DD10-0x060000, 0x06ED28-0x070000,
    0x1D3072-0x1D8000, 0x1E0000-0x1FFFFF.
- **Graphics text:** survey in `docs/re/graphics.md`; still Japanese in the marker tour (graphics, phase 7/8):
  title menu, save/load headers, production/planet column labels, battle panels, HQ banner, attract year card.
- **Open bugs:** none.
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not hand-tested (headless agent run);
  scripted input verified. Non-blocking: title logo has no known official English version, so per D5 it gets
  redrawn in English.
