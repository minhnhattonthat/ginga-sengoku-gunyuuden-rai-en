# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9 (release) done: v1.0 zip built and verified locally (`release/GingaSengokuRai_EN_v1.0.zip`,
  patch sha1 c3960cdfe4bf52a94a92ce115b911e4ad8f6fddb, patched CRC32 3A23D092). Not published: publishing is the
  owner's call (`references/pipeline.md` §Publish; never `gh release create` without the owner).
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
  first letter; `tools/patches.py` 5-cell layout). v1.0 zip predates it: rebuild the release before publishing.
- **Open bugs:** map notice bar showing only "et!" (owner screenshot, Great Gojo game ~85 s after boot); trigger
  unknown, not reproduced: no script line ends "et!" past a box edge.
- **Waiting on the user:** publish v1.0 (owner's call); GUI keyboard input in `tools/mesen/Mesen.exe` not hand-tested
  (headless agent run; scripted input verified).
