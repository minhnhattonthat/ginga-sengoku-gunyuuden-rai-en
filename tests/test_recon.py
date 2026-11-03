"""Phase 1 findings as tests: table, LZ codec, known strings. ROM-dependent tests skip on a clone without the ROM."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from lz import compress, decompress  # noqa: E402
from rle import decode  # noqa: E402
from tbl import Table  # noqa: E402

ROM = ROOT / 'rom' / 'Ginga Sengoku Gunyuuden Rai (Japan).sfc'
rom_only = pytest.mark.skipif(not ROM.exists(), reason='original ROM not present')


def test_lz_roundtrip():
    import random
    r = random.Random(7)
    for n in (0, 1, 8, 9, 257, 3000):
        raw = bytes(r.choice(b'\x00\x00\x01\x02ab') for _ in range(n))
        assert decompress(compress(raw))[0] == raw


def test_table_values_unique():
    t = Table.load(ROOT / 'tbl/jp.tbl')
    vals = list(t.dec.values())
    assert len(vals) == len(set(vals)), 'two codes decode to the same text: encode(decode()) would break'


@rom_only
def test_lz_chain_title():
    rom = ROM.read_bytes()
    pos, sizes = 0x0F0000, []
    for _ in range(5):
        raw, used = decompress(rom, pos)
        sizes.append(len(raw))
        pos += used
    assert sizes == [0x1160, 0x800, 0x5080, 0x800, 0x1140]  # DMA sizes logged on the title screen


@rom_only
def test_known_strings():
    rom = ROM.read_bytes()
    t = Table.load(ROOT / 'tbl/jp.tbl')
    text, used = t.decode(rom, 0x011A46)
    assert text.startswith('南京楼軍 竜我雷') and text.endswith('物資豊かな南京楼を拠点に銀河を駆け巡る{end}')
    assert t.encode(text) == rom[0x011A46:0x011A46 + used]


@rom_only
def test_rle_tilemap_streams_back_to_back():
    rom = ROM.read_bytes()
    # the word-RLE tilemap streams in bank $AD are contiguous: each ends where the next begins
    words, end = decode(rom, 0x168000)
    assert len(words) == 4096 and end == 0x169C15
    words, end = decode(rom, 0x169C15)
    assert len(words) == 512 and end == 0x169F7C


@rom_only
def test_lz_chains_missed_by_immediates():
    rom = ROM.read_bytes()
    # blocks the A2/A9 scan misses because they are selected at runtime (pointer from WRAM), verified by
    # tools/lua/lzlog.lua on a boot-to-map tour: bank $98 (0x0C0000..), bank $A0 (0x100000..), bank $AC (0x160000)
    for start, sizes in [(0x0C0000, [0x460] * 31), (0x100000, [0x3B20, 0x2600, 0x800, 0x800, 0x800, 0x2C0]),
                         (0x160000, [0x2000])]:
        pos = start
        for size in sizes:
            raw, used = decompress(rom, pos)
            assert len(raw) == size, (hex(pos), len(raw), size)
            pos += used
