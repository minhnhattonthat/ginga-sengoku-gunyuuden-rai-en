# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9 (release) done: v1.0 published 2026-11-04 on github.com/minhnhattonthat/ginga-sengoku-gunyuuden-rai-en
  (`release/GingaSengokuRai_EN_v1.0.zip`, patch sha1 ec47b97a62822c77377bed0fb2639539a5499988, patched CRC32
  2F2AF74B; includes the two post-playtest fixes below). Next release: bump the version, never overwrite v1.0.
- **Gates (all green at release):** build + 31 tests + lint (0 errors); smoke; `jp_left` over every text unit the
  build wrote: 0 runs; visual QA 58/58 tour sheets ok/fixed (`work/qa/manifest.tsv`, round 2 verdicts
  `work/qa/verdicts/r2_chunk_*.tsv`, `recheck_1.tsv`); story pass 17/17 chapters (`work/qa/story/`); `docs/polish.md`
  all ticked.
- **Release:** `python -X utf8 tools/release.py --version X.Y` (stops at first failure; `--force` to overwrite).
  Release README template: `docs/README.release.txt`.
- **Graphics text:** all rows in `data/gfx.tsv` (LZ, word-RLE, title tilemaps). Latest: reinforcement speaker tag
  援軍 = LZ 0AFBC0 (loaded to `$7E:8000` by `$00:8401`, DMA to VRAM $7000) -> "Reinf."; prisoner "Level" dakuten
  rows cleared. Title logo stays Japanese (D5).
- **Fixed fields too long as letter pairs** now fall back to condensed cells (`build.english_edits` `squeeze`):
  000CA6 "Great Gojo" (10-byte field).
- **Known limits (README, visual-qa brief):** odd-length inserted name -> two spaces ("Ryuga  Fleet:"); a few abbreviations (Flagshp/Btlship/Destryr, PLNT/FLT, Reinf.).
- **Caveats:** LEVEL UP!! (LZ 105339) and "Pick fleet" (LZ 166080) were drawn from the block layout but no tour scene
  reaches them; 165 lint warnings are "budget is a guess" (officer_name, full_name, battle_cmd boxes): those fit in
  every tour shot that shows them, not measured with `tools/stress.py`.
- **Post-v1.0 (2026-11-04, owner playtest):** label boxes now draw from x = 4 (list cursor box no longer covers the
  first letter; `tools/patches.py` 5-cell layout).- **Fixed (owner savestate `work/states/gg_text.mss`, press A = Launch fleet):** the notice "No fleets stationed."
  showed "et!": `$8B:8448` / `$8B:82C2` (`LDA #$82 / LDX #$A9xx / JSR $B8C0`) were `n` rows in `data/imm16.tsv`, so
  the build left them pointing at the old offsets. Now `y`. The other unverified LDX/LDY rows load other banks or
  constants (checked by shape, not each in game).
- **Open bugs:** none.
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not hand-tested
  (headless agent run; scripted input verified).
