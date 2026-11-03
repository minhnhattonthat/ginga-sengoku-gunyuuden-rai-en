# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| [text.md](text.md) | header/map, encoding + font, both string formats, dialogue control codes, 16-bit tables, 24-bit event pointers, text ranges | encoding + dialogue codes verified; ranges and event format partly guessed |
| [graphics.md](graphics.md) | LZ codec, block list, RLE tilemaps, graphics-text survey, free space | LZ verified; survey partial; free space candidates only |

No earlier fan translation was found (web search 2026-11-03: romhacking.net listings, general search).
