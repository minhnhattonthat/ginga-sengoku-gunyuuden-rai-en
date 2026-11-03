"""First-guess kanji for font codes: template-match each 12x12 glyph against MS Gothic's 12 px bitmaps, then use
the font's JIS ordering (it is stored in JIS order, in a few runs) to pick, among the top candidates, the one that
fits between its neighbours.

    python -X utf8 tools/font_match.py ROM --first 0xFB --last 0x533 [--font C:/Windows/Fonts/msgothic.ttc] > out.tsv

Output: code, chosen char, score, top-3 candidates with scores, flag ("order" when the order rule changed the pick,
"low" when the best score is weak). A first guess only: read flagged rows against the zoomed sheet (font_sheet.py).
"""
import argparse

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from font_sheet import glyph


def jis_kanji():
    out = []
    for hi in list(range(0x88, 0xA0)) + list(range(0xE0, 0xEB)):
        for lo in list(range(0x40, 0x7F)) + list(range(0x80, 0xFD)):
            try:
                c = bytes([hi, lo]).decode('cp932')
            except UnicodeDecodeError:
                continue
            if '\u4e00' <= c <= '\u9fff':
                out.append(c)
    return out  # in JIS order


def bitmap(font, ch):
    im = Image.new('1', (14, 14), 0)
    ImageDraw.Draw(im).text((1, 1), ch, font=font, fill=1)
    return np.array(im, dtype=np.float32).reshape(-1)


def shifts(g):
    """g: 12x12 0/1 rows -> (9, 196) array, the glyph at every 1-px offset inside a 14x14 frame."""
    out = []
    for dy in range(3):
        for dx in range(3):
            m = np.zeros((14, 14), np.float32)
            m[dy:dy + 12, dx:dx + 12] = np.array(g, np.float32)
            out.append(m.reshape(-1))
    return np.stack(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom')
    ap.add_argument('--first', type=lambda s: int(s, 0), default=0xFB)
    ap.add_argument('--last', type=lambda s: int(s, 0), default=0x533)
    ap.add_argument('--base', type=lambda s: int(s, 0), default=0xA8000)
    ap.add_argument('--font', default='C:/Windows/Fonts/msgothic.ttc')
    a = ap.parse_args()
    rom = open(a.rom, 'rb').read()
    font = ImageFont.truetype(a.font, 12)
    cands = jis_kanji()
    order = {c: i for i, c in enumerate(cands)}
    B = np.stack([bitmap(font, c) for c in cands])  # (n, 196)
    bsum = B.sum(1)
    codes = list(range(a.first, a.last + 1))
    S = np.zeros((len(codes), len(cands)), np.float32)
    for i, code in enumerate(codes):
        G = shifts(glyph(rom, a.base, code))  # (9, 196)
        S[i] = (2 * (G @ B.T) / (G.sum(1)[:, None] + bsum[None, :] + 1e-9)).max(0)
    # DP: picks increase in JIS order within a run; starting a new run costs PENALTY.
    PENALTY = 0.6
    n, m = S.shape
    best = np.zeros((n, m), np.float32)
    back = np.zeros((n, m), np.int32)  # previous j, or -1 - j for a run restart
    best[0] = S[0]
    for i in range(1, n):
        prev = best[i - 1]
        pm = np.maximum.accumulate(np.concatenate([[-1e9], prev[:-1]]))  # max over j' < j
        arg = np.zeros(m, np.int32)
        cur = -1
        for j in range(1, m):  # argmax of prefix, vectorised poorly but m*n is small enough
            if cur < 0 or prev[j - 1] >= prev[cur]:
                cur = j - 1
            arg[j] = cur
        g = int(prev.argmax())
        restart = prev[g] - PENALTY
        use_r = restart > pm
        best[i] = S[i] + np.where(use_r, restart, pm)
        back[i] = np.where(use_r, -1 - g, arg)
    j = int(best[-1].argmax())
    path = [0] * n
    for i in range(n - 1, -1, -1):
        path[i] = j
        b = back[i, j]
        j = b if b >= 0 else -1 - b
    for i, code in enumerate(codes):
        idx = np.argsort(-S[i])[:3]
        pick = cands[path[i]]
        restart = i and back[i, path[i]] < 0
        flag = ' '.join(f for f, on in (('run', restart), ('differs', pick != cands[idx[0]]),
                                         ('low', S[i, path[i]] < 0.7)) if on)
        print('%03X\t%s\t%.2f\t%s\t%s' % (code, pick, S[i, path[i]],
                                          ' '.join('%s%.2f' % (cands[k], S[i, k]) for k in idx), flag))


if __name__ == '__main__':
    main()
