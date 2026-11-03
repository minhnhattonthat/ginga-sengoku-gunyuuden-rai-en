# RAM map (phase 2)

Game-state addresses found during the phase-2 debug-tool work. Addresses are WRAM `$7E:xxxx` (the `$00:xxxx`
mirror most code uses reads the same bytes). Provenance is marked; a value confirmed against the game's own
code (disassembly or a breakpoint/transition observed) is **verified**, otherwise **guess**.

## Top-level flow (verified by PC tracing `tools/lua/trace_timeline.lua`)

Cold boot → attract/intro (bank `$84`) → **title** (`$8A980E`, ~frame 323–634) → **faction select**
(`$89937D`, bank `$89`, ~frame 634+) → **intro event** (bank `$8D` event interpreter, ~frame 1000–4449) →
**strategy map** (`$8B8000`, bank `$8B`, entered ~frame 4449 with mash-A interval 90). The map loop is entered
from `$80:0319` (new game) or `$80:0340` (returning, `$008340`), which call `JSL $8B8000` and never return.

The boot is a fixed sequence; there is no single "mode" byte. The per-screen state lives in the variables below.

## Key variables

| Addr | Meaning | Values | Provenance |
|---|---|---|---|
| `$073D` | player faction | 0=南京楼 (竜我雷), 1=練 (羅候), 2=南天連合 (独眼竜正宗), 3=大五丈 (骸羅) | verified: `$8A9494` reads it and checks the three *other* leaders' HP to decide game-over |
| `$0A91` | strategy-map sub-mode | 0–23, jump table at `$8B8046`; 1 = main map | verified: `$8B803E` dispatches on it |
| `$0791` | map entry flag | 0 = first entry, 1 = returning | guess: `$8B8008` compares to 1 |
| `$0E20` | faction-select cursor | 0–3 (left/right moves, A confirms) | verified: `$89966F` reads it (`AND #$03`), cursor moved 0→1 on a right press |
| `$0ABF`/`$0AC0` | set to `01`/`FF` just before `JSL $8B8000` | | verified: observed on map entry |
| `$073C` | ? (adjacent to faction) | | |

## Character data (verified against スーファミチート wiki, values re-read from the map state)

Array base `$7E6E20`, stride `$50`, ~80 entries. The four leaders are at indices 0, 11, 20, 35:

| | 竜我雷 | 羅候 | 独眼竜正宗 | 骸羅 | field (offset) |
|---|---|---|---|---|---|
| addr | `$6E20` | `$7190` | `$7460` | `$7910` | |
| +0 | | | | | HP (u16 LE, max 0x1000) |
| +2 | | | | | max HP (u16) |
| +4 | 00 | 0B | 14 | 23 | 艦隊指揮 (fleet command id) |
| +5 | 80 | 01 | 02 | 03 | 状態; low 2 bits = faction (00/01/10/11) |
| +6 | | | | | Lv |
| +7 | | | | | EXP (FF = level every fight) |
| +8 | | | | | 攻撃 (u16) |
| +A | | | | | 防御 |
| +B | | | | | 回避 |
| +C | | | | | 指揮 |
| +D | | | | | 忠誠 |
| +E | | | | | 部隊数 display |
| +F | | | | | formation |

Writing `80h` to every character's 状態 (+5) stops enemy attacks (wiki comment).

## Planet data (verified: 南京楼 values match wiki)

Base `$7F7571` for 南京楼 (planet id 01); each planet is `+0x30` apart (planet address = base + 0x30 × (id − 1)).
23 planets, ids 01–22: 益州都 02 南蛮王都 03 南帝閣 04 座王都 05 洛火閣 06 虎卓関 07 流北平 08 斉王都
09 武王都 10 遼陽 11 鴨緑江 12 魔天嶺 13 旅順 14 鳳凰城 15 艾塔堡子 16 言堡子 17 大堡屯 18 弓張嶺
19 紅沙嶺 20 孫家塞 21 藍家屯 22 延高城. Fields (relative to base): `+1` 技術力 (u16), `+3` 工業力 (u16),
`+7` 要塞 (fortress count). (Wiki: `-01h` 陣営 owner.)

## Battle data (from wiki, not yet re-verified here)

- Fleet battle: `$7E5E70` flagship 耐久 (u16), `$7E5E8E` max; 部隊 1–9 at `+0x20`; next fleet `+0x150`
  (mixed sides). Use only on the battle map.
- Fortress: `$7E6B90` 耐久 (u16), `$7E6BAE` max; +0x20 per fortress, up to 20.
- Melee (白兵戦): `$7E1B68` attacker HP (u16), `$7E1C08` defender HP (u16).
- Battle phase: `$7E5E68 = 0x0A`, `$7E5E7F = 0x0A` (force-end move phase), `$7E5E82 = 0x00` (attack phase).

## Joypad (verified: `$008356` reads `$4218`, low byte = `$0023`, high = `$0024`)

SNES JOY1 low byte bits: B=80 Y=40 select=20 start=10 up=08 down=04 left=02 right=01; high byte A=01 X=02 L=04 R=08.
The faction-select handler reads `$0023` bit 1 (left) / bit 0 (right) for the cursor and `$0024` bit 7 for confirm.

## Warp recipes (see `tools/debug/scenes.lua`)

- title: no input.
- faction_select: press start on the title.
- intro_<faction>: title → start → (right × faction) → A → mash A through the intro.
- map: title → start → A (default 南京楼) → mash A ~3900 frames, or any faction by moving the cursor first.
- Map sub-screens: set `$0A91` (sub-modes 8+ switch to the bank `$BA` menu subsystem).
