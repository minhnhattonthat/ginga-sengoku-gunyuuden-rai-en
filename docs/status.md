# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8 (emulator QA) in progress. Phases 6 (translate, reviewed) and 7 (insert/fit, build green) done.
- **Font:** digraph cells, ~770 of 1,309 free cells used; condensed glyph strips (`font_en.strip`) take spare cells.
- **Phase 8 text/layout fixes done** (all verified in fresh warps, `work/qa/tour/<scene>/final.png`):
  notice garbage (imm16 rows 05AB8C/05ABC9/062305 are 8-bit LDA: `n`); save-panel labels (`build.CODE_LABELS`);
  names split after 3 cells (5-cell label pitch); speech boxes (battle quotes `$81:ECE2`, advisor `$8B:DA66`):
  no 『』, speaker tags for names > 7 letters (`build.speech_tags`, `glossary.md` short forms, condensed 8-letter
  names); `Fort n` fortress header; battle tabs + unit-data header read an English class-record copy at file
  0x7C00 (left-aligned, long names condensed); fleet-command tag 4 px in; zero-width msg codes no longer cut a
  letter pair (`en.runs`). All hooks: `docs/re/hooks.md`.
- **Known limits (document in visual-qa brief / polish, not bugs):** a name inserted by `{FFFE}`/`{FFFD}` with an
  odd letter count ends in a half-blank cell ("Ryuga  Fleet:"): digraph font, needs a VWF to fix. List cursor
  box overlaps the first letter (5-cell label routine draws from x=0; JP names were centred).
- **Next (phase 8): graphics text** (D5: translate all; the title LOGO stays Japanese, it has no official English
  version, D5 keeps it). Tools: `tools/lua/finaldump.lua` (regen `--probe`: VRAM/CGRAM/OAM at the final shot;
  JP dumps for all 55 scenes in `work/gfx/jp/<scene>/`), `tools/gfx_locate.py SCENE X Y W H` (BG tiles of a
  screen rect -> LZ block + tile), `tools/gfx.py sheet` (block sheet with grid), decompressed blocks in
  `work/gfx/blocks/` (from `data/lz_blocks.tsv`). Sources found so far:
  - LZ 08D6D3 (16-wide layout): 新造戦艦名 (tiles 0x22-0x2B/0x32-0x3B, outlined: fill 2, outline 8, bg 6),
    攻撃 防御 回避 射程 速力 (3 tiles each at 0x40.., rows 0x40/0x50; fg 8 on bg 2, text rows 3-14).
  - LZ 0E48FE bottom rows: 艦隊戦画面環境設定 (battle config title); LZ 105339 レベルアップ!!; LZ 166080 艦隊選択.
  - Prisoner panel labels (体力 指揮 忠誠 レベル ...): NOT LZ: `$81:8B99` composites raw ROM bank `$90`
    (mask AND at `$90:85A0`, overlay ORA after it, 2 planes) into `$7E:3330`, sent each frame by `$81:90E6`.
  - Still to locate: side panel 惑星/艦隊 (map screens), faction map labels (LZ 0FC121), production headers,
    planet/fleet list headers, save/load titles, HQ banner 南京楼軍本陣, prisoner buttons 登用する/処刑する
    (likely sprites), formation 指揮, title copyright line.
  Plan: `tools/gfx.py` draws English into block images per `data/gfx.tsv` rows (block, rect, text, style), the
  build recompresses (must not grow: else relocate) and writes; then cold-boot warps + visual QA.
- **Then:** full tour regen + visual-qa round 2 (`qa_gate.py`), tick/waive `docs/polish.md` (99 open; release
  refuses while open), story pass if the skill's release steps need it, `tools/release.py`.
- **Open bugs:** none reported.
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not hand-tested (headless agent run);
  scripted input verified.
