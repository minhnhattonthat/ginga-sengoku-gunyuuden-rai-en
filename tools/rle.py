"""The game's word-RLE tilemap codec ($BA:82C8, docs/re/graphics.md).

Command byte C (0 = end of stream): count n = C >> 2, mode = C & 3.
  mode 0 (literal):   copy n words from the stream, one after the other.
  mode 1 (increment): write running+1, running+2, ..., running+n (n words).
  mode 2 (repeat):    write the running word n times.
  mode 3 (decrement): write running-1, running-2, ..., running-n.
The running word carries across commands (after literal it is the last literal word; after increment it is
running+n; after decrement running-n; repeat leaves it). Initial running value is [1B15] (bank byte) at the
call, but a leading literal run makes it moot in practice.

Source: 24-bit pointer at $1B10/$1B12 read by `LDA [$00],y`; dest: WRAM $7E:<offset> (DB=$1B15). The callers set
$1B10 = lo:hi (STX), $1B12 = bank (STA); see tools/rle_ptrs.py for the source list.

    python -X utf8 tools/rle.py ROM OFFSET [OUT.bin]    decode one stream, print length and word count
"""
import sys


def decode(data, pos=0, running=0, maxwords=0x10000):
    """Decode the word-RLE stream at data[pos:]. Returns (list of 16-bit words, bytes consumed)."""
    out = []
    n = len(data)
    while pos < n:
        c = data[pos]
        pos += 1
        if c == 0:
            break
        cnt = c >> 2
        mode = c & 3
        if mode == 0:
            for _ in range(cnt):
                if pos + 1 >= n:
                    break
                w = data[pos] | data[pos + 1] << 8
                pos += 2
                out.append(w)
                running = w
        elif mode == 1:
            for _ in range(cnt):
                running = (running + 1) & 0xFFFF
                out.append(running)
        elif mode == 2:
            for _ in range(cnt):
                out.append(running)
        else:
            for _ in range(cnt):
                running = (running - 1) & 0xFFFF
                out.append(running)
        if len(out) > maxwords:
            break
    return out, pos


def encode(words):
    """Inverse of decode(), byte-identical to the original tool on all 50 known streams (tests/test_identity.py).

    Its rules: start with a literal; at each word take the longest repeat/increment/decrement run (1..63 words)
    from the running word, ties in that order; otherwise extend the literal (chunks of 63); end with 0."""
    out = bytearray()
    lit = []
    running = None
    i = 0

    def flush():
        while lit:
            chunk = lit[:63]
            del lit[:63]
            out.append(len(chunk) << 2)
            for w in chunk:
                out.extend(w.to_bytes(2, 'little'))

    while i < len(words):
        best = None
        if running is not None:
            for mode, step in ((2, 0), (1, 1), (3, -1)):
                n = 0
                while n < 63 and i + n < len(words) and words[i + n] == (running + step * (n + 1)) & 0xFFFF:
                    n += 1
                if n and (best is None or n > best[1]):
                    best = (mode, n, step)
        if best:
            flush()
            mode, n, step = best
            out.append(n << 2 | mode)
            running = (running + step * n) & 0xFFFF
            i += n
        else:
            lit.append(words[i])
            running = words[i]
            i += 1
    flush()
    out.append(0)
    return bytes(out)


def main():
    rom = open(sys.argv[1], 'rb').read()
    off = int(sys.argv[2], 16)
    out, used = decode(rom, off)
    print('offset %06X words %d consumed %#x end %06X' % (off, len(out), used - off, used))
    if len(sys.argv) > 3:
        open(sys.argv[3], 'wb').write(b''.join(w.to_bytes(2, 'little') for w in out))


if __name__ == '__main__':
    main()
