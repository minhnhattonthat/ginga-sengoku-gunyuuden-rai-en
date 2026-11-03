-- Dump WRAM at each frame listed in FRAMES_AT (comma-separated) to ram_<frame>.bin.
--   emu.py ROM --frames N --script tools/lua/probe_ram_multi.lua --var "FRAMES_AT='400,600,800'"
local want = {}
for f in (FRAMES_AT or ""):gmatch("%d+") do want[tonumber(f)] = true end
L.on_frame(function(f)
  if want[f] then L.dump_ram(string.format("ram_%06d.bin", f)) end
end)
