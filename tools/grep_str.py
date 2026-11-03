"""Find a Japanese string's encoding in the ROM (16-bit font-cell codes), for menu/help text RE.

Usage: python -X utf8 tools/grep_str.py "惑星データの表示" [rom] [--context N]
Prints every offset the encoded string occurs at, plus an ASCII dump of the bytes around each hit.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tbl

rom = Path("rom/Ginga Sengoku Gunyuuden Rai (Japan).sfc")
ctx = 32
args = []
skip = False
for i, a in enumerate(sys.argv[1:], 1):
    if skip:
        skip = False
    elif a == "--context":
        ctx = int(sys.argv[i + 1])
        skip = True
    elif a == "--rom":
        rom = Path(sys.argv[i + 1])
        skip = True
    else:
        args.append(a)
text = args[0]

t = tbl.Table.load("tbl/jp.tbl")
needle = t.encode(text)
d = rom.read_bytes()
hits = []
i = d.find(needle)
while i != -1:
    hits.append(i)
    i = d.find(needle, i + 1)
print(f"{text!r} -> {needle.hex()} ({len(needle)} bytes), {len(hits)} hits")
for h in hits:
    lo = max(0, h - ctx)
    hi = min(len(d), h + len(needle) + ctx)
    print(f"\n== file 0x{h:06X}")
    for o in range(lo, hi, 16):
        row = d[o:min(o + 16, hi)]
        mark = " <<<" if o <= h < o + 16 else ""
        print(f"{o:06X}  {' '.join(f'{b:02X}' for b in row)}{mark}")
