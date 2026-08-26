#!/usr/bin/env python3
"""AD103 Lab 04 - break one number on purpose.

Copies results/w_ladder.log and moves the W = 10 um current by 3 %, which is
roughly what a wrong W would do and far too small to notice by eye. Then
`make broken` feeds that copy to the checker so you can read the FAIL it
produces while you already know the answer.

Reading a FAIL is a skill. The best time to practise it is when you caused it.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wl import RESULTS  # noqa: E402

src = RESULTS / "w_ladder.log"
dst = RESULTS / "w_ladder_bent.log"
if not src.exists():
    raise SystemExit("no results/w_ladder.log - run 'make sweeps' first")

out = []
for line in src.read_text().splitlines():
    m = re.match(r"(\s*i10\s*=\s*)([-\d.eE+]+)\s*$", line)
    if m:
        bent = float(m.group(2)) * 1.03
        out.append(f"{m.group(1)}{bent:.6e}")
        print(f"  i10: {float(m.group(2)):.6e} -> {bent:.6e}  (+3 %)")
    else:
        out.append(line)
dst.write_text("\n".join(out) + "\n")
print(f"  wrote {dst}")
