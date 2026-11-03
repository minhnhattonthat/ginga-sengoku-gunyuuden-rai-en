"""Event scripts (bank $8D interpreter, docs/re/text.md §Event scripts): list every script, its lines and the
dialogue pointers its message commands reach.

    python -X utf8 tools/events.py ROM [--lines]

Script = lines of [word line number][cmd byte, arg word]*[00]; the line numbered FFFF is the last one.
Script starts: word table $8D:933F (bank $8D), entries $8BD7 unused. Handlers: word table $8D:938B.
Cmd 18 (show message, $8D:864B) takes a record in bank $8D whose bytes +3..+5 are a 24-bit text pointer; the
next messages of the box are read on from the end of the previous one (renderer), one per cmd 1A/1B.
"""
import argparse

BANK = 0x068000  # file offset of $8D:8000
STARTS = 0x933F
NSTARTS = 38
UNUSED = 0x8BD7
MSG_CMD = 0x18


def w(rom, o):
    return rom[o] | rom[o + 1] << 8


def f(addr):
    """$8D:xxxx -> file offset"""
    return BANK + (addr & 0x7FFF)


def lorom(lo, hi, bank):
    return ((bank & 0x7F) << 15) | ((hi & 0x7F) << 8) | lo


def script(rom, start):
    """[(line no, [(cmd, arg, offset of the cmd byte)])] up to and including line FFFF."""
    y, out = start, []
    while True:
        no = w(rom, f(y))
        y += 2
        cmds = []
        while rom[f(y)]:
            cmds.append((rom[f(y)], w(rom, f(y) + 1), f(y)))
            y += 3
        y += 1
        out.append((no, cmds))
        if no == 0xFFFF:
            return out
        assert len(out) < 2000, f'script {start:04X} runs away'


def scripts(rom):
    """{event index: start address}"""
    out = {}
    for i in range(NSTARTS):
        a = w(rom, f(STARTS) + 2 * i)
        if a != UNUSED:
            out[i] = a
    return out


def messages(rom):
    """[(event index, record address, file offset of the 24-bit pointer, target file offset, continues)]:
    one per cmd 18; continues = cmd 1A/1B count up to the next cmd 18 in the same script."""
    out = []
    for ev, start in scripts(rom).items():
        cur = None
        for _no, cmds in script(rom, start):
            for c, arg, _o in cmds:
                if c == MSG_CMD:
                    p = f(arg) + 3
                    cur = [ev, arg, p, lorom(rom[p], rom[p + 1], rom[p + 2]), 0]
                    out.append(cur)
                elif c in (0x1A, 0x1B) and cur:
                    cur[4] += 1
    return [tuple(m) for m in out]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom')
    ap.add_argument('--lines', action='store_true')
    a = ap.parse_args()
    rom = open(a.rom, 'rb').read()
    if a.lines:
        for ev, start in scripts(rom).items():
            print(f'# event {ev:02X} start $8D:{start:04X}')
            for no, cmds in script(rom, start):
                print(f'{no:04X} ' + ' '.join(f'{c:02X}:{arg:04X}' for c, arg, _ in cmds))
    for ev, rec, p, t, n in messages(rom):
        print(f'{ev:02X}\t{rec:04X}\t{p:06X}\t{t:06X}\t{n}')


if __name__ == '__main__':
    main()
