-- Log each dialogue string the window renderer starts (BA:92CD reads [D+0],y with D = window+4), and the PC
-- that last wrote the window's pointer bytes before it.
--   emu.py ... --script tools/lua/msgptr.lua
local mem = emu.memType.snesMemory
local last = {}
local writer = {}
L.on_write(0x7E0000, 0x7E1FFF, function(addr, value)
  local s = emu.getState()
  writer[addr & 0x1FFF] = (s["cpu.k"] << 16) | s["cpu.pc"]
end)
L.on_exec(0xBA92CD, 0xBA92CD, function()
  local s = emu.getState()
  local d = s["cpu.d"]
  local p = emu.read(d, mem) | emu.read(d + 1, mem) << 8 | emu.read(d + 2, mem) << 16
  if last[d] ~= nil then return end
  last[d] = p
  L.log(string.format("f%d win=%04X ptr=%06X off=%06X wr=%06X", L.frame, d, p, L.rom_off(p), writer[d] or 0))
end)
-- forget a window when its text ends, so the next string logs too
L.on_exec(0xBA92EA, 0xBA92EA, function()
  local d = emu.getState()["cpu.d"]
  last[d] = nil
end)
