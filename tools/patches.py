"""Code patches for the English build (docs/re/hooks.md), applied by tools/build.py in en and marker modes.

Each patch: (CPU address, original bytes or None = free space (must be all FF), new bytes, why). Bytes are
hand-assembled; tests/test_patches.py disassembles every one with dis65816.py and checks the originals.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import en  # noqa: E402


def off(addr):
    return ((addr & 0x7F0000) >> 1) | (addr & 0x7FFF)


def ptr24(a):
    return a.to_bytes(3, 'little')


FETCH = 0xBC8000  # free space (file 0x1E0000, banks $BC-$BF all FF)

# Label boxes (production, HQ, panels): three copies of a length-indexed layout family draw a 2..5-cell string
# with spread-out spacing for 2-4 cells and packed 12-px cells for 5 (docs/re/font.md). English uses the packed
# routine for every length; its glyph fetch then reads past {end}, so the fetch draws FFFF as a blank cell and
# holds the string pointer (callers add 2 to $1AF0 after each glyph; D = $1AF0 inside the fetch).
FETCH_CODE = bytes.fromhex(
    'B700'      # LDA [$00],y
    'C9FFFF'    # CMP #$FFFF
    'D007'      # BNE +7
    'C600'      # DEC $00     ($1AF0: the string pointer)
    'C600'      # DEC $00
    'A9') + en.SPACE.to_bytes(2, 'little') + bytes.fromhex(  # LDA #blank cell
    '0A'        # ASL A       (the two instructions the JSL replaced)
    '0A'        # ASL A
    '6B')       # RTL

JSL_FETCH = b'\x22' + ptr24(FETCH)
FAMILIES = [  # (dispatch table: 3-byte ptrs indexed 3*len, packed len-5 routine, glyph fetch, length check or None)
    (0x8EC9C6, 0x8ECB1C, 0x8ECBCA, 0x8EC9A7),
    (0x8EF2ED, 0x8EF443, 0x8EF4F1, 0x8EF2D1),
    (0xBA8BED, 0xBA8D44, 0xBA8DF2, None),
]

PATCHES = [(FETCH, None, FETCH_CODE, 'label glyph fetch: {end} -> blank cell, pointer held')]
for table, five, fetch, cpy in FAMILIES:
    PATCHES.append((fetch + 5, bytes.fromhex('B7000A0A'), JSL_FETCH, 'label glyph fetch hook'))
    for n in (1, 2, 3, 4):
        PATCHES.append((table + 3 * n, 'table', ptr24(five), f'label layout: {n} cells packed'))
    if cpy:
        PATCHES.append((cpy, bytes.fromhex('C00400'), bytes.fromhex('C00200'), 'label: draw 1-cell strings too'))


# Fleet-command name tag ($8B:C8E0): the game copies the first 2-3 cells of the officer name into $0E00 with
# {FFFE} skips for spacing. English: copy up to 5 cells as they are (X = name pointer, A/X 16-bit, DB maps $0E00
# to WRAM as in the original stores), then continue at the draw ($8B:C938).
NAMECOPY = FETCH + len(FETCH_CODE)
NAMECOPY_CODE = bytes.fromhex(
    'A00000'     # LDY #$0000
    'BF000000'   # loop: LDA $000000,x
    '99000E'     # STA $0E00,y
    'C9FFFF'     # CMP #$FFFF
    'F00F'       # BEQ done
    'E8E8C8C8'   # INX INX INY INY
    'C00A00'     # CPY #$000A (5 cells)
    'D0EB'       # BNE loop
    'A9FFFF'     # LDA #$FFFF
    '99000E'     # STA $0E00,y
    '6B')        # done: RTL
PATCHES += [
    (NAMECOPY, None, NAMECOPY_CODE, 'fleet-command name tag: copy up to 5 cells'),
    (0x8BC8ED, bytes.fromhex('BF040000C9FFFF'), b'\x22' + ptr24(NAMECOPY) + bytes.fromhex('8045EA'),
     'fleet-command name tag: JSL namecopy / BRA $C938'),
]


def apply(rom):
    """rom: build.Rom. Checks the original bytes of every patch site before writing."""
    for addr, old, new, why in PATCHES:
        o = off(addr)
        cur = rom.orig[o:o + len(new)]
        if old is None:
            assert cur == b'\xff' * len(new), f'{addr:06X}: free space is not FF ({why})'
        elif old == 'table':
            assert cur[2] == addr >> 16, f'{addr:06X}: not a pointer into this bank ({why})'
        else:
            assert cur == old, f'{addr:06X}: expected {old.hex()}, found {cur.hex()} ({why})'
        rom.write(o, new, f'patch:{addr:06X}')
