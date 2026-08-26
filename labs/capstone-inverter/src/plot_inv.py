#!/usr/bin/env python3
"""AD103 capstone - the three figures, drawn from your own runs.

    python3 src/plot_inv.py                 # writes PNGs into results/
    python3 src/plot_inv.py --outdir /tmp
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")          # no X server, no display, no surprises
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np               # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inv import RESULTS, VDD, analyse, read_wrdata  # noqa: E402

INK = "#1b3a6b"
MEAS = "#1f77b4"
RULE = "#b3243b"
ACCENT = "#d97706"
GREEN = "#2ca089"
C5 = ["#1b3a6b", "#1f77b4", "#2ca089", "#d97706", "#b3243b"]

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "font.size": 11, "axes.grid": True, "grid.alpha": 0.3,
    "axes.spines.top": False, "axes.spines.right": False,
    "savefig.dpi": 140, "savefig.bbox": "tight",
})


def fig_vtc(out: Path) -> None:
    d = read_wrdata(RESULTS / "vtc.txt")
    v = analyse(d[:, 0], d[:, 1])
    slope = np.gradient(v.vout, v.vin)

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.6))

    ax.plot([0, VDD], [0, VDD], ":", color="#888", lw=1.3)
    ax.text(1.45, 1.52, "$V_{out} = V_{in}$", color="#888", fontsize=9,
            rotation=32)
    ax.axvline(VDD / 2, color=RULE, ls="--", lw=1.4)
    ax.text(VDD / 2 + 0.03, 1.62, "$V_{DD}/2$ = 0.900 V\nwhat you predicted",
            color=RULE, fontsize=9, va="top")
    ax.plot(v.vin, v.vout, color=MEAS, lw=2.3)
    ax.plot([v.vm], [v.vm], "o", color=INK, ms=8, zorder=5)
    ax.annotate(f"$V_M$ = {v.vm:.4f} V", xy=(v.vm, v.vm), xytext=(0.16, 0.42),
                fontsize=10, color=INK,
                arrowprops=dict(arrowstyle="->", color=INK, lw=1.2))
    ax.set_xlabel("$V_{in}$  (V)")
    ax.set_ylabel("$V_{out}$  (V)")
    ax.set_xlim(0, VDD)
    ax.set_ylim(0, VDD)
    ax.set_title("$W_n = W_p$ = 1 µm, $L$ = 0.15 µm", loc="left")

    ax2.axhline(-1, color=RULE, ls="--", lw=1.4)
    ax2.text(0.06, -2.4, "gain = −1: the edges of the\nundefined region",
             color=RULE, fontsize=9)
    ax2.plot(v.vin, slope, color=ACCENT, lw=2.1)
    ax2.plot([v.vin_at_gain], [v.gain], "o", color=INK, ms=7)
    ax2.annotate(f"{v.gain:.2f}", xy=(v.vin_at_gain, v.gain),
                 xytext=(v.vin_at_gain + 0.22, v.gain + 0.9),
                 fontsize=10, color=INK,
                 arrowprops=dict(arrowstyle="->", color=INK, lw=1.2))
    for x, lbl in ((v.vil, f"$V_{{IL}}$\n{v.vil:.3f}"),
                   (v.vih, f"$V_{{IH}}$\n{v.vih:.3f}")):
        ax2.axvline(x, color="#888", lw=1, ls=":")
        ax2.text(x, 0.6, lbl, fontsize=8.5, color=INK, ha="center")
    ax2.set_xlabel("$V_{in}$  (V)")
    ax2.set_ylabel("$dV_{out}/dV_{in}$")
    ax2.set_xlim(0, VDD)
    ax2.set_ylim(-14.5, 1.6)
    ax2.set_title("The slope of that same curve", loc="left")

    fig.tight_layout()
    fig.savefig(out / "ad103-inverter-vtc.png")
    plt.close(fig)
    print(f"   wrote {out / 'ad103-inverter-vtc.png'}")


def fig_ratio(out: Path) -> None:
    d = read_wrdata(RESULTS / "vtc_ratio.txt")
    widths = [1.0, 2.0, 2.5, 3.5, 4.0]
    res = [analyse(d[:, 0], d[:, i + 1]) for i in range(len(widths))]

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.6))

    ax.plot([0, VDD], [0, VDD], ":", color="#888", lw=1.3)
    ax.axvline(VDD / 2, color=RULE, ls="--", lw=1.3)
    for wp, r, c in zip(widths, res, C5):
        ax.plot(r.vin, r.vout, color=c, lw=2.0,
                label=f"$W_p$ = {wp:g} µm   $V_M$ = {r.vm:.4f} V")
        ax.plot([r.vm], [r.vm], "o", color=c, ms=5.5)
    ax.set_xlabel("$V_{in}$  (V)")
    ax.set_ylabel("$V_{out}$  (V)")
    ax.set_xlim(0.5, 1.25)
    ax.set_ylim(0.3, 1.5)
    ax.legend(fontsize=8.5, loc="upper right")
    ax.set_title("Zoomed on the crossing — $W_n$ = 1 µm throughout", loc="left")

    err = [(r.vm - VDD / 2) * 1e3 for r in res]
    ax2.axhline(0, color=RULE, ls="--", lw=1.4)
    ax2.plot(widths, err, "o-", color=GREEN, lw=2.1, ms=7)
    for wp, e in zip(widths, err):
        ax2.annotate(f"{e:+.1f}", (wp, e), textcoords="offset points",
                     xytext=(0, 9), ha="center", fontsize=9, color=INK)
    ax2.axvline(2.4959, color=ACCENT, ls=":", lw=1.6)
    ax2.text(2.44, -52, "2.496 — the ratio that\nmatches the two\nsaturation currents",
             color=ACCENT, fontsize=8.5, ha="right")
    ax2.set_xlabel("$W_p$  (µm)")
    ax2.set_ylabel("$V_M - V_{DD}/2$   (mV)")
    ax2.set_ylim(-72, 18)
    ax2.set_title("Matching the currents is not centring the threshold",
                  loc="left")

    fig.tight_layout()
    fig.savefig(out / "ad103-inverter-ratio.png")
    plt.close(fig)
    print(f"   wrote {out / 'ad103-inverter-ratio.png'}")


def fig_amp(out: Path) -> None:
    short = read_wrdata(RESULTS / "vtc.txt")
    long = read_wrdata(RESULTS / "vtc_long.txt")
    vs = analyse(short[:, 0], short[:, 1])
    vl = analyse(long[:, 0], long[:, 1])
    idd = short[:, 2] * 1e6

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.6))

    ax.plot(vs.vin, vs.vout, color=MEAS, lw=2.2,
            label=f"$L$ = 0.15 µm   gain {vs.gain:.1f}")
    ax.plot(vl.vin, vl.vout, color=RULE, lw=2.2,
            label=f"$L$ = 0.5 µm    gain {vl.gain:.1f}")
    ax.plot([vs.vm], [vs.vm], "o", color=MEAS, ms=7)
    ax.plot([vl.vm], [vl.vm], "o", color=RULE, ms=7)
    ax.set_xlabel("$V_{in}$  (V)")
    ax.set_ylabel("$V_{out}$  (V)")
    ax.set_xlim(0.4, 1.2)
    ax.set_ylim(0, VDD)
    ax.legend(fontsize=9, loc="upper right")
    ax.set_title("Same two transistors, longer channels", loc="left")

    ax2.plot(short[:, 0], idd, color=ACCENT, lw=2.2)
    peak = idd.max()
    at = short[int(np.argmax(idd)), 0]
    ax2.plot([at], [peak], "o", color=INK, ms=7)
    ax2.annotate(f"{peak:.2f} µA at $V_{{in}}$ = {at:.3f} V",
                 xy=(at, peak), xytext=(1.02, peak * 0.75), fontsize=9.5,
                 color=INK,
                 arrowprops=dict(arrowstyle="->", color=INK, lw=1.2))
    ax2.set_xlabel("$V_{in}$  (V)")
    ax2.set_ylabel("supply current  (µA)")
    ax2.set_xlim(0, VDD)
    ax2.set_title("What the switch costs while it is switching", loc="left")

    fig.tight_layout()
    fig.savefig(out / "ad103-inverter-gain.png")
    plt.close(fig)
    print(f"   wrote {out / 'ad103-inverter-gain.png'}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=str(RESULTS))
    args = ap.parse_args()
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    fig_vtc(out)
    fig_ratio(out)
    fig_amp(out)


if __name__ == "__main__":
    main()
