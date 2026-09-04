#!/usr/bin/env python3
"""AD103 Lab 04 verdict.

Recomputes ten numbers from the runs this lab just did and compares each one
with a reference measured on hpretl/iic-osic-tools:2026.08. Every reference
below came out of a real run of these exact decks. None is a textbook value.

    python3 src/check.py
    python3 src/check.py --w-log results/w_ladder_bent.log
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wl import read_log, vth  # noqa: E402

# ------------------------------------------------------------- references
# Currents in microamps, thresholds in millivolts, both from the reference run.
REF = {
    "I_D  W=1  L=1":            (127.1470, 0.05, "uA"),
    "I_D  W=5  L=1":            (696.2755, 0.05, "uA"),
    "I_D  W=10 L=1":           (1395.3200, 0.05, "uA"),
    "I_D  W=50 L=1":           (6762.1370, 0.05, "uA"),
    "I_D  W=5  L=0.15":        (2644.1910, 0.05, "uA"),
    "I_D  W=5  L=4":            (197.9738, 0.05, "uA"),
    "I_D  W=0.75 L=0.15":       (364.9284, 0.05, "uA"),
    "I_D  W=20 L=4":            (798.0193, 0.05, "uA"),
    "two W=5 in parallel":     (1392.5510, 0.05, "uA"),
    "vth(W=10) - vth(W=5)":     (-12.8354, 0.20, "mV"),
}

w_path = "w_ladder.log"
if "--w-log" in sys.argv:
    w_path = Path(sys.argv[sys.argv.index("--w-log") + 1]).name

try:
    w = read_log(w_path)
    l = read_log("l_ladder.log")
    s = read_log("same_ratio.log")
    d = read_log("double_w.log")
except SystemExit as exc:
    print(f"FAIL\n  - {exc}")
    sys.exit(1)

got = {
    "I_D  W=1  L=1":        w["i1"] * 1e6,
    "I_D  W=5  L=1":        w["i5"] * 1e6,
    "I_D  W=10 L=1":        w["i10"] * 1e6,
    "I_D  W=50 L=1":        w["i50"] * 1e6,
    "I_D  W=5  L=0.15":     l["j015"] * 1e6,
    "I_D  W=5  L=4":        l["j4"] * 1e6,
    "I_D  W=0.75 L=0.15":   s["k1"] * 1e6,
    "I_D  W=20 L=4":        s["k5"] * 1e6,
    "two W=5 in parallel":  d["ic"] * 1e6,
    "vth(W=10) - vth(W=5)": (vth(d, "xb") - vth(d, "xa")) * 1e3,
}

print("  YOUR NUMBERS")
problems = []
for name, (ref, tol, unit) in REF.items():
    val = got[name]
    ok = abs(val - ref) <= max(tol, abs(ref) * 1e-4)
    print(f"  {'ok' if ok else 'XX'}  {name:<26} {val:12.4f} {unit:<3} "
          f"(reference {ref:.4f})")
    if not ok:
        problems.append((name, val, ref))

# --- one relationship, not just ten values ---------------------------------
# Two W=5 devices in parallel must carry exactly twice one of them. If that
# is not exact, something is wrong with the run, not with the physics.
two_a = 2 * d["ia"] * 1e6
par = d["ic"] * 1e6
print()
print(f"  2 x I_D(W=5)           = {two_a:12.4f} uA")
print(f"  two W=5 in parallel    = {par:12.4f} uA   "
      f"(difference {par - two_a:+.6f} uA)")
if abs(par - two_a) > 1e-3:
    problems.append(("parallel devices do not add", par, two_a))

if problems:
    print()
    print("FAIL")
    for name, val, ref in problems:
        print(f"  - {name}: got {val:.4f}, reference {ref:.4f} "
              f"({100*(val-ref)/ref:+.2f} %)")
    print()
    print("  Three things cause this, in order of how often:")
    print("   1. A unit suffix on W or L somewhere in spice/. They are plain")
    print("      microns. Check with:  grep -n 'W=[0-9.]*[a-z]' spice/*.spice")
    print("   2. You edited a deck and changed a device rather than adding one.")
    print("      Restore it with:  git checkout spice/")
    print("   3. The models did not load. Look for 'could not find a valid")
    print("      modelname' in results/*.log - that is cause 1 wearing a hat.")
    sys.exit(1)

print()
print("PASS  all ten measured values match the reference run")
sys.exit(0)
