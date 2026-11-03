# Ginga Sengoku Gunyuuden Rai (SNES) English translation

Skill: translate-retro-game; `python tools/skill.py` prints its folder. Read its SKILL.md before ROM, text or QA work. `"$(python tools/skill.py)"` works in bash and PowerShell; never paste a `plugins/cache/<hash>` path.

## Commands (run from repo root)
- Build:    `python -X utf8 tools/build.py`  -> build/rai_en.sfc (checks the dump against `rom.sha1` first; phase 3+)
- Check:    `python -X utf8 tools/check.py`  (tests + lint; the pre-commit hook runs this)
- Smoke:    `python -X utf8 "$(python tools/skill.py)/scripts/emu.py" build/rai_en.sfc --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 "$(python tools/skill.py)/scripts/emu.py" build/rai_en.sfc --sav work/saves/blank.srm --out work/qa/warp --script tools/debug/scenes.lua --script tools/debug/warp.lua --var "SCENE='<name>'" --frames 24000 --timeout 1800 --sheet` (scene list + step language: `tools/debug/scenes.lua`, `warp.lua`; never ask the user to play to a scene)
- Regen:    `python -X utf8 tools/debug/regen.py [--rom build/rai_en.sfc] [--only a,b] [--jobs 6]` (every scene from a cold boot -> `work/states/<scene>.mss`, shots in `work/qa/warp/<scene>/`; save fixtures in `work/saves/`)
- Release:  `python -X utf8 tools/release.py` (patch + verify; never publish without the user)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)
- Hooks:    `git config core.hooksPath tools/hooks` once per clone.

## Paths
- Original ROM: `rom/Ginga Sengoku Gunyuuden Rai (Japan).sfc` (gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`). LoROM 2 MiB, 8 KiB SRAM.
- Emulator: this repo's own copy in `tools/mesen/` (MesenCE 2.2.1, https://github.com/nesdev-org/MesenCE/releases/download/2.2.1/Mesen_2.2.1_Windows.zip; gitignored; settings in `tools/emu-config/`). Savestates: `work/states/`.
- Text: `script/` (format: phase 4). Tables: `tbl/`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.
- Repo copies of skill tools the build imports: `tools/tbl.py`, `tools/bps.py`, `tools/romdiff.py`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the `.claude/agents/` types (translator, reviewer, visual-qa, playtester), never general-purpose: their short tool list cuts each agent's start-up context from ~43k to ~9k tokens.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- `fetch_emu.py` on this machine needs `SSL_CERT_FILE=$(python -c "import certifi;print(certifi.where())")` (Python's store lacks the issuer).
- Boot timing: Start at frame ~550 skips the intro; character/faction select shows by ~700.

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
