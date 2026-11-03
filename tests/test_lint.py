"""Box budget lint (tools/lint.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import lint  # noqa: E402


def test_skip_counts_cells():
    # {skip:0100} indents one 12-px cell = 2 letters (measured: work/qa/stress/prol2)
    assert lint.lines_of('ab{br}{skip:0100}cd{br}{skip:0400}e{end}', 'br') == [2, 4, 9]


def test_expand_n_pads_to_width():
    assert lint.expand_n('ab{n}cde{n}f{end}', 6) == 'ab    cde   f{end}'
    assert lint.expand_n('{c5}ab{c6}{n}x', 4) == '{c5}ab{c6}  x'  # codes take no room


def test_boxes_parse():
    boxes, owner = lint.load_boxes()
    assert boxes['dialogue']['letters'] == 40 and owner
