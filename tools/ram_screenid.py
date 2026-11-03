"""Find a stable 'screen id' byte: same across two title captures, same across two faction-select
captures, but different across {title, faction, map}."""
import sys
from pathlib import Path

t1 = Path(sys.argv[1]).read_bytes()   # title a
t2 = Path(sys.argv[2]).read_bytes()   # title b
f1 = Path(sys.argv[3]).read_bytes()   # faction a
f2 = Path(sys.argv[4]).read_bytes()   # faction b
m = Path(sys.argv[5]).read_bytes()    # map

for i in range(0x20000):
    if t1[i] != t2[i]:
        continue
    if f1[i] != f2[i]:
        continue
    tv, fv, mv = t1[i], f1[i], m[i]
    if not (tv != fv and fv != mv and tv != mv):
        continue
    # screen id candidates: prefer small values
    if max(tv, fv, mv) <= 0x40:
        print(f"{i:05X}  title={tv:02X} faction={fv:02X} map={mv:02X}")
