#!/usr/bin/env python3
"""AD103 Lab 03 - draw the curves you just measured.

    python3 src/plot_curves.py                 # writes PNGs into results/
    python3 src/plot_curves.py --outdir /tmp   # writes them somewhere else

Every figure on the AD103 MOSFET pages was produced by this script, from the
files ngspice wrote into results/. Change a deck, re-run, and your figure
changes with it - that is the whole point of shipping the plotter instead of
a picture.
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")          # no X server, no display, no surprises
import matplotlib.pyplot as plt
import numpy as np

from mosfit import (RESULTS, SPICE, deck_geometries, knee_voltage,
                    labelled_columns, read_wrdata,
                    subthreshold_slope, vth_linear_extrapolation,
                    vth_sqrt_extrapolation, derivative)

# Model vdsat for W=5 L=1 at V_DS = 1.8 V, printed by spice/op_params.spice,
# keyed by the V_GS it was measured at. Add a curve to spice/id_vds.spice and
# it simply has no entry here - it gets drawn, and left off the knee locus,
# rather than borrowing the neighbouring gate's vdsat.
VDSAT_MODEL = {0.6: 0.06482127, 0.9: 0.2557139, 1.2: 0.4424141,
               1.5: 0.6124524, 1.8: 0.7794634}
VTH_MODEL = 0.5894596

# The first five are the palette every published AD103 figure uses; the last
# three only ever appear if you add curves to a deck, so the colour cycle
# does not wrap round and give two curves the same colour.
C = ["#1b3a6b", "#1f77b4", "#2ca089", "#d97706", "#b3243b",
     "#7c3aed", "#0f766e", "#a16207"]
TRIODE_FILL = "#dbeafe"
SAT_FILL = "#fef3c7"

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "font.size": 11, "axes.grid": True, "grid.alpha": 0.3,
    "axes.spines.top": False, "axes.spines.right": False,
    "savefig.dpi": 140, "savefig.bbox": "tight",
})


def fig_id_vds(out):
    # Curve labels come from the deck, not from a list in this file. Add a
    # sixth sweep to spice/id_vds.spice and every legend below stays true.
    vds, curves = labelled_columns(SPICE / "id_vds.spice", RESULTS / "id_vds.txt")
    curves.sort(key=lambda gc: gc[0])
    fig, ax = plt.subplots(figsize=(7.8, 5.2))

    # The knee locus: for each curve, the point where the model says the
    # channel pinched off (V_DS = vdsat). Left of it is triode, right of it
    # is saturation - so shade horizontally, level of current by level.
    knee = [(VDSAT_MODEL[vg], cur) for vg, cur in curves if vg in VDSAT_MODEL]
    kx = np.array([vd for vd, _ in knee])
    ky = np.array([np.interp(vd, vds, cur) for vd, cur in knee]) * 1e6
    igrid = np.linspace(0, 760, 400)
    xsplit = np.interp(igrid, ky, kx, left=0.0, right=kx[-1] + 0.001)
    ax.fill_betweenx(igrid, 0, xsplit, color=TRIODE_FILL, zorder=0)
    ax.fill_betweenx(igrid, xsplit, 1.8, color=SAT_FILL, zorder=0)

    for n, (vg, cur) in enumerate(curves):
        c = C[n % len(C)]
        ax.plot(vds, cur * 1e6, color=c, lw=2.1)
        ax.text(1.84, cur[-1] * 1e6, f"$V_{{GS}}$ = {vg:g} V",
                color=c, fontsize=9.5, va="center", ha="left")

    ax.plot(kx, ky, "k--", lw=1.4, zorder=5)
    ax.plot(kx, ky, "ko", ms=5.5, zorder=6)
    ax.annotate("$V_{DS} = V_{DSAT}$ — the drain end\nof the channel pinches off",
                xy=(kx[min(3, len(kx)-1)], ky[min(3, len(ky)-1)]),
                xytext=(0.84, 520),
                fontsize=9.5, ha="left",
                arrowprops=dict(arrowstyle="->", color="k", lw=1.1), zorder=7)

    ax.text(0.13, 745, "TRIODE", fontsize=11, color="#1e40af",
            ha="left", va="top", weight="bold")
    ax.text(0.13, 712, "a resistor the gate sets", fontsize=9.5, color="#1e40af",
            ha="left", va="top")
    ax.text(1.60, 600, "SATURATION", fontsize=11, color="#92400e",
            ha="center", va="top", weight="bold")
    ax.text(1.60, 568, "a current source the gate sets", fontsize=9.5,
            color="#92400e", ha="center", va="top")

    ax.set_xlim(0, 2.28)
    ax.set_ylim(0, 760)
    ax.spines["bottom"].set_bounds(0, 1.8)
    ax.set_xticks(np.arange(0, 1.81, 0.2))
    ax.set_xlabel("$V_{DS}$  (V)")
    ax.set_ylabel("$I_D$  ($\\mu$A)")
    ax.set_title("SKY130 nfet_01v8, W = 5 µm, L = 1 µm — output characteristic")
    fig.savefig(out / "ad103-id-vds-family.png")
    plt.close(fig)


def fig_id_vgs(out):
    vgs, (id_lin, id_sat) = read_wrdata(RESULTS / "id_vgs.txt")
    fig, axs = plt.subplots(1, 2, figsize=(11.2, 4.4))

    axs[0].plot(vgs, id_lin * 1e6, color=C[1], lw=2)
    axs[0].set_title("$V_{DS}$ = 0.05 V — the channel as a resistor")
    axs[0].set_ylabel("$I_D$  ($\\mu$A)")
    axs[1].plot(vgs, id_sat * 1e6, color=C[4], lw=2)
    axs[1].set_title("$V_{DS}$ = 1.8 V — saturation")
    axs[1].set_ylabel("$I_D$  ($\\mu$A)")
    for a in axs:
        a.axvline(VTH_MODEL, color="0.45", ls=":", lw=1.4)
        a.annotate("model $V_{TH}$ = 0.589 V", xy=(VTH_MODEL, 0),
                   xytext=(VTH_MODEL + 0.06, 0.72), textcoords=("data", "axes fraction"),
                   fontsize=9.5, color="0.3")
        a.set_xlim(0, 1.8)
        a.set_ylim(bottom=0)
        a.set_xlabel("$V_{GS}$  (V)")
    fig.suptitle("Same transistor, same gate sweep, two drain voltages", y=1.02)
    fig.savefig(out / "ad103-id-vgs.png")
    plt.close(fig)


def fig_vth(out):
    vgs, (id_lin, id_sat) = read_wrdata(RESULTS / "id_vgs.txt")
    vth_l, vg_pk, slope, xint = vth_linear_extrapolation(vgs, id_lin, 0.05)
    vth_s, sq_slope, mask = vth_sqrt_extrapolation(vgs, id_sat)

    fig, axs = plt.subplots(1, 2, figsize=(11.2, 4.4))

    ax = axs[0]
    ax.plot(vgs, id_lin * 1e6, color=C[1], lw=2, label="measured $I_D$")
    tl = np.linspace(0.4, 1.4, 50)
    ax.plot(tl, (slope * (tl - xint)) * 1e6, "k--", lw=1.4,
            label="tangent at steepest point")
    ax.plot([vg_pk], [np.interp(vg_pk, vgs, id_lin) * 1e6], "ko", ms=6)
    ax.plot([xint], [0], "o", ms=7, color=C[4])
    ax.annotate(f"intercept {xint:.4f} V\n$-\\,V_{{DS}}/2$\n$V_{{TH}}$ = {vth_l:.4f} V",
                xy=(xint, 0), xytext=(1.02, 4), fontsize=10,
                arrowprops=dict(arrowstyle="->", lw=1.1))
    ax.set_xlim(0, 1.8)
    ax.set_ylim(-4, 70)
    ax.set_xlabel("$V_{GS}$  (V)")
    ax.set_ylabel("$I_D$  ($\\mu$A)")
    ax.set_title("Linear extrapolation, $V_{DS}$ = 0.05 V")
    ax.legend(loc="upper left", frameon=False, fontsize=9.5)

    ax = axs[1]
    root = np.sqrt(np.clip(id_sat, 0, None))
    ax.plot(vgs, root * 1e3, color=C[4], lw=2, label="$\\sqrt{I_D}$ measured")
    tl = np.linspace(0.4, 1.8, 50)
    ax.plot(tl, sq_slope * (tl - vth_s) * 1e3, "k--", lw=1.4,
            label="straight-line fit, 1.0–1.4 V")
    ax.plot(vgs[mask], root[mask] * 1e3, color="k", lw=3.2, alpha=0.35)
    ax.plot([vth_s], [0], "o", ms=7, color=C[0])
    ax.annotate(f"$V_{{TH}}$ = {vth_s:.4f} V", xy=(vth_s, 0), xytext=(0.86, 2.6),
                fontsize=10, arrowprops=dict(arrowstyle="->", lw=1.1))
    ax.axvline(VTH_MODEL, color="0.45", ls=":", lw=1.4)
    ax.text(VTH_MODEL + 0.03, 18.5, "model $V_{TH}$\n0.589 V", fontsize=9,
            color="0.35", ha="left", va="top")
    ax.set_xlim(0, 1.8)
    ax.set_ylim(-1.5, 28)
    ax.set_xlabel("$V_{GS}$  (V)")
    ax.set_ylabel("$\\sqrt{I_D}$  ($\\mathrm{mA}^{1/2}$)")
    ax.set_title("$\\sqrt{I_D}$ extrapolation, $V_{DS}$ = 1.8 V")
    ax.legend(loc="upper left", frameon=False, fontsize=9.5)

    fig.suptitle("Two honest ways to measure one threshold — and they disagree", y=1.02)
    fig.savefig(out / "ad103-vth-extraction.png")
    plt.close(fig)


def fig_subthreshold(out):
    vgs, (id_,) = read_wrdata(RESULTS / "id_vgs_log.txt")
    ss, mask = subthreshold_slope(vgs, id_)
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    ax.semilogy(vgs, id_, color=C[0], lw=2)
    ax.semilogy(vgs[mask], id_[mask], color=C[3], lw=3.6, alpha=0.85,
                label=f"fit window — {ss:.1f} mV/decade")
    ax.axvline(VTH_MODEL, color="0.45", ls=":", lw=1.4)
    ax.annotate("model $V_{TH}$ = 0.589 V", xy=(VTH_MODEL, 1e-9),
                xytext=(0.63, 1e-10), fontsize=10, color="0.3")
    ax.axvspan(0, VTH_MODEL, color="#f1f5f9", zorder=0)
    ax.text(0.29, 2e-5, 'the region a textbook\ncalls "off"',
            ha="center", fontsize=10.5, color="#334155", weight="bold")
    i0 = int(np.argmin(np.abs(vgs - 0.0)))
    i6 = int(np.argmin(np.abs(vgs - 0.6)))
    ax.plot([vgs[i0], vgs[i6]], [id_[i0], id_[i6]], "o", ms=6, color="#b91c1c",
            zorder=6)
    ax.annotate(f"{np.log10(id_[i6]/id_[i0]):.2f} decades of current\n"
                f"for 0.6 V of gate",
                xy=(0.6, id_[i6]), xytext=(0.72, 2e-8), fontsize=9.5,
                color="#b91c1c",
                arrowprops=dict(arrowstyle="->", color="#b91c1c", lw=1.0))
    ax.set_xlim(0, 1.8)
    ax.set_ylim(1e-13, 3e-3)
    ax.set_xlabel("$V_{GS}$  (V)")
    ax.set_ylabel("$I_D$  (A, log scale)")
    ax.set_title("Same sweep, log axis: $I_D$ never reaches zero")
    ax.legend(loc="lower right", frameon=False, fontsize=10)
    fig.savefig(out / "ad103-subthreshold.png")
    plt.close(fig)


def fig_gm(out):
    vgs, (id_lin, id_sat) = read_wrdata(RESULTS / "id_vgs.txt")
    gm = derivative(id_sat, vgs)
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    ax.plot(vgs, gm * 1e6, color=C[2], lw=2, label="$g_m = dI_D/dV_{GS}$ (from the sweep)")
    mv = [0.6, 0.9, 1.2, 1.5, 1.8]
    mg = [39.4793, 376.930, 634.0277, 809.7057, 915.3117]
    ax.plot(mv, mg, "ko", ms=7, mfc="none", mew=1.8,
            label="ngspice's own $g_m$ (spice/op_params.spice)")
    ax.set_xlim(0, 1.8)
    ax.set_ylim(0, 1000)
    ax.set_xlabel("$V_{GS}$  (V)")
    ax.set_ylabel("$g_m$  ($\\mu$S)")
    ax.set_title("Transconductance, measured two ways, $V_{DS}$ = 1.8 V")
    ax.legend(loc="upper left", frameon=False, fontsize=10)
    fig.savefig(out / "ad103-gm.png")
    plt.close(fig)


def fig_wl(out):
    vds, geo = read_wrdata(RESULTS / "wl_sweep.txt")
    shapes = deck_geometries(SPICE / "wl_sweep.spice")   # labels from the deck
    names = [f"{'ABCDEFGH'[n]}  {f'W={w:g} µm, L={l:g} µm':<16} (W/L = {w/l:.3g})"
             for n, (w, l) in enumerate(shapes)]
    cols = [C[1], C[2], C[0], C[4]]
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    for n, (cur, name) in enumerate(zip(geo, names)):
        ax.plot(vds, cur * 1e6, color=cols[n % len(cols)], lw=2, label=name)
    wl_ratio = (shapes[-1][0] / shapes[-1][1]) / (shapes[0][0] / shapes[0][1])
    ax.plot(vds, geo[0] * 1e6 * wl_ratio, color=C[4], lw=1.4, ls="--",
            label=f"what W/L alone predicts for {'ABCDEFGH'[len(shapes)-1]}")
    ax.set_xlim(0, 1.8)
    ax.set_ylim(0, 1500)
    ax.set_xlabel("$V_{DS}$  (V)")
    ax.set_ylabel("$I_D$  ($\\mu$A)")
    ax.set_title("$V_{GS}$ = 1.8 V — four shapes of the same transistor")
    ax.legend(loc="upper left", frameon=False, fontsize=9.5)
    fig.savefig(out / "ad103-wl-sweep.png")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=str(RESULTS))
    args = ap.parse_args()
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    figs = [(fig_id_vds, "ad103-id-vds-family.png"),
            (fig_id_vgs, "ad103-id-vgs.png"),
            (fig_vth, "ad103-vth-extraction.png"),
            (fig_subthreshold, "ad103-subthreshold.png"),
            (fig_gm, "ad103-gm.png"),
            (fig_wl, "ad103-wl-sweep.png")]
    for f, name in figs:
        f(out)
        print(f"   wrote {out}/{name}")


if __name__ == "__main__":
    main()
