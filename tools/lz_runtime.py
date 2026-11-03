"""List LZ blocks decompressed at runtime (lzlog.lua lines in emulator logs) that the static scan misses.

    python -X utf8 tools/lz_runtime.py work/qa/warp/*/log.txt [--tsv work/recon/lz_runtime.tsv]

Reads every `src=XXXXXX` line, decompresses each block from the ROM (tools/lz.py) to get its packed and
unpacked size, and marks blocks absent from work/recon/lz_blocks.tsv (the static immediate/chain scan) as NEW,
with the scenes (log folder names) that load them.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import lz  # noqa: E402

ROM = ROOT / "rom" / "Ginga Sengoku Gunyuuden Rai (Japan).sfc"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("logs", nargs="+")
    ap.add_argument("--tsv", help="write offset, packed, unpacked, known/NEW, scenes")
    args = ap.parse_args()
    rom = ROM.read_bytes()
    known = {int(l.split("\t")[0], 16) for l in (ROOT / "work/recon/lz_blocks.tsv").read_text().splitlines() if l}
    seen: dict[int, set[str]] = {}
    for log in args.logs:
        p = Path(log)
        for m in re.finditer(r"src=([0-9A-F]{6})", p.read_text(encoding="utf-8", errors="replace")):
            seen.setdefault(int(m.group(1), 16), set()).add(p.parent.name)
    rows = []
    for off in sorted(seen):
        raw, used = lz.decompress(rom, off)
        rows.append((off, used, len(raw), "known" if off in known else "NEW", ",".join(sorted(seen[off]))))
    new = [r for r in rows if r[3] == "NEW"]
    for r in rows:
        if r[3] == "NEW":
            print("%06X\t%X\t%X\t%s\t%s" % r)
    print(f"{len(rows)} blocks seen, {len(new)} not in lz_blocks.tsv", file=sys.stderr)
    if args.tsv:
        Path(args.tsv).write_text("".join("%06X\t%X\t%X\t%s\t%s\n" % r for r in rows), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
