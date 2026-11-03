-- SNES (Mesen): per PC, the lowest and highest ROM address it reads and the read count, frames FROM..TO.
-- Unlike snes_romreads.lua (first read only), this shows which range a copy loop or text reader covers.
--   emu.py ... --script tools/lua/romrange.lua --var FROM=650 --var TO=662
-- Prints at frame TO: "pc=XXXXXX lo=off hi=off n=count" (file offsets, LoROM). Opcode fetches are skipped.
local from, to = FROM or 0, TO or math.huge
local lo, hi, n = {}, {}, {}
local function hook(addr, value)
  if L.frame < from or L.frame > to then return end
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  local d = (addr & 0x7FFFFF) - (pc & 0x7FFFFF)
  if d >= 0 and d < 4 then return end  -- opcode/operand fetch
  local o = L.rom_off(addr)
  if not n[pc] then lo[pc], hi[pc], n[pc] = o, o, 0 end
  if o < lo[pc] then lo[pc] = o end
  if o > hi[pc] then hi[pc] = o end
  n[pc] = n[pc] + 1
end
for bank = 0, 0xFF do
  if bank < 0x7E or bank > 0x7F then
    emu.addMemoryCallback(L.safe(hook), emu.callbackType.read, (bank << 16) | 0x8000, (bank << 16) | 0xFFFF,
      emu.cpuType.snes, emu.memType.snesMemory)
  end
end
L.on_frame(function(f)
  if f == to then
    local pcs = {}
    for pc in pairs(n) do pcs[#pcs + 1] = pc end
    table.sort(pcs)
    for _, pc in ipairs(pcs) do
      L.log(string.format("pc=%06X lo=%06X hi=%06X n=%d", pc, lo[pc], hi[pc], n[pc]))
    end
  end
end)
