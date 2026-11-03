-- Debug-tool warp driver: reach a named scene from a cold boot.
--
--   python -X utf8 "$(python tools/skill.py)/scripts/emu.py" "rom/Ginga Sengoku Gunyuuden Rai (Japan).sfc" \
--     --out work/qa/warp/my_scene --script tools/debug/scenes.lua --script tools/debug/warp.lua \
--     --var "SCENE='planet_production'" --frames 12000 --state-out work/states/planet_production.mss --sheet
--
-- scenes.lua must be loaded first (it defines SCENES = { name -> scene }). A scene is a list of `steps` played
-- one at a time. Each step waits on a RAM flag or holds an input, never on a guess at the frame number:
--
--   { wait  = "map" }            wait for a named predicate (see PREDS below); timeout fails the run
--   { wait  = "title", hits = 90 }  also require 90 frames to have matched (a one-off boot page hit is not a screen)
--   { wait  = "title", stable = 30 }  or require them consecutively
--   { wait  = 5 }                wait for strategy-map sub-mode $0A91 = 5 (the mode jump table at $8B8046)
--   { wait  = { script = 0x8D9458, hi = 0x8D9470 } }  wait for the event-script pointer $1B21-23 in [script, hi)
--   { wait  = { ram = { [0x0915] = 1, [0x0737] = 8 } } }  wait until every listed byte has that value
--   { force = { pc = 0x8A842B, write = { [0x0973] = 2 } } }  write those bytes whenever the CPU reaches pc
--   { cursor_to = { 0x118, 0x1F8 } }  steer the map cursor to that world position (planet hit boxes: $7E:E037)
--   { battle_auto = true, goal = 0x0F }  play the hex battle (AUTO each player attack phase) until the goal
--   { text  = 12 }             wait until the dialogue renderer has drawn 12 more glyphs (text is on screen)
--   { exit_map = true, zero = { 0x7E7190 } }  zero these u16s (leader HP) and make the map loop return, so the
--                                game runs its own game-over / victory check (see exit_map below)
--   { press = "right", frames = 2 }   hold buttons `frames` frames, then release for `gap` (default 10)
--   { press = "a", times = 10, frames = 6, gap = 40 }   repeat that press (advance dialogue boxes)
--   { mash  = "a", goal = "map", every = 90, len = 6, timeout = 8000 }
--                                press `mash` every `every` frames until the predicate holds
--   { poke  = { [0x7F7571] = 0 } }    one-shot WRAM writes
--   { hold  = { [0x091B] = 3 } }      write these every frame from here on
--   { release = true }           stop all per-frame holds
--   { sleep = 60 }               wait N frames (only where nothing observable changes, e.g. fades)
--   { check = "map" }            assert a predicate now (short timeout), fail if it never holds
--   { shot  = "planet_menu" }    screenshot into the run's --out directory
--   { log   = "text" }           log a line
--
-- When the steps run out the driver waits `settle` frames (scene field, default 40), saves final.png, logs the
-- RAM fingerprint and saves --state-out. A failed wait/check exits 2 with the scene and step in the message, so
-- tools/debug/regen.py can gate on the exit code.
--
-- TRACE=1 logs every change of $0A91 (sub-mode), PC page and $073D (faction), for building new scenes.

