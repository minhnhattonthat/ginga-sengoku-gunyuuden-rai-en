-- regen.py --probe: log each distinct (glyph cell, caller) passed to the font index routine $81:E0F4 (A = cell),
-- with the JSL return address and the next stack bytes, to find label strings drawn from the font.
local mem = emu.memType.snesMemory
local seen = {}
local function hook()
  local s = emu.getState()
  local sp = s["cpu.sp"]
  local ret = emu.read(sp + 3, mem) << 16 | emu.read(sp + 2, mem) << 8 | emu.read(sp + 1, mem)
  local up = {}
  for i = 4, 9 do up[#up + 1] = string.format("%02X", emu.read(sp + i, mem)) end
  local key = string.format("%04X %06X", s["cpu.a"] & 0xFFFF, ret)
  if not seen[key] then
    seen[key] = true
    L.log(string.format("glyph %s stack %s f%d Y=%04X DB=%02X", key, table.concat(up, " "), L.frame, s["cpu.y"], s["cpu.dbr"]))
  end
end
L.on_exec(0x81E0F4, 0x81E0F4, hook)
