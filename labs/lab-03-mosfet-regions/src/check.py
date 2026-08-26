#!/usr/bin/env python3
"""AD103 Lab 03 verdict.

Recomputes the nine numbers this lab is built on and compares each with the
reference run recorded on hpretl/iic-osic-tools:2026.04. Prints them whether it
passes or fails, because the numbers are the point and a bare PASS teaches
nothing.

The first line covers results/id_vds.txt, the file the extensions in the README
tell you to edit. It reads that file's column labels out of spice/id_vds.spice
the same way extract.py does, so adding a curve keeps passing and mis-wiring a
'let ... dcN' line fails here instead of quietly printing the wrong current
under the right label.
"""
import sys

import numpy as np

from mosfit import (RESULTS, SPICE, deck_geometries, labelled_columns, read_wrdata,
                    subthreshold_slope, derivative, vth_linear_extrapolation,
                    vth_sqrt_extrapolation)

# Reference values. Every one measured, not quoted.
REF = [
    # label                              reference   tol    unit
    ("I_D  from id_vds.txt, V_GS=1.8 V",  696.275,   1.0,  "uA"),
    ("I_D  W=5 L=1, V_GS=V_DS=1.8 V",     696.275,   1.0,  "uA"),
    ("I_D  W=10 L=1, same bias",         1395.320,   2.0,  "uA"),
    ("I_D  W=5 L=2, same bias",           380.728,   1.0,  "uA"),
    ("I_D  W=1 L=0.15, same bias",        501.046,   1.0,  "uA"),
    ("V_TH by linear extrapolation",        0.6016,  0.005, "V"),
    ("V_TH by sqrt(I_D) extrapolation",     0.5159,  0.005, "V"),
    ("g_m at V_GS = 1.8 V",               914.650,   2.0,  "uS"),
    ("subthreshold slope",                 85.6,     1.0,  "mV/dec"),
]

# The shapes spice/wl_sweep.spice had when the references above were measured.
# Extension 3 tells you to change one of them, so this is checked separately and
# reported as a changed experiment, not as a wrong answer.
REF_GEOM = [(5.0, 1.0), (10.0, 1.0), (5.0, 2.0), (1.0, 0.15)]


def geometry_note():
    """Text describing how spice/wl_sweep.spice differs from the reference run."""
    shapes = deck_geometries(SPICE / "wl_sweep.spice")
    if shapes == REF_GEOM:
        return None
    lines = []
    for n in range(max(len(shapes), len(REF_GEOM))):
        mine = shapes[n] if n < len(shapes) else None
        ref = REF_GEOM[n] if n < len(REF_GEOM) else None
        if mine != ref:
            tag = "ABCDEFGH"[n]
            fmt = lambda g: "absent" if g is None else f"W={g[0]:g} L={g[1]:g}"
            lines.append(f"    device {tag}: yours is {fmt(mine)}, "
                         f"the reference measured {fmt(ref)}")
    return lines


def measure():
    _, curves = labelled_columns(SPICE / "id_vds.spice", RESULTS / "id_vds.txt")
    by_gate = dict(curves)
    if 1.8 not in by_gate:
        raise ValueError("spice/id_vds.spice no longer sweeps a V_GS = 1.8 V curve; "
                         f"it sweeps {' '.join(f'{g:g}' for g in sorted(by_gate))}")
    id_vds_18 = by_gate[1.8][-1] * 1e6

    vgs, (id_lin, id_sat) = read_wrdata(RESULTS / "id_vgs.txt")
    vgl, (idl,) = read_wrdata(RESULTS / "id_vgs_log.txt")
    _, geo = read_wrdata(RESULTS / "wl_sweep.txt")
    vth_l, *_ = vth_linear_extrapolation(vgs, id_lin, 0.05)
    vth_s, *_ = vth_sqrt_extrapolation(vgs, id_sat)
    ss, _ = subthreshold_slope(vgl, idl)
    return [id_vds_18,
            geo[0][-1] * 1e6, geo[1][-1] * 1e6, geo[2][-1] * 1e6, geo[3][-1] * 1e6,
            vth_l, vth_s, derivative(id_sat, vgs)[-1] * 1e6, ss]


def main():
    missing = [f for f in ("id_vds.txt", "id_vgs.txt", "id_vgs_log.txt",
                           "wl_sweep.txt") if not (RESULTS / f).exists()]
    if missing:
        print("FAIL")
        print(f"  - no results yet: {', '.join(missing)}")
        print("    run 'make curves' first, or just 'make'")
        return 1

    try:
        mine = measure()
    except Exception as exc:                       # noqa: BLE001 - student-facing
        print("FAIL")
        print(f"  - could not read the sweeps: {exc}")
        return 1

    note = geometry_note()
    if note:
        print("  NOTE  spice/wl_sweep.spice is not the deck the references below")
        print("        were measured on:")
        for line in note:
            print(line)
        print("        The I_D lines are therefore comparing your transistor")
        print("        against a differently-shaped one. If you are doing")
        print("        extension 3, that XX is the extension working.")
        print()

    print("  YOUR NUMBERS")
    bad = []
    for (label, ref, tol, unit), got in zip(REF, mine):
        ok = abs(got - ref) <= tol
        mark = "ok " if ok else "XX "
        print(f"  {mark} {label:34} {got:10.4f} {unit:<7} (reference {ref:.4f})")
        if not ok:
            bad.append((label, got, ref, unit))

    print()
    if bad:
        print("FAIL")
        for label, got, ref, unit in bad:
            print(f"  - {label}: got {got:.4f} {unit}, reference {ref:.4f} {unit}")
        print()
        print("  Most likely causes, in the order they actually happen:")
        print("   * a unit suffix on W or L somewhere in spice/ - it must be W=5,")
        print("     never W=5u. Run 'make wrong-units' to see what that looks like.")
        print("   * a deck edited but not re-run: 'make clean && make'")
        print("   * a different model corner: the decks load "
              "sky130.lib.spice.tt.red tt")
        print("   * if only the first line failed, you edited spice/id_vds.spice:")
        print("     check that each 'let ... = -dcN.i(vds)' names the run that")
        print("     actually swept that gate. dcN is a run counter, not a bias.")
        return 1

    print("PASS  all nine extracted parameters match the reference run")
    return 0


if __name__ == "__main__":
    sys.exit(main())