local scene = SCENES and SCENES[SCENE or ""]
if not scene then
  local names = {}
  for k in pairs(SCENES or {}) do names[#names + 1] = k end
  table.sort(names)
  L.fail("unknown scene '" .. tostring(SCENE) .. "' (known: " .. table.concat(names, ", ") .. ")")
  return
end

local mem = emu.memType.snesMemory
local function rd(a) return emu.read(a, mem) end
local function wr(a, v) emu.write(a, v, mem) end
local function pc()
  local s = emu.getState()
  return (s["cpu.k"] << 16) | s["cpu.pc"]
end

-- Named predicates. "map" also checks the bank: every map sub-mode runs from $8B8046 and the bank stays $8B
-- until a menu subsystem ($BA, production, battle) takes over.
local PREDS = {
  title   = function() return (pc() & 0xFFFF00) == 0x8A9800 end,  -- $8A:98xx idle loop
  -- the title's input wait ($8A:98E1-$98FF): logo and PRESS START are drawn, so this is the shot to keep
  title_ready = function()
    local o = pc() & 0xFFFF
    return (pc() & 0xFF0000) == 0x8A0000 and o >= 0x98E1 and o <= 0x98FF
  end,
  faction = function() return (pc() & 0xFFFF00) == 0x899300 end,  -- $89:937D faction select
  event   = function() return (pc() & 0xFF0000) == 0x8D0000 end,  -- $8D event interpreter
  map     = function() return (pc() & 0xFF0000) == 0x8B0000 and rd(0x0A91) == 1 end,
  -- attract demo: the title returns 3 after its timeout ($0E32) and the main loop calls $8C:D0F0
  demo = function() return (pc() & 0x7F0000) == 0x0C0000 end,
  -- after-battle HQ screen ($8A:A79E, "<army> 本陣"), its wait loop $8A:A7F8-$A7FD
  hq = function() return (pc() & 0x7FFFF0) == 0x0AA7F0 end,
  -- prisoner screens (recruit / execute a captured officer) run in bank $8E (NMI wait $8E:F831-F836)
  prisoner = function() return (pc() & 0x7F0000) == 0x0E0000 end,
  -- advisor message box on the map (after loading a save), its wait loop $8B:D9A5
  advisor = function() return (pc() & 0xFFFF00) == 0x8BD900 end,
  -- load screen (title LOAD -> $BA:A7F5), its confirm loop $BA:A81A
  load_screen = function() return (pc() & 0xFFFF00) == 0xBAA800 end,
  -- battle report ($8A:8456) fully drawn: its wait-for-A loop $8A:8558-$856B
  battle_report = function()
    local p = pc()
    return (p & 0x7F0000) == 0x0A0000 and (p & 0xFFFF) >= 0x8558 and (p & 0xFFFF) <= 0x856B
  end,
  -- map mode 1 with $0A94 = 1: picking a fleet's destination (after the fleet bar's move icon)
  move_target = function() return rd(0x0A91) == 1 and rd(0x0A94) == 1 end,
}
-- Event-script pointer $1B21-$1B23 (bank $8D interpreter); transiently 0 between commands.
local function script_ptr() return (rd(0x1B23) << 16) | (rd(0x1B22) << 8) | rd(0x1B21) end
PREDS.gameover = function()  -- game-over screen $89:A417 (player leader HP 0 when the map loop returns)
  local p = pc()
  return (p & 0xFF0000) == 0x890000 and (p & 0xFFFF) >= 0xA417 and (p & 0xFFFF) < 0xAA00
end
-- Numeric wait/check = strategy-map sub-mode $0A91. The mode table is at $8B8046 (docs/re/ram.md).
-- Table {script = lo, hi = hi} = event-script pointer in [lo, hi) (hi defaults to lo + $100).
local function pred(p)
  if type(p) == "number" then return function() return rd(0x0A91) == p end end
  if type(p) == "table" and p.ram then  -- { ram = { [addr] = value, ... } }: every byte matches
    return function()
      for a, v in pairs(p.ram) do if rd(a) ~= v then return false end end
      return true
    end
  end
  if type(p) == "table" then
    local lo, hi = p.script, p.hi or (p.script + 0x100)
    return function() local s = script_ptr(); return s >= lo and s < hi end
  end
  local fn = PREDS[p]
  if not fn then L.fail("unknown predicate '" .. tostring(p) .. "'") end
  return fn
end

