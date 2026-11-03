# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 7 (insert, fit, check) done; phase 8 (emulator QA) next.
  - Phase 6 done: all 1,595 strings translated (`work/tl/b001-b018`, `tools/batches.py`), batch check 0 errors,
    reviewer pass on every batch (`work/qa/review/bNNN.txt` from `tools/pairs.py`, brief `docs/reviewer-brief.md`),
    every Critical/Important fixed; Minors deferred to `docs/polish.md` (release blocks until ticked).
  - Phase 7 done: `python -X utf8 tools/build.py` green (lint 0 errors, romdiff clean), identity and marker builds
    still pass, smoke ok (faction select shows English). Build now relocates (docs/re/text.md §Relocation):
    split overflowing blocks into free space, rewrite verified imm16 operands, p24-only units to banks `$BD-$BF`
    (talk block 1D8000 etc.), `tail_en` for shared name tails (0010A8 Princess Shimon, 0010CA Rai Ryuga).
    Melee labels / retreat-quote table found and split out (14884A fixed:80, 14889A base).
- **Font:** digraph cells, 770 of 1,309 free cells used by the English script.
- **Next (phase 8):**
  1. `python -X utf8 tools/debug/regen.py --rom build/rai_en.sfc` -> shots per scene; contact sheets; visual-qa
     subagent verdicts (`qa_gate.py`). Watch: relocated text (talk/recruit, battle quotes bank $82, names
     block 00114C, ship labels 000CEC), officer names in the fleet-command tag (8 letters shown; D4),
     full_name box (guess 18 letters), battle_cmd/battle_orders (never measured: play to a real melee).
  2. Unverified imm16 rows (`verified=n`) are ignored by the en build: if a string shows garbage, check its row.
  3. Retreat table word 50 (0x94A) still points at base+0x94A (block end in JP): check if any officer uses it.
  4. Graphics text still Japanese (`docs/re/graphics.md` survey): title logo (D5: redraw), map labels
     (南京楼, 練, 南天連合, 大五丈 on the faction map), menus drawn as tiles.
  5. Code-built save-slot labels ("######") and fortress header `##5####` (marker): allocate pair codes.
  6. Attract prologue layout script, save-error panel counts (engine work).
- **Open bugs:** none reported.
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not hand-tested (headless agent run);
  scripted input verified. Non-blocking: title logo has no known official English version, so per D5 it gets
  redrawn in English.
