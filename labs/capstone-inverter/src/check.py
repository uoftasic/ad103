#!/usr/bin/env python3
"""AD103 capstone verdict.

Recomputes nine numbers from the sweeps this lab just ran and compares each
with a reference measured on hpretl/iic-osic-tools:2026.08. Every reference
came out of a real run of these exact decks.

    python3 src/check.py
    python3 src/check.py --vtc results/vtc_broken.txt
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inv import RESULTS, VDD, analyse, read_wrdata  # noqa: E402

# ------------------------------------------------------------- references
REF = {
    "I_D  NMOS W=1 L=0.15":      (501.0462, 0.05,  "uA"),
    "I_D  PMOS W=1 L=0.15":      (200.7478, 0.05,  "uA"),
    "NMOS / PMOS drive ratio":     (2.4959, 0.001, ""),
    "V_M   Wn = Wp = 1":         (0.838027, 0.0005, "V"),
    "gain at V_M, L = 0.15":     (-13.1253, 0.05,  ""),
    "V_M   Wp = 2.5":            (0.882739, 0.0005, "V"),
    "V_M   Wp = 3.5":            (0.899865, 0.0005, "V"),
    "V_M   L = 0.5, Wn = Wp":    (0.714056, 0.0005, "V"),
    "gain at V_M, L = 0.5":     (-116.0341, 0.5,   ""),
    "t_pHL  Wp = 2.5":            (30.2508, 0.05,  "ps"),
    "t_pLH  Wp = 2.5":            (30.7067, 0.05,  "ps"),
    "t_pLH / t_pHL  Wp = 1":       (2.3341, 0.005, ""),
}

vtc_path = RESULTS / "vtc.txt"
broken = False
if "--vtc" in sys.argv:
    vtc_path = Path(sys.argv[sys.argv.index("--vtc") + 1])
    if not vtc_path.is_absolute():
        vtc_path = RESULTS.parent / vtc_path
    broken = True

def scalars(name: str) -> dict[str, float]:
    out: dict[str, float] = {}
    path = RESULTS / name
    if path.exists():
        for line in path.read_text().splitlines():
            m = re.match(r"\s*([a-z_][a-z0-9_]*)\s*=\s*([-\d.eE+]+)", line)
            if m:
                out.setdefault(m.group(1), float(m.group(2)))
    return out


drive = scalars("drive.log")
delay = scalars("delay.log")

problems: list[str] = []

d = read_wrdata(vtc_path)
try:
    v = analyse(d[:, 0], d[:, 1])
except SystemExit as exc:
    print("  The sweep ran. 1801 rows, no errors, no warnings.")
    print("  Here is what it says the output does:")
    print()
    print("    V_in       V_out          supply current")
    for x in (0.0, 0.3, 0.6, 0.9, 1.2, 1.5, 1.8):
        vo = float(np.interp(x, d[:, 0], d[:, 1]))
        ii = float(np.interp(x, d[:, 0], d[:, 2])) * 1e6 if d.shape[1] > 2 else float("nan")
        print(f"    {x:.3f} V    {vo:12.9f} V   {ii:12.6f} uA")
    print()
    print(f"  {exc}")
    print()
    print("FAIL  this circuit is not an inverter")
    sys.exit(1)

dr = read_wrdata(RESULTS / "vtc_ratio.txt")
lg = read_wrdata(RESULTS / "vtc_long.txt")
v25 = analyse(dr[:, 0], dr[:, 3])
v35 = analyse(dr[:, 0], dr[:, 4])
vl = analyse(lg[:, 0], lg[:, 1])

got = {
    "I_D  NMOS W=1 L=0.15":   drive.get("i_n", float("nan")) * 1e6,
    "I_D  PMOS W=1 L=0.15":   drive.get("i_p", float("nan")) * 1e6,
    "NMOS / PMOS drive ratio": drive.get("i_n", float("nan")) / drive.get("i_p", float("nan")),
    "V_M   Wn = Wp = 1":      v.vm,
    "gain at V_M, L = 0.15":  v.gain,
    "V_M   Wp = 2.5":         v25.vm,
    "V_M   Wp = 3.5":         v35.vm,
    "V_M   L = 0.5, Wn = Wp": vl.vm,
    "gain at V_M, L = 0.5":   vl.gain,
    "t_pHL  Wp = 2.5":        delay.get("tphl2", float("nan")) * 1e12,
    "t_pLH  Wp = 2.5":        delay.get("tplh2", float("nan")) * 1e12,
    "t_pLH / t_pHL  Wp = 1":  delay.get("tplh1", float("nan")) / delay.get("tphl1", float("nan")),
}

print("  YOUR NUMBERS")
for name, (ref, tol, unit) in REF.items():
    val = got[name]
    ok = abs(val - ref) <= tol
    print(f"  {'ok' if ok else 'XX'}  {name:<24} {val:12.4f} {unit:<3} "
          f"(reference {ref:.4f})")
    if not ok:
        problems.append(f"{name}: got {val:.6f}, reference {ref:.6f}")

# One relationship rather than one value: an inverter must invert.
print()
print(f"  V_out(0.0 V) = {v.vout[0]:.6f} V   "
      f"V_out(1.8 V) = {v.vout[-1]:.6e} V")
if not (v.vout[0] > 1.7 and v.vout[-1] < 0.1):
    problems.append("the output does not swing rail to rail - one of the two "
                    "transistors is not connected to its supply")

if problems:
    print()
    print("FAIL")
    for p in problems:
        print(f"  - {p}")
    if not broken:
        print()
        print("  Three things cause this, in order of how often:")
        print("   1. A device line edited rather than added. Restore with:")
        print("      git checkout spice/")
        print("   2. The PMOS source or body on the wrong node. It needs vdd")
        print("      on BOTH - it is the third and fourth node on its line.")
        print("   3. A unit suffix on W or L. They are plain microns: W=1.")
    sys.exit(1)

print()
print("PASS  all twelve measured values match the reference run")
sys.exit(0)
