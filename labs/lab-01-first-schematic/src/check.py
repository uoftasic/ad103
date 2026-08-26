#!/usr/bin/env python3
"""AD103 Lab 00 verdict.

Reads the XSchem netlist and the ngspice log this lab just produced, and says
PASS or FAIL in one line. Nothing here is magic: it checks two things a first
schematic can plausibly get wrong.
"""
import re
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
NETLIST = LAB / "xschem" / "simulation" / "nmos_probe.spice"
LOG = LAB / "results" / "nmos_op.log"

REF_ID_UA = 501.046      # microamps, measured on iic-osic-tools:2026.04
TOL_UA = 0.5

problems = []
notes = []

# --- 1. the netlist XSchem wrote -------------------------------------------
if not NETLIST.exists():
    problems.append(f"no netlist at {NETLIST} - did 'make netlist' run?")
else:
    text = NETLIST.read_text()
    dev = [ln for ln in text.splitlines() if ln.startswith("XM1 ")]
    if not dev:
        problems.append("netlist has no XM1 line - the nfet symbol did not resolve "
                        "(check PDK=sky130A, then re-run)")
    else:
        line = dev[0]
        notes.append(f"device line : {line.strip()}")
        m = re.search(r"\bW=([^\s]+)", line)
        w = m.group(1) if m else "?"
        if w.endswith("u") or w.endswith("n") or w.endswith("m"):
            problems.append(f"W={w} carries a unit suffix - SKY130 wants plain "
                            f"microns, i.e. W=1")
        elif w != "1":
            notes.append(f"W is {w}, reference schematic uses 1 (not an error)")

# --- 2. the current ngspice computed ---------------------------------------
if not LOG.exists():
    problems.append(f"no simulation log at {LOG} - did 'make sim' run?")
else:
    log = LOG.read_text()
    if "could not find a valid modelname" in log:
        problems.append("ngspice said 'could not find a valid modelname' - W or L "
                        "landed outside every model bin. Drop the 'u'.")
    m = re.search(r"i\(vds\)\s*=\s*(-?[0-9.eE+-]+)", log)
    if not m:
        problems.append("no 'i(vds) =' line in the log - the analysis never ran")
    else:
        i_ua = abs(float(m.group(1))) * 1e6
        notes.append(f"drain current : {i_ua:.3f} uA  (reference {REF_ID_UA:.3f} uA)")
        if abs(i_ua - REF_ID_UA) > TOL_UA:
            problems.append(f"drain current {i_ua:.3f} uA is not the reference "
                            f"{REF_ID_UA:.3f} uA")

for n in notes:
    print(f"  {n}")

if problems:
    print()
    print("FAIL")
    for p in problems:
        print(f"  - {p}")
    sys.exit(1)

print()
print("PASS  netlist and operating point match the reference run")
sys.exit(0)
