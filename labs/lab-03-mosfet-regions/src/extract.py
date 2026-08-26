#!/usr/bin/env python3
"""AD103 Lab 03 - pull the parameters out of your own curves.

Reads the four result files ngspice just wrote and prints every number this
lab asks you to be able to defend. Nothing is quoted from a datasheet: each
line below is arithmetic on the sweep sitting in results/.
"""
import re

import numpy as np

from mosfit import (RESULTS, knee_voltage, read_wrdata, subthreshold_slope,
                    vth_linear_extrapolation, vth_sqrt_extrapolation, derivative)

VGS_STEPS = [0.6, 0.9, 1.2, 1.5, 1.8]
GEOM = [("A  W=5   L=1",    5.0, 1.0),
        ("B  W=10  L=1",   10.0, 1.0),
        ("C  W=5   L=2",    5.0, 2.0),
        ("D  W=1   L=0.15", 1.0, 0.15)]


def model_params():
    """Whatever spice/op_params.spice printed, as {param: [A, B, C, D]}.

    The log is optional - if you have not run `make op` yet, extract.py simply
    skips the comparison table instead of failing.
    """
    log = RESULTS / "op_params.log"
    if not log.exists():
        return None
    vals = {}
    for line in log.read_text().splitlines():
        m = re.match(r"@m\.(xm[a-d])\.msky130_fd_pr__nfet_01v8\[(\w+)\]\s*=\s*"
                     r"(-?[\d.eE+-]+)", line.strip())
        if m:
            vals.setdefault(m.group(2), {}).setdefault(m.group(1), float(m.group(3)))
    return vals