-- exit_map: the map loop $8B:8000 returns only through $8B:8597 (after a battle that reports a result), and the
-- main loop $80:808B then runs the game-over check ($8A:946D, player leader HP) and the victory check ($8A:9494,
-- the three rival leaders' HP) -> ending event $8D:8012 + credits. The step points the mode-1 entry of the mode
-- jump table (ROM $8B:8048, file 0x058048) at $8B:8597 in the emulator's copy of the ROM for one dispatch, then
-- puts the original bytes back. The ROM file is never touched.
local prg = emu.memType.snesPrgRom
local MODE1_ENTRY = 0x058048
local map_exited = false
L.on_exec(0x8B8597, 0x8B8597, function() map_exited = true end)
-- Glyphs drawn by the dialogue window renderer ($BA:92CD reads a code; $BA:93FB is the draw-a-character path).
local glyphs = 0
L.on_exec(0xBA93FB, 0xBA93FB, function() glyphs = glyphs + 1 end)

local function buttons(spec)
  local b = {}
  if spec and spec ~= "-" then for n in spec:gmatch("[^+]+") do b[n] = true end end
  return b
end

local steps = scene.steps or {}
local i, t, sub = 1, 0, 0
local input = {}
local holds = {}
local frame = 0
local finished = false
local trace = (TRACE or 0) ~= 0
local lastmode, lastpage = -1, -1

local function status()
  return string.format("f%d step%d mode=%02X faction=%d pc=%06X", frame, i, rd(0x0A91), rd(0x073D), pc())
end

local function advance()
  i, t, sub, input = i + 1, 0, 0, {}
end

local function finish()
  finished = true
  L.shot("final.png")
  L.log(string.format("SCENE %s reached %s", SCENE, status()))
  if STATE_OUT then L.save_state(STATE_OUT, function() L.finish(0) end) else L.finish(0) end
end

L.on_frame(function(f)
  frame = f
  if finished then return end
  -- per-frame holds (menu item counts the game leaves at 0, cursor pins, ...)
  for a, v in pairs(holds) do wr(a, v) end

  if trace then
    local mode, page = rd(0x0A91), pc() >> 16
    if mode ~= lastmode or page ~= lastpage then
      L.log(string.format("f%d mode=%02X page=%04X faction=%d", f, mode, page, rd(0x073D)))
      lastmode, lastpage = mode, page
    end
  end

  local st = steps[i]
  t = t + 1
  if not st then
    -- Steps are done: let the screen settle, then shoot and save.
    if t > (scene.settle or 40) then finish() end
    return
  end

  if st.poke then
    local n = 0
    for a, v in pairs(st.poke) do wr(a, v); n = n + 1 end
    L.log(string.format("f%d poke step %d: %d writes", f, i, n))
    advance()
  elseif st.hold then
    for a, v in pairs(st.hold) do holds[a] = v end
    L.log(string.format("f%d hold step %d", f, i))
    advance()
  elseif st.release then
    holds = {}
    L.log(string.format("f%d release step %d", f, i))
    advance()
  elseif st.force then
    -- From now on, write these bytes each time the CPU reaches st.force.pc (just before the game reads them).
    local f_pc, writes = st.force.pc, st.force.write
    L.on_exec(f_pc, f_pc, function() for a, v in pairs(writes) do wr(a, v) end end)
    L.log(string.format("f%d force at %06X", f, f_pc))
    advance()
  elseif st.cursor_to then
    -- Map cursor world position = screen $0A95/$0A96 + scroll $0A98/$0A9A (16-bit); steer with the d-pad.
    local cx = rd(0x0A95) + (rd(0x0A98) | (rd(0x0A99) << 8))
    local cy = rd(0x0A96) + (rd(0x0A9A) | (rd(0x0A9B) << 8))
    local tx, ty = st.cursor_to[1], st.cursor_to[2]
    local b = {}
    if cx < tx - 2 then b.right = true elseif cx > tx + 2 then b.left = true end
    if cy < ty - 2 then b.down = true elseif cy > ty + 2 then b.up = true end
    if next(b) == nil then
      input = {}
      advance()
    elseif t > (st.timeout or 1200) then
      L.fail(string.format("SCENE %s: cursor stuck at %X,%X (target %X,%X)", SCENE, cx, cy, tx, ty))
    else
      input = b
    end
  elseif st.battle_auto then
    -- Player attack-phase wait ($0A91 = $17, $0915 = 1, $0737 = 2): Y, right x3, A = AUTO on the battle bar.
    -- Player move-phase wait ($0915 = 0, $0737 = 2): Y, right x4, A = END (end the move phase). Otherwise A every
    -- 90 frames (dialogue, reports). Stops when `goal` holds.
    local SEQ = {
      [1] = { "y", "-", "right", "-", "right", "-", "right", "-", "a", "-" },
      [0] = { "y", "-", "right", "-", "right", "-", "right", "-", "right", "-", "a", "-" },
    }
    local seq = SEQ[st.phase or 1] or SEQ[1]
    if pred(st.goal)() then
      advance()
    elseif t > (st.timeout or 20000) then
      L.fail(string.format("SCENE %s: battle_auto until '%s' timed out (%s)", SCENE, tostring(st.goal), status()))
    elseif (st.qi or 0) > 0 then
      local k = seq[st.qi]
      input = (k ~= "-") and buttons(k) or {}
      st.qt = st.qt + 1
      if st.qt >= (k == "-" and 40 or 6) then st.qi, st.qt = st.qi + 1, 0 end
      if st.qi > #seq then st.qi = 0 end
    elseif rd(0x0A91) == 0x17 and rd(0x0915) <= 1 and rd(0x0737) == 2 then
      st.phase, st.qi, st.qt = rd(0x0915), 1, 0
    else
      input = ((t - 1) % 90 < 6) and buttons("a") or {}
    end
  elseif st.text then
    if t == 1 then st.base = glyphs end
    if glyphs - st.base >= st.text then
      advance()
    elseif t > (st.timeout or 1200) then
      L.fail(string.format("SCENE %s: fewer than %d glyphs drawn (%s)", SCENE, st.text, status()))
    end
  elseif st.exit_map then
    if sub == 0 then
      if rd(0x0A91) == 1 and (pc() & 0xFF0000) == 0x8B0000 then
        for _, a in ipairs(st.zero or {}) do wr(a, 0); wr(a + 1, 0) end
        st.orig = { emu.read(MODE1_ENTRY, prg), emu.read(MODE1_ENTRY + 1, prg) }
        emu.write(MODE1_ENTRY, 0x97, prg)
        emu.write(MODE1_ENTRY + 1, 0x85, prg)
        map_exited, sub = false, 1
        L.log(string.format("f%d exit_map: %d HP zeroed, mode-1 entry -> $8B8597", f, #(st.zero or {})))
      elseif t > (st.timeout or 600) then
        L.fail(string.format("SCENE %s: exit_map never saw map mode 1 (%s)", SCENE, status()))
      end
    elseif map_exited then
      emu.write(MODE1_ENTRY, st.orig[1], prg)
      emu.write(MODE1_ENTRY + 1, st.orig[2], prg)
      advance()
    elseif t > (st.timeout or 600) then
      L.fail(string.format("SCENE %s: map loop did not exit (%s)", SCENE, status()))
    end
  elseif st.shot then
    L.shot(st.shot .. ".png")
    L.log(string.format("f%d shot %s", f, st.shot))
    advance()
  elseif st.log then
    L.log(string.format("f%d %s", f, st.log))
    advance()
  elseif st.press then
    local len, gap = st.frames or 6, st.gap or 10
    local times = st.times or 1
    local cycle = len + gap
    if ((t - 1) % cycle) < len then input = buttons(st.press) else input = {} end
    if t >= cycle * times then advance() end
  elseif st.mash then
    local every, len = st.every or 60, st.len or 6
    if st.goal and pred(st.goal)() then
      advance()
    elseif t > (st.timeout or 8000) then
      L.fail(string.format("SCENE %s: mash until '%s' timed out (%s)", SCENE, tostring(st.goal), status()))
    else
      input = ((t - 1) % every < len) and buttons(st.mash) or {}
    end
  elseif st.wait or st.check then
    local p = st.wait or st.check
    local need = st.hits or st.stable or 1
    if pred(p)() then
      sub = (sub or 0) + 1
    elseif st.stable then
      sub = 0
    end
    if sub >= need then
      advance()
    elseif t > (st.timeout or (st.check and 600 or 4000)) then
      L.fail(string.format("SCENE %s: %s '%s' timed out (%s)", SCENE,
        st.check and "check" or "wait", tostring(p), status()))
    end
  elseif st.sleep then
    if t >= st.sleep then advance() end
  else
    L.fail(string.format("SCENE %s: step %d has no action", SCENE, i))
  end
end)

-- Own input injection: the driver's queue stays empty (no L.press calls), so this is the only writer.
emu.addEventCallback(L.safe(function() emu.setInput(input, 0) end), emu.eventType.inputPolled)
