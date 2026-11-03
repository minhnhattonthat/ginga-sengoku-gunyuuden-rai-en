"""Regenerate every debug-tool scene from a cold boot: shots in work/qa/warp/<scene>/, states in work/states/.

    python -X utf8 tools/debug/regen.py                 # every scene in tools/debug/scenes.lua
    python -X utf8 tools/debug/regen.py --only map_ren  # one scene (comma-separated for several)
    python -X utf8 tools/debug/regen.py --jobs 4 --keep # parallel, keep old run folders

Each scene is its own cold-boot emulator run of the original ROM (or --rom) through tools/debug/warp.lua, with
no playthrough. Every run gets an explicit battery save: blank (no save) unless the scene names a fixture with
`sav = "..."`; fixtures are made by a scene of their own (FIXTURES below: save_game saves in game) that runs
first, so the whole library still starts from nothing. A run passes when emu.py exits 0 and its log says
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


SAVES = ROOT / "work" / "saves"
# Every run boots with an explicit battery save, so a save left in tools/mesen/Saves/ can't change the title menu.
# blank = no save (the title shows START only); a fixture is made by the scene named here and copied from its run.
FIXTURES = {"nankyourou_start": "save_game"}


def scene_blocks() -> dict[str, str]:
    """scene name -> its source text in scenes.lua (up to the next scene)."""
    text = SCENES.read_text(encoding="utf-8")
    heads = list(re.finditer(r"^  ([a-z0-9_]+) = \{", text, re.M))
    if not heads:
        sys.exit(f"no scenes found in {SCENES}")
    return {m.group(1): text[m.start():(heads[i + 1].start() if i + 1 < len(heads) else len(text))]
            for i, m in enumerate(heads)}


def scene_names() -> list[str]:
    return list(scene_blocks())


def scene_sav(name: str) -> str:
    m = re.search(r'\bsav = "([a-z0-9_]+)"', scene_blocks()[name])
    return m.group(1) if m else "blank"


def sav_path(sav: str) -> Path:
    p = SAVES / f"{sav}.srm"
    if sav == "blank" and not p.exists():
        SAVES.mkdir(parents=True, exist_ok=True)
        p.write_bytes(bytes(8192))  # 8 KiB SRAM of zeros: the game sees no valid save
    return p


PROBES: list[str] = []  # --probe: extra Lua hooks appended to every run (e.g. tools/lua/lzlog.lua)


def run(name: str, keep: bool) -> tuple[str, bool, str]:
    out = OUT / name
    if out.exists() and not keep:
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    state = STATES / f"{name}.mss"
    sav = sav_path(scene_sav(name))
    if not sav.exists():
        return name, False, f"save fixture {sav.name} missing (run scene {FIXTURES.get(sav.stem, '?')} first)"
    cmd = [
        sys.executable, "-X", "utf8", str(Path(SCRIPTS) / "emu.py"), str(ROM),
        "--sav", str(sav),
        "--out", str(out),
        "--script", str(SCENES),
        "--script", str(ROOT / "tools" / "debug" / "warp.lua"),
        "--var", f"SCENE='{name}'",
        "--frames", str(FRAME_CAP),
        "--timeout", "1800",  # wall-clock seconds; endings + credits run ~13000 frames
        "--state-out", str(state),
        "--sheet",
    ]
    for probe in PROBES:
        cmd += ["--script", probe]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = out / "log.txt"
    text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    ok = p.returncode == 0 and f"SCENE {name} reached" in text
    if not ok:
        detail = (p.stderr or p.stdout or "").strip().splitlines()
        reason = detail[-1] if detail else f"exit {p.returncode}"
        lua_err = [l for l in (p.stdout or "").splitlines() if "Lua error" in l]
        if lua_err:
            reason = lua_err[-1]
        return name, False, reason
    for fixture, maker in FIXTURES.items():
        if maker == name:  # emu.py leaves the game's SRAM in --out as <rom stem>.srm
            shutil.copyfile(out / f"{ROM.stem}.srm", SAVES / f"{fixture}.srm")
    frames = re.search(r"SCENE \S+ reached f(\d+)", text)
    return name, True, f"f{frames.group(1)}" if frames else "reached"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", help="comma-separated scene names")
    ap.add_argument("--jobs", type=int, default=3, help="parallel cold-boot runs (default 3)")
    ap.add_argument("--keep", action="store_true", help="do not delete an existing run folder first")
    ap.add_argument("--rom", help="ROM to warp on (default: the original); e.g. build/rai_en.sfc")
    ap.add_argument("--probe", action="append", default=[], help="extra --script for every run (repeatable)")
    args = ap.parse_args()
    PROBES.extend(str(Path(p).resolve()) for p in args.probe)

    global ROM
    if args.rom:
        ROM = Path(args.rom).resolve()
    if not ROM.exists():
        sys.exit(f"ROM not found: {ROM}")
    names = args.only.split(",") if args.only else scene_names()
    known = set(scene_names())
    for n in names:
        if n not in known:
            sys.exit(f"unknown scene {n!r}; scenes.lua has: {', '.join(sorted(known))}")

    # Fixture makers run first (a scene needing a missing fixture pulls its maker in), then everything else.
    makers = [m for f, m in FIXTURES.items() if m in names or
              (not (SAVES / f"{f}.srm").exists() and any(scene_sav(n) == f for n in names))]
    rest = [n for n in names if n not in makers]
    print(f"{len(makers) + len(rest)} scene(s), {args.jobs} job(s)")
    failed = []
    for batch in (makers, rest):
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
            futures = {pool.submit(run, n, args.keep): n for n in batch}
            for fut in concurrent.futures.as_completed(futures):
                name, ok, detail = fut.result()
                print(f"  {'PASS' if ok else 'FAIL'} {name:22s} {detail}", flush=True)
                if not ok:
                    failed.append(name)
    names = makers + rest

    if failed:
        print(f"\n{len(failed)} failed: {', '.join(failed)}")
        return 1
    print(f"\nall {len(names)} scenes reached from a cold boot")
    return 0


if __name__ == "__main__":
    sys.exit(main())
