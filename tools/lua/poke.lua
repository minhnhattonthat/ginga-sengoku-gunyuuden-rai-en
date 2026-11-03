-- Apply one-shot RAM writes at a frame, for probes.
--   emu.py ROM --frames 900 --route-str "..." --script tools/lua/poke.lua --var "POKE_AT=400" \
--     --var "POKES={ [0x091B]=3, [0x091C]=0 }"
local mem = emu.memType.snesMemory
local at = POKE_AT or 400
local pokes = POKES or {}
local every = POKES_EVERY or 0          -- >0: re-apply every N frames from `at` (for vars the game resets)
local done = false
L.on_frame(function(f)
  if f < at then return end
  if f ~= at and (every <= 0 or f % every ~= 0) then return end
  local n = 0
  for a, v in pairs(pokes) do
    emu.write(a, v, mem)
    n = n + 1
  end
  if not done or every > 0 then
    done = true
    L.log(string.format("poke at f%d: %d writes", f, n))
  end
end)
