-- regen.py --probe: log PC, registers and the stack top when font cell CELL (default 0x337, 体) is read from the
-- 12x12 font ($95:8000 + 24 * cell), to find code that renders a label from the font.
local cell = CELL or 0x337
local seen = {}
local function hook()
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  local sp = s["cpu.sp"]
  local st = {}
  for i = 1, 16 do st[#st + 1] = string.format("%02X", emu.read(sp + i, emu.memType.snesMemory)) end
  local key = pc .. table.concat(st)
  if not seen[key] then
    seen[key] = true
    L.log(string.format("glyph read pc=%06X f%d A=%04X X=%04X Y=%04X D=%04X stack=%s", pc, L.frame, s["cpu.a"],
      s["cpu.x"], s["cpu.y"], s["cpu.d"], table.concat(st, " ")))
  end
end
for _, base in ipairs({0x958000, 0x158000}) do
  local lo = base + 24 * cell
  emu.addMemoryCallback(L.safe(hook), emu.callbackType.read, lo, lo + 23, emu.cpuType.snes, emu.memType.snesMemory)
end
