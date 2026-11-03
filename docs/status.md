# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** Step 0 (repo setup) done; next is phase 1 (research and recon). No build yet.
- **Done:** MesenCE 2.2.1 in `tools/mesen/`; original ROM smoke-boots with `tools/routes/boot.txt` (Start at 550 -> faction select, verified with a shot); Lua `L.log` reaches log.txt; skill guard hook blocks `sed -i` (plugin hook loaded); pre-commit hook (`core.hooksPath tools/hooks`) rejects a failing test; `rom.sha1` pinned; `tools/check.py` + `tests/`; rulings D1-D7 recorded.
- **Next:** phase 1 recon: earlier patches/docs, text encoding (likely 2-byte kanji font), pointer tables, compression, free space, graphics-text survey (title logo, faction-select names, menus). Notes go in `docs/re/`.
- **Open bugs:** none.
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not hand-tested (headless agent run); scripted input verified.
