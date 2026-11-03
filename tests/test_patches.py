"""Code patches (tools/patches.py): originals checked on the dump, new code disassembles as intended."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build  # noqa: E402
import dis65816  # noqa: E402
import patches  # noqa: E402

pytestmark = pytest.mark.skipif(not build.ORIG.exists(), reason='original ROM not present')


def ops(rom, addr, n):
    return [line[30:].split(';')[0].strip() for line in dis65816.disasm(rom, addr, n)]  # after 'BB:AAAA  OFFSET  hex'


def test_patches_apply_and_disassemble():
    rom = build.Rom(build.ORIG.read_bytes())
    patches.apply(rom)
    new = bytes(rom.buf)
    assert ops(new, patches.FETCH, 9) == ['LDA [$00],y', 'CMP #$FFFF', 'BNE $800E', 'DEC $00', 'DEC $00',
                                          'LDA #$003E', 'ASL A', 'ASL A', 'RTL']
    for table, five, fetch, cpy in patches.FAMILIES:
        assert ops(new, fetch, 3) == ['REP #$20', 'LDY #$0000', 'JSL $BC8000']
        assert ops(new, fetch + 9, 1) == ['ASL A']  # the instruction after the two the hook replaced
        for n in range(1, 6):
            o = patches.off(table + 3 * n)
            assert int.from_bytes(new[o:o + 3], 'little') == five
