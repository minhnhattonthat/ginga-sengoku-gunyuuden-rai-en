"""Text-coverage gaps: bytes inside the scan's text regions (work/recon/regions.tsv) that no extracted string,
pointer slot or listed non-text range (data/not_text.tsv) explains. For each gap: its strings and every
16-bit word in the same bank equal to their CPU address (table entries and immediates, with the opcode before).

    python -X utf8 tools/gaps.py ROM [--min 4] [--refs]
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import extract  # noqa: E402
import text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def covered(rom):
    cov = bytearray(len(rom))
    for b in extract.blocks(rom):
        for e in b['entries']:
            cov[e['off']:e['off'] + e['len']] = b'\1' * e['len']
    for kind, slot, *_ in extract.all_refs(rom):
        n = {'p16': 2, 'p24': 3, 'rel16': 2}.get(kind, 0)
        cov[slot:slot + n] = b'\2' * n
    for s, e, _why in extract.not_text():
        cov[s:e] = b'\3' * (e - s)
    return cov


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom')
    ap.add_argument('--min', type=int, default=4)
    ap.add_argument('--refs', action='store_true')
    ap.add_argument('--regions', default=str(ROOT / 'data/text_scan.tsv'))
    a = ap.parse_args()
    rom = open(a.rom, 'rb').read()
    cov = covered(rom)
    total = 0
    for line in Path(a.regions).read_text(encoding='utf-8').splitlines():
        if line.startswith('#'):
            continue
        fmt, s, e = line.split('\t')[:3]
        s, e = int(s, 16), int(e, 16)
        i = s
        while i < e:
            if cov[i]:
                i += 1
                continue
            j = i
            while j < e and not cov[j]:
                j += 1
            if j - i >= a.min:
                total += j - i
                try:
                    t, _ = text.table(fmt).decode(rom, i, maxlen=400)
                except ValueError:
                    t = '?'
                print(f'{fmt}\t{i:06X}\t{j - i}\t{t[:70]}')
                if a.refs:
                    addr = 0x8000 | (i & 0x7FFF)
                    bank = i & ~0x7FFF
                    for m in re.finditer(re.escape(addr.to_bytes(2, 'little')), rom[bank:bank + 0x8000]):
                        o = bank + m.start()
                        print(f'\t\tref {o:06X} {rom[o - 1]:02X} [{rom[o - 3:o + 5].hex(" ")}]')
            i = j
    print(f'# {total} bytes unexplained')


if __name__ == '__main__':
    main()
