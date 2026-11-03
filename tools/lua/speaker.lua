-- regen.py --probe: force the speech-box speaker to officer SPEAKER (default 2, Sho Shigen: condensed tag) when
-- the box draws its name: $094F at $81:ECE2 (battle quotes), $0E01 at $8B:DA66 (advisor). Checks speaker tags
-- (patches.TAGNAME).
local who = SPEAKER or 2
local mem = emu.memType.snesMemory
L.on_exec(0x81ECE2, 0x81ECE2, function() emu.write(0x094F, who, mem) end)
L.on_exec(0x8BDA66, 0x8BDA66, function() emu.write(0x0E01, who, mem) end)
