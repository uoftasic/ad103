#!/usr/bin/env python3
"""AD103 Lab 04 - draw the three figures from the runs you just did.

    python3 src/plot_wl.py                 # writes PNGs into results/
    python3 src/plot_wl.py --outdir /tmp   # writes them somewhere else

Every W/L figure in the AD103 docs came out of this script, reading the logs
ngspice wrote into results/. Change a deck, re-run, and the figure changes
with it - which is why the plotter ships instead of the picture.
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
from wl import RESULTS, cgg, read_log  # noqa: E402

INK = "#1b3a6b"
MEAS = "#1f77b4"
RULE = "#b3243b"
ACCENT = "#d97706"
GREEN = "#2ca089"

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "font.size": 11, "axes.grid": True, "grid.alpha": 0.3,
    "axes.spines.top": False, "axes.spines.right": False,
    "savefig.dpi": 140, "savefig.bbox": "tight",
})


def fig_w_ladder(out: Path) -> None:
    log = read_log("w_ladder.log")
    w = np.array([1, 2, 5, 10, 20, 50], dtype=float)
    i = np.array([log[k] for k in ("i1", "i2", "i5", "i10", "i20", "i50")]) * 1e6

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.4))

    anchor = i[2] / w[2]                       # uA per micron, from W = 5
    ax.plot(w, anchor * w, "--", color=RULE, lw=1.6,
            label=f"proportional to $W$  ({anchor:.2f} µA/µm, from $W$ = 5)")
    ax.plot(w, i, "o-", color=MEAS, lw=2.1, ms=6, label="measured")
    ax.set_xlabel("$W$  (µm)")
    ax.set_ylabel("$I_D$  (µA)")
    ax.set_title("The W ladder — $L$ = 1 µm, $V_{GS}=V_{DS}=1.8$ V", loc="left")
    ax.legend(fontsize=9, loc="upper left")

    ax2.axhline(i[2] / w[2], color=RULE, ls="--", lw=1.6)
    ax2.plot(w, i / w, "o-", color=ACCENT, lw=2.1, ms=6)
    for wi, y in zip(w, i / w):
        ax2.annotate(f"{y:.2f}", (wi, y), textcoords="offset points",
                     xytext=(0, 8), ha="center", fontsize=8.5, color=INK)
    ax2.set_xscale("log")
    ax2.set_xticks(w)
    ax2.set_xticklabels([f"{v:g}" for v in w])
    ax2.set_xlabel("$W$  (µm), log scale")
    ax2.set_ylabel("$I_D / W$  (µA/µm)")
    ax2.set_ylim(120, 145)
    ax2.set_title("Current per micron of width is not a constant", loc="left")

    fig.tight_layout()
    fig.savefig(out / "ad103-w-ladder.png")
    plt.close(fig)
    print(f"   wrote {out / 'ad103-w-ladder.png'}")


def fig_l_ladder(out: Path) -> None:
    log = read_log("l_ladder.log")
    l = np.array([0.15, 0.25, 0.5, 1, 2, 4])
    i = np.array([log[k] for k in
                  ("j015", "j025", "j05", "j1", "j2", "j4")]) * 1e6

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.4))

    anchor = i[3]                              # L = 1 um
    fine = np.linspace(0.15, 4, 300)
    ax.plot(fine, anchor / fine, "--", color=RULE, lw=1.6,
            label="proportional to $1/L$ (from $L$ = 1 µm)")
    ax.plot(l, i, "o-", color=MEAS, lw=2.1, ms=6, label="measured")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks(l)
    ax.set_xticklabels([f"{v:g}" for v in l])
    ax.set_xlabel("$L$  (µm), log scale")
    ax.set_ylabel("$I_D$  (µA), log scale")
    ax.set_title("The L ladder — $W$ = 5 µm", loc="left")
    ax.legend(fontsize=9, loc="lower left")
    ax.annotate(f"{i[0]:.0f} µA measured, against\n{anchor/l[0]:.0f} µA the rule predicts",
                xy=(l[0], i[0]), xytext=(0.55, 2600), fontsize=9, color=INK,
                ha="left",
                arrowprops=dict(arrowstyle="->", color=INK, lw=1.1,
                                connectionstyle="arc3,rad=0.25"))

    ax2.axhline(anchor, color=RULE, ls="--", lw=1.6,
                label="what $1/L$ would make constant")
    ax2.plot(l, i * l, "o-", color=GREEN, lw=2.1, ms=6)
    for li, y in zip(l, i * l):
        ax2.annotate(f"{y:.0f}", (li, y), textcoords="offset points",
                     xytext=(0, 9), ha="center", fontsize=8.5, color=INK)
    ax2.set_xscale("log")
    ax2.set_xticks(l)
    ax2.set_xticklabels([f"{v:g}" for v in l])
    ax2.set_xlabel("$L$  (µm), log scale")
    ax2.set_ylabel(r"$I_D \times L$   (µA·µm)")
    ax2.set_ylim(350, 850)
    ax2.legend(fontsize=9, loc="lower right")
    ax2.set_title("It is not a constant. It doubles.", loc="left")

    fig.tight_layout()
    fig.savefig(out / "ad103-l-ladder.png")
    plt.close(fig)
    print(f"   wrote {out / 'ad103-l-ladder.png'}")


def fig_same_ratio(out: Path) -> None:
    log = read_log("same_ratio.log")
    sizes = [(0.75, 0.15), (2.5, 0.5), (5, 1), (10, 2), (20, 4)]
    keys = ["k1", "k2", "k3", "k4", "k5"]
    insts = ["xs1", "xs2", "xs3", "xs4", "xs5"]
    i = np.array([log[k] for k in keys]) * 1e6
    area = np.array([w * l for w, l in sizes])
    cap = np.array([cgg(log, n) for n in insts]) * 1e15
    labels = [f"{w:g}/{l:g}" for w, l in sizes]

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.4))

    x = np.arange(len(sizes))
    ax.bar(x, i, color=MEAS, width=0.6)
    ax.axhline(i[2], color=RULE, ls="--", lw=1.6,
               label=f"what $W/L$ predicts for all five ({i[2]:.1f} µA)")
    for xi, y in zip(x, i):
        ax.annotate(f"{y:.1f}", (xi, y), textcoords="offset points",
                    xytext=(0, 4), ha="center", fontsize=9, color=INK)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlabel("$W$ / $L$  (µm), all with $W/L$ = 5")
    ax.set_ylabel("$I_D$  (µA)")
    ax.set_ylim(0, 900)
    ax.legend(fontsize=9, loc="upper left")
    ax.set_title("Same ratio, five sizes, five different currents", loc="left")

    ax2.plot(area, i, "o-", color=ACCENT, lw=2.1, ms=7)
    for (w, l), a, y, c in zip(sizes, area, i, cap):
        ax2.annotate(f"{w:g}/{l:g}\n{c:.2f} fF", (a, y),
                     textcoords="offset points", xytext=(6, -14),
                     fontsize=8.5, color=INK)
    ax2.set_xscale("log")
    ax2.set_xlabel("gate area $W \\times L$  (µm²), log scale")
    ax2.set_ylabel("$I_D$  (µA)")
    ax2.set_xlim(0.07, 400)
    ax2.set_ylim(300, 900)
    ax2.set_title(f"{area[-1]/area[0]:.0f}× the area buys "
                  f"{i[-1]/i[0]:.2f}× the current", loc="left")

    fig.tight_layout()
    fig.savefig(out / "ad103-same-ratio.png")
    plt.close(fig)
    print(f"   wrote {out / 'ad103-same-ratio.png'}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=str(RESULTS))
    args = ap.parse_args()
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    fig_w_ladder(out)
    fig_l_ladder(out)
    fig_same_ratio(out)


if __name__ == "__main__":
    main()
