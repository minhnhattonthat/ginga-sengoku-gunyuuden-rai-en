-- Log the joypad copies $0022-$0026 so a route can be checked against the bytes the game actually reads.
--   emu.py ROM --state-in S --frames 200 --route-str "60 -;6 right;40 -;6 a;40 -" --script tools/lua/joy.lua
local mem = emu.memType.snesMemory
local last = {}
L.on_frame(function(f)
  local parts = {}
  for a = 0x20, 0x27 do
    parts[#parts + 1] = string.format("%02X=%02X", a, emu.read(a, mem))
  end
  local line = table.concat(parts, " ")
  if line ~= LASTLINE then
    LASTLINE = line
    L.log(string.format("f%d %s", f, line))
  end
end)
