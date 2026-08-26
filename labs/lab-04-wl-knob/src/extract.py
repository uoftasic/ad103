#!/usr/bin/env python3
"""AD103 Lab 04 - every number this lab teaches, with its working shown.

Four blocks, one per deck. Each one prints the raw measurement, the
prediction it is being compared against, and the arithmetic in between, so
that nothing here has to be taken on trust.

    python3 src/extract.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wl import cgg, gds, pct, read_log, vdsat, vth  # noqa: E402

w_log = read_log("w_ladder.log")
l_log = read_log("l_ladder.log")
s_log = read_log("same_ratio.log")
d_log = read_log("double_w.log")

bar = "  " + "-" * 74

# ---------------------------------------------------------------- part 1: W
print()
print("== 1. The W ladder      L = 1 um, V_GS = V_DS = 1.8 V")
print(bar)
print("   W (um)      I_D           I_D / W        W x I(W=1)     model vth")
W = [1, 2, 5, 10, 20, 50]
KEY = ["i1", "i2", "i5", "i10", "i20", "i50"]
INST = ["xw1", "xw2", "xw5", "xw10", "xw20", "xw50"]
base = w_log["i1"] * 1e6
for w, k, inst in zip(W, KEY, INST):
    i_ua = w_log[k] * 1e6
    pred = base * w
    print(f"   {w:<6g}  {i_ua:10.4f} uA  {i_ua/w:8.4f} uA/um  "
          f"{pct(pred, i_ua):+8.2f} %     {vth(w_log, inst)*1e3:8.4f} mV")
print()
print("   The 'W x I(W=1)' column scales the narrowest device up by its width")
print("   ratio. If current were exactly proportional to W, that column would")
print("   be all zeros. It is not: current per micron of width climbs "
      f"{100*((w_log['i10']*1e6/10)/(w_log['i1']*1e6/1) - 1):.1f} %")
print(f"   from W = 1 to W = 10, then falls "
      f"{100*(1 - (w_log['i50']*1e6/50)/(w_log['i10']*1e6/10)):.1f} % again by W = 50.")
print("   The vth column moves in step, and it moves the right way: a wider")
print("   device has a lower threshold, so it turns on harder at the same gate")
print(f"   voltage. From W = 1 to W = 50 the model drops vth by "
      f"{(vth(w_log,'xw1')-vth(w_log,'xw50'))*1e3:.4f} mV.")

# ------------------------------------------------------- part 2: doubling W
print()
print("== 2. Five ways to build 'twice as wide'   (W=5 L=1 is the reference)")
print(bar)
a = d_log["ia"] * 1e6
rows = [
    ("A   W=5",           "the reference",              "ia"),
    ("B   W=10",          "drawn twice as wide",        "ib"),
    ("C   W=5 + W=5",     "two of A, wired in parallel", "ic"),
    ("D   W=5 m=2",       "ngspice's own multiplier",   "id"),
    ("E   W=5 mult=2",    "the subckt's 'multiplier'",  "ie"),
    ("F   W=10 nf=2",     "folded into two fingers",    "if_"),
]
for label, note, key in rows:
    i_ua = d_log[key] * 1e6
    print(f"   {label:<16} {i_ua:10.4f} uA   {i_ua/a:6.4f} x A   {note}")
print()
print(f"   A doubled by hand   {2*a:10.4f} uA")
print()
print("   Read C and D against that last line. Two W = 5 um transistors wired")
print("   in parallel carry EXACTLY twice one of them, to every digit ngspice")
print("   prints. So does m=2, which is the same thing said in one line.")
print()
print(f"   B - the single W = 10 um device - carries {d_log['ib']*1e6 - 2*a:+.4f} uA more "
      f"({pct(d_log['ib']*1e6, 2*a):+.3f} %).")
print("   It is not two of A. It is one wider transistor, and the model knows:")
print(f"     vth(W=5)  = {vth(d_log,'xa')*1e3:.4f} mV")
print(f"     vth(W=10) = {vth(d_log,'xb')*1e3:.4f} mV   "
      f"({(vth(d_log,'xb')-vth(d_log,'xa'))*1e3:+.4f} mV)")
print()
print("   E is the trap. 'mult' is a parameter the sky130 subcircuit declares")
print("   and then never uses, so mult=2 is accepted in silence and changes")
print(f"   nothing at all: E and A agree to the digit ({d_log['ie']*1e6:.4f} uA).")
print("   XSchem's symbol gets this right - it writes BOTH 'mult=2' and 'm=2'")
print("   on the device line, and only the second one does anything.")
print()
print(f"   F is the surprise: {d_log['if_']*1e6:.4f} uA, "
      f"{pct(d_log['if_']*1e6, d_log['ib']*1e6):+.2f} % above B for the same")
print("   W and the same L. nf=2 folds the 10 um channel into two 5 um fingers")
print("   that share a drain, which changes the diffusion the current has to")
print("   cross. That is layout, not W/L, and AD104 is where you draw it.")

# ---------------------------------------------------------------- part 3: L
print()
print("== 3. The L ladder      W = 5 um, V_GS = V_DS = 1.8 V")
print(bar)
print("   L (um)      I_D         I_D x L      vs 1/L from L=1   vth      vdsat")
L = [0.15, 0.25, 0.5, 1, 2, 4]
KEY = ["j015", "j025", "j05", "j1", "j2", "j4"]
INST = ["xl015", "xl025", "xl05", "xl1", "xl2", "xl4"]
anchor = l_log["j1"] * 1e6
for l, k, inst in zip(L, KEY, INST):
    i_ua = l_log[k] * 1e6
    pred = anchor / l
    print(f"   {l:<6g}  {i_ua:10.4f} uA  {i_ua*l:9.4f}      "
          f"{pct(pred, i_ua):+8.2f} %    {vth(l_log,inst)*1e3:7.2f}  "
          f"{vdsat(l_log,inst)*1e3:7.2f} mV")
print()
print("   I_D x L would be a constant if 1/L were the law. It is not constant:")
print(f"   it runs from {l_log['j015']*1e6*0.15:.3f} at L = 0.15 um to "
      f"{l_log['j4']*1e6*4:.3f} at L = 4 um, a factor of "
      f"{(l_log['j4']*1e6*4)/(l_log['j015']*1e6*0.15):.3f}.")
print("   1/L over-promises on every short device and under-promises on every")
print("   long one, and vdsat is the receipt. Saturation begins at "
      f"{vdsat(l_log,'xl015')*1e3:.1f} mV")
print(f"   for the 0.15 um device and {vdsat(l_log,'xl4')*1e3:.1f} mV for the 4 um one, "
      "against an")
print(f"   overdrive of {(1.8-vth(l_log,'xl015'))*1e3:.1f} mV and "
      f"{(1.8-vth(l_log,'xl4'))*1e3:.1f} mV respectively. The short device gave up")
print("   on the drain voltage at a third of its overdrive.")

# --- how much of the L gap does the threshold alone explain? -----------------
print()
print("   Closing the L = 0.15 um gap, one effect at a time:")
naive = anchor / 0.15
meas = l_log["j015"] * 1e6
ov_ref = 1.8 - vth(l_log, "xl1")
ov_015 = 1.8 - vth(l_log, "xl015")
step1 = anchor * (1 / 0.15) * (ov_015 / ov_ref) ** 2
print(f"     1/L alone                                  {naive:9.3f} uA")
print(f"     1/L, with each device's own vth and (V_ov)^2 {step1:9.3f} uA")
print(f"     measured                                   {meas:9.3f} uA")
print(f"   The threshold step closes "
      f"{100*(naive-step1)/(naive-meas):.1f} % of the gap. The rest is velocity")
print("   saturation: no arithmetic on vth reaches it, and the square law has")
print("   no term for it. This is where hand calculation stops and the")
print("   simulator starts, and knowing exactly where that line is is the")
print("   most useful thing on this page.")

# ----------------------------------------------------- part 4: same W/L
print()
print("== 4. Five devices with identical W/L = 5")
print(bar)
print("   W / L        I_D          gate area      cgg        I_D per um^2")
SZ = [(0.75, 0.15), (2.5, 0.5), (5, 1), (10, 2), (20, 4)]
KEY = ["k1", "k2", "k3", "k4", "k5"]
INST = ["xs1", "xs2", "xs3", "xs4", "xs5"]
for (w, l), k, inst in zip(SZ, KEY, INST):
    i_ua = s_log[k] * 1e6
    area = w * l
    print(f"   {w:>5g} / {l:<5g} {i_ua:10.4f} uA  {area:8.4f} um^2  "
          f"{cgg(s_log,inst)*1e15:9.4f} fF  {i_ua/area:9.2f} uA/um^2")
print()
i_small, i_big = s_log["k1"] * 1e6, s_log["k5"] * 1e6
print(f"   Same ratio, every time. The current still spans a factor of "
      f"{i_big/i_small:.4f}.")
print(f"   The biggest of them buys {i_big/i_small:.2f}x the current of the smallest for")
print(f"   {(20*4)/(0.75*0.15):.1f}x the gate area and "
      f"{cgg(s_log,'xs5')/cgg(s_log,'xs1'):.1f}x the gate capacitance.")
print(f"   Per square micron of gate, the small device is "
      f"{(i_small/(0.75*0.15))/(i_big/(20*4)):.0f}x more efficient.")
print()
print("   And what you buy with the area is on the gds column of the same run:")
print(f"     gds(0.75/0.15) = {gds(s_log,'xs1')*1e6:8.3f} uS  ->  r_o = "
      f"{1/gds(s_log,'xs1')/1e3:7.2f} kohm")
print(f"     gds(20/4)      = {gds(s_log,'xs5')*1e6:8.3f} uS  ->  r_o = "
      f"{1/gds(s_log,'xs5')/1e3:7.2f} kohm")
print(f"   {1/gds(s_log,'xs5')/(1/gds(s_log,'xs1')):.2f}x the output resistance. An amplifier's gain is "
      "g_m x r_o, so that")
print("   factor is the whole reason analog designers pay for long channels.")
print()
