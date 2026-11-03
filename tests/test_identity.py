"""Phase 3 identity build: unpack and repack every known container with no edits -> the original ROM, byte for byte.
Plus one edit per container type, to prove the repack path really moves data (an identity build that skips
everything would also pass the first test)."""
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build  # noqa: E402
import extract  # noqa: E402
import lz  # noqa: E402
import rle  # noqa: E402

pytestmark = pytest.mark.skipif(not build.ORIG.exists(), reason='original ROM not present')


@pytest.fixture(scope='module')
def full():
    return build.build(repack_all=True)


def test_repack_all_is_identical(full):
    rom, blocks = full
    assert bytes(rom.buf) == rom.orig
    assert len(blocks) >= 48 and sum(len(b['entries']) for b in blocks) >= 1561


def test_codecs_byte_identical_per_container():
    orig = build.ORIG.read_bytes()
    for off, packed_len, _ in build.rows('lz_blocks.tsv'):
        raw, used = lz.decompress(orig, off)
        assert lz.compress(raw) == orig[off:off + used], f'lz {off:06X}'
    for (off,) in build.rows('rle_streams.tsv'):
        words, end = rle.decode(orig, off)
        assert rle.encode(words) == orig[off:end], f'rle {off:06X}'


@pytest.mark.parametrize('start', [0x01020A, 0x18EC39, 0x1D8000])  # p16 pool, p24 message chain, rel16 talk tables
def test_text_edit_moves_refs(start):
    orig = build.ORIG.read_bytes()
    block = next(b for b in extract.blocks(orig) if b['start'] == start)
    first = block['entries'][0]
    m = re.match(r'\{\w+(?::\w+)?\}|.', first['jp'])  # drop the first character or control code
    rom, _ = build.build(edits={'text': {first['off']: first['jp'][m.end():]}})
    new = bytes(rom.buf)
    cut = len(extract.encode(first['jp'], first['pre'], first['fmt'])) - len(
        extract.encode(first['jp'][m.end():], first['pre'], first['fmt']))
    assert new != orig and cut > 0
    moved = {e['off']: e['off'] - (cut if e is not first else 0) for e in block['entries']}
    w = lambda o: new[o] | new[o + 1] << 8  # noqa: E731
    for e in block['entries']:
        to = moved[e['off']]
        want = first['jp'][m.end():] if e is first else e['jp']
        assert extract.decode(new, to, e['fmt'])[0] == want, f'{e["off"]:06X}'
        for kind, slot, x in e['refs']:
            if kind == 'p16':
                assert w(slot) == 0x8000 | to & 0x7FFF, f'{slot:06X}'
            elif kind == 'p24':
                assert ((new[slot + 2] & 0x7F) << 15 | w(slot) & 0x7FFF) == to, f'{slot:06X}'
            elif kind == 'rel16':
                assert w(slot) == to - moved[x], f'{slot:06X}'


def test_lz_and_rle_edits_roundtrip():
    orig = build.ORIG.read_bytes()
    off = 0x0F0000
    raw = bytearray(lz.decompress(orig, off)[0])
    raw[0] ^= 0xFF
    roff = 0x168000
    words, end = rle.decode(orig, roff)
    # first real change that still fits in place (the build refuses a grown stream)
    i = next(i for i in range(1, len(words)) if words[i] != words[i - 1]
             and len(rle.encode(words[:i] + [words[i - 1]] + words[i + 1:])) <= end - roff)
    words[i] = words[i - 1]
    rom, _ = build.build(edits={'lz': {off: bytes(raw)}, 'rle': {roff: words}})
    assert bytes(rom.buf) != orig
    assert lz.decompress(rom.buf, off)[0] == raw
    assert rle.decode(rom.buf, roff)[0] == words
