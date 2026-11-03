"""The game's LZ codec ($00:8401, docs/re/graphics.md).

Block: u16 LE decompressed size, then groups of a flag byte (MSB first) and 8 items. Flag 0: one literal byte.
Flag 1: two bytes `lo len`; copy `len` bytes (0 = 256) from dest + (0xFF00 | lo) - 0x10000, i.e. 1..256 back.
Decoding stops when the output reaches the size, mid-group.

    python -X utf8 tools/lz.py ROM OFFSET [OUT.bin]     decompress one block, print size and bytes consumed
    python -X utf8 tools/lz.py --selftest
"""
import sys


def decompress(data, pos=0):
    """Returns (bytes, consumed)."""
    start = pos
    size = data[pos] | data[pos + 1] << 8
    pos += 2
    out = bytearray()
    while len(out) < size:
        flags = data[pos]
        pos += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                lo, n = data[pos], data[pos + 1] or 256
                pos += 2
                src = len(out) - 0x100 + lo
                if src < 0:
                    raise ValueError('copy before start at %#x' % pos)
                for _ in range(n):
                    out.append(out[src])
                    src += 1
            else:
                out.append(data[pos])
                pos += 1
        else:
            continue
    return bytes(out[:size]), pos - start


def compress(raw):
    """Greedy LZ, byte-identical to the original tool on all 162 known blocks (tests/test_identity.py).

    Its rules: copies of 2..255 bytes from 1..255 back (lo 0 and len 0 never used); backs searched nearest first,
    a later (farther) equal-length match wins, but the search stops at the first 255-byte match."""
    out = bytearray(len(raw).to_bytes(2, 'little'))
    i = 0
    while i < len(raw):
        flagpos = len(out)
        out.append(0)
        for bit in range(8):
            if i >= len(raw):
                break
            best, blen = 0, 0
            for back in range(1, min(255, i) + 1):
                s = i - back
                n = 0
                while n < 255 and i + n < len(raw) and raw[s + n] == raw[i + n]:
                    n += 1
                if n >= blen:
                    best, blen = back, n
                if n == 255:
                    break
            if blen >= 2:
                out[flagpos] |= 0x80 >> bit
                out += bytes([(0x100 - best) & 0xFF, blen & 0xFF])
                i += blen
            else:
                out.append(raw[i])
                i += 1
    return bytes(out)


def selftest():
    import random
    r = random.Random(1)
    for n in (0, 1, 7, 8, 9, 300, 5000):
        raw = bytes(r.choice(b'\x00\x00\x00\x11\x22abc') for _ in range(n))
        assert decompress(compress(raw))[0] == raw, n
    print('lz selftest ok')


if __name__ == '__main__':
    if sys.argv[1:] == ['--selftest']:
        selftest()
    else:
        rom = open(sys.argv[1], 'rb').read()
        raw, used = decompress(rom, int(sys.argv[2], 16))
        print('size %#x consumed %#x end %#x' % (len(raw), used, int(sys.argv[2], 16) + used))
        if len(sys.argv) > 3:
            open(sys.argv[3], 'wb').write(raw)
