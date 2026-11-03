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

SCENES = {
  title = {
    desc = "Title screen with PRESS START (cold boot, no input)",
    settle = 20,
    steps = {
      { wait = "title_ready", hits = 40, timeout = 2500 },
      { check = "title_ready" },
    },
  },
  faction_select = {
    desc = "Faction select (press Start on the title)",
    settle = 30,
    steps = boot(),
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
  planet_data = { desc = "Planet data bar (planet menu icon 1)", settle = 40, steps = planet_icon(0, 0x0D) },
  fleet_sortie = { desc = "Fleet sortie: commander list (planet menu icon 2)", settle = 40, steps = planet_icon(1, 0x11) },
  production = { desc = "Ship production screen (planet menu icon 3)", settle = 40, steps = planet_icon(2, 0x12) },
  fleet_command = { desc = "Fleet command bar for 竜我雷 (sortie -> A)", settle = 30, steps = fleet_command() },
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
  planet_menu = {
    desc = "Planet command menu (3 icons: planet data / fleet sortie / production)",
    settle = 30,
    steps = planet_menu(),
  },
}
