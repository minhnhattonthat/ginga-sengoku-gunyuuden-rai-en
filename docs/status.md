# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5 (engine spike + marker build) in progress: font decided and proven, marker build + tour done,
  missed text extracted, label renderers patched, 10 of 21 box variants measured. Left: see "Next".
- **Font (decided, `docs/re/font.md`):** digraph cells, two 5-px letters per 12x12 cell, allocated per build
  (`tools/font_en.py`, `tools/en.py`; `Alloc` fails if pairs > 1,309 free cells). Torture line (all printable
  ASCII + `…`) renders correctly (`work/qa/stress/torture`).
- **Build:** `tools/build.py` modes: default `en` (en fields; untranslated strings keep their JP cells),
  `--marker` (every string `ID The quick brown fox...` with each JP run's cell count kept; unused cells show
  `##`), `--qa ID=TEXT` overrides (stress builds may move strings pinned only by `verified=n` immediates),
  `--out`. Code patches: `tools/patches.py` (list + why in `docs/re/hooks.md`, test `tests/test_patches.py`):
  label families pack names at 12 px; fleet-command name tag copies the whole name. Free space used from
  `$BC:8000`.
- **QA tools:** `tools/stress.py NAME SCENE ID=TEXT.. [--settle N] [--every N] [--crop]` (`{ruler:N}`),
  `tools/debug/regen.py --rom build/rai_marker.sfc --out work/qa/marker` (all 50 scenes reach on the marker
  build), warp.lua `--var SETTLE=N`, `tools/lua/readpc.lua` (who reads an address range; both LoROM mirrors).
- **Extraction (phase-4 blind spots fixed):** counted strings (`$1AF0` = cells, `$1AF1-3` = pointer, no end
  code): `refs.counted()` immediate sweep, `refs.FIXED` save prompts 1DFB2B, `refs.P16_FAR` formation help
  16E05B, attract prologue 0FC029 (124 cells drawn in counted steps from RAM `$1B24` via `$8C:D240`/`$8C:E2C7`;
  the stepping script is not found, so its English must keep the JP cell layout until it is). script/: 54
  blocks, 1,594 strings.
- **Box budgets:** `data/boxes.tsv` (format in `tools/lint.py`; lint runs in `tools/check.py`, warns on `guess`
  rows once en text exists). Measured: dialogue 40x3 ({skip} indent counts), talk 28x3, faction_desc 40x2,
  label 10, officer_name 8 (fleet-command tag shows 4 cells), advisor 26x3, battle_quote 26x3, help_line 36,
  game_over 32x2, prisoner_judge 32x3, prompt32 32. Guess: narration, vertical_name, unit_label, map_notice,
  save_error, flagship_speech, battle_cmd, attract.
- **Next (finish phase 5):**
  1. Measure the guess rows: narration 10EC1C/19E244 (find when the epilogue/prologue pages show: ending_*
     and intro scenes, `--every` shots), staff roll 19E244 fixed:40 (credits), map_notice (stress a fragment
     that isn't pinned, or the whole composite), unit/option labels (battle_config, battle_unit_data),
     save_error (load_screen with a corrupt save), vertical names (map side panel: 005E17/005E61 shown
     horizontally, `{FFFE}` = spacing, drop it), flagship_speech 08F1DB and battle_cmd 148000 (need debug-tool
     scenes: new-flagship speech, melee/deployment).
  2. Widen the fleet-command name tag to 5 cells (10 letters) or record 8 as the officer-name limit in the
     glossary (D4: engine work first).
  3. Code-built save-slot labels ("######" in save/load): cells `$03D0 $02CA $02F4` written by `LDY #imm /
     STY $1B6x` around `$BA:ABC0..AC00`, drawn as counted strings from RAM `$1B60`; sweep all such builds
     (`LDY #cell / STY $1Bxx`) and have the build write allocated pair codes into those immediates (phase 7
     at the latest).
  4. Then phase 6 (translate): translators get box budgets from `data/boxes.tsv`; plain `pad` boxes wrap by
     width, so en text needs `{n}` line breaks that the build pads (not implemented yet: add to
     `build.english_edits` + `lint.lines_of` already splits on `{n}`).
- **Known limits (documented in `docs/re/font.md`):** odd-length names in composite notices leave a 12-px gap;
  names block 00114C is full (English names need relocation in phase 7; strings pinned by imm16 refs).
- **Graphics text:** survey in `docs/re/graphics.md`; still Japanese (phase 7/8): title menu + copyright,
  save/load headers, production/planet column labels, battle panels, HQ banner, attract year card graphics.
- **Open bugs:** none.
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not hand-tested (headless agent run);
  scripted input verified. Non-blocking: title logo has no known official English version, so per D5 it gets
  redrawn in English.
