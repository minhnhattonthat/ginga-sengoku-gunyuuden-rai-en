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
| `$0791` | a valid save exists | 0 = no (title: START only), 1 = yes (START…LOAD) | verified: set by `$8A:9F75` from SRAM; picks the title return table `$00D88D` |
| `$0E32` | title timed out | 1 -> title returns 3 -> attract demo `$8C:D0F0` | verified (`$8A:9901`) |
| `$1B21-23` | event-script pointer (bank `$8D` interpreter) | 0 between commands | verified: per-faction intro/ending starts logged, see `tools/debug/scenes.lua` |
| `$0A94` | map: choosing a fleet destination | 1 after the fleet bar's move icon | verified (`$8B:873E`) |
| `$0A95/$0A96`, `$0A98/$0A9A` | map cursor screen x/y (bytes), scroll x/y (words) | world = screen + scroll | verified (`$8B:8838`) |
| `$0915` / `$0737` | battle phase / step | phase 0 player move, 1 player attack, 2 enemy move, 3 enemy attack; step 2 = waiting for the player, `$10`/`$0F` = battle bar (attack/move) | verified: `$81:A133` dispatch |
| `$0973` | battle outcome | 1 report only; 2 we captured officers; 3 ours captured (both -> HQ `$8A:A79E` + prisoner screens, bank `$8E`) | verified: `$8A:842B` |
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

Record `i` (0–22) at `$7F7570 + $30 × i` (verified by dump, `tools/debug` phase 2): `+0` planet id (= i),
`+1` owner faction (0–3), `+2` 技術力 (u16), `+4` 工業力 (u16), `+8` 要塞 (fortress count). Poking every owner
to 0 makes the AI fleets parked next to "their" planets invade at once (the `invasion` warp).
Order: 南京楼 益州都 南蛮王都 南帝閣 座王都 洛火閣 虎卓関 流北平 斉王都 武王都 遼陽 鴨緑江 魔天嶺 旅順 鳳凰城
艾塔堡子 言堡子 大堡屯 弓張嶺 紅沙嶺 孫家塞 藍家屯 延高城. Map hit boxes: `$7E:E037`, 23 × {x, y} words
(world coordinates, same order).

Note: the character array and battle data live in bank `$7E` above `$2000`; write them as `$7E6E20`, never
`$6E20` (bank `$00` mirrors only `$0000-$1FFF`; the first game-over probe failed that way).

## Battle data

- Fortress (verified): `$7E6B90` 耐久 (u16), `$7E6BAE` max; +0x20 per fortress (6 at 紅沙嶺, 8 at 洛火閣). HP 1
  at battle start makes the defence fall in ~8000 frames.
- Fleet battle (wiki; **not** confirmed: setting every non-zero unit HP to 1 did not end a battle):
  `$7E5E70` flagship 耐久 (u16), `$7E5E8E` max; 部隊 1–9 at `+0x20`; next fleet `+0x150`.
- Melee (白兵戦): `$7E1B68` attacker HP (u16), `$7E1C08` defender HP (u16).
- Battle phase (wiki, stayed 0 here): `$7E5E68`, `$7E5E7F`, `$7E5E82`. Use `$0915`/`$0737` instead.

## Joypad (verified: `$008356` reads `$4218`/`$4219`)

`$0022`/`$0023` held, `$0024`/`$0025` newly pressed. `$0022`/`$0024` = JOY1 low byte (A=80 X=40 L=20 R=10),
`$0023`/`$0025` = high byte (B=80 Y=40 select=20 start=10 up=08 down=04 left=02 right=01). Start in an event
(`$0023` bit 4, `$8D:8211`) skips the intro to `$8D:940D`.

## Main loop and map controls (verified by disassembly)

`$80:8052`: title `$8A980E` (returns 0 new game, 1 load `$BAA7F5`, 3 demo `$8CD0F0`) → faction select →
intro `$8D8000` → map `$008319` (`JSL $8B8000`). The map loop returns only via `$8B:8597` (after a battle with a
result); then `$8A:946D` (player leader HP 0 → game over `$89:A417`) and `$8A:9494` (all three rival leaders HP 0
→ ending `$8D:8012` = faction ending + shared epilogue/staff roll). The `exit_map` warp step forces that return.

Map mode 1 (`$8B:873E`): A = object under the cursor (fleets → mode 2/3, else planet → mode 5), Y = system bar
(mode 4: fleet list `$0B`, planet list `$09`, save `$08`), L/R = jump between own planets, Start = pause.
Planet menu (mode 5): planet data `$0D`, sortie `$11`, production `$12`. Sortie → commander → fleet bar (mode 3) →
move → destination (`$0A94` = 1). Arrival: notice mode `$14`, battle mode `$17` (bank `$81`), report `$8A:8456`,
then `$0F` / `$19` (post-battle notice).

Battle bar (Y when `$0737` = 2): attack phase = unit data, officer data, retreat, AUTO, END, CONFIG; move phase =
unit data, officer data, reinforcements?, retreat?, END, CONFIG. A on a fleet in the move phase: move / range /
formation turn.

## Warp recipes

`tools/debug/scenes.lua` is the list (each entry documents its route); `python -X utf8 tools/debug/regen.py`
replays all of them from a cold boot. Saves: every run boots with `work/saves/blank.srm` (zeros = no save) unless
the scene names a fixture; `save_game` saves in game and its SRAM becomes `work/saves/nankyourou_start.srm`.
Never let Mesen keep a save in `tools/mesen/Saves/`: it would turn every cold boot's title into START…LOAD.
