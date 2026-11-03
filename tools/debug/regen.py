"""Regenerate every debug-tool scene from a cold boot: shots in work/qa/warp/<scene>/, states in work/states/.

    python -X utf8 tools/debug/regen.py                 # every scene in tools/debug/scenes.lua
    python -X utf8 tools/debug/regen.py --only map_ren  # one scene (comma-separated for several)
    python -X utf8 tools/debug/regen.py --jobs 4 --keep # parallel, keep old run folders

Each scene is its own cold-boot emulator run of the original ROM through tools/debug/warp.lua, so no run depends
on another and none needs a save or a playthrough. A run passes when emu.py exits 0 and its log says
"SCENE <name> reached"; anything else exits 1 with the scene names that failed. The scene list is read from
scenes.lua itself, so it can never drift from the warps that are actually tested.
"""
import argparse
import concurrent.futures
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SCRIPTS  # noqa: E402  (emu.py path)

ROM = ROOT / "rom" / "Ginga Sengoku Gunyuuden Rai (Japan).sfc"
SCENES = ROOT / "tools" / "debug" / "scenes.lua"
OUT = ROOT / "work" / "qa" / "warp"
STATES = ROOT / "work" / "states"
FRAME_CAP = 24000  # hard stop; scenes finish on their own (warp.lua saves and exits as soon as steps are done)


def scene_names() -> list[str]:
    names = re.findall(r"^  ([a-z0-9_]+) = \{", SCENES.read_text(encoding="utf-8"), re.M)
    if not names:
        sys.exit(f"no scenes found in {SCENES}")
    return names


def run(name: str, keep: bool) -> tuple[str, bool, str]:
    out = OUT / name
    if out.exists() and not keep:
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    state = STATES / f"{name}.mss"
    cmd = [
        sys.executable, "-X", "utf8", str(Path(SCRIPTS) / "emu.py"), str(ROM),
        "--out", str(out),
        "--script", str(SCENES),
        "--script", str(ROOT / "tools" / "debug" / "warp.lua"),
        "--var", f"SCENE='{name}'",
        "--frames", str(FRAME_CAP),
        "--timeout", "1800",  # wall-clock seconds; endings + credits run ~13000 frames
        "--state-out", str(state),
        "--sheet",
    ]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = out / "log.txt"
    text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    ok = p.returncode == 0 and f"SCENE {name} reached" in text
    if not ok:
        detail = (p.stderr or p.stdout or "").strip().splitlines()
        reason = detail[-1] if detail else f"exit {p.returncode}"
        if "timed out" in text:
            reason = next(l for l in text.splitlines() if "timed out" in l)
        return name, False, reason
    frames = re.search(r"SCENE \S+ reached f(\d+)", text)
    return name, True, f"f{frames.group(1)}" if frames else "reached"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", help="comma-separated scene names")
    ap.add_argument("--jobs", type=int, default=3, help="parallel cold-boot runs (default 3)")
    ap.add_argument("--keep", action="store_true", help="do not delete an existing run folder first")
    args = ap.parse_args()

    if not ROM.exists():
        sys.exit(f"original ROM not found: {ROM}")
    names = args.only.split(",") if args.only else scene_names()
    known = set(scene_names())
    for n in names:
        if n not in known:
            sys.exit(f"unknown scene {n!r}; scenes.lua has: {', '.join(sorted(known))}")

    print(f"{len(names)} scene(s), {args.jobs} job(s)")
    failed = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(run, n, args.keep): n for n in names}
        for fut in concurrent.futures.as_completed(futures):
            name, ok, detail = fut.result()
            print(f"  {'PASS' if ok else 'FAIL'} {name:22s} {detail}", flush=True)
            if not ok:
                failed.append(name)

    if failed:
        print(f"\n{len(failed)} failed: {', '.join(failed)}")
        return 1
    print(f"\nall {len(names)} scenes reached from a cold boot")
    return 0


if __name__ == "__main__":
    sys.exit(main())
