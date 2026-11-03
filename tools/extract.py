"""Extract every text string to script/<block>.json (docs/re/text.md §Extraction).

    python -X utf8 tools/extract.py            write missing script files; report jp drift in existing ones
    python -X utf8 tools/extract.py --force    also rewrite jp/ptr fields of existing files (en, notes kept by id)
    python -X utf8 tools/extract.py --list     print blocks (start, end, entries, first text)

Strings come from the pointer forms in tools/refs.py. From each target the extractor reads on through the
strings stored after it (the game reaches those by skipping ends: message chains, per-officer groups) while
they decode cleanly, are non-empty and no other target, slot or not-text range starts there. A block is a run
of strings stored back to back: the build's repack unit (tools/build.py). Entry fields:
  id    file offset of the string (hex), stable
  fmt   plain | msg | fixed (fixed-length field, no end code) ; pre = raw prefix bytes (hex) before the text
  jp    decoded text (tbl/jp.tbl, tbl/msg_codes.tbl), en = English ("" = not translated), max = original bytes
  ptr   refs to it ("p16 010DC8", "p24 06B0AC", "rel16 1D1A7C", "fixed 07061C"); read_on = no ref of its own
  tails refs that point inside it ("p16 0118BA +4"): the build keeps them only while the string is unchanged;
        tail_en {"4": "English{end}"} = the tail's own English, stored after the host's (tools/build.py)
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import refs  # noqa: E402
import text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'script'
ORIG = ROOT / 'rom' / 'Ginga Sengoku Gunyuuden Rai (Japan).sfc'
KEEP = ('en', 'tail_en', 'status', 'notes')  # translator fields: never overwritten


def not_text():
    """[(start, end, why)] from data/not_text.tsv: scanned 'text' that is data, fill or tables (reviewed)."""
    out = []
    for line in (refs.DATA / 'not_text.tsv').read_text(encoding='utf-8').splitlines():
        if line.strip() and not line.startswith('#'):
            s, e, why = line.split('\t', 2)
            out.append((int(s, 16), int(e, 16), why))
    return out


def all_refs(rom):
    return refs.collect(rom)


def parse_fmt(fmt):
    """'plain' / 'msg' / 'plain@4' (4-byte raw prefix) / 'fixed:80' -> (codec, prefix, fixed length)"""
    if fmt.startswith('fixed:'):
        return 'plain', 0, int(fmt[6:])
    codec, _, pre = fmt.partition('@')
    return codec, int(pre or 0), None


def decode(rom, off, fmt):
    """-> (jp, prefix bytes, total length)"""
    codec, pre, fixed = parse_fmt(fmt)
    tab = text.table(codec)
    if fixed:
        jp, n = tab.decode(rom, off, length=fixed)
        return jp, b'', n
    jp, n = tab.decode(rom, off + pre, maxlen=3000)
    return jp, bytes(rom[off:off + pre]), pre + n


def encode(jp, pre, fmt):
    return bytes(pre) + text.table(parse_fmt(fmt)[0]).encode(jp)


def blocks(rom):
    """[{'start', 'end', 'entries': [{'off', 'len', 'fmt', 'jp', 'pre', 'refs', 'tails', 'read_on'}]}]"""
    R = all_refs(rom)
    fmt_at = {}
    for kind, slot, t, fmt, _x in R:
        if fmt and fmt_at.setdefault(t, fmt) != fmt:
            raise ValueError(f'{t:06X}: refs disagree on the format ({fmt_at[t]} / {fmt})')
    covered_by = {}
    for kind, slot, t, fmt, _x in R:
        if not fmt and t not in fmt_at:
            covered_by[t] = 'plain'  # immediates: a string start only if no other target's string covers it
    stop = bytearray(len(rom) + 1)  # read-on never enters these
    for kind, slot, *_ in R:
        n = {'p16': 2, 'p24': 3, 'rel16': 2}.get(kind, 0)
        stop[slot:slot + n] = b'\1' * n
    for s, e, _ in not_text():
        stop[s:e] = b'\1' * (e - s)
    entries = {}
    fmt_at.update((t, f) for t, f in covered_by.items() if t not in fmt_at)
    for t in sorted(fmt_at):
        if t in entries or any(e['off'] < t < e['off'] + e['len'] for e in _near(entries, t)):
            continue
        fmt = fmt_at[t]
        pos, first = t, True
        while True:
            try:
                jp, pre, n = decode(rom, pos, fmt)
            except ValueError:
                if first:
                    raise
                break
            if not first and ('[' in jp or jp == '{end}' or any(stop[pos:pos + n]) or pos in fmt_at
                              or pos in entries):
                break
            entries[pos] = {'off': pos, 'len': n, 'fmt': fmt, 'jp': jp, 'pre': pre, 'refs': [], 'tails': [],
                            'read_on': not first}
            first = False
            pos += n
            if parse_fmt(fmt)[1] or parse_fmt(fmt)[2]:
                break  # prefixed records and fixed fields are each referenced: no read-on
    order = sorted(entries)
    for kind, slot, t, fmt, x in R:
        if t in entries:
            entries[t]['refs'].append((kind, slot, x))
            entries[t]['read_on'] = False
        else:
            host = next(entries[o] for o in reversed(order) if o < t)
            assert t < host['off'] + host['len'], f'{t:06X}: target in no string'
            host['tails'].append((kind, slot, x, t - host['off']))
    out = []
    for o in order:
        e = entries[o]
        if out and out[-1]['end'] == o:
            out[-1]['entries'].append(e)
            out[-1]['end'] = o + e['len']
        else:
            out.append({'start': o, 'end': o + e['len'], 'entries': [e]})
    return out


def _near(entries, t):
    return (e for o, e in entries.items() if t - 4000 < o < t)


def ref_str(r):
    kind, slot, x = r[:3]
    s = f'{kind} {slot:06X}'
    if kind == 'rel16':
        s += f' base {x:06X}'
    return s + (f' +{r[3]}' if len(r) > 3 else '')


def to_json(b):
    out = []
    for e in b['entries']:
        d = {'id': f'{e["off"]:06X}', 'fmt': e['fmt']}
        if e['pre']:
            d['pre'] = e['pre'].hex().upper()
        d.update(jp=e['jp'], en='', max=e['len'])
        if e['refs']:
            d['ptr'] = [ref_str(r) for r in e['refs']]
        if e['read_on']:
            d['read_on'] = True
        if e['tails']:
            d['tails'] = [ref_str(r) for r in e['tails']]
        out.append(d)
    return {'block': f'{b["start"]:06X}', 'end': f'{b["end"]:06X}', 'entries': out}


def dump(rom, force=False):
    SCRIPT.mkdir(exist_ok=True)
    wrote = drift = 0
    for b in blocks(rom):
        new = to_json(b)
        path = SCRIPT / f'{new["block"]}.json'
        if path.exists():
            old = json.loads(path.read_text(encoding='utf-8'))
            keep = {e['id']: {k: e[k] for k in KEEP if e.get(k)} for e in old['entries']}
            oldjp = {e['id']: e['jp'] for e in old['entries']}
            changed = [e['id'] for e in new['entries'] if oldjp.get(e['id']) != e['jp']]
            if not changed and len(oldjp) == len(new['entries']):
                continue
            drift += 1
            if not force:
                print(f'{path.name}: jp differs from the ROM for {changed[:5]} (re-run with --force)')
                continue
            for e in new['entries']:
                e.update(keep.get(e['id'], {}))
        path.write_text(json.dumps(new, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        wrote += 1
    return wrote, drift


def load_script():
    """{id offset: entry dict} from script/*.json"""
    out = {}
    for p in sorted(SCRIPT.glob('*.json')):
        for e in json.loads(p.read_text(encoding='utf-8'))['entries']:
            out[int(e['id'], 16)] = e
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--list', action='store_true')
    a = ap.parse_args()
    rom = ORIG.read_bytes()
    if a.list:
        for b in blocks(rom):
            e = b['entries']
            print(f'{b["start"]:06X}\t{b["end"]:06X}\t{len(e)}\t{e[0]["fmt"]}\t{e[0]["jp"][:30]}\t…{e[-1]["jp"][-20:]}')
        return
    wrote, drift = dump(rom, a.force)
    print(f'wrote {wrote} script files; {drift} with jp drift')


if __name__ == '__main__':
    main()
