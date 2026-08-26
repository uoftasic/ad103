#!/usr/bin/env python3
"""AD103 Lab 02 - draw the two plots, and print the numbers that are on them.

Reads results/diode_iv.txt (written by spice/diode_iv.spice) and writes
results/ad103-diode-iv-linear.png, results/ad103-diode-iv-log.png
and results/ad103-diode-load-line.png.

    python3 src/plot_iv.py

Nothing here is decorative. The linear plot is the one that hides the physics;
the log plot is the one that shows it. Both are drawn from the same 1901 rows.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")           # no X server, no display, no window
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from iv import (LAB, VT, FIT_LO, FIT_HI, read_iv, decade_table,
                fit_exponential, fit_line, rs_departure, series_resistance,
                local_slope)

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
DATA = "#2a78d6"     # categorical slot 1
FITC = "#eb6834"     # categorical slot 2
GRID = "#d8d7d2"

OUT = LAB / "results"


def style(ax):
    ax.set_facecolor(SURFACE)
    ax.figure.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=INK_2, labelsize=10)
    ax.grid(True, color=GRID, linewidth=0.8, alpha=0.9)
    ax.set_axisbelow(True)


def plot_linear(v, i):
    fig, ax = plt.subplots(figsize=(8.0, 4.6), dpi=150)
    style(ax)
    ax.plot(v, [x * 1e6 for x in i], color=DATA, linewidth=2.0)
    ax.axhline(0, color=GRID, linewidth=1.0)
    ax.set_xlabel("Diode voltage (V)", color=INK_2, fontsize=11)
    ax.set_ylabel("Current (µA)", color=INK_2, fontsize=11)
    ax.set_title("One SKY130 diode, 1 µm² — linear axes",
                 color=INK, fontsize=13, loc="left", pad=12)
    ax.annotate("everything from −1 V to +0.5 V\nlooks like a flat zero here",
                xy=(-0.35, 0), xytext=(-0.95, max(i) * 1e6 * 0.55),
                color=INK_2, fontsize=10,
                arrowprops=dict(arrowstyle="->", color=INK_2, linewidth=1.2))
    fig.tight_layout()
    fig.savefig(OUT / "ad103-diode-iv-linear.png", facecolor=SURFACE)
    plt.close(fig)


def plot_log(v, i, mvdec, n, i0, dep):
    fwd = [(vv, ii) for vv, ii in zip(v, i) if vv >= 0 and ii > 0]
    fig, ax = plt.subplots(figsize=(8.0, 5.2), dpi=150)
    style(ax)
    ax.semilogy([p[0] for p in fwd], [p[1] for p in fwd],
                color=DATA, linewidth=2.0, label="simulated")
    line_v = [x / 1000.0 for x in range(200, 901, 5)]
    ax.semilogy(line_v, [fit_line(x, mvdec, i0) for x in line_v],
                color=FITC, linewidth=2.0, linestyle="--",
                label=f"straight line, {mvdec:.1f} mV/decade")
    if dep:
        ax.plot([dep[0]], [dep[1]], marker="o", markersize=9, color=DATA,
                markeredgecolor=SURFACE, markeredgewidth=2, zorder=5)
        ax.annotate(f"data falls 10 % below the line\nat {dep[0]:.3f} V, "
                    f"{dep[1]*1e6:.2f} µA",
                    xy=(dep[0], dep[1]), xytext=(0.30, 3e-4),
                    color=INK_2, fontsize=10,
                    arrowprops=dict(arrowstyle="->", color=INK_2, linewidth=1.2))
    ax.set_ylim(1e-13, 1e-3)
    ax.set_xlim(0, 0.9)
    ax.set_xlabel("Diode voltage (V)", color=INK_2, fontsize=11)
    ax.set_ylabel("Forward current (A, log scale)", color=INK_2, fontsize=11)
    ax.set_title("The same 1901 numbers, log vertical axis",
                 color=INK, fontsize=13, loc="left", pad=12)
    leg = ax.legend(frameon=False, loc="lower right", fontsize=10)
    for text in leg.get_texts():
        text.set_color(INK_2)
    fig.tight_layout()
    fig.savefig(OUT / "ad103-diode-iv-log.png", facecolor=SURFACE)
    plt.close(fig)


LOADS = [(1e5, "100 kΩ", (0.27, 16.4)), (1e6, "1 MΩ", (0.29, 3.9))]
VDD = 1.8


def crossing(v, i, res):
    """Where the measured curve meets the load line (V, I) - read off the data."""
    prev = None
    for vv, ii in zip(v, i):
        if vv < 0.3:
            continue
        f = ii - (VDD - vv) / res
        if prev is not None and prev[1] < 0 <= f:
            v0, f0 = prev
            frac = (0 - f0) / (f - f0)
            vx = v0 + frac * (vv - v0)
            return vx, (VDD - vx) / res
        prev = (vv, f)
    return None


def plot_load_line(v, i):
    """The diode curve and two resistor load lines, on linear axes.

    Where a load line crosses the diode curve, the resistor and the diode
    agree on the voltage and the current at the same time. That crossing is
    the operating point, and it is what `op` in a SPICE deck goes looking for.
    """
    fig, ax = plt.subplots(figsize=(8.0, 5.0), dpi=150)
    style(ax)
    fwd = [(vv, ii * 1e6) for vv, ii in zip(v, i) if 0 <= vv <= 0.9]
    ax.plot([p[0] for p in fwd], [p[1] for p in fwd],
            color=DATA, linewidth=2.0, label="the diode, swept")
    first = True
    for res, label, tpos in LOADS:
        xs = [0.0, 0.9]
        ys = [(VDD - x) / res * 1e6 for x in xs]
        ax.plot(xs, ys, color=FITC, linewidth=2.0, linestyle="--",
                label="a resistor from 1.8 V" if first else None)
        first = False
        ax.annotate(f"{label}", xy=(0.03, ys[0] + 0.6),
                    color=INK_2, fontsize=10)
        c = crossing(v, i, res)
        if c:
            ax.plot([c[0]], [c[1] * 1e6], marker="o", markersize=9,
                    color=INK, markeredgecolor=SURFACE, markeredgewidth=2,
                    zorder=6)
            ax.annotate(f"{c[0]:.4f} V, {c[1]*1e6:.2f} µA",
                        xy=(c[0], c[1] * 1e6),
                        xytext=tpos,
                        color=INK, fontsize=10,
                        arrowprops=dict(arrowstyle="->", color=INK_2,
                                        linewidth=1.2))
    ax.set_ylim(0, 20)
    ax.set_xlim(0, 0.9)
    ax.set_xlabel("Voltage across the diode (V)", color=INK_2, fontsize=11)
    ax.set_ylabel("Current (µA)", color=INK_2, fontsize=11)
    ax.set_title("Load lines: two resistors, one diode, 1.8 V",
                 color=INK, fontsize=13, loc="left", pad=12)
    leg = ax.legend(frameon=False, loc="upper center", fontsize=10)
    for text in leg.get_texts():
        text.set_color(INK_2)
    fig.tight_layout()
    fig.savefig(OUT / "ad103-diode-load-line.png", facecolor=SURFACE)
    plt.close(fig)


def main():
    v, i = read_iv()
    OUT.mkdir(exist_ok=True)
    mvdec, n, i0, npts = fit_exponential(v, i)
    dep = rs_departure(v, i, mvdec, i0)

    plot_linear(v, i)
    plot_log(v, i, mvdec, n, i0, dep)

    print(f"  rows read          : {len(v)}")
    print(f"  reverse at -1.000 V: {i[0]*1e12:.4f} pA")
    print()
    print("  current      forward V     mV since previous decade")
    for cur, vd, step in decade_table(v, i):
        s = "        -" if step is None else f"{step:9.2f}"
        print(f"  {cur:8.0e} A   {vd:.6f} V   {s}")
    print()
    print(f"  fit over {npts} points from {FIT_LO:.0e} A to {FIT_HI:.0e} A:")
    print(f"    slope           : {mvdec:.3f} mV/decade")
    print(f"    thermal voltage : {VT*1e3:.4f} mV  (27 degC)")
    print(f"    ideality n      : {n:.4f}")
    print(f"    I0 (V=0 intercept): {i0*1e15:.4f} fA")
    if dep:
        print(f"    leaves the line : {dep[0]:.3f} V, {dep[1]*1e6:.4f} uA "
              f"(line says {dep[2]*1e6:.4f} uA)")
    rs = series_resistance(v, i, mvdec, i0)
    if rs:
        print()
        print(f"  series resistance, from the top of the curve:")
        print(f"    at {rs[0]:.3f} V the diode carries {rs[1]*1e6:.4f} uA")
        print(f"    the straight line needs only {rs[2]:.6f} V for that current")
        print(f"    so {rs[3]*1e3:.3f} mV is dropped outside the junction")
        print(f"    rs = {rs[3]*1e3:.3f} mV / {rs[1]*1e6:.4f} uA = {rs[4]:.1f} ohm")
    print()
    print("  local slope, measured over a 20 mV window:")
    print("     V        I(A)         mV/decade")
    for vv, ii, sl in local_slope(v, i):
        print(f"  {vv:6.3f}  {ii:.4e}   {sl:9.2f}")
    print()
    plot_load_line(v, i)
    for name in ("ad103-diode-iv-linear.png", "ad103-diode-iv-log.png",
                 "ad103-diode-load-line.png"):
        print(f"  wrote results/{name}")


if __name__ == "__main__":
    main()
