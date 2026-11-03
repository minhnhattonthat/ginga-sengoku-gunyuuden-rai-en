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
- **Next (engine work, in order):**
  1. Label layouts: strings shorter than 5 cells are drawn by length-indexed routines that spread the cells
     (16-px pitch: "aa bb cc"). Families: `$8E:C9D8/CA23/CA92/CB1C` (table `$8E:C9C6`, 3-byte ptrs, index =
     3*len, callers `$8E:84FE/8551/857C/8597`, glyph fetch `$8E:CBCA`), `$8E:F2FF/F34A/F3B9/F443`,
     `$BA:8C00/8C4B/8CBA/8D44` (find their tables/helpers). Plan: point lengths 2-4 at the len-5 routine and
     patch the glyph fetch so `FFFF` draws blank (`3E`) and holds the pointer (callers `INC $1AF0` x2 after each
     glyph). Code goes in free space `$BC:8000` (file 0x1E0000, all FF). Needs a patch list in the build
     (hand-assembled bytes, original bytes checked, `dis65816.py` re-check in a test).
  2. Other font users not yet classified: `$81:E86F`, `$81:EAE0`, `$83:BCE1`, `$8C:E2CA`, `$8E:C772`,
     `$8E:C85F`, `$8E:F099`, `$8E:F197`, `$BA:896B` (search `A9 95`). Fleet-list names spread ("q ui ck").
  3. Review every marker shot (`work/qa/marker`), list box variants, stress-measure each (talk window 1D8000 via
     prisoner_recruit, battle quotes, advisor, map notices, help line, game over, prisoner judge, epilogue,
     staff roll, flagship speech, unit/option labels, names in lists), write `data/boxes.tsv` + box per string,
     lint warning on unmeasured variants (`tools/check.py`).
  4. Odd-length names inserted at runtime leave a 6-px gap: check in the tour; fix if ugly.
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
