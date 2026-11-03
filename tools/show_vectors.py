"""Show SNES interrupt vectors and the reset entry for the ROM (LoROM)."""
import sys

rom = open(sys.argv[1], "rb").read()
for name, off in [("NMI", 0x7FEA), ("IRQ", 0x7FEE), ("BRK", 0x7FF2), ("COP", 0x7FF4),
                  ("ABORT", 0x7FF8), ("RESET", 0x7FFC)]:
    v = rom[off] | (rom[off + 1] << 8)
    print(f"{name:6s} @ 0x{off:04X}: ${v:04X}")
