#!/usr/bin/env python3
"""AD103 Lab 02 verdict.

Reads what this lab just produced and says PASS or FAIL in one line. Every
reference number below came from a real run of these decks inside
hpretl/iic-osic-tools:2026.08 - none of them is a textbook value.

    python3 src/check.py
    python3 src/check.py --data results/diode_iv_bent.txt
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from iv import LAB, VT, read_iv, decade_table, fit_exponential, rs_departure

# ---------------------------------------------------------------- references
# GOLDEN: same image, same deck, same seedless solver -> same digits.
REF_ROWS = 1901

# BALLPARK: currents are checked to 1 %, voltages to 1 mV. A different ngspice
# build can move the last digit or two; it cannot move these.
REF_I_AT = {0.450: 2.488707e-09,     # amps at this exact sweep voltage
            0.600: 2.194466e-07,
            0.700: 3.917437e-06}
REF_I_TOL = 0.01                     # 1 %

REF_V_AT = {1e-9: 0.419503,          # volts at this exact current
            1e-8: 0.496518,
            1e-7: 0.573602}
REF_V_TOL = 0.001                    # 1 mV

REF_MV_DECADE = 77.0367              # mV per decade, fitted 1 nA - 100 nA
REF_N = 1.29351                      # ideality factor from that slope
REF_I0_FA = 3.5864                   # femtoamps, the V=0 intercept of the fit
REF_REV_PA = -1.003559               # picoamps at -1.000 V (mostly GMIN)

MODEL_CARD_N = 1.2928                # what sky130's own model card says

problems, notes = [], []


def near(a, b, frac):
    return abs(a - b) <= abs(b) * frac


data = LAB / "results" / "diode_iv.txt"
if "--data" in sys.argv:
    data = Path(sys.argv[sys.argv.index("--data") + 1])
    if not data.is_absolute():
        data = LAB / data

if not data.exists():
    print(f"FAIL\n  - no sweep data at {data} - run 'make sweep' first")
    sys.exit(1)

v, i = read_iv(data)

# --- 1. did the sweep run to the end? ---------------------------------------
if len(v) != REF_ROWS:
    problems.append(f"sweep has {len(v)} rows, reference has {REF_ROWS} - "
                    f"did the .dc line change?")

# --- 2. three currents, at three voltages -----------------------------------
lookup = {round(a, 3): b for a, b in zip(v, i)}
for volts, ref in REF_I_AT.items():
    got = lookup.get(round(volts, 3))
    if got is None:
        problems.append(f"no sweep point at {volts:.3f} V")
        continue
    notes.append(f"I({volts:.3f} V) = {got:.6e} A   (reference {ref:.6e})")
    if not near(got, ref, REF_I_TOL):
        problems.append(f"I({volts:.3f} V) is {got:.6e} A, reference is "
                        f"{ref:.6e} A - off by "
                        f"{100*(got-ref)/ref:+.2f} %")

# --- 3. the reverse floor ----------------------------------------------------
rev_pa = i[0] * 1e12
notes.append(f"I(-1.000 V) = {rev_pa:.4f} pA  (reference {REF_REV_PA:.4f} pA)")
if abs(rev_pa - REF_REV_PA) > 0.01:
    problems.append(f"reverse current {rev_pa:.4f} pA is not the reference "
                    f"{REF_REV_PA:.4f} pA")

# --- 4. the decade voltages --------------------------------------------------
rows = decade_table(v, i)
by_current = {c: vv for c, vv, _ in rows}
for cur, ref in REF_V_AT.items():
    got = by_current.get(cur)
    if got is None:
        problems.append(f"the curve never reaches {cur:.0e} A")
        continue
    notes.append(f"V at {cur:.0e} A = {got:.6f} V   (reference {ref:.6f})")
    if abs(got - ref) > REF_V_TOL:
        problems.append(f"V at {cur:.0e} A is {got:.6f} V, reference is "
                        f"{ref:.6f} V")

# --- 5. the slope, and the parameter hiding in it ---------------------------
try:
    mvdec, n, i0, npts = fit_exponential(v, i)
except ValueError as exc:
    print("FAIL")
    print(f"  - {exc}")
    sys.exit(1)
notes.append(f"slope       = {mvdec:.4f} mV/decade over {npts} points "
             f"(reference {REF_MV_DECADE:.4f})")
notes.append(f"ideality n  = {n:.5f}          (reference {REF_N:.5f}; "
             f"sky130's model card says {MODEL_CARD_N})")
notes.append(f"I0          = {i0*1e15:.4f} fA        "
             f"(reference {REF_I0_FA:.4f} fA)")
if not near(mvdec, REF_MV_DECADE, 0.005):
    problems.append(f"slope {mvdec:.4f} mV/decade is not the reference "
                    f"{REF_MV_DECADE:.4f}")
if not near(i0 * 1e15, REF_I0_FA, 0.02):
    problems.append(f"I0 is {i0*1e15:.4f} fA, reference is {REF_I0_FA:.4f} fA "
                    f"- the whole curve is scaled wrong, which usually means "
                    f"the junction is not the size you think it is")

dep = rs_departure(v, i, mvdec, i0)
if dep:
    notes.append(f"leaves the straight line at {dep[0]:.3f} V, "
                 f"{dep[1]*1e6:.4f} uA")

# --- 6. the additivity run, if it is there ----------------------------------
log = LAB / "results" / "straight_line.log"
if log.exists():
    vals = {}
    for line in log.read_text().splitlines():
        if "=" in line and line.split("=")[0].strip().startswith("i_"):
            k, _, val = line.partition("=")
            try:
                vals[k.strip()] = float(val)
            except ValueError:
                pass
    if {"i_r_sum", "i_r_ab", "i_d_sum", "i_d_ab"} <= vals.keys():
        r_err = abs(vals["i_r_ab"] - vals["i_r_sum"]) / vals["i_r_ab"]
        ratio = vals["i_d_ab"] / vals["i_d_sum"]
        notes.append(f"resistor: superposition off by {r_err*100:.4f} %")
        notes.append(f"diode   : superposition off by a factor of {ratio:,.1f}")
        if r_err > 1e-6:
            problems.append("the resistor did not obey superposition - that "
                            "should be impossible; check straight_line.log")
        if ratio < 1000:
            problems.append(f"the diode is only {ratio:.1f}x off superposition; "
                            f"the reference run says about 15,618x")
else:
    notes.append("(no results/straight_line.log yet - run 'make line')")

for n_ in notes:
    print(f"  {n_}")

if problems:
    print("\nFAIL")
    for p in problems:
        print(f"  - {p}")
    sys.exit(1)

print("\nPASS  every number matches the reference run")
sys.exit(0)
