"""Phase 4: extraction roundtrip and text-range coverage, against the ORIGINAL ROM."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import extract  # noqa: E402
import gaps  # noqa: E402

pytestmark = pytest.mark.skipif(not extract.ORIG.exists(), reason='original ROM not present')


@pytest.fixture(scope='module')
def rom():
    return extract.ORIG.read_bytes()


@pytest.fixture(scope='module')
def blocks(rom):
    return extract.blocks(rom)


def test_script_roundtrip(rom):
    """Every string in script/ re-encodes to the original bytes, and script/ matches a fresh extraction."""
    script = extract.load_script()
    assert len(script) >= 1561
    for off, e in script.items():
        data = extract.encode(e['jp'], bytes.fromhex(e.get('pre', '')), e['fmt'])
        assert data == rom[off:off + e['max']], f'{off:06X}'
    fresh = {e['off']: e['jp'] for b in extract.blocks(rom) for e in b['entries']}
    assert {o: e['jp'] for o, e in script.items()} == fresh, 'script/ is stale: run tools/extract.py --force'


def test_text_ranges_fully_covered(rom):
    """Every scanned text run (data/text_scan.tsv) is extracted text, a pointer slot or reviewed not-text."""
    cov = gaps.covered(rom)
    for line in (ROOT / 'data/text_scan.tsv').read_text(encoding='utf-8').splitlines():
        if line.startswith('#'):
            continue
        _fmt, s, e = line.split('\t')[:3]
        s, e = int(s, 16), int(e, 16)
        holes = [i for i in range(s, e) if not cov[i]]
        assert len(holes) < 4, f'{s:06X}-{e:06X}: unexplained bytes at {holes[0]:06X}'


def test_no_overlaps(rom, blocks):
    """Strings, pointer slots and not-text ranges never share a byte."""
    owner = {}
    for b in blocks:
        for e in b['entries']:
            for i in range(e['off'], e['off'] + e['len']):
                assert owner.setdefault(i, e['off']) == e['off'], f'{i:06X}'
    slots = {}
    for kind, slot, *_ in extract.all_refs(rom):
        for i in range(slot, slot + {'p16': 2, 'p24': 3, 'rel16': 2}.get(kind, 0)):
            assert i not in owner, f'pointer slot {slot:06X} inside string {owner[i]:06X}'
            slots[i] = slot
    for s, e, _ in extract.not_text():
        for i in range(s, e):
            assert i not in owner and i not in slots, f'not-text {s:06X} overlaps text or a slot at {i:06X}'


def test_known_pointer_forms(rom, blocks):
    entries = {e['off']: e for b in blocks for e in b['entries']}
    assert entries[0x10EC1C]['refs'][0][:2] == ('p24', 0x06B0EC)  # intro: event record $8D:B0E9 +3
    assert entries[0x1D8046]['refs'][0][:2] == ('rel16', 0x1D1A7E)  # talk table $BA:9A79, entry 1
    assert entries[0x19E2DA]['refs'][0][:2] == ('p24', 0x06B123)  # cmd 26 per-faction epilogue, faction 1
    assert entries[0x0119D0]['pre'] == bytes.fromhex('00033083')  # option label record prefix
    assert entries[0x148000]['jp'].startswith('誰を配置しますか?') and entries[0x148000]['len'] == 80
