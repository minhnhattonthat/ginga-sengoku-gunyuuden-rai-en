"""Every place the ROM holds a given text address: 16-bit words anywhere (with the opcode byte before, so code
immediates like LDX #$hhll stand out) and 24-bit forms.

    python -X utf8 tools/find_refs.py ROM OFFSET [OFFSET...] [--bank-only]
"""
import argparse
import re


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom')
    ap.add_argument('offsets', nargs='+')
    ap.add_argument('--bank-only', action='store_true', help='16-bit hits only inside the target bank')
    a = ap.parse_args()
    rom = open(a.rom, 'rb').read()
    for s in a.offsets:
        t = int(s, 16)
        addr, bank = 0x8000 | (t & 0x7FFF), t >> 15
        lo = addr.to_bytes(2, 'little')
        print(f'{t:06X} = ${0x80 | bank:02X}:{addr:04X}')
        for m in re.finditer(re.escape(lo), rom):
            o = m.start()
            if a.bank_only and o >> 15 != bank:
                continue
            tag = '24' if rom[o + 2] in (bank, bank | 0x80) else '16'
            print(f'  {tag} {o:06X} ${0x80 | o >> 15:02X}:{0x8000 | o & 0x7FFF:04X} [{rom[o - 3:o].hex(" ")} | '
                  f'{rom[o:o + 2].hex(" ")} | {rom[o + 2:o + 5].hex(" ")}]')


if __name__ == '__main__':
    main()
