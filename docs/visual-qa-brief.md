# Visual-QA reviewer brief - Ginga Sengoku Gunyuuden Rai (SNES)

You review screenshots from the English build's QA tour and give each one a verdict. Read-only on everything
except your one verdict file: no edits to the repo, no git, no subagents.

## Inputs (in your dispatch)
- A chunk file: one `id<TAB>path` line per shot. Read every shot in it; none may be skipped.
- Your verdict file: `work/qa/verdicts/<chunk>.tsv`.
- The original ROM's shot of the same scene: `work/gfx/jp/<scene>/final.png` (the scene is the folder name in
  the path), and `glossary.md`.

## How to look
- Read each shot whole first. Where text is small, zoom into it with
  `python -X utf8 "$(python tools/skill.py)/scripts/sheet.py" SHOT.png --crop x,y,w,h --zoom 3 --out <scratch>.png`
  (scratch = a path under `work/qa/scratch/`) and read that.
- When something looks wrong, open the original's shot of the same scene. If the original shows the same thing
  (same layout, same garbage), it is the game's own behaviour: `ok`, with a note.

## Judge
An `issue` is any of:
- Japanese still visible (say whether it is font text or a graphic: logos, map labels and tile-drawn menu words
  are graphics);
- text overflowing a box, clipped by a frame, or running off screen;
- garbage tiles, wrong or missing glyphs, `##` cells, a strike or stray pixels across letters;
- broken line breaks: a word split mid-line, a page ending mid-sentence, a one-word last line;
- an empty box where text belongs;
- a name that differs from `glossary.md`.

The font draws two letters per 12-px cell, so letters are narrow and spacing is tight: that is by design.

Standing non-bugs, `ok`:
- text still typing out, a box mid-fade or mid-scroll, a cursor caught mid-blink;
- a map or scene still loading after a warp;
- anything identical in the original's shot;
- the title-screen logo stays Japanese by the owner's decision (docs/decisions.md D5);
- a name inserted mid-sentence with an odd letter count is followed by a blank half cell, so two spaces show
  ("Ryuga  Fleet:"): digraph font limit;
- a list cursor box overlapping the first letter of the selected name (fleet / planet lists): engine draws the
  label from x = 0;
- short labels abbreviated to fit (Flagshp, Btlship, Destryr, PLNT, FLT, Reinf.).

## Verdicts
Write your verdict file once you have read every shot, one line per id in the chunk:
`id<TAB>ok|issue<TAB>what and where` (for an issue: which area, which text, what is wrong).
Then return a short summary: counts, and the issues one per line.
