-- regen.py --probe: log writes into VRAM bytes VLO..VHI (default tile 0x10 at byte 0x200-0x21F) with the PC and
-- the DMA channel 7 source registers, to trace where a screen's tile came from (runtime-built tiles).
local lo, hi = VLO or 0x200, VHI or 0x21F
local mem = emu.memType.snesMemory
local last = -1
local function hook(addr, value)
  if L.frame == last then return end
  last = L.frame
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  local src = emu.read(0x4374, mem) << 16 | emu.read(0x4373, mem) << 8 | emu.read(0x4372, mem)
  L.log(string.format("vram %04X=%02X pc=%06X f%d dma7src=%06X", addr, value, pc, L.frame, src))
end
emu.addMemoryCallback(L.safe(hook), emu.callbackType.write, lo, hi, emu.cpuType.snes, emu.memType.snesVideoRam)
