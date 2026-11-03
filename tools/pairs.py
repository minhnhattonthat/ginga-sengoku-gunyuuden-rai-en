"""pairs.py: reviewer input. For each batch bNNN: work/qa/review/bNNN.txt with `>> id | box | JP` / `EN` per string,
in script order (neighbours are the context). EN comes from script/*.json (what the build inserts).

    python -X utf8 tools/pairs.py [bNNN ...]   (default: every work/tl/bNNN.tsv)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import extract  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TL, OUT = ROOT / 'work/tl', ROOT / 'work/qa/review'


def main(names):
    script = extract.load_script()
    OUT.mkdir(parents=True, exist_ok=True)
    for name in names or sorted(p.stem for p in TL.glob('b[0-9][0-9][0-9].tsv')):
        out = []
        for line in (TL / f'{name}.tsv').read_text(encoding='utf-8').splitlines():
            sid, box, _, jp = line.split('\t')
            out.append(f'>> {sid} | {box} | {jp}\n   {script.get(int(sid, 16), {}).get("en", "<missing>")}\n')
        (OUT / f'{name}.txt').write_text('\n'.join(out), encoding='utf-8', newline='\n')
        print(name, len(out))


if __name__ == '__main__':
    main(sys.argv[1:])
