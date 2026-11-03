-- Dump WRAM ($7E0000-$7FFFFF) at frame DUMP_AT (default FRAMES-1) to <out>/ram.bin, plus a short hex
-- note of the low WRAM mirror region. For RAM analysis of the current scene.
--   emu.py ROM --state-in work/states/foo.mss --frames N --script tools/lua/probe_ram.lua
local at = DUMP_AT or (FRAMES and FRAMES - 1) or 0
L.on_frame(function(f)
  if f == at then
    L.dump_ram("ram.bin")
    L.log("ram dumped at frame " .. f)
  end
end)
