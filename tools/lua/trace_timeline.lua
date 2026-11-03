-- Full-boot timeline: log frame, PC bank, and key state bytes every EVERY frames.
--   emu.py ROM --frames 13000 --mash 90 --script tools/lua/trace_timeline.lua --var EVERY=60
local mem = emu.memType.snesMemory
local function rd(a) return emu.read(a, mem) end
local every = EVERY or 60
local last = {}
local function snap()
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  local vals = { 0x073D, 0x0A91, 0x0791, 0x0ABF, 0x0AC0, 0x0E30 }
  local line = string.format("f%d pc=%06X", L.frame, pc)
  for _, a in ipairs(vals) do line = line .. string.format(" %04X=%02X", a, rd(a)) end
  return line
end
L.on_frame(function(f)
  if f % every == 0 then L.log(snap()) end
end)
-- Also log on the $8B8000 (map loop) entry and $8A980E (title) entry
L.on_exec(0x8B8000, 0x8B8000, function() L.log("ENTER 8B8000 (map) " .. snap()) end)
L.on_exec(0x8A980E, 0x8A980E, function() L.log("ENTER 8A980E (title) " .. snap()) end)
