# Text engine, encoding, pointers

ROM: LoROM 2 MiB, map mode `$30` (FastROM), header title `GINGASENGOKUGUNYUUDEN`. File offset = `((addr & 0x7F0000) >> 1) | (addr & 0x7FFF)`.

## Encoding (verified: decoded known strings, see `tests/test_recon.py`)

- Every character is a **16-bit little-endian code = font cell number**. No Shift-JIS anywhere (the jpscan "SJIS" hits in bank 0 are pointer tables).
- Font: **12x12 1bpp at file 0x0A8000** (bank `$95`), 24 bytes per glyph (12 rows of 2 bytes, MSB = left pixel), cells `0x000-0x527` (1,320). Past 0x527 is other data. Read by `$81:DFBE..E0D3` (verified with `tools/lua/romrange.lua`, faction select) and `$BA:94ED..9511` (dialogue window).
- Layout: `00-09` digits, `0A-23` A-Z, `24-3D` a-z, `3E` space, `3F-56` punctuation (`、`=55 `。`=56 `「」`=4D/4E `…`=4A `ー`=47 `!`=44 `?`=43), `57-A6` hiragana in gojuon order (dakuten forms after the plain row, then small kana), `A7-F8` katakana the same way, `F9` ©, `FA-527` kanji (grouped roughly by reading, not strict JIS order; `111-117` blank).
- `tbl/jp.tbl`: all cells, read by eye from `tools/font_sheet.py` sheets, cross-checked with context in decoded strings (`tools/font_cells.py` zooms single cells). Five fixes from context: 44E 嶺 (魔天嶺), 499 領 (占領), 4A3 赦 (容赦), 4BF 獅 (獅子), 4D6 貫 (貫き通す). **guess** for kanji that appear in no decoded string yet; `font_match.py` (MS Gothic template match) is too weak to verify alone. True duplicate cells: 4C5 = 油 (418), 4EC = 叡 (14A), tagged `#2`.
- Text is horizontal, 12 px per character; the faction-select box is a 30x4-tile bitmap canvas on BG3 (2bpp), so the engine draws glyphs into tiles: a VWF fits the same path.

## Two string formats

**Plain** (menus, battle quotes, descriptions, tutorial): codes, ended by bare `FFFF` (`{end}`). Many strings are padded with spaces to the box width (20 cells per line on faction select) instead of a newline code. `FFFE` = `{FFFE}` and `FFFD` = `{FFFD}` depend on the renderer (verified by disassembly): `$81:E962` inserts an officer name (`$00:90DC[$0950]`, e.g. `{FFFE}殿`) or a planet name (`$00:9C36[$0950]`, e.g. `{FFFD}を占領しました`); `$81:E4E5` (vertical faction/leader/ship names) treats `FFFE` as "skip one cell". Some records carry raw bytes before the text (`pre` in script/: 1 layout byte for ship classes, 4 bytes for unit and option labels).

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

## Event scripts (bank `$8D`, verified by disassembly of `$8D:8185..82FB`; `tools/events.py`)

- Script starts: word table `$8D:933F` (38 events, `$8BD7` = unused); event index from the caller (`$8D:8000` intro, `$8D:8012` ending).
- Script = lines `[word line number] ([cmd byte][word arg])* 00`; line `FFFF` is the last. Each cmd calls handler `$8D:938B[cmd]` with X = arg (a parameter record in bank `$8D`). Interpreter `$8D:82BC`.
- Cmd `18` (`$8D:864B`): show message; record bytes +3..+5 = 24-bit text pointer to `$1B64`. The next messages of the scene are read on from the end of the previous one (one per cmd `1A`/`1B`), so one pointer reaches a whole chain.
- Cmd `26` (`$8D:8854`): per-faction epilogue; 24-bit pointers at record +0D + 3 * faction (`$1B2B`).
- A 6-byte header (`04xx 0000 00nn`) sits before several chains; the renderer doesn't read it (kept as not-text).

## Pointer forms (all in `tools/refs.py`; verified when every target lands on a string start, test `tests/test_extract.py`)

| Kind | Where | What |
|---|---|---|
| p16 | `data/ptr_tables.tsv` (24 tables) | 16-bit in-bank tables; phase 4 merged split tables and added words between them (several point at shared tails) |
| p16 | `refs.P16_TABLES` | ship classes 0x000CB0 (`[layout byte][text]`), vertical faction/leader/ship names 0x005E0F/0x005E59/0x006339, option labels 0x0119C6 and unit labels 0x0118B8 (`[4 bytes][text]`) |
| p16 | `refs.QUOTE_LISTS` | bank `$82` battle quotes: index 0x013098 and 0x0132C9 (odd) -> per-officer lists `[opponent id or FE][word ptr]... FF` |
| p24 | event cmd 18 / 26 records | story dialogue chains, per-faction epilogues |
| p24 | `refs.P24_TABLES` | `$80:A41B` new-flagship speeches (bank `$91`), `$8D:9243` staff-roll leader lines (4 x 40-byte fixed fields) |
| p24 + rel16 | `$BA:9925` | talk (recruit/diplomacy) texts: 8 pairs (cell map, table); table = 24-bit base + 80 word offsets (one per officer). Type 2 (`$BA:9E27`, base 0x1D9BA4 `・・・`) offsets land mid-string in type 3: a stale table, kept as tails |
| rel16 | `$8E:CEC7` | battle-start quotes: 52 offsets from `$A9:8050` (base loaded by `LDX #$8050 / LDA #$A9`, `$8E:9B98`) |
| fixed | `refs.FIXED` | base + index * stride: faction names `$8C60`/`$8C88` (10 bytes), unit labels `$AC91` (8), column labels `$8C:A3D8`, deployment prompts `$A9:8000` (40 cells) |
| fixed | `data/imm16.tsv` | code immediates `LDX/LDY/LDA #$hhll` (`tools/find_imm16.py`); `verified=y` = one routine loads consecutive strings, `n` = may be a constant. The build never rewrites them, so their strings stay in place |

Tails: refs that point inside a string (shared name tails in bank 0, the stale talk table). The build keeps them only while the host string is unchanged.

## Extraction (`tools/extract.py` -> `script/<block>.json`)

From each ref target the extractor reads on while strings decode cleanly, are non-empty and hit no other target, slot or not-text range. A block = strings stored back to back = the build's repack unit. 48 blocks, 1561 strings, 3579 refs. Coverage: every run in `data/text_scan.tsv` (`tools/text_regions.py --min 16 --gap 8`) is text, a slot or a reviewed row of `data/not_text.tsv` (`tools/gaps.py` = 0 unexplained bytes). Free-space candidates found on the way (FF fill): 0x017172-0x018000, 0x040800-0x048000, 0x05DD10-0x060000, 0x06ED28-0x070000, 0x1D3072-0x1D8000 (unverified: trap-test before use).

## Tools

`tools/font_sheet.py` (labelled font sheet), `tools/font_cells.py` (zoom chosen cells), `tools/font_match.py` (template first guess), `tools/scan_text.py` (string runs), `tools/find_ptrs.py` (16-bit tables), `tools/find_ptr24.py` (24-bit pointers, noisy), `tools/text_regions.py` (text ranges), `tools/events.py` (event scripts and their message pointers), `tools/find_refs.py` (every 16/24-bit occurrence of an address), `tools/find_imm16.py` / `tools/find_imm24.py` (code immediates), `tools/gaps.py` (coverage gaps, `--refs`), `tools/lua/romrange.lua` (per-PC ROM read ranges), `tools/lua/msgptr.lua` (dialogue window pointer log; slow: WRAM write hook).
