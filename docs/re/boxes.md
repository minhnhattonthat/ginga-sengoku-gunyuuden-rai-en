# Box budgets (width gate, phase 5)

Budgets live in `data/boxes.tsv` (one row per box variant; `tools/lint.py` checks every `en` against them).
Letters are 6 px (two per 12-px digraph cell, `docs/re/font.md`). `{skip:0N00}` indents N cells = 2N letters.

## How they were measured

`tools/stress.py NAME SCENE ID=TEXT..` builds the marker ROM with overrides (`{ruler:N}` = digit ruler of N
letters), warps there with the debug tool and zooms the last frame. The budget is the last letter still whole
on screen. Shots: `work/qa/stress/<name>/` (regenerate with the same command; the evidence column names it).

## Per box notes

- **narration** (prologue/epilogue bottom box): lines start at x=8, 40 letters reach x=248; 3 lines show, a
  4th is half off-screen and then the box moves on. 10EC5A/10EC6A/10EC74 are appended to the line they start on.
- **narration_page** (full-screen pages: 10ECDC, epilogue 19E244..19E408, 19E53C, 19E56A): lines start at x=0,
  42 letters fit. The page's glyphs go to a tile buffer of **112 cells**: the 113th glyph cell overwrites other
  tiles (garbage at the top of the screen, `e113` vs `e112`). Lint wrap `page` checks the cell total.
- **staff_caption**: the four 40-byte leader fields under the credits portraits show whole (centre with spaces).
- **vertical_name**: shown horizontally in the map side panel; letter 12 wraps to the next tile row. `{FFFE}`
  (a spacing cell in the vertical renderer `$81:E4E5`) is dropped in English.
- **map_notice**: the red/blue notice bar starts at x=8 (the help bar starts at x=32 after its icon); its edge is
  at x=250, so 40 letters for the whole composite line (planet/faction/officer names + fragments).
- **save_error**: slot panel text at x=44; reached with `save_empty` / `save_broken` (`$1B28` = FF / FE forced
  at `$BA:AAF4`). The fields are 8 and 9 cells, drawn by count immediates at `$BA:AC2C` / `$AC54`.
- **flagship_speech**: `flagship_speech` scene (map mode `$1B` forced). 16-cell lines (32 letters), 3 per page,
  paged by the arrow. `$8B:D46D` copies 768 bytes of the speech to `$7E:8000`: at most 24 lines.
- **unit_label / column_label**: measured from code only (counted 4-cell / 2-cell draws in the JP cells).
- **attract**: the attract prologue is one 124-cell stream (`$8C:D240` draws from RAM `$1B24`); the per-line
  breaks and positions come from a script not found yet, so English keeps the JP line cells (row evidence).
- **battle_cmd** (148000: deployment prompts, melee quotes, bank `$8E`): see `docs/status.md`.
