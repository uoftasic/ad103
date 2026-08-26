#!/usr/bin/env python3
"""Make a deliberately wrong copy of the sweep, for 'make broken'.

Scales every current by 1.05 - a 5 % error, small enough that the plot still
looks perfect and large enough that the checker refuses it. This is what a
plausible-looking wrong answer feels like.
"""
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
src = LAB / "results" / "diode_iv.txt"
dst = LAB / "results" / "diode_iv_bent.txt"

out = []
for line in src.read_text().splitlines():
    p = line.split()
    if len(p) < 2:
        continue
    out.append(f"{float(p[0]):.8e} {float(p[1]) * 1.05:.8e}")
dst.write_text("\n".join(out) + "\n")
print("  wrote results/diode_iv_bent.txt (every current multiplied by 1.05)")
