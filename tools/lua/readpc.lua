-- SNES (Mesen): log the PC of every distinct code location that reads CPU addresses LO..HI (once per PC),
-- immediately (no end-of-run report, so it works beside warp.lua, which owns the frame callback).
--   emu.py ... --script tools/lua/readpc.lua --var LO=0xBBFB2D --var HI=0xBBFBAD
local seen = {}
local function hook(addr, value)
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  local d = (addr & 0x7FFFFF) - (pc & 0x7FFFFF)
  if d >= 0 and d < 4 then return end  -- opcode/operand fetch
  if not seen[pc] then
    seen[pc] = true
    L.log(string.format("read %06X pc=%06X f%d", addr, pc, L.frame))
  end
end
emu.addMemoryCallback(L.safe(hook), emu.callbackType.read, LO, HI, emu.cpuType.snes, emu.memType.snesMemory)
-- also the other LoROM mirror ($00-$3F <-> $80-$BF)
emu.addMemoryCallback(L.safe(hook), emu.callbackType.read, LO ~ 0x800000, HI ~ 0x800000, emu.cpuType.snes,
  emu.memType.snesMemory)
