-- regen.py --probe: log each distinct PC that writes WRAM LO..HI (default $7E:8200-$7E:820F, the LZ output
-- of prisoner-panel label tile 0x10), with the value, to find code that builds or patches tiles.
local lo, hi = WLO or 0x7E8200, WHI or 0x7E820F
local seen = {}
local function hook(addr, value)
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  if not seen[pc] then
    seen[pc] = true
    L.log(string.format("write %06X=%02X pc=%06X f%d A=%04X X=%04X Y=%04X", addr, value, pc, L.frame,
      s["cpu.a"], s["cpu.x"], s["cpu.y"]))
  end
end
emu.addMemoryCallback(L.safe(hook), emu.callbackType.write, lo, hi, emu.cpuType.snes, emu.memType.snesMemory)
