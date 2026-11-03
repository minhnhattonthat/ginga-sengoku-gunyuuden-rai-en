# Code patches (hook list)

Every code change the English build makes. Source of truth: `tools/patches.py` (hand-assembled bytes, original
bytes checked before writing; `tests/test_patches.py` disassembles them). Free space used: `$BC:8000-` (file
0x1E0000-, all FF).

| Where | Was | Now | Why | State |
|---|---|---|---|---|
| `$BC:8000` | FF | label glyph fetch: `LDA [$00],y`, `FFFF` -> blank cell `3E` and `DEC $00` x2 (holds the string pointer), `ASL` x2, `RTL` | packed layout below reads past `{end}` for short strings | verified: production screen, `work/qa/stress/lbl2` |
| `$8E:CBCF`, `$8E:F4F6`, `$BA:8DF7` | `LDA [$00],y / ASL / ASL` | `JSL $BC8000` | hook into each family's glyph fetch | verified (same) |
| `$8E:C9C9..C9D2`, `$8E:F2F0..F2F9`, `$BA:8BF0..8BF9` | per-length layout ptrs (1-4 cells: spread, 16-px pitch) | the 5-cell routine (`$8E:CB1C`, `$8E:F443`, `$BA:8D44`): 12-px packed, left-aligned | digraph names in label boxes read "aa bb cc" otherwise | verified (same) |
| 5-cell routine +13/+2E/+39/+3E/+52/+62 (each family) | cells 1-3 at x = 0, 12, 24 (s0 store tile 0, s4 OR tile 1, s0 store tile 3) | x = 4, 16, 28 (s4 store tile 0, s0 store tile 2, s4 OR tile 3); cells 4-5 stay at the original 40, 52 | even 12-px pitch ("Nankin ro" gap gone) and a 4-px left margin: the list cursor box covered the first letter | verified: fleet_sortie, fleet_list, planet_list, production, planet_data |
| `$8E:C9A7`, `$8E:F2D1` | `CPY #$0004` (skip strings < 2 cells) | `CPY #$0002` | 1-cell English strings (2 letters) would not draw | guess (no 1-cell string tested yet) |

| `$BC:8011` | FF | name copy: up to 5 cells of the officer name to `$0E00` verbatim, `FFFF`-terminated | fleet-command name tag | verified: `work/qa/stress/fcname` |
| `$8B:C8ED` | `LDA $000004,x / CMP #$FFFF` (2- vs 3-cell name, adds `{FFFE}` spacing) | `JSL $BC8011 / BRA $C938` | the game copied only 3 cells | verified (same); the tag box shows 4 cells (8 letters): widen in phase 7 |
| `$BC:8030` | FF | speaker tag: A = officer; word at `$BC:9000 + 2A` (bank `$BC` pointer, set by `build.speech_tags`) or the name from `$00:90DC`; draw at `$8200` via `$81:E962` | names over 3 cells ran into the 『 cell and the text | verified: continue_map (+ `tools/lua/speaker.lua` forcing officer 2) |
| `$81:ECEA` (battle quotes), `$8B:DA6E` (advisor) | `ASL / TAX / LDA $0090DC,x` | `JSL $BC8030 / BRA` past the name draw | speech boxes | verified: offense_move_phase, continue_map |
| `$81:ED13`, `$81:ED36`, `$8B:DA99`, `$8B:DAB9` | draw 『 / 』 | NOP | the name now uses cells 0-3; English needs no 『』 beside a speaker label | verified (same) |
| `$81:DCDB..DD27` | 第 n 要塞 built in `$0E00` | `Fort n`: Y starts at 4, "Fo"/"rt" immediates from `build.CODE_LABELS`, blank cell, `CMP #$04` for the 1-digit layout | fortress header in battle unit data | verified: battle_unit_data |

Label-box family: caller sets `$1AF0` = 24-bit string pointer, `$1AF4` = tile buffer; `$8E:C96D` counts cells
(max 5, stops at `FFFF`) and picks the routine from the table by 3 * length; the routine draws each glyph via
fetch (`$8E:CBCA`: font pointer `$95:8000 + c * 24` at `$1A00`) + shift (`CBEA` 0, `CBFE` 2 px, `CC1B` 4 px) +
store (`CC40` store, `CC59` OR) into 8-px columns of the buffer. Callers of `$8E:C96D`: `$8E:84FE/8551/857C/8597`.
