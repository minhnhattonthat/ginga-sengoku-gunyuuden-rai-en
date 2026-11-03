Ginga Sengoku Gunyuuden Rai (SNES) - English Translation v{VERSION}
===================================================================

An unofficial fan translation of Angel's 1996 Super Famicom strategy game
"Ginga Sengoku Gunyuuden Rai" (based on Joji Manabe's manga) into English.

Translated:
- All story events, faction openings and endings, battle quotes, advisor
  and officer dialogue, and the staff credits.
- Menus, help lines, officer, planet, fleet and ship-class names, battle
  messages, save/load screens.
- Graphics text: menu headers, stat labels, buttons, the faction map, the
  battle unit-data panel, banners and the title-screen copyright line.
- Left in Japanese: the title logo (it has no official English version).

The Japanese font is replaced by a two-letters-per-cell English font.

Applying the patch
------------------
Apply GingaSengokuRai_EN_v{VERSION}.bps to an unmodified, unheadered dump with
Flips, Beat or RomPatcher.js (https://www.marcrobledo.com/RomPatcher.js/).

Base ROM: Ginga Sengoku Gunyuuden Rai (Japan).sfc (No-Intro), 2,097,152 bytes
  {BASE}
Patched ROM: 2,097,152 bytes
  {PATCHED}

If your file is 2,097,664 bytes it has a 512-byte copier header: remove it first.

Notes
-----
- Tested in Mesen 2.2.1. Start from a fresh boot: save states made with the
  Japanese game hold pointers to the old text. Battery saves made with the
  Japanese game are untested.

Known issues
------------
- A name inserted mid-sentence with an odd number of letters is followed by
  two spaces ("Ryuga  Fleet:"), a limit of the two-letter font cells.
- Some short labels are abbreviated to fit (Flagshp, Btlship, PLNT, FLT,
  Reinf.).

Report bugs at https://github.com/minhnhattonthat/ginga-sengoku-gunyuuden-rai-en/issues
(a savestate helps most).

Credits
-------
Translation, tools and hacking: minhnhattonthat, with extensive AI assistance
(Claude by Anthropic). Corrections are very welcome.

This is an unofficial fan work, not affiliated with the rights holders.
Do not distribute pre-patched ROMs.
