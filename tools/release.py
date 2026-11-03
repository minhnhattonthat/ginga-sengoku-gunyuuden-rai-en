"""release.py: build -> tests -> smoke -> jp_left -> QA gates -> polish -> checksum -> BPS (re-applied, compared) -> zip.

    python -X utf8 tools/release.py [--version 1.0] [--force]

Stops at the first failure. Writes release/GingaSengokuRai_EN_v<version>.{bps,zip} + README.txt (local, gitignored)
and keeps the playable patched image in build/rai_en_v<version>.sfc. Refuses to overwrite an existing version's files
without --force. The debug tool is Lua only (tools/debug/*.lua), so no debug code is ever in the ROM. Never publishes.

jp_left scans every text unit the build wrote (build/writes.log `text:` rows): a run unchanged from the original
there is a string left in Japanese. Old copies of relocated blocks are dead and not scanned.
"""
import argparse
import hashlib
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SCRIPTS  # noqa: E402

ROM = ROOT / "rom" / "Ginga Sengoku Gunyuuden Rai (Japan).sfc"
BUILT = ROOT / "build" / "rai_en.sfc"
QA = ROOT / "work" / "qa"
NAME = "GingaSengokuRai_EN"
PY = [sys.executable, "-X", "utf8"]


def run(*cmd):
    print("+", " ".join(map(str, cmd)), flush=True)
    if subprocess.run([*PY, *map(str, cmd)], cwd=ROOT).returncode:
        sys.exit(f"release: failed: {Path(str(cmd[0])).name}")


def hashes(data):
    return f"CRC32 {zlib.crc32(data):08X}, MD5 {hashlib.md5(data).hexdigest()}, SHA-1 {hashlib.sha1(data).hexdigest()}"


def text_ranges():
    """--range args covering every text unit the build wrote (adjacent units merged)."""
    spans = []
    for line in (ROOT / "build" / "writes.log").read_text(encoding="utf-8").splitlines():
        off, _, new, who = line.split()
        if who.startswith("text:"):
            spans.append((int(off, 16), int(off, 16) + len(new) // 2))
    merged = []
    for a, b in sorted(spans):
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    return [x for a, b in merged for x in ("--range", f"{a:X}-{b - 1:X}")]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--force", action="store_true", help="overwrite this version's existing release files")
    a = ap.parse_args()
    out = ROOT / "release"
    patch, zpath = out / f"{NAME}_v{a.version}.bps", out / f"{NAME}_v{a.version}.zip"
    if (patch.exists() or zpath.exists()) and not a.force:
        sys.exit(f"release: {patch.name} or {zpath.name} exists; pass --force to overwrite")

    run(ROOT / "tools" / "build.py")
    run(ROOT / "tools" / "check.py")
    run(Path(SCRIPTS) / "emu.py", BUILT, "--out", QA / "smoke", "--route", ROOT / "tools" / "routes" / "boot.txt",
        "--smoke")
    run(Path(SCRIPTS) / "jp_left.py", BUILT, "--orig", ROM, "--tbl", ROOT / "tbl" / "jp.tbl", "--le16",
        "--min", "4", *text_ranges())
    # shortcut: the gates check the sheets/chapters, not that the tour shot this build; re-tour after any change
    for manifest in sorted(QA.glob("**/manifest.tsv")):
        run(Path(SCRIPTS) / "qa_gate.py", "check", manifest, manifest.parent / "verdicts")
    open_lines = [l for l in (ROOT / "docs" / "polish.md").read_text(encoding="utf-8").splitlines()
                  if l.startswith("- [ ]")]
    if open_lines:
        sys.exit(f"release: docs/polish.md has {len(open_lines)} unticked lines:\n" + "\n".join(open_lines[:10]))

    final = ROOT / "build" / f"rai_en_v{a.version}.sfc"
    run(ROOT / "tools" / "bps.py", "snes-checksum", BUILT, "--out", final)
    out.mkdir(exist_ok=True)
    run(ROOT / "tools" / "bps.py", "make", ROM, final, patch)
    work = ROOT / "work" / "release"
    work.mkdir(parents=True, exist_ok=True)
    check = work / "reapplied.sfc"
    run(ROOT / "tools" / "bps.py", "apply", ROM, patch, check)
    if check.read_bytes() != final.read_bytes():
        sys.exit("release: the re-applied patch differs from the build")
    check.unlink()
    readme = (ROOT / "docs" / "README.release.txt").read_text(encoding="utf-8")
    readme = (readme.replace("{VERSION}", a.version).replace("{BASE}", hashes(ROM.read_bytes()))
              .replace("{PATCHED}", hashes(final.read_bytes())))
    (out / "README.txt").write_text(readme, encoding="utf-8", newline="\r\n")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(patch, patch.name)
        z.write(out / "README.txt", "README.txt")
    print(f"release: {zpath.relative_to(ROOT)} (patch sha1 {hashlib.sha1(patch.read_bytes()).hexdigest()}); "
          f"playable image {final.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
