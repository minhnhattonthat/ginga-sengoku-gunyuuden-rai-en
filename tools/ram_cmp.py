"""Compare RAM dumps across states to find candidate 'mode'/state bytes.

Usage: python -X utf8 tools/ram_cmp.py <title.bin> <faction.bin> <map.bin>
Prints bytes with small values (0..64) that are stable-ish and differ across the three screens,
focusing on the direct page and low WRAM where mode vars usually live.
"""
import sys
from pathlib import Path

files = [Path(p) for p in sys.argv[1:]]
d = [f.read_bytes() for f in files]
names = [f.name for f in files]

# For each byte offset, gather the three values.
candidates = []
for i in range(0x20000):
    vals = [x[i] for x in d]
    if len(set(vals)) < 2:
        continue
    if all(0 <= v <= 64 for v in vals):
        candidates.append((i, vals))

print(f"{len(candidates)} candidate bytes (small values, differ across states)\n")
print("offset | " + " | ".join(names))
for i, vals in candidates:
    print(f"{i:05X}   | " + "   | ".join(f"{v:02X} ({v:3d})" for v in vals))
