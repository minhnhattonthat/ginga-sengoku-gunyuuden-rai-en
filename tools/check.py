"""check.py: the repo's one-command check (tests + text lint). The pre-commit hook runs it; exit code gates the commit.

    python -X utf8 tools/check.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

tests = subprocess.run([sys.executable, "-X", "utf8", "-m", "pytest", "-q", str(ROOT / "tests")], cwd=ROOT).returncode
lint = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools" / "lint.py")], cwd=ROOT).returncode
sys.exit(tests or lint)
