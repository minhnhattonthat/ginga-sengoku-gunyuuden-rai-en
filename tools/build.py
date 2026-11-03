"""build.py: original ROM -> build/rai_en.sfc, with a write log and a romdiff check.

    python -X utf8 tools/build.py               normal build (repacks only edited containers; none yet)
    python -X utf8 tools/build.py --repack-all  identity build: unpack and repack every known container

Containers (lists in data/): LZ blocks (data/lz_blocks.tsv, tools/lz.py), word-RLE tilemaps
(data/rle_streams.tsv, tools/rle.py), and text blocks: runs of strings stored back to back, with every ref to
them (tools/extract.py, tools/refs.py; tbl/jp.tbl, tbl/msg_codes.tbl). Both codecs are byte-identical to the original tools, so --repack-all with no
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
import extract  # noqa: E402
import lz  # noqa: E402
import rle  # noqa: E402
import romdiff  # noqa: E402
from bps import snes_checksum  # noqa: E402

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


def repack_text(rom, edits=None):
    """Rewrite text blocks (tools/extract.py): each block's strings back to back from its start, then every ref.
    edits: {string offset: new jp-style text}; None = repack every block unchanged. Returns the blocks repacked.

    Refs: p16/p24 get the string's new address, rel16 the new distance from its (moved) base string, tails the
    host's new address + offset (host must be unchanged). Fixed refs (code immediates, base + index forms) can't
    be rewritten: their strings, and every string before them in the block, must keep their offsets."""
    blocks = extract.blocks(rom.orig)
    if edits is not None:
        blocks = [b for b in blocks if any(b['start'] <= s < b['end'] for s in edits)]
    for b in blocks:
        new, blob = {}, bytearray()
        for e in b['entries']:
            new[e['off']] = b['start'] + len(blob)
            text = (edits or {}).get(e['off'])
            data = extract.encode(e['jp'] if text is None else text, e['pre'], e['fmt'])
            fixed = extract.parse_fmt(e['fmt'])[2]
            if fixed and len(data) != fixed:
                raise ValueError(f'text {e["off"]:06X}: fixed field is {fixed} bytes, got {len(data)}')
            if text is not None and e['tails'] and text != e['jp']:
                raise ValueError(f'text {e["off"]:06X}: edited string has refs into its middle (tails)')
            blob += data
        if len(blob) > b['end'] - b['start']:
            raise ValueError(f'text block {b["start"]:06X}-{b["end"]:06X}: {len(blob)} bytes > '
                             f'{b["end"] - b["start"]} (relocation needed)')
        rom.write(b['start'], bytes(blob), f'text:{b["start"]:06X}')
        for e in b['entries']:
            for kind, slot, x, *delta in e['refs'] + e['tails']:
                t = new[e['off']] + (delta[0] if delta else 0)
                if kind == 'fixed':
                    if t != e['off'] + (delta[0] if delta else 0):
                        raise ValueError(f'text {e["off"]:06X}: moved, but code at {slot:06X} holds it fixed')
                elif (t ^ b['start']) & ~0x7FFF:
                    raise ValueError(f'text {e["off"]:06X}: string left its bank')
                elif kind == 'p16':
                    rom.write(slot, (0x8000 | t & 0x7FFF).to_bytes(2, 'little'), f'ptr:{slot:06X}')
                elif kind == 'p24':
                    rom.write(slot, bytes([t & 0xFF, 0x80 | (t >> 8) & 0x7F, rom.orig[slot + 2] & 0x80 | t >> 15]),
                              f'ptr:{slot:06X}')
                elif kind == 'rel16':
                    rom.write(slot, (t - new[x]).to_bytes(2, 'little'), f'ptr:{slot:06X}')
    return blocks


def build(repack_all=False, edits=None):
    """edits: {'lz': {off: raw}, 'rle': {off: words}, 'text': {off: text}} (tests; phases 5-7 fill these)."""
    check_rom.check()
    rom = Rom(ORIG.read_bytes())
    edits = edits or {}
    repack_lz(rom, None if repack_all else edits.get('lz', {}))
    repack_rle(rom, None if repack_all else edits.get('rle', {}))
    blocks = repack_text(rom, None if repack_all else edits.get('text', {}))
    fixed, _ = snes_checksum(rom.buf)
    for off in range(0x7FDC, 0x7FE0):
        rom.write(off, fixed[off:off + 1], 'checksum')
    return rom, blocks


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--repack-all', action='store_true')
    a = ap.parse_args()
    rom, blocks = build(a.repack_all)
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
              f'{sum(1 for _ in rows("rle_streams.tsv"))} RLE streams, {len(blocks)} text blocks '
              f'({sum(len(b["entries"]) for b in blocks)} strings, '
              f'{sum(len(e["refs"]) + len(e["tails"]) for b in blocks for e in b["entries"])} refs)')
    print(f'{OUT.relative_to(ROOT)}  {len(rom.writes)} writes  sha1 {hashlib.sha1(rom.buf).hexdigest()}'
          f'  {"identical to original" if rom.buf == rom.orig else "changed"}')


if __name__ == '__main__':
    main()
