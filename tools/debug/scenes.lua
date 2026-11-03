-- Scene list for Ginga Sengoku Gunyuuden Rai: name -> how to reach it from a cold boot (no save, no playthrough).
--
-- Loaded by tools/debug/warp.lua (this file is inlined as a --script before warp.lua, so it just sets the global
-- SCENES). Each entry is { desc, settle, steps }: the step language is documented at the top of warp.lua. Waits
-- are RAM flags (`wait = "map"` or `wait = <$0A91 mode>`), never frame counts; `sleep` is only used where nothing
-- observable changes (fades, dialogue pacing).
--
-- Verified paths (docs/re/ram.md): title -> start -> faction select -> A -> intro events -> map at ~f4400.
-- Faction-select cursor ($0E20) moves with right and confirms with A.

-- Title and faction select, common to every scene.
local function boot()
  return {
    { wait = "title", hits = 90, timeout = 2500 }, -- attract/boot init ends, title loop $8A:98xx holds
    { press = "start", frames = 6, gap = 45 },
    { wait = "faction", hits = 20, timeout = 900 }, -- faction-select loop $89:937D
  }
end

-- Leader HP words (character array $7E6E20, stride $50; leaders at indices 0, 11, 20, 35), by faction.
local LEADER = { [0] = 0x7E6E20, 0x7E7190, 0x7E7460, 0x7E7910 }
-- Event-script pointers ($1B21-23): the second command of each faction's intro (its first text box) up to the
-- third, and the same for each faction's ending (event $8D:8012). Logged with tools/lua/mode_log.lua.
local INTRO_BOX = { [0] = { 0x8D9458, 0x8D9470 }, { 0x8D9593, 0x8D95A5 }, { 0x8D976A, 0x8D9779 }, { 0x8D9875, 0x8D9884 } }
local ENDING_BOX = { [0] = { 0x8D9D79, 0x8D9D94 }, { 0x8DA0FD, 0x8DA115 }, { 0x8DA3A9, 0x8DA3C4 }, { 0x8DA865, 0x8DA874 } }
local CREDITS = 0x8D9B1E -- shared epilogue event: staff roll command (all factions)

