"""Phase 1 findings as tests: table, LZ codec, known strings. ROM-dependent tests skip on a clone without the ROM."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from lz import compress, decompress  # noqa: E402
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
