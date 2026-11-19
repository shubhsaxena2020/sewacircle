"""Generate an original, tiny Radiance studio environment for the landing scene."""
import math
import struct
from pathlib import Path

width, height = 64, 32
out = Path(__file__).resolve().parents[2] / 'frontend/public/models/studio.hdr'
out.parent.mkdir(parents=True, exist_ok=True)

def rgbe(red, green, blue):
    maximum = max(red, green, blue)
    if maximum < 1e-32:
        return bytes(4)
    mantissa, exponent = math.frexp(maximum)
    scale = mantissa * 256 / maximum
    return bytes((min(255, int(red * scale)), min(255, int(green * scale)),
                  min(255, int(blue * scale)), exponent + 128))

with out.open('wb') as file:
    file.write(b'#?RADIANCE\nFORMAT=32-bit_rle_rgbe\n\n-Y 32 +X 64\n')
    for y in range(height):
        v = y / height
        for x in range(width):
            u = x / width
            softbox = math.exp(-((u - .28) / .085) ** 2 - ((v - .34) / .13) ** 2) * 2.8
            edge = math.exp(-((u - .78) / .08) ** 2 - ((v - .45) / .19) ** 2) * 1.3
            base = .24 + .22 * (1 - v)
            file.write(rgbe(base + softbox + edge * 1.1,
                            base * 1.04 + softbox * .9 + edge * .75,
                            base * 1.22 + softbox * .73 + edge * .52))
print(f'{out}: {out.stat().st_size} bytes')
