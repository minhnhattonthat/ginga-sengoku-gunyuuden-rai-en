-- Log the map cursor/scroll variables every frame they change, with the PC.
--   emu.py ROM --state-in work/states/map_nankyourou.mss --route-str "..." --script tools/lua/mapvars.lua
local mem = emu.memType.snesMemory
local function rd(a) return emu.read(a, mem) end
local W = { 0x0A91, 0x0A94, 0x0A95, 0x0A96, 0x0A98, 0x0A99, 0x0A9A, 0x0A9B, 0x0E00, 0x0E01, 0x0E10, 0x0917, 0x0918 }
local last = {}
L.on_frame(function(f)
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  local parts, changed = {}, false
  for _, a in ipairs(W) do
    local v = rd(a)
    if last[a] ~= v then changed = true end
    last[a] = v
    parts[#parts + 1] = string.format("%04X=%02X", a, v)
  end
  if changed then L.log(string.format("f%d pc=%06X %s", f, pc, table.concat(parts, " "))) end
end)
