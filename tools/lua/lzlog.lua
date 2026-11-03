-- SNES (Mesen): log every LZ decompression by hooking the decoder entry $00:8401 and reading its source
-- pointer ($06D8) and bank ($06DA) from WRAM. Catches blocks the static scan misses (pointer-table and
-- runtime-selected sources). Dedupes by source file offset.
--   emu.py ... --script tools/lua/lzlog.lua
local mem = emu.memType.snesMemory
local seen = {}
local function log(addr, value)
  local d = emu.read(0x6D8, mem) | emu.read(0x6D9, mem) << 8
  local bank = emu.read(0x6DA, mem)
  local f = ((bank & 0x7F) << 15) | (d & 0x7FFF)
  if seen[f] and not LZ_ALL then return end  -- LZ_ALL (set in a wrapper probe): log every decompression
  seen[f] = true
  local dest = emu.read(0x6DB, mem) | emu.read(0x6DC, mem) << 8
  L.log(string.format("f%d src=%06X bank=%02X dest=%04X", L.frame, f, bank, dest))
end
L.on_exec(0x008401, 0x008401, log)
