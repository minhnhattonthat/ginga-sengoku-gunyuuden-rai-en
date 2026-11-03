# English font: digraph cells (phase 5 decision)

## Decision (2026-11-03)

Two 5-px letters per 12x12 font cell, cells allocated per build. No renderer code is patched.

Why, from the renderers (verified by disassembly):
- Every glyph read in the game goes through one address form: cell `c` at `$95:8000 + c * 24` (file 0x0A8000).
  20 load sites in `$81:DD4D..E0CF` (menus, faction select, vertical names, battle panels; index from
  `$81:E0F4`, X = c * 24) and one in `$BA:94C4` (event dialogue window). Searched: `BF xx 80 95`, `69 00 80`.
- The dialogue window (`$BA:92CD`) draws glyph pairs into a 3x2-tile block (bit 6 of the window flags picks the
  left or the right half, the right glyph shifted 4 px), and the menu renderer (`$81:DFA3..E0EF`) draws into a
  bitmap canvas with its own 4-px shift path. A VWF means rewriting both families (21 sites, several layouts);
  a digraph cell changes only font data and works on every path at once, including fixed-length fields
  (`fixed:N`: N/2 cells = N letters) and the vertical name renderer.
- Density: 6 px per letter. A VWF averages about 5-6 px with this glyph height, so it would buy little.

Cost and limits:
- Cells 0x000-0x527 (1,320). Reserved: `00-09` (digits: numbers are drawn by code from these cells), `3E`
  (blank; also the pair `"  "`). Free: 1,309, minus the cells of any string still in Japanese (the build keeps
  those so a partly translated build shows both). `tools/en.py` `Alloc` fails the build if the script needs
  more pairs than that. Estimate: ~1,000-1,300 distinct pairs for 90k chars of English; if it overflows, the
  next step is a font copy in WRAM with a 16-bit index (2,730 cells), patched at the 21 load sites.
- Pairs are cut from the start of each text run between control codes, so an odd run ends in "x " (half a
  cell of blank). Names inserted at runtime (`{FFFE}`/`{FFFD}` on `$81:E962`) are their own strings: an
  odd-length name leaves a 6-px gap after it. Fine as a word gap after a name; check in the marker tour.
- Composite lines (map notices: name + fragment + planet + fragment, `0048FE`/`006181`/`00641F` with names
  and planets) join strings at cell boundaries: an odd-length name ends in a blank half-cell, so a fragment
  that starts with a space shows a 12-px gap after it instead of 6. Cosmetic; the glossary can prefer
  even-length names where it costs nothing. The cell grid can't hold a half-width pad.
- Label renderers that spread short strings were patched to pack (`docs/re/hooks.md`); the vertical name
  blocks (005E17/005E61/006375) use `{FFFE}` as a spacing cell, so English simply drops those codes.
- Numbers drawn by code use the 12-px digit cells 0-9 (wider than the 6-px letters). Left as is.

## Font

`tools/font_en.py`: 94 glyphs (printable ASCII minus `{}` which delimit control codes, plus `…`), 5 px wide,
caps 7 rows, descenders 2, on cell rows 2-10 (the left letter in px 0-4, the right in px 6-10). Drawn for this
project (MIT). Self-test asserts the width; `--sheet` previews.

## Build

`tools/build.py` (mode `en`: strings with an `en` field; `--marker`: every string as `[id] The quick brown
fox...` with the cell count of each Japanese run kept, so layout and byte lengths are unchanged; `--qa ID=TEXT`
overrides one string). Font cells are written at `0x0A8000 + c * 24` (`font:XXX` in the write log).
