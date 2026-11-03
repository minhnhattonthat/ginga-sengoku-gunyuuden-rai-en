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
    # The 5-cell routine puts cells at x = 0, 12, 24, 40, 52 (4 px gap after the 3rd, hidden by kanji):
    # cell 3 -> shift 4, OR into tile 4 (x = 36); cell 4 -> shift 0, store into tile 6 (x = 48).
    jsl = {k: b'\x22' + ptr24(fetch + d) for k, d in (('s0', 0x20), ('s4', 0x51), ('st', 0x76), ('or', 0x8F))}
    for d, old, new in ((0x76, jsl['s0'], jsl['s4']), (0x81, b'\xA0', b'\x80'), (0x86, jsl['st'], jsl['or']),
                        (0x99, jsl['s4'], jsl['s0']), (0xA9, jsl['or'], jsl['st'])):
        PATCHES.append((five + d, old, new, 'label: 12-px pitch for cells 4-5'))


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

# Speech box ($81:ECE2 battle quotes, officer in $094F; $8B:DA66 advisor, officer in $0E01): JP draws the speaker name (3 cells), 『 at
# cell 3, the text from cell 4, 』 after it. English names run past 3 cells, so the 『』 draws go and the name gets
# cells 0-3; names over 7 letters use a tag from TAG_TABLE (build.speech_tags: word per officer, bank $BC pointer,
# 0 = the officer's name as usual).
TAG_TABLE = 0xBC9000
TAGNAME = NAMECOPY + len(NAMECOPY_CODE)
TAGNAME_CODE = bytes.fromhex(  # A (16-bit) = officer
    '0A'         # ASL A
    'AA'         # TAX
    'BF') + ptr24(TAG_TABLE) + bytes.fromhex(  # LDA tag,x
    'F00A'       # BEQ orig
    'AA'         # TAX
    'E220'       # SEP #$20
    'A9') + bytes([TAG_TABLE >> 16]) + bytes.fromhex(  # LDA #$BC
    '8D0709'     # STA $0907     (string bank)
    '800A'       # BRA draw
    'BFDC9000'   # orig: LDA $0090DC,x
    'AA'         # TAX
    'E220'       # SEP #$20
    '9C0709'     # STZ $0907
    '9C0609'     # draw: STZ $0906
    '9C0509'     # STZ $0905
    'A00082'     # LDY #$8200
    '2262E981'   # JSL $81E962
    '6B')        # RTL
PATCHES += [
    (TAGNAME, None, TAGNAME_CODE, 'speech box: speaker tag or name'),
    (0x81ECEA, bytes.fromhex('0AAABFDC9000'), b'\x22' + ptr24(TAGNAME) + bytes.fromhex('8013'),
     'speech box: JSL tagname / BRA $ED03'),
    (0x81ED13, bytes.fromhex('2236DD81'), b'\xEA' * 4, 'speech box: no 『'),
    (0x81ED36, bytes.fromhex('2236DD81'), b'\xEA' * 4, 'speech box: no 』'),
    # the advisor's copy of the box ($8B:DA66, officer in $0E01, 『/』 strings at $00:E4B1/E4B5)
    (0x8BDA6E, bytes.fromhex('0AAABFDC9000'), b'\x22' + ptr24(TAGNAME) + bytes.fromhex('8012'),
     'advisor box: JSL tagname / BRA $DA86'),
    (0x8BDA99, bytes.fromhex('20D0C0'), b'\xEA' * 3, 'advisor box: no 『'),
    (0x8BDAB9, bytes.fromhex('20D0C0'), b'\xEA' * 3, 'advisor box: no 』'),
]

# Ship class names in the battle tabs ($83:8FE2) and the unit-data header ($81:DC92) read the class records at
# $00:8CB0 ([layout byte: 0 = 2 kanji spread, 1 = 3, 2 = 4 cells][text]) and offset short ones. English: a copy of
# the records at CLASS_TABS (file 0x7C00, bank $00 free space; build.class_names) with layout 2 and names over 8
# letters condensed into 4 cells, and the battle tab always starts at the left.
CLASS_TABS = 0x00FC00
PATCHES += [
    (0x838FEF, bytes.fromhex('BFB08C00'), b'\xBF' + ptr24(CLASS_TABS), 'battle tab: class records copy'),
    (0x838FFD, bytes.fromhex('F011'), bytes.fromhex('8018'), 'battle tab: BRA $9017 (no centering offset)'),
    (0x81DC9C, bytes.fromhex('BFB08C00'), b'\xBF' + ptr24(CLASS_TABS), 'unit data: class records copy'),
]

# Fortress header ($81:DCD9): code builds 第 <1-2 digits> 要塞 in $0E00. English "Fort <n>": start Y at 4 so the
# digits land after three prefix cells; build.CODE_LABELS fills the "Fo"/"rt" immediates (placeholders here).
PATCHES += [
    (0x81DCDB, bytes.fromhex('A00000'), bytes.fromhex('A00400'), 'fortress header: Y = 4 (digits after "Fort ")'),
    (0x81DCE1, bytes.fromhex('99000E'), bytes.fromhex('99FC0D'), 'fortress header: "Fo" -> $0E00'),
    (0x81DD0B, bytes.fromhex('99040EA92F0399060EA9FFFF99080E'),  # $DD08 LDA #imm kept: "rt" (CODE_LABELS)
     bytes.fromhex('8D020EA93E008D040EA9FFFF99040E'), 'fortress header: "rt", blank, {end}'),
    (0x81DD26, bytes.fromhex('C900'), bytes.fromhex('C904'), 'fortress header: one digit when Y = 4'),
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
