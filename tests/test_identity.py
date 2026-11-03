"""Phase 3 identity build: unpack and repack every known container with no edits -> the original ROM, byte for byte.
Plus one edit per container type, to prove the repack path really moves data (an identity build that skips
everything would also pass the first test)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build  # noqa: E402
import lz  # noqa: E402
import rle  # noqa: E402
from tbl import Table  # noqa: E402

pytestmark = pytest.mark.skipif(not build.ORIG.exists(), reason='original ROM not present')


@pytest.fixture(scope='module')
def full():
    return build.build(repack_all=True)


def test_repack_all_is_identical(full):
    rom, pools, skipped = full
    assert bytes(rom.buf) == rom.orig
    assert len(pools) == 37 and sum(len(p[3]) for p in pools) == 628 and not skipped


def test_codecs_byte_identical_per_container():
    orig = build.ORIG.read_bytes()
    for off, packed_len, _ in build.rows('lz_blocks.tsv'):
        raw, used = lz.decompress(orig, off)
        assert lz.compress(raw) == orig[off:off + used], f'lz {off:06X}'
    for (off,) in build.rows('rle_streams.tsv'):
        words, end = rle.decode(orig, off)
        assert rle.encode(words) == orig[off:end], f'rle {off:06X}'


def test_text_edit_moves_pointers():
    orig = build.ORIG.read_bytes()
    table = Table.load(ROOT / 'tbl/jp.tbl')
    pools, _ = build.text_pools(orig, table)
    lo, hi, starts, slots = max(pools, key=lambda p: len(p[2]))
    first = starts[0]
    text = table.decode(orig, first)[0]
    rom, _, _ = build.build(edits={'text': {first: text[1:]}})  # one character shorter
    new = bytes(rom.buf)
    assert new != orig
    for slot, target in slots:
        ptr = (slot & ~0x7FFF) | (new[slot] | new[slot + 1] << 8) & 0x7FFF
        want = text[1:] if target == first else table.decode(orig, target)[0]
        assert table.decode(new, ptr)[0] == want, f'slot {slot:06X}'
        assert target == first or ptr == target - 2  # every later string moved up one code


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
    rom, _, _ = build.build(edits={'lz': {off: bytes(raw)}, 'rle': {roff: words}})
    assert bytes(rom.buf) != orig
    assert lz.decompress(rom.buf, off)[0] == raw
    assert rle.decode(rom.buf, roff)[0] == words
