-- Log every change of the map sub-mode $0A91 (and the register dump around it) plus the PC bank,
-- so a route of button presses can be mapped onto the screens it opens.
--   emu.py ROM --state-in work/states/map_nankyourou.mss --frames 1200 \
--     --route-str "60 -;4 a;90 -;..." --shot-every 30 --sheet --script tools/lua/mode_log.lua
local mem = emu.memType.snesMemory
local function rd(a) return emu.read(a, mem) end
local WATCH = WATCH or { 0x0A91, 0x0791, 0x073D, 0x0ABF, 0x0AC0, 0x1B10, 0x1B11, 0x1B12, 0x08DD }
if type(WATCH) == "number" then WATCH = { WATCH } end
local last = {}
L.on_frame(function(f)
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  local line = {}
  local changed = false
  for _, a in ipairs(WATCH) do
    local v = rd(a)
    if last[a] ~= v then changed = true end
    last[a] = v
    line[#line + 1] = string.format("%04X=%02X", a, v)
  end
  if changed or (LASTBANK ~= (pc >> 16)) then
    LASTBANK = pc >> 16
    L.log(string.format("f%d pc=%06X %s", f, pc, table.concat(line, " ")))
  end
end)
