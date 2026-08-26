#!/usr/bin/env python3
"""AD103 Lab 04 - score the predictions you wrote down.

Reads predictions.txt, reads the sweeps this lab just ran, and puts the two
side by side. It does not grade you. It shows you the size and the SIGN of
each error, because the sign is where the physics is.

    python3 src/predict.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wl import LAB, read_log, pct  # noqa: E402

FORM = LAB / "predictions.txt"

# What the W/L rule gives, anchored on the measured 696.2755 uA at W=5 L=1.
ANCHOR = 696.2755
RULE = {
    "P1": ("W=10   L=1   ", 10 / 1, "w_ladder", "i10"),
    "P2": ("W=50   L=1   ", 50 / 1, "w_ladder", "i50"),
    "P3": ("W=5    L=2   ", 5 / 2, "l_ladder", "j2"),
    "P4": ("W=5    L=0.15", 5 / 0.15, "l_ladder", "j015"),
    "P5": ("W=0.75 L=0.15", 0.75 / 0.15, "same_ratio", "k1"),
    "P6": ("W=20   L=4   ", 20 / 4, "same_ratio", "k5"),
}

logs = {n: read_log(f"{n}.log") for n in ("w_ladder", "l_ladder", "same_ratio")}

yours: dict[str, float] = {}
if FORM.exists():
    for line in FORM.read_text().splitlines():
        m = re.match(r"\s*(P[1-6])\b.*=\s*([-\d.eE+]+)\s*$", line)
        if m:
            try:
                yours[m.group(1)] = float(m.group(2))
            except ValueError:
                pass

blank = [k for k in RULE if k not in yours]
if blank:
    print(f"  predictions.txt still has {len(blank)} blank(s): "
          f"{', '.join(sorted(blank))}")
    print("  Fill them in and run 'make predict' again. Writing a number down")
    print("  and being wrong is the entire mechanism of this lab; reading the")
    print("  answers first costs you the only thing it has to give.")
    print()

print("  device            W/L    the W/L rule       measured       rule err"
      "   your guess    your err")
print("  " + "-" * 96)
for key, (label, ratio, log, vec) in RULE.items():
    ref = ANCHOR * ratio / (5 / 1)
    got = logs[log][vec] * 1e6
    mine = yours.get(key)
    mine_s = f"{mine:10.1f} uA" if mine is not None else "         --"
    mine_e = f"{pct(mine, got):+7.1f} %" if mine is not None else "       --"
    print(f"  {label}  {ratio:6.2f}  {ref:10.3f} uA  {got:10.4f} uA  "
          f"{pct(ref, got):+7.1f} %  {mine_s}  {mine_e}")

print()
print("  Read the 'rule err' column top to bottom before anything else.")
print("  P1 and P2 changed only W, and the rule is within 3 % on both.")
print("  P3 to P6 changed L, and the rule is out by 8 to 91 % - positive every")
print("  time you made L shorter, negative every time you made it longer.")
print("  W is a multiplier you can trust. L is not. Part 2 is why.")