def main():
    out = {}

    # ---- 1. output characteristic -----------------------------------------
    vds, ids = read_wrdata(RESULTS / "id_vds.txt")
    print("== I_D vs V_DS   (W=5, L=1)")
    print(f"   {'V_GS':>6} {'I_D at V_DS=1.8':>16} {'knee V_DS':>11} "
          f"{'channel R at V_DS=10 mV':>25}")
    knees = []
    i10 = int(np.argmin(np.abs(vds - 0.01)))
    for vg, cur in zip(VGS_STEPS, ids):
        k = knee_voltage(vds, cur)
        knees.append(k)
        r = vds[i10] / cur[i10]
        print(f"   {vg:6.2f} {cur[-1]*1e6:13.3f} uA {k:10.2f} V "
              f"{r:20.1f} ohm")
    out["id_sat_18"] = ids[-1][-1]
    out["knees"] = knees

    # ---- 2. threshold, from the linear-region sweep -----------------------
    vgs, (id_lin, id_sat) = read_wrdata(RESULTS / "id_vgs.txt")
    vth_lin, vg_peak, slope, xint = vth_linear_extrapolation(vgs, id_lin, vds_used=0.05)
    print()
    print("== V_TH by linear extrapolation   (V_DS = 0.05 V)")
    print(f"   steepest point      V_GS = {vg_peak:.3f} V")
    print(f"   tangent slope       {slope*1e6:.3f} uA/V")
    print(f"   tangent hits zero   V_GS = {xint:.4f} V")
    print(f"   minus V_DS/2        V_TH = {vth_lin:.4f} V")
    out["vth_lin"] = vth_lin

    # ---- 3. threshold, from the saturation sweep --------------------------
    vth_sat, sq_slope, _ = vth_sqrt_extrapolation(vgs, id_sat)
    print()
    print("== V_TH by sqrt(I_D) extrapolation   (V_DS = 1.8 V, fit 1.0-1.4 V)")
    print(f"   sqrt(I_D) slope     {sq_slope*1e3:.4f} mA^0.5 / V")
    print(f"                       V_TH = {vth_sat:.4f} V")
    out["vth_sat"] = vth_sat

    # ---- 4. transconductance ----------------------------------------------
    gm = derivative(id_sat, vgs)
    print()
    print("== g_m = dI_D/dV_GS   (V_DS = 1.8 V)")
    for vg in (0.9, 1.2, 1.5, 1.8):
        i = int(np.argmin(np.abs(vgs - vg)))
        idv = id_sat[i]
        print(f"   V_GS = {vg:.2f} V   I_D = {idv*1e6:9.3f} uA   "
              f"g_m = {gm[i]*1e6:8.3f} uS   g_m/I_D = {gm[i]/idv:6.2f} /V")
    out["gm_18"] = gm[-1]

    # ---- 5. the region the textbook calls off -----------------------------
    vgl, (idl,) = read_wrdata(RESULTS / "id_vgs_log.txt")
    ss, _ = subthreshold_slope(vgl, idl)
    i0 = int(np.argmin(np.abs(vgl - 0.0)))
    i3 = int(np.argmin(np.abs(vgl - 0.3)))
    i6 = int(np.argmin(np.abs(vgl - 0.6)))
    print()
    print("== below threshold   (V_DS = 1.8 V)")
    print(f"   V_GS = 0.00 V   I_D = {idl[i0]:.4e} A")
    print(f"   V_GS = 0.30 V   I_D = {idl[i3]:.4e} A")
    print(f"   V_GS = 0.60 V   I_D = {idl[i6]:.4e} A")
    print(f"   decades from 0.0 V to 0.6 V : {np.log10(idl[i6]/idl[i0]):.2f}")
    print(f"   subthreshold slope          : {ss:.1f} mV/decade")
    out["ss"] = ss
    out["id_vgs0"] = idl[i0]

    # ---- 6. W/L ------------------------------------------------------------
    vds2, geo = read_wrdata(RESULTS / "wl_sweep.txt")
    print()
    print("== W/L is a knob   (V_GS = 1.8 V, V_DS = 1.8 V)")
    ref = geo[0][-1]
    print(f"   {'device':16} {'W/L':>6} {'I_D':>12} {'I_D/I_D(A)':>11} {'(W/L)/(W/L)_A':>14}")
    for (name, w, l), cur in zip(GEOM, geo):
        wl = w / l
        print(f"   {name:16} {wl:6.2f} {cur[-1]*1e6:9.3f} uA "
              f"{cur[-1]/ref:11.4f} {wl/5.0:14.4f}")
    out["geo_last"] = [g[-1] for g in geo]

    # ---- 7. your extraction vs the model's own opinion --------------------
    mp = model_params()
    if mp:
        print()
        print("== your number vs the model's own number   (device A)")
        rows = [("V_TH  (linear extrapolation)", vth_lin, mp["vth"]["xma"], "V"),
                ("V_TH  (sqrt extrapolation)",  vth_sat, mp["vth"]["xma"], "V"),
                ("g_m at V_GS = 1.8 V",         gm[-1] * 1e6,
                 mp["gm"]["xma"] * 1e6, "uS")]
        print(f"   {'quantity':32} {'yours':>10} {'ngspice':>10}   diff")
        for name, mine, theirs, unit in rows:
            d = 100 * (mine - theirs) / theirs
            print(f"   {name:32} {mine:10.4f} {theirs:10.4f} {unit:>3}  {d:+6.2f} %")
        print()
        print("   knee of each curve vs the model's vdsat")
        print(f"   {'V_GS':>6} {'V_GS - V_TH':>12} {'your knee':>10} {'vdsat':>9}")
        # vdsat stepped over V_GS sits at the end of the log, one block per gate
        step = re.findall(r"@m\.xma\.msky130_fd_pr__nfet_01v8\[vdsat\]\s*=\s*"
                          r"(-?[\d.eE+-]+)", (RESULTS / "op_params.log").read_text())
        stepped = [float(s) for s in step[-5:]]
        for vg, k, vd in zip(VGS_STEPS, knees, stepped):
            print(f"   {vg:6.2f} {vg - vth_lin:12.3f} {k:10.2f} {vd:9.3f}")
    return out


if __name__ == "__main__":
    main()
