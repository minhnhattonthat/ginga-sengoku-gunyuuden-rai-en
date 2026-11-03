-- regen.py --probe: dump VRAM/CGRAM/OAM (final.vram.bin etc.) when warp.lua takes final.png.
local shot = L.shot
L.shot = function(name)
  shot(name)
  if name == "final.png" then L.dump_ppu("final") end
end
