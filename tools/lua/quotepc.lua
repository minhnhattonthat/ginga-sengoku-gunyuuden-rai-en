-- regen.py --probe: log the call stack top when font cell 4F (『, file 0x0A8768 = $95:8768) is read, to find
-- the code that draws a speech box's opening quote.
local seen = {}
local function hook()
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  local sp = s["cpu.sp"]
  local ret = {}
  for i = 1, 12 do ret[#ret + 1] = string.format("%02X", emu.read(sp + i, emu.memType.snesMemory)) end
  local key = pc .. table.concat(ret)
  if not seen[key] then
    seen[key] = true
    L.log(string.format("4F read pc=%06X f%d A=%04X X=%04X Y=%04X stack=%s", pc, L.frame, s["cpu.a"], s["cpu.x"],
      s["cpu.y"], table.concat(ret, " ")))
  end
end
for _, lo in ipairs({0x958768, 0x158768}) do
  emu.addMemoryCallback(L.safe(hook), emu.callbackType.read, lo, lo + 23, emu.cpuType.snes, emu.memType.snesMemory)
end
