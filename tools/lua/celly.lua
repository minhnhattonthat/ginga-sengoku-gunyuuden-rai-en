-- regen.py --probe: log Y, A and $0905/$0906 at every entry of the glyph draw $81:DD36 (speech box layout).
local n = 0
L.on_exec(0x81DD36, 0x81DD36, function()
  if n >= 400 then return end
  n = n + 1
  local s = emu.getState()
  L.log(string.format("DD36 f%d A=%04X Y=%04X 0905=%02X 0906=%02X", L.frame, s["cpu.a"], s["cpu.y"],
    emu.read(0x0905, emu.memType.snesMemory), emu.read(0x0906, emu.memType.snesMemory)))
end)
