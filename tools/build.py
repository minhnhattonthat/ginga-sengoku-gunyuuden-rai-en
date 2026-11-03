"""build.py: original ROM -> build/rai_en.sfc, with a write log and a romdiff check.

    python -X utf8 tools/build.py               normal build (repacks only edited containers; none yet)
    python -X utf8 tools/build.py --repack-all  identity build: unpack and repack every known container

Containers (lists in data/): LZ blocks (data/lz_blocks.tsv, tools/lz.py), word-RLE tilemaps
(data/rle_streams.tsv, tools/rle.py), and pools of plain strings behind 16-bit pointer tables
(data/ptr_tables.tsv, tbl/jp.tbl). Both codecs are byte-identical to the original tools, so --repack-all with no
edits gives the original ROM (tests/test_identity.py). Every changed byte goes through Rom.write, which logs it
to build/writes.log in romdiff.py's --writes format; romdiff then fails on any change outside the log.
"""
import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import check_rom  # noqa: E402
import lz  # noqa: E402
import rle  # noqa: E402
import romdiff  # noqa: E402
from bps import snes_checksum  # noqa: E402
from tbl import Table  # noqa: E402

ORIG = ROOT / 'rom' / 'Ginga Sengoku Gunyuuden Rai (Japan).sfc'
OUT = ROOT / 'build' / 'rai_en.sfc'
DATA = ROOT / 'data'


def rows(name):
    """Rows of a data/*.tsv file as lists of ints (hex fields), skipping # comments."""
    for line in (DATA / name).read_text(encoding='utf-8').splitlines():
        if line.strip() and not line.startswith('#'):
            yield [int(f, 16) for f in line.split('\t')]


class Rom:
    def __init__(self, orig):
        self.orig = bytes(orig)
        self.buf = bytearray(orig)
        self.writes = []  # (offset, orig bytes, new bytes, writer)

    def write(self, off, data, who):
        if off + len(data) > len(self.orig):
            raise ValueError(f'{who}: write at {off:#x} runs past the ROM end')  # shortcut: no expansion yet
        old = bytes(self.buf[off:off + len(data)])
        if old != data:
            self.writes.append((off, self.orig[off:off + len(data)], bytes(data), who))
            self.buf[off:off + len(data)] = data


def repack_lz(rom, edits=None):
    """edits: {offset: new raw bytes}; None = repack every block unchanged. Packed size must not grow."""
    for off, packed_len, raw_len in rows('lz_blocks.tsv'):
        if edits is not None and off not in edits:
            continue
        raw, used = lz.decompress(rom.orig, off)
        assert (used, len(raw)) == (packed_len, raw_len), f'lz {off:06X}: list says {packed_len:#x}/{raw_len:#x}'
        packed = lz.compress(edits[off] if edits else raw)
        if len(packed) > used:
            raise ValueError(f'lz {off:06X}: repacked {len(packed):#x} > original {used:#x} (relocation needed)')
        rom.write(off, packed, f'lz:{off:06X}')


def repack_rle(rom, edits=None):
    for (off,) in rows('rle_streams.tsv'):
        if edits is not None and off not in edits:
            continue
        words, end = rle.decode(rom.orig, off)
        packed = rle.encode(edits[off] if edits else words)
        if len(packed) > end - off:
            raise ValueError(f'rle {off:06X}: repacked {len(packed)} > original {end - off} bytes')
        rom.write(off, packed, f'rle:{off:06X}')


