"""check.py: the repo's one-command check (tests + text lint). The pre-commit hook runs it; exit code gates the commit.

    python -X utf8 tools/check.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Text lint joins here once script/ exists (phase 4+).
sys.exit(subprocess.run([sys.executable, "-X", "utf8", "-m", "pytest", "-q", str(ROOT / "tests")], cwd=ROOT).returncode)
