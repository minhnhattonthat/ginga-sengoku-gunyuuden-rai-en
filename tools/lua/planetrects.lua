-- Dump the map cursor/planet hit-test table at $7E:E037 (23 entries of {x,y} words) at chosen frames.
--   emu.py ROM --state-in work/states/map_nankyourou.mss --frames 300 --script tools/lua/planetrects.lua
local mem = emu.memType.snesMemory
local function rdw(a) return emu.read(a, mem) | (emu.read(a + 1, mem) << 8) end
local AT = AT or 120
L.on_frame(function(f)
  if f ~= AT then return end
  local parts = {}
  for i = 0, 0x16 do
    local x = rdw(0xE037 + i * 4)
    local y = rdw(0xE039 + i * 4)
    parts[#parts + 1] = string.format("%2d:%04X,%04X", i + 1, x, y)
  end
  L.log("rects " .. table.concat(parts, " "))
  L.log(string.format("cursor %04X,%04X scroll %04X,%04X 0E00=%02X 0917=%02X",
    0x0A95 + 0, 0x0A96 + 0, rdw(0x0A98), rdw(0x0A9A), emu.read(0x0E00, mem), emu.read(0x0917, mem)))
end)