def text_pools(orig, table):
    """Split the pointer tables' targets into pools: runs of strings stored back to back (each string ends where
    the next target starts). A pool may serve several tables, and tables or other data may sit between pools.

    Returns (pools, skipped). A pool is (start, end, [string offsets], [(slot offset, target)]). skipped lists
    targets that start inside another string (shared tails): the phase-7 inserter must place those itself."""
    slots = []
    for off, cnt in rows('ptr_tables.tsv'):
        for k in range(cnt):
            p = off + 2 * k
            slots.append((p, (p & ~0x7FFF) | (orig[p] | orig[p + 1] << 8) & 0x7FFF))
    runs, skipped = [], []
    for t in sorted({t for _, t in slots}):
        end = t + table.decode(orig, t)[1]
        if runs and t == runs[-1][1]:
            runs[-1][1] = end
            runs[-1][2].append(t)
        elif runs and t < runs[-1][1]:
            runs[-1][3] = True
            skipped.append(t)
        else:
            runs.append([t, end, [t], False])
    pools = []
    for lo, hi, starts, bad in runs:
        if not bad:
            pools.append((lo, hi, starts, [s for s in slots if lo <= s[1] < hi]))
    return pools, skipped


def repack_text(rom, table, edits=None):
    """edits: {original string offset: new text}; None = repack every pool unchanged."""
    pools, skipped = text_pools(rom.orig, table)
    if edits is not None:
        pools = [p for p in pools if any(p[0] <= s < p[1] for s in edits)]
    for lo, hi, starts, slots in pools:
        new = {}
        blob = bytearray()
        for s in starts:
            new[s] = lo + len(blob)
            blob += table.encode((edits or {}).get(s) or table.decode(rom.orig, s)[0])
        if len(blob) > hi - lo:
            raise ValueError(f'text pool {lo:06X}-{hi:06X}: {len(blob)} bytes > {hi - lo}')
        rom.write(lo, bytes(blob), f'text:{lo:06X}')
        for slot, target in slots:
            if (new[target] ^ lo) & ~0x7FFF:
                raise ValueError(f'text pool {lo:06X}: string left its bank')
            rom.write(slot, (0x8000 | new[target] & 0x7FFF).to_bytes(2, 'little'), f'ptr:{slot:06X}')
    return pools, skipped


def build(repack_all=False, edits=None):
    """edits: {'lz': {off: raw}, 'rle': {off: words}, 'text': {off: text}} (tests; phases 5-7 fill these)."""
    check_rom.check()
    rom = Rom(ORIG.read_bytes())
    table = Table.load(ROOT / 'tbl' / 'jp.tbl')
    edits = edits or {}
    repack_lz(rom, None if repack_all else edits.get('lz', {}))
    repack_rle(rom, None if repack_all else edits.get('rle', {}))
    pools, skipped = repack_text(rom, table, None if repack_all else edits.get('text', {}))
    fixed, _ = snes_checksum(rom.buf)
    for off in range(0x7FDC, 0x7FE0):
        rom.write(off, fixed[off:off + 1], 'checksum')
    return rom, pools, skipped


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--repack-all', action='store_true')
    a = ap.parse_args()
    rom, pools, skipped = build(a.repack_all)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_bytes(rom.buf)
    log = OUT.with_name('writes.log')
    log.write_text(''.join(f'{o:06X} {old.hex()} {new.hex()} {who}\n' for o, old, new, who in rom.writes),
                   encoding='utf-8')
    errs, _ = romdiff.check(rom.orig, bytes(rom.buf), set(), romdiff.load_writes(log))
    if errs:
        sys.exit('romdiff:\n' + '\n'.join(errs))
    if a.repack_all:
        print(f'repacked {sum(1 for _ in rows("lz_blocks.tsv"))} LZ blocks, '
              f'{sum(1 for _ in rows("rle_streams.tsv"))} RLE streams, {len(pools)} text pools '
              f'({sum(len(p[2]) for p in pools)} strings, {sum(len(p[3]) for p in pools)} pointers; '
              f'skipped, target inside a string: {[f"{t:06X}" for t in skipped]})')
    print(f'{OUT.relative_to(ROOT)}  {len(rom.writes)} writes  sha1 {hashlib.sha1(rom.buf).hexdigest()}'
          f'  {"identical to original" if rom.buf == rom.orig else "changed"}')


if __name__ == '__main__':
    main()
