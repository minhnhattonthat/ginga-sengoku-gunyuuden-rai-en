-- regen.py --probe: log each distinct PC that writes WRAM $7E:3330-$7E:333F (prisoner-panel label tiles
-- re-sent to VRAM every frame by $81:90E6), with the value, to find the code that builds them.
local seen = {}
local function hook(addr, value)
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  if not seen[pc] then
    seen[pc] = true
    L.log(string.format("write %06X=%02X pc=%06X f%d A=%04X X=%04X Y=%04X DB=%02X", addr, value, pc, L.frame,
      s["cpu.a"], s["cpu.x"], s["cpu.y"], s["cpu.dbr"] or 0))
  end
end
emu.addMemoryCallback(L.safe(hook), emu.callbackType.write, 0x7E3330, 0x7E333F, emu.cpuType.snes,
  emu.memType.snesMemory)
