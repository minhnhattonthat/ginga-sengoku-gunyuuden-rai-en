-- Cycle the map sub-mode $0A91 through 0..MAX, holding each for HOLD frames, logging the PC
-- (which jump-table handler runs) and $0A91. Also log LZ decompressions to identify graphics.
--   emu.py ROM --state-in map.mss --frames N --script tools/lua/cycle_mapmode.lua --var "START=0" --var "MAX=23" --var "HOLD=20"
local mem = emu.memType.snesMemory
local function rd(a) return emu.read(a, mem) end
local function wr(a, v) emu.write(a, v, mem) end
local start = START or 0
local max = MAX or 23
local hold = HOLD or 20
local idx = start
local seen = {}
-- LZ block log
L.on_exec(0x008401, 0x008401, function()
  local d = rd(0x6D8) | rd(0x6D9) << 8
  local bank = rd(0x6DA)
  local f = ((bank & 0x7F) << 15) | (d & 0x7FFF)
  if not seen[f] then seen[f] = true; L.log(string.format("  LZ src=%06X", f)) end
end)
L.on_frame(function(f)
  if f % hold == 0 and f > 0 then
    idx = idx + 1
    if idx <= max then wr(0x0A91, idx) end
    L.log(string.format("f%d SET 0A91=%d", f, idx))
  end
  -- log PC each frame for the current mode (only when it changes)
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  if not seen[pc .. "/" .. idx] then
    seen[pc .. "/" .. idx] = true
    L.log(string.format("f%d 0A91=%d pc=%06X", f, rd(0x0A91), pc))
  end
end)
