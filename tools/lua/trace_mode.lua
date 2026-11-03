-- Trace top-level mode transitions over a full boot: log the dispatch value A at $808062 and a
-- candidate set of state bytes whenever any of them changes.
--   emu.py ROM --frames 12000 --mash 90 --script tools/lua/trace_mode.lua ...
local mem = emu.memType.snesMemory
local function rd(a) return emu.read(a, mem) end
local watched = { 0x073D, 0x0E00, 0x0E05, 0x0E30, 0x0E20, 0x08DD, 0x073C }
local last = {}
for _, a in ipairs(watched) do last[a] = -1 end
local lastA = -1
L.on_exec(0x808062, 0x808062, function()
  local s = emu.getState()
  local A = s["cpu.a"] & 0xFF
  local changed = (A ~= lastA)
  local vals = {}
  for _, a in ipairs(watched) do
    local v = rd(a)
    vals[#vals + 1] = string.format("%04X=%02X", a, v)
    if v ~= last[a] then changed = true; last[a] = v end
  end
  lastA = A
  if changed then
    L.log(string.format("f%d A=%02X %s", L.frame, A, table.concat(vals, " ")))
  end
end)
