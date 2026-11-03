# Text engine, encoding, pointers

ROM: LoROM 2 MiB, map mode `$30` (FastROM), header title `GINGASENGOKUGUNYUUDEN`. File offset = `((addr & 0x7F0000) >> 1) | (addr & 0x7FFF)`.

## Encoding (verified: decoded known strings, see `tests/test_recon.py`)

- Every character is a **16-bit little-endian code = font cell number**. No Shift-JIS anywhere (the jpscan "SJIS" hits in bank 0 are pointer tables).
- Font: **12x12 1bpp at file 0x0A8000** (bank `$95`), 24 bytes per glyph (12 rows of 2 bytes, MSB = left pixel), cells `0x000-0x527` (1,320). Past 0x527 is other data. Read by `$81:DFBE..E0D3` (verified with `tools/lua/romrange.lua`, faction select) and `$BA:94ED..9511` (dialogue window).
- Layout: `00-09` digits, `0A-23` A-Z, `24-3D` a-z, `3E` space, `3F-56` punctuation (`、`=55 `。`=56 `「」`=4D/4E `…`=4A `ー`=47 `!`=44 `?`=43), `57-A6` hiragana in gojuon order (dakuten forms after the plain row, then small kana), `A7-F8` katakana the same way, `F9` ©, `FA-527` kanji (grouped roughly by reading, not strict JIS order; `111-117` blank).
- `tbl/jp.tbl`: all cells, read by eye from `tools/font_sheet.py` sheets, cross-checked with context in decoded strings (`tools/font_cells.py` zooms single cells). Five fixes from context: 44E 嶺 (魔天嶺), 499 領 (占領), 4A3 赦 (容赦), 4BF 獅 (獅子), 4D6 貫 (貫き通す). **guess** for kanji that appear in no decoded string yet; `font_match.py` (MS Gothic template match) is too weak to verify alone. True duplicate cells: 4C5 = 油 (418), 4EC = 叡 (14A), tagged `#2`.
- Text is horizontal, 12 px per character; the faction-select box is a 30x4-tile bitmap canvas on BG3 (2bpp), so the engine draws glyphs into tiles: a VWF fits the same path.

## Two string formats

**Plain** (menus, battle quotes, descriptions, tutorial): codes, ended by bare `FFFF` (`{end}`). `FFFE` appears inside some (likely line break, **guess**). Many strings are padded with spaces to the box width (20 cells per line on faction select) instead of a newline code.

**Dialogue** (event scenes, read by the window renderer `$BA:92CD`, verified by disassembly + trace `tools/lua/msgptr.lua`): codes with inline commands `FFFF <cmd>`:

| Cmd | Args (words) | Effect (from `$BA:92D5..93F8`) |
|---|---|---|
| `0000` | 0 | end of message (clears window busy bit 7) |
| `0001` | 0 | new line (`$08 += $30`, `$18 += $40`) |
| `0002 n` | 1 | indent / skip: new line plus `n` half-cells (`$12 += 6` per 2) |
| `0003 a b` | 2 | wait / speed `(a<<4)|b` into `$02` |
| `0005` / `0006` | 0 | set / clear flag `$1E` bit 0 (typewriter on/off; speaker name is printed before the `0005`) |
| `0007` / `0008` | 0 | set / clear flag `$1E` bit 8 |

Other command numbers are ignored by the renderer. Typical message: `師真{c5}「いいだろ{c6}{spd:0200 0000}う ...」{end}`.

## Pointers

- **16-bit in-bank tables** for plain strings: a table of `$8000+` words directly before its strings (bank 01: tables at 0x010000, 0x01003A, 0x0102CC, 0x010332...; bank 04: 0x040008...; bank 00: 0x000FC0, 0x0010DC, 0x001C36, 0x00589D). `tools/find_ptrs.py` lists 37 tables (`work/recon/ptrs.tsv`); some strings are reached by code immediates instead (not yet swept).
- **24-bit pointers in event records** for dialogue (verified: record at 0x06B0EA `FF 00 08 | 1C EC A1 | ...` points at 0x10EC1C, the first message seen in the intro). The event command at `$8D:8652` copies record bytes +3..+5 to the window pointer `$1B64`. Messages after the first are read **on from the end of the previous one** (renderer pointer advances, `wr=BA92E5` in the trace), so a block of messages has one pointer at its start. Event scripts live at least in bank `$8D` (file 0x068000-0x06FFFF). A full event-script parser is phase 4 work.

## Text ranges (`tools/text_regions.py`, `work/recon/regions.tsv`)

| Range | Format | Content |
|---|---|---|
| 0x000C60-0x0012C0, 0x001C64-0x001D1C, 0x002C89, 0x0058A5-0x005933, 0x005E17, 0x006375, 0x00641F | plain | faction/general/planet names, unit labels, system messages |
| 0x01004E-0x017170 | plain | battle commands, battle quotes, faction descriptions, capture/defeat quotes |
| 0x040016-0x0407FE | plain | advisor tutorial pages |
| 0x10EC1A-0x10EFAC, 0x1161FB-0x116557, 0x116A09-0x11701B, 0x11FC98-0x11FFB2, 0x12EA2F-0x12ED67, 0x176E64-0x17773A, 0x17FBD8-0x17FFA6, 0x187AB9-0x187F03, 0x18EC33-0x18FC47, 0x19E242-0x19E636 | dialogue | story scenes, per-faction intros and endings (banks shared with graphics) |
| 0x148000-0x1491E4 | plain/dialogue mix | deployment prompts, general battle lines |
| 0x1D8000-0x1DE866 | dialogue-like | recruitment / diplomacy lines |

Not yet proven complete: code-built strings, numbers, and small strings under 64 bytes (`--min`). Phase 4 sweeps code immediates and event records.

## Tools

`tools/font_sheet.py` (labelled font sheet), `tools/font_cells.py` (zoom chosen cells), `tools/font_match.py` (template first guess), `tools/scan_text.py` (string runs), `tools/find_ptrs.py` (16-bit tables), `tools/find_ptr24.py` (24-bit pointers, noisy), `tools/text_regions.py` (text ranges), `tools/lua/romrange.lua` (per-PC ROM read ranges), `tools/lua/msgptr.lua` (dialogue window pointer log; slow: WRAM write hook).
