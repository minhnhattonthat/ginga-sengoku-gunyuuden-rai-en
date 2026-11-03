-- Log the program counter at the given frames (or every N frames) to see which code is running.
--   emu.py ROM --state-in F --frames N --script tools/lua/trace_pc.lua --var EVERY=30
local every = EVERY or 60
L.on_frame(function(f)
  if f % every == 0 then
    local s = emu.getState()
    L.log(string.format("f%d pc=%06X", f, (s["cpu.k"] << 16) | s["cpu.pc"]))
  end
end)
