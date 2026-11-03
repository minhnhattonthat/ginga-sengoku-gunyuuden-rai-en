"""Phase 5: English digraph font, encoder and the marker build (docs/re/font.md)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build  # noqa: E402
import en  # noqa: E402
import extract  # noqa: E402
import font_en  # noqa: E402


def test_font_selftest():
    font_en.selftest()


def test_encoder_selftest():
    en.selftest()


@pytest.mark.skipif(not build.ORIG.exists(), reason='original ROM not present')
def test_marker_build_keeps_layout_and_shows_ids():
    rom, blocks = build.build(mode='marker')
    new = bytes(rom.buf)
    font_end = en.FONT + en.CELLS * 24
    for off, _old, data, who in rom.writes:
        assert who.startswith(('text:', 'font:', 'patch:', 'checksum')), who  # same lengths: no pointer moves
        if who.startswith('font:'):
            assert en.FONT <= off and off + len(data) <= font_end
    edits, cells, _, _ = build.english_edits(rom.orig, 'marker')
    decode = {}
    for off, glyph in cells.items():
        assert new[en.FONT + off * 24:en.FONT + off * 24 + 24] == glyph
    assert set(cells) == set(range(en.CELLS)) - en.RESERVED  # unused cells show '##' in the marker build
    for b in blocks:
        for e in b['entries']:
            assert len(edits[e['off']]) == e['len'], f'{e["off"]:06X}'
            decode[e['off']] = build.marker(e, extract.parse_fmt(e['fmt'])[0])
    for o, t in decode.items():
        visible = ''.join(s for is_code, s in en.runs(t) if not is_code)
        if len(visible) >= 8:
            assert visible.startswith(f'{o:06X} '), (hex(o), t)
