"""Width gate / torture runs: marker build with --qa overrides, warp to a scene, shots (docs/re/boxes.md).

    python -X utf8 tools/stress.py NAME SCENE ID=TEXT [ID=TEXT ..] [--settle 300] [--every 30] [--crop x,y,w,h]

Builds build/stress_NAME.sfc (tools/build.py --marker --qa ...), cold-boots it to SCENE with the debug tool
(tools/debug/warp.lua, SETTLE frames after the scene is reached), writes shots to work/qa/stress/NAME/ and a
zoomed crop of the final frame to work/qa/stress/NAME/zoom.png. Rulers for a line: `ruler(n)` below gives
'1234567890' repeated, so the last digit still visible in the zoom is the line's length in letters.
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tools' / 'debug'))
import regen  # noqa: E402  (scene save fixtures)
from skill import SCRIPTS  # noqa: E402


def ruler(n):
    return ''.join(str((i + 1) % 10) for i in range(n))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('name')
    ap.add_argument('scene')
    ap.add_argument('qa', nargs='+', help='ID=TEXT; {ruler:N} in TEXT expands to a digit ruler of N letters')
    ap.add_argument('--settle', type=int, default=300)
    ap.add_argument('--every', type=int, default=0, help='also a shot every N frames')
    ap.add_argument('--crop', default='0,0,256,224')
    a = ap.parse_args()
    rom = ROOT / 'build' / f'stress_{a.name}.sfc'
    out = ROOT / 'work' / 'qa' / 'stress' / a.name
    cmd = [sys.executable, '-X', 'utf8', str(ROOT / 'tools' / 'build.py'), '--marker', '--out', str(rom)]
    for q in a.qa:
        while '{ruler:' in q:
            s = q.index('{ruler:')
            e = q.index('}', s)
            q = q[:s] + ruler(int(q[s + 7:e])) + q[e + 1:]
        cmd += ['--qa', q]
    subprocess.run(cmd, check=True)
    emu = [sys.executable, '-X', 'utf8', str(Path(SCRIPTS) / 'emu.py'), str(rom), '--out', str(out),
           '--sav', str(regen.sav_path(regen.scene_sav(a.scene))),
           '--script', str(ROOT / 'tools' / 'debug' / 'scenes.lua'),
           '--script', str(ROOT / 'tools' / 'debug' / 'warp.lua'),
           '--var', f"SCENE='{a.scene}'", '--var', f'SETTLE={a.settle}', '--frames', '24000', '--timeout', '1800']
    if a.every:
        emu += ['--shot-every', str(a.every)]
    r = subprocess.run(emu)
    if r.returncode:
        sys.exit(f'emu.py exit {r.returncode}')
    subprocess.run([sys.executable, '-X', 'utf8', str(Path(SCRIPTS) / 'sheet.py'), str(out / 'final.png'),
                    '--crop', a.crop, '--zoom', '3', '--out', str(out / 'zoom.png')], check=True)
    print(out / 'zoom.png')


if __name__ == '__main__':
    main()
