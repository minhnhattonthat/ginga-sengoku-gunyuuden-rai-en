"""Map contiguous text regions: runs of clean strings, back to back, in either string format.

    python -X utf8 tools/text_regions.py ROM [--gap 32] [--min 64] > work/recon/regions.tsv

Format "msg" (event dialogue): codes with FFFF <cmd> inline commands, ended by FFFF 0000.
Format "plain" (menus, quotes): codes ended by a bare FFFF (FFFE inside = line break, guess).
A word position is text when it is a font code (< 0x528) or part of a command of the format. Regions closer than
--gap bytes merge; regions under --min bytes are dropped. Prints start, end (exclusive), size, strings, kana share.
"""
import argparse

FONT_END = 0x528


def regions(rom, align, fmt):
    out = []
    pos = align
    cur = None  # [start, end, strings, kana, codes]
    n = len(rom) - 1
    while pos < n:
        w = rom[pos] | rom[pos + 1] << 8
        step = 2
        ok = False
        end = False
        if w < FONT_END:
            ok = True
        elif w == 0xFFFE and fmt == 'plain':
            ok = True
        elif w == 0xFFFF:
            if fmt == 'plain':
                ok = end = True
            elif pos + 3 < n:
                c = rom[pos + 2] | rom[pos + 3] << 8
                argw = {0: 0, 1: 0, 2: 1, 3: 2, 5: 0, 6: 0, 7: 0, 8: 0}.get(c)
                if argw is not None:
                    ok = True
                    step = 4 + 2 * argw
                    end = c == 0
        if ok:
            if cur is None:
                cur = [pos, pos, 0, 0, 0, pos]
            if w < FONT_END:
                cur[4] += 1
                if 0x55 <= w < FONT_END:
                    cur[3] += 1
            if end:
                cur[2] += 1
                cur[1] = pos + step
                cur[5] = pos + step
        else:
            if cur is not None and cur[2]:
                out.append(cur)
            cur = None
        pos += step
    if cur is not None and cur[2]:
        out.append(cur)
    return [(s, e, k, kana, codes) for s, e, k, kana, codes, _ in out]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom')
    ap.add_argument('--gap', type=int, default=32)
    ap.add_argument('--min', type=int, default=64)
    a = ap.parse_args()
    rom = open(a.rom, 'rb').read()
    for fmt in ('msg', 'plain'):
        rs = sorted(regions(rom, 0, fmt) + regions(rom, 1, fmt))
        merged = []
        for r in rs:
            if merged and r[0] - merged[-1][1] <= a.gap and (r[0] - merged[-1][0]) % 2 == 0:
                m = merged[-1]
                merged[-1] = (m[0], max(m[1], r[1]), m[2] + r[2], m[3] + r[3], m[4] + r[4])
            else:
                merged.append(r)
        for s, e, k, kana, codes in merged:
            if e - s >= a.min and codes and kana / codes >= 0.6:
                print('%s\t%06X\t%06X\t%d\t%d\t%.2f' % (fmt, s, e, e - s, k, kana / codes))


if __name__ == '__main__':
    main()