-- Boot through the faction-select screen into the chosen faction's intro, stopping on its first text box.
local function to_intro(faction)
  local s = boot()
  for _ = 1, faction do s[#s + 1] = { press = "right", frames = 6, gap = 30 } end
  s[#s + 1] = { press = "a", frames = 6, gap = 60 }
  s[#s + 1] = { wait = "event", timeout = 900 }
  local box = INTRO_BOX[faction]
  s[#s + 1] = { mash = "a", goal = { script = box[1], hi = box[2] }, every = 40, len = 6, timeout = 3000 }
  s[#s + 1] = { text = 10, timeout = 900 }  -- the first line is on screen
  return s
end

-- Boot through the faction's intro onto the strategy map (mode 1). Mash A through the event; the wait stops
-- as soon as the map loop is running, so the run costs only the intro's real length.
local function to_map(faction)
  local s = to_intro(faction)
  s[#s + 1] = { mash = "a", goal = "map", every = 60, len = 5, timeout = 20000 }
  return s
end

-- From the map, kill the rival leaders (HP 0) and let the map loop return: the game's own victory check then
-- plays this faction's ending event; the shot is its first text box.
local function to_ending(faction)
  local s = to_map(faction)
  local zero = {}
  for f = 0, 3 do if f ~= faction then zero[#zero + 1] = LEADER[f] end end
  s[#s + 1] = { exit_map = true, zero = zero }
  local box = ENDING_BOX[faction]
  s[#s + 1] = { mash = "a", goal = { script = box[1], hi = box[2] }, every = 60, len = 6, timeout = 3000 }
  s[#s + 1] = { text = 10, timeout = 900 }
  return s
end

-- On the map: nudge the cursor onto planet 1 (its hit box corner is exactly the start position, $8B:BD67) and
-- open the planet command menu (mode 5).
local function planet_menu()
  local s = to_map(0)
  s[#s + 1] = { press = "right", frames = 2, gap = 10 }
  s[#s + 1] = { press = "down", frames = 2, gap = 10 }
  s[#s + 1] = { press = "a", frames = 8, gap = 20 }
  s[#s + 1] = { wait = 5, timeout = 600 }
  return s
end

-- Y on the map opens the system icon bar (mode 4): fleet list (mode $0B), planet list ($09), game save ($08).
-- `icon` = how many times to press right before A; nil = stop on the bar itself.
local function system_bar(icon, mode)
  local s = to_map(0)
  s[#s + 1] = { sleep = 30 }
  s[#s + 1] = { press = "y", frames = 6, gap = 50 }
  s[#s + 1] = { wait = 4, timeout = 300 }
  if icon then
    if icon > 0 then s[#s + 1] = { press = "right", times = icon, frames = 6, gap = 50 } end
    s[#s + 1] = { press = "a", frames = 8, gap = 20 }
    s[#s + 1] = { wait = mode, timeout = 600 }
  end
  return s
end

-- Planet command menu icons (mode 5): planet data ($0D), fleet sortie ($11), ship production ($12).
local function planet_icon(icon, mode)
  local s = planet_menu()
  s[#s + 1] = { sleep = 20 }
  if icon > 0 then s[#s + 1] = { press = "right", times = icon, frames = 4, gap = 50 } end
  s[#s + 1] = { press = "a", frames = 8, gap = 20 }
  s[#s + 1] = { wait = mode, timeout = 600 }
  return s
end

-- Sortie list -> A on the first commander (竜我雷) -> fleet command bar (mode 3: move / ... icons).
local function fleet_command()
  local s = planet_icon(1, 0x11)
  s[#s + 1] = { sleep = 60 }
  s[#s + 1] = { press = "a", frames = 8, gap = 20 }
  s[#s + 1] = { wait = 3, timeout = 600 }
  return s
end

-- Battle: zero byte +0 of every planet record ($7F7571 + $30 * i; guess: garrison strength) and the AI invades
-- 南京楼 within ~700 frames: invasion notice (map mode $14), then the hex battle (mode $17, bank $81). Battle
-- state: $0915 = phase (0 player move, 1 player attack, 2 enemy move, 3 enemy attack), $0737 = step in it.
local function to_invasion()
  local s = to_map(0)
  local poke = {}
  for i = 0, 22 do poke[0x7F7571 + 0x30 * i] = 0 end
  s[#s + 1] = { poke = poke }
  s[#s + 1] = { wait = 0x14, timeout = 3000 }
  return s
end

local function to_battle(phase, step)
  local s = to_invasion()
  s[#s + 1] = { mash = "a", goal = { ram = { [0x0915] = phase, [0x0737] = step, [0x0A91] = 0x17 } },
                every = 90, len = 6, timeout = 6000 }
  return s
end

-- Battle bar (Y in the player attack phase, $0737 = $10): unit data, officer data, retreat, AUTO, END, CONFIG.
local function battle_bar(icon)
  local s = to_battle(1, 2)
  s[#s + 1] = { sleep = 20 }
  s[#s + 1] = { press = "y", frames = 6, gap = 50 }
  s[#s + 1] = { wait = { ram = { [0x0737] = 0x10 } }, timeout = 300 }
  if icon then
    if icon > 0 then s[#s + 1] = { press = "right", times = icon, frames = 6, gap = 44 } end
    s[#s + 1] = { press = "a", frames = 6, gap = 60 }
  end
  return s
end

-- Lose the invasion battle fast: the six fortresses of 紅沙嶺 ($7E6B90 + $20 * i, HP u16) start at 1 HP.
-- `outcome` forces the battle result byte $0973 where $8A:842B reads it (1 = what the lost defence really gives:
-- report only; 2 = we captured enemy officers, 3 = they captured ours -> HQ screen + prisoner screens).
local function to_battle_end(goal, outcome)
  local s = to_battle(0, 0x19)  -- battle set up (fortress HP filled in); an earlier poke is overwritten
  local poke = {}
  for i = 0, 5 do poke[0x7E6B90 + 0x20 * i] = 1; poke[0x7E6B91 + 0x20 * i] = 0 end
  s[#s + 1] = { poke = poke }
  if outcome then s[#s + 1] = { force = { pc = 0x8A842B, write = { [0x0973] = outcome } } } end
  s[#s + 1] = { battle_auto = true, goal = goal, timeout = 15000 }
  return s
end

local function to_prisoner(outcome)
  local s = to_battle_end("hq", outcome)
  s[#s + 1] = { mash = "a", goal = "prisoner", every = 60, len = 6, timeout = 1500 } -- HQ waits for A ($8A:A828)
  s[#s + 1] = { wait = "prisoner", hits = 150, timeout = 1500 }  -- "この武将をどう処分されますか?" prompt
  return s
end

-- Offensive: 竜我雷's fleet sorties and is sent at planet 6 (owner 南天連合, hit box $0110,$01F0 in the $7E:E037
-- table; planet records $7F7570 + $30 * i: +0 id, +1 owner).
local function to_offensive()
  local s = fleet_command()
  s[#s + 1] = { sleep = 40 }
  s[#s + 1] = { press = "a", frames = 8, gap = 20 }
  s[#s + 1] = { wait = "move_target", timeout = 600 }
  s[#s + 1] = { cursor_to = { 0x118, 0x1F8 } }
  s[#s + 1] = { sleep = 20 }
  s[#s + 1] = { press = "a", frames = 8, gap = 30 }
  return s
end

-- The fleet arrives (~2300 frames): attack notice (mode $14), then the hex battle in the player move phase.
local function to_offense_battle()
  local s = to_offensive()
  s[#s + 1] = { wait = 0x11, timeout = 300 }          -- back on the sortie list
  s[#s + 1] = { press = "b", frames = 6, gap = 40 }
  s[#s + 1] = { wait = 5, timeout = 300 }             -- planet menu
  s[#s + 1] = { press = "b", frames = 6, gap = 40 }
  s[#s + 1] = { wait = 0x14, timeout = 5000 }
  s[#s + 1] = { mash = "a", goal = { ram = { [0x0A91] = 0x17, [0x0915] = 0 } }, every = 90, len = 6, timeout = 2000 }
  return s
end

SCENES = {
  title = {
    desc = "Title screen with PRESS START (cold boot, no input)",
    settle = 20,
    steps = {
      { wait = "title_ready", hits = 40, timeout = 2500 },
      { check = "title_ready" },
    },
  },
  attract_demo = {
    desc = "Attract demo after the title times out ($8C:D0F0)",
    settle = 300,
    steps = {
      { wait = "title_ready", hits = 40, timeout = 2500 },
      { wait = "demo", hits = 30, timeout = 6000 },
    },
  },
  faction_select = {
    desc = "Faction select (press Start on the title)",
    settle = 30,
    steps = boot(),
  },
  -- $8D:8000 runs event 4 (story prologue, 10EC1C) before every faction's intro: stop on its first page
  prologue = {
    desc = "New-game story prologue (event 4, before the faction intro)",
    settle = 400,
    steps = (function()
      local s = boot()
      s[#s + 1] = { press = "a", frames = 6, gap = 60 }
      s[#s + 1] = { wait = "event", timeout = 900 }
      s[#s + 1] = { text = 10, timeout = 1500 }
      return s
    end)(),
  },
  intro_nankyourou = {
    desc = "南京楼 (竜我雷) intro event",
    steps = to_intro(0),
  },
  intro_ren = {
    desc = "練 (羅候) intro event",
    steps = to_intro(1),
  },
  intro_nanten = {
    desc = "南天連合 (独眼竜正宗) intro event",
    steps = to_intro(2),
  },
  intro_daigojou = {
    desc = "大五丈 (骸羅) intro event",
    steps = to_intro(3),
  },
  map_nankyourou = {
    desc = "Strategy map as 南京楼 (竜我雷)",
    steps = to_map(0),
  },
  map_ren = {
    desc = "Strategy map as 練 (羅候)",
    steps = to_map(1),
  },
  map_nanten = {
    desc = "Strategy map as 南天連合 (独眼竜正宗)",
    steps = to_map(2),
  },
  map_daigojou = {
    desc = "Strategy map as 大五丈 (骸羅)",
    steps = to_map(3),
  },
  system_bar = { desc = "Map system icon bar (Y): fleet list / planet list / save", settle = 30, steps = system_bar() },
  fleet_list = { desc = "All fleets list (system bar icon 1)", settle = 40, steps = system_bar(0, 0x0B) },
  planet_list = { desc = "All planets list (system bar icon 2)", settle = 40, steps = system_bar(1, 0x09) },
  save_screen = { desc = "Game save screen (system bar icon 3)", settle = 40, steps = system_bar(2, 0x08) },
  -- the slot panel ($BA:AAF4) reads the slot state $1B28: FF = no record (1D2C9B), FE = record broken (1D2CAB)
  save_empty = { desc = "Save screen, slot forced to 'no record'", settle = 40,
                 steps = (function() local s = system_bar(); s[#s + 1] = { force = { pc = 0xBAAAF4, write = { [0x1B28] = 0xFF } } }
                   s[#s + 1] = { press = "right", times = 2, frames = 6, gap = 50 }; s[#s + 1] = { press = "a", frames = 8, gap = 20 }
                   s[#s + 1] = { wait = 0x08, timeout = 600 }; return s end)() },
  save_broken = { desc = "Save screen, slot forced to 'record broken'", settle = 40,
                  steps = (function() local s = system_bar(); s[#s + 1] = { force = { pc = 0xBAAAF4, write = { [0x1B28] = 0xFE } } }
                    s[#s + 1] = { press = "right", times = 2, frames = 6, gap = 50 }; s[#s + 1] = { press = "a", frames = 8, gap = 20 }
                    s[#s + 1] = { wait = 0x08, timeout = 600 }; return s end)() },
  planet_data = { desc = "Planet data bar (planet menu icon 1)", settle = 40, steps = planet_icon(0, 0x0D) },
  fleet_sortie = { desc = "Fleet sortie: commander list (planet menu icon 2)", settle = 40, steps = planet_icon(1, 0x11) },
  production = { desc = "Ship production screen (planet menu icon 3)", settle = 40, steps = planet_icon(2, 0x12) },
  fleet_command = { desc = "Fleet command bar for 竜我雷 (sortie -> A)", settle = 30, steps = fleet_command() },
  formation = {
    desc = "Fleet formation screen (fleet bar icon 4, bank $8C: column labels 0623D8, help 16E05B)",
    settle = 120,
    steps = (function()
      local s = fleet_command()
      s[#s + 1] = { sleep = 40 }
      s[#s + 1] = { press = "right", times = 3, frames = 6, gap = 40 }
      s[#s + 1] = { press = "a", frames = 8, gap = 20 }
      s[#s + 1] = { sleep = 120 }
      return s
    end)(),
  },
  fleet_move = {
    desc = "Picking a fleet's destination (fleet bar: move)",
    settle = 30,
    steps = (function()
      local s = fleet_command()
      s[#s + 1] = { sleep = 40 }
      s[#s + 1] = { press = "a", frames = 8, gap = 20 }
      s[#s + 1] = { wait = "move_target", timeout = 600 }
      return s
    end)(),
  },
  invasion = { desc = "Enemy fleet invades 紅沙嶺: notice on the map", settle = 60, steps = to_invasion() },
  battle_move_phase = { desc = "Hex battle, player move phase", settle = 20, steps = to_battle(0, 0x19) },
  battle_enemy_attack = { desc = "Enemy attack: side-view fleet battle animation", settle = 60, steps = to_battle(3, 8) },
  battle_attack_menu = { desc = "Player attack phase: command bar", settle = 30, steps = to_battle(1, 8) },
  battle_target = { desc = "Player attack phase: target / range overlay", settle = 30, steps = to_battle(1, 0x0A) },
  battle_bar = { desc = "Battle command bar (Y in the attack phase)", settle = 30, steps = battle_bar() },
  -- icons 1 and 2 hand over a unit cursor (it starts on one of ours): A on it opens the data window
  battle_unit_data = { desc = "Battle bar icon 1: unit data (fortress under the cursor)", settle = 60,
                       steps = (function() local s = battle_bar(0); s[#s + 1] = { press = "a", frames = 6, gap = 60 }; return s end)() },
  battle_officer_data = { desc = "Battle bar icon 2: officer data", settle = 60,
                          steps = (function() local s = battle_bar(1); s[#s + 1] = { press = "a", frames = 6, gap = 60 }; return s end)() },
  battle_config = { desc = "Battle bar icon 6: settings (ship speed / battle animation / cursor ship count)",
                    settle = 60, steps = battle_bar(5) },
  battle_result = { desc = "Battle report after 紅沙嶺 falls ($8A:8456)", settle = 20, steps = to_battle_end("battle_report") },
  battle_aftermath = { desc = "Map notice: 紅沙嶺 taken by 大五丈 (mode $19)", settle = 60, steps = to_battle_end(0x19) },
  -- Save fixture: regen.py copies this run's SRAM to work/saves/nankyourou_start.srm for the `sav` scenes below.
  save_game = {
    desc = "Game saved (save screen -> OK); its SRAM is the save fixture",
    settle = 120,
    steps = (function()
      local s = system_bar(2, 0x08)
      s[#s + 1] = { sleep = 40 }
      s[#s + 1] = { press = "a", frames = 6, gap = 20 }
      return s
    end)(),
  },
  title_load = {
    desc = "Title with a save: START ... LOAD, cursor on LOAD",
    sav = "nankyourou_start",
    settle = 30,
    steps = {
      { wait = "title_ready", hits = 40, timeout = 2500 },
      { press = "right", frames = 6, gap = 40 },
    },
  },
  load_screen = {
    desc = "Load screen (title LOAD)",
    sav = "nankyourou_start",
    settle = 60,
    steps = {
      { wait = "title_ready", hits = 40, timeout = 2500 },
      { press = "right", frames = 6, gap = 40 },
      { press = "start", frames = 6, gap = 20 },
      { wait = "load_screen", hits = 30, timeout = 600 },
    },
  },
  continue_map = {
    desc = "Map after loading the save (advisor message)",
    sav = "nankyourou_start",
    settle = 120,
    steps = {
      { wait = "title_ready", hits = 40, timeout = 2500 },
      { press = "right", frames = 6, gap = 40 },
      { press = "start", frames = 6, gap = 20 },
      { wait = "load_screen", hits = 30, timeout = 600 },
      { press = "a", frames = 6, gap = 20 },
      { wait = "advisor", hits = 90, timeout = 1500 },
    },
  },
  fleet_sent = { desc = "竜我雷's fleet ordered to planet 6 (南天連合)", settle = 60, steps = to_offensive() },
  attack_notice = {
    desc = "Map notice: 竜我雷's fleet attacks planet 6",
    settle = 60,
    steps = (function() local s = to_offense_battle(); s[#s] = nil; return s end)(),
  },
  offense_move_phase = { desc = "Offensive battle at planet 6: player move phase", settle = 200, steps = to_offense_battle() },
  hq_screen = { desc = "After-battle HQ screen (南京楼軍本陣)", settle = 60, steps = to_battle_end("hq", 2) },
  prisoner_judge = { desc = "Captured enemy officer (骸羅): recruit or execute?", settle = 20, steps = to_prisoner(2) },
  prisoner_recruit = {
    desc = "Recruit the prisoner: confirm, then his answer",
    settle = 30,
    steps = (function()
      local s = to_prisoner(2)
      s[#s + 1] = { press = "a", frames = 6, gap = 60 }   -- 登用する
      s[#s + 1] = { press = "a", frames = 6, gap = 20 }   -- はい
      s[#s + 1] = { sleep = 120 }
      return s
    end)(),
  },
  prisoner_execute = {
    desc = "Execute the prisoner: confirm, then the result",
    settle = 30,
    steps = (function()
      local s = to_prisoner(2)
      s[#s + 1] = { press = "right", frames = 6, gap = 40 } -- 処刑する
      s[#s + 1] = { press = "a", frames = 6, gap = 60 }
      s[#s + 1] = { press = "a", frames = 6, gap = 20 }   -- はい
      s[#s + 1] = { sleep = 120 }
      return s
    end)(),
  },
  prisoner_ours = { desc = "Our officer (竜我雷) captured: red prisoner screen", settle = 20, steps = to_prisoner(3) },
  game_over = {
    desc = "Game over (player leader 竜我雷 HP 0, map loop returns)",
    steps = (function()
      local s = to_map(0)
      s[#s + 1] = { exit_map = true, zero = { LEADER[0] } }
      s[#s + 1] = { wait = "gameover", timeout = 600 }
      s[#s + 1] = { sleep = 560 }           -- the text fades in over a still picture; nothing to wait on
      return s
    end)(),
  },
  ending_nankyourou = { desc = "南京楼 ending (rival leaders HP 0)", steps = to_ending(0) },
  ending_ren = { desc = "練 ending", steps = to_ending(1) },
  ending_nanten = { desc = "南天連合 ending", steps = to_ending(2) },
  ending_daigojou = { desc = "大五丈 ending", steps = to_ending(3) },
  credits = {
    desc = "Staff roll after the 南京楼 ending (shared epilogue event)",
    steps = (function()
      local s = to_ending(0)
      s[#s + 1] = { mash = "a", goal = { script = CREDITS, hi = CREDITS + 1 }, every = 60, len = 6, timeout = 12000 }
      s[#s + 1] = { sleep = 640 }           -- first staff card fades in (drawn as graphics, no text hook)
      return s
    end)(),
  },
  -- map mode $1B ($8B:8565) fades out and plays the new-flagship speech ($8B:D064) for ship type $098C
  -- ($8B:D3AB: 08 = 新金剛 -> speech 3, 08F60B)
  flagship_speech = {
    desc = "New-flagship speech (map mode $1B forced, ship type 08)",
    settle = 600,
    steps = (function()
      local s = to_map(0)
      s[#s + 1] = { poke = { [0x098C] = 0x08, [0x06E2] = 1, [0x0A91] = 0x1B } }
      s[#s + 1] = { wait = { ram = { [0x0A91] = 0x1B } }, timeout = 60 }
      s[#s + 1] = { sleep = 200 }
      return s
    end)(),
  },
  planet_menu = {
    desc = "Planet command menu (3 icons: planet data / fleet sortie / production)",
    settle = 30,
    steps = planet_menu(),
  },
}
