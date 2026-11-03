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
| [text.md](text.md) | header/map, encoding + font, both string formats, control codes, event-script format, every pointer form, extraction + coverage | verified (disassembly, every ref lands on a string start, roundtrip + coverage tests); `data/imm16.tsv` rows with `verified=n` are candidates |
| [ram.md](ram.md) | game-state RAM (faction, map modes, battle phase/outcome, characters, planets, script pointer), main loop, map/battle controls, warp recipes | mostly verified (disassembly + warps); fleet-unit HP layout guessed |
| [graphics.md](graphics.md) | LZ codec, block list, RLE tilemaps, graphics-text survey, free space | LZ + RLE verified; runtime-only LZ blocks found (lzlog.lua); survey complete for title→map, still needs phase-2 screens |

No earlier fan translation was found (web search 2026-11-03: romhacking.net listings, general search).
