#!/usr/bin/env python3
"""AD103 capstone - every number, with its working shown.

    python3 src/extract.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inv import RESULTS, VDD, analyse, load, read_wrdata  # noqa: E402

bar = "  " + "-" * 74


def read_log_scalars(name: str) -> dict[str, float]:
    path = RESULTS / name
    out: dict[str, float] = {}
    if not path.exists():
        return out
    for line in path.read_text().splitlines():
        # ngspice prints scalars as "name = value"; .meas adds trig/targ
        # columns after the value, so do not anchor on end of line.
        m = re.match(r"\s*([a-z_][a-z0-9_]*)\s*=\s*([-\d.eE+]+)", line)
        if m:
            out.setdefault(m.group(1), float(m.group(2)))
    return out


# --------------------------------------------------------- 1. the two halves
drive = read_log_scalars("drive.log")
print()
print("== 1. What each transistor can do on its own   W = 1 um, L = 0.15 um")
print(bar)
if drive:
    i_n, i_p = drive["i_n"] * 1e6, drive["i_p"] * 1e6
    print(f"   NMOS, gate and drain at 1.8 V        {i_n:10.4f} uA")
    print(f"   PMOS, gate and drain at 0 V          {i_p:10.4f} uA")
    print(f"   NMOS / PMOS                          {i_n/i_p:10.4f}")
    print()
    print("   The NMOS is the same device Lab 01 measured, at the same bias, so")
    print(f"   {i_n:.3f} uA should be a number you have seen before.")
    print()
    print("   Electrons move more easily through silicon than holes do, so a")
    print("   p-channel device of the same shape is the weaker half of every")
    print(f"   CMOS gate ever built. Here that costs a factor of {i_n/i_p:.4f}.")
else:
    print("   (no results/drive.log - run 'make sweeps')")

# --------------------------------------------------- 2. the naive inverter
v = load("vtc.txt")
print()
print("== 2. The inverter you would draw first   Wn = Wp = 1 um, L = 0.15 um")
print(bar)
print(f"   switching threshold V_M      {v.vm:9.6f} V   "
      f"(V_DD/2 would be {VDD/2:.6f})")
print(f"   steepest slope               {v.gain:9.4f}     at V_in = "
      f"{v.vin_at_gain:.3f} V")
print(f"   V_IL / V_IH                  {v.vil:9.3f} / {v.vih:.3f} V")
print(f"   V_OH / V_OL                  {v.voh:9.4f} / {v.vol:.4f} V")
print(f"   noise margin high / low      {v.nmh:9.4f} / {v.nml:.4f} V")
print()
print(f"   V_M is {1000*(VDD/2 - v.vm):.1f} mV BELOW the middle of the supply. The")
print("   pull-down is stronger than the pull-up, so it takes less input")
print("   voltage than you would think to drag the output down.")
print()
print("   Note what V_M is not: it is not a threshold voltage of either device")
print(f"   (those are 769.27 mV and 510.03 mV), and it is not their average.")
print("   It is the input at which the two currents happen to be equal.")

# ------------------------------------------------------- 3. sizing it back
print()
print("== 3. Making it symmetric - two attempts")
print(bar)
d = read_wrdata(RESULTS / "vtc_ratio.txt")
widths = [1.0, 2.0, 2.5, 3.5, 4.0]
print("   Wp (um)   Wp/Wn        V_M        error vs 0.9 V      gain")
best = None
for idx, wp in enumerate(widths):
    r = analyse(d[:, 0], d[:, idx + 1])
    err = (r.vm - VDD / 2) * 1e3
    print(f"   {wp:<8g}  {wp:5.2f}   {r.vm:9.6f} V   {err:+9.2f} mV     "
          f"{r.gain:8.4f}")
    if best is None or abs(err) < abs(best[1]):
        best = (wp, err, r)
print()
if drive:
    ratio = drive["i_n"] / drive["i_p"]
    r25 = analyse(d[:, 0], d[:, 3])
    print(f"   Attempt 1 - match the saturation currents. Part 1 says the NMOS")
    print(f"   is {ratio:.4f}x stronger, so Wp = 2.5 um should balance it.")
    print(f"   It gives V_M = {r25.vm:.6f} V: "
          f"{1000*(VDD/2 - r25.vm):.1f} mV out, against "
          f"{1000*(VDD/2 - v.vm):.1f} mV before.")
    print("   Two thirds of the error gone, and a third of it still there.")
    print()
    print("   Attempt 2 - ask what V_M actually requires. At V_M the input is")
    print("   V_M, so the NMOS has V_GS = V_M and the PMOS has V_SG = 1.8 - V_M.")
    print("   Neither is at 1.8 V. Matching the currents at FULL drive is a")
    print("   different condition from matching them at the crossing point,")
    print("   and Part 1 measured the wrong one.")
    print(f"   Sweeping Wp finds it: Wp = {best[0]:g} um gives V_M = "
          f"{best[2].vm:.6f} V, {abs(best[1]):.2f} mV out.")
    print()
    print(f"   The ratio that centres this inverter is {best[0]:.1f}, not "
          f"{ratio:.2f}.")

# ------------------------------------------------- 3b. the other criterion
delay = read_log_scalars("delay.log")
print()
print("== 4. The same three inverters, timed   Wn = 1 um, 10 fF of load")
print(bar)
if delay:
    print("   Wp (um)      t_pHL         t_pLH      pull-up / pull-down")
    for wp, n in ((1.0, 1), (2.5, 2), (3.5, 3)):
        hl = delay[f"tphl{n}"] * 1e12
        lh = delay[f"tplh{n}"] * 1e12
        print(f"   {wp:<8g} {hl:9.4f} ps  {lh:9.4f} ps        {lh/hl:6.3f}")
    hl2, lh2 = delay["tphl2"] * 1e12, delay["tplh2"] * 1e12
    hl3, lh3 = delay["tphl3"] * 1e12, delay["tplh3"] * 1e12
    print()
    print("   Read the last column. The inverter whose two delays match is the")
    print(f"   Wp = 2.5 um one: {hl2:.4f} ps down against {lh2:.4f} ps up, "
          f"{100*abs(lh2-hl2)/hl2:.1f} % apart.")
    print(f"   The Wp = 3.5 um one, the one with the centred threshold, rises")
    print(f"   {100*(1-lh3/hl3):.0f} % faster than it falls.")
    print()
    print("   So the two sizings are not competing answers to one question.")
    print("   They are answers to two different ones:")
    print()
    print("     match the currents  (Wp = 2.5)  ->  equal RISE and FALL TIME")
    print("     centre V_M          (Wp = 3.5)  ->  equal NOISE MARGINS")
    print()
    print("   And the first of those closes exactly. Delay is charge divided by")
    print("   current - the same 10 fF, the same 0.9 V - so making the two")
    print("   saturation currents equal is precisely what makes the two delays")
    print("   equal. Part 1's ratio was never the wrong number. It was the right")
    print("   answer to the question Part 3 was not asking.")
else:
    print("   (no results/delay.log - run 'make sweeps')")

# --------------------------------------------------- 5. it is an amplifier
print()
print("== 5. The same circuit as an amplifier")
print(bar)
lng = load("vtc_long.txt")
print(f"   L = 0.15 um, Wn = Wp = 1 um    gain {v.gain:9.4f} at V_in = "
      f"{v.vin_at_gain:.3f} V")
print(f"   L = 0.5  um, Wn = Wp = 1 um    gain {lng.gain:9.4f} at V_in = "
      f"{lng.vin_at_gain:.3f} V")
print(f"                                  V_M  {lng.vm:9.6f} V")
print()
print(f"   {lng.gain/v.gain:.2f}x the voltage gain for 3.33x the channel length, with the")
print("   same two transistors and the same supply. Nothing about the circuit")
print("   changed except how long the channels are.")
print()
print("   Lab 04 measured why: r_o goes up with L, gain is g_m x (r_on || r_op),")
print("   and a longer device has a flatter saturation region to work in.")
print()
print("   A logic gate wants that number to be big enough to restore a signal")
print("   and does not care beyond that. An amplifier wants every bit of it.")
print("   Same two transistors, different L, different job.")

# ------------------------------------------------------ 5. what it costs
dd = read_wrdata(RESULTS / "vtc.txt")
idd = dd[:, 2] * 1e6
peak = float(idd.max())
at = float(dd[int(np.argmax(idd)), 0])
print()
print("== 6. What the switch costs while it is switching")
print(bar)
print(f"   supply current at V_in = 0 V         {idd[0]:12.6f} uA")
print(f"   supply current at V_in = 1.8 V       {idd[-1]:12.6f} uA")
print(f"   peak supply current                  {peak:12.4f} uA   "
      f"at V_in = {at:.3f} V")
print()
print("   At both ends one transistor is off and the gate draws essentially")
print("   nothing - that is the whole reason CMOS won. In between, both are on")
print(f"   at once and {peak:.1f} uA runs straight from vdd to ground doing no")
print("   useful work at all.")
print()
print("   Multiply by a hundred million gates and you have why a processor")
print("   gets hot when it computes and cool when it idles.")
print()
