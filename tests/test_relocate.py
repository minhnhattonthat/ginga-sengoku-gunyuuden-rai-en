"""Text block layout when English outgrows a block (tools/build.py layout/place)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import build  # noqa: E402


def entry(off, refs, read_on=False):
    return {'off': off, 'refs': refs, 'tails': [], 'read_on': read_on}


def test_overflow_splits_at_units_and_reuses_free_space():
    b = {'start': 0x10000, 'end': 0x10010, 'entries': [
        entry(0x10000, [('p16', 0, None)]),
        entry(0x10008, [('p16', 2, None)]),
        entry(0x1000C, [], read_on=True)]}  # read on from the one before: moves with it
    free = [[0x17000, 0x17100, False]]
    out = build.layout(b, [10, 6, 6], free, [], b'')
    assert out == [(0x10000, [0]), (0x17000, [1, 2])]
    assert free == [[0x17000 + 12, 0x17100, False], [0x1000A, 0x10010, False]]  # leftover room joins free


def test_p24_unit_goes_far_without_crossing_a_bank():
    b = {'start': 0x10000, 'end': 0x10004, 'entries': [entry(0x10000, [('p24', 0, None)])]}
    far = [[0x1E8000 - 4, 0x1F0010, False]]
    assert build.layout(b, [8], [], far, b'') == [(0x1E8000, [0])]


def test_p16_unit_stays_in_bank():
    b = {'start': 0x10000, 'end': 0x10004, 'entries': [entry(0x10000, [('p16', 0, None)])]}
    try:
        build.layout(b, [8], [], [[0x1E8000, 0x1F0000, False]], b'')
    except ValueError as err:
        assert 'no free space' in str(err)
    else:
        raise AssertionError('a p16 string left its bank')
