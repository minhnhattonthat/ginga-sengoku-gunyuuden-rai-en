"""Repo setup tests. ROM-dependent tests skip when the dump is absent (a fresh clone)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
ROM = ROOT / "rom" / "Ginga Sengoku Gunyuuden Rai (Japan).sfc"


@pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump")
def test_rom_matches_sha1():
    import check_rom
    check_rom.check()  # sys.exit on mismatch fails the test


def test_hooks_path_points_at_repo_hooks():
    assert (ROOT / "tools" / "hooks" / "pre-commit").is_file()
