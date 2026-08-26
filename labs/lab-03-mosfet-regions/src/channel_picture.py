#!/usr/bin/env python3
"""AD103 Lab 03 - draw the channel, not the equation.

    python3 src/channel_picture.py [--outdir DIR]

Four cross-sections of the same n-channel MOSFET at four bias points. The only
thing that changes between panels is how much inversion charge sits under the
oxide at each point along the channel - and that single picture is where all
three regions come from.

The channel thickness drawn here is proportional to the local inversion charge

    Q(x) ~ V_GS - V_TH - V(x)

with V(x) the channel potential from the gradual-channel solution. It is a
sketch of the physics, not a device simulation; the measured curves in
results/ are the device simulation.
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle

LAB = Path(__file__).resolve().parent.parent

SUB = "#e2e8f0"      # p-substrate
NPLUS = "#94a3b8"    # n+ source / drain
OXIDE = "#fde68a"    # gate oxide
POLY = "#cbd5e1"     # poly gate
CHAN = "#1d4ed8"     # inversion channel
DEPL = "#fca5a5"     # pinched-off / depleted stretch

VTH = 0.589          # the model's own V_TH for W=5 L=1, from op_params.spice


def channel_profile(vgs, vds, n=400):
    """Local channel 'thickness' along x, normalised to 1 at the source end."""
    vov = vgs - VTH
    if vov <= 0:
        return np.linspace(0, 1, n), np.zeros(n), None
    x = np.linspace(0, 1, n)
    if vds < vov:
        # triode: V(x) solves V_ov V - V^2/2 = x (V_ov V_DS - V_DS^2/2)
        k = x * (vov * vds - vds ** 2 / 2)
        v = vov - np.sqrt(np.clip(vov ** 2 - 2 * k, 0, None))
        q = (vov - v) / vov
        return x, q, None
    # saturation: the channel ends where V(x) reaches V_ov. Beyond that point
    # the inversion layer is gone and the rest of V_DS falls across a short
    # depleted stretch that gets longer as V_DS grows.
    xp = min(1.0, vov / vds * 1.0)
    xp = 1.0 - 0.32 * (1 - vov / vds)          # drawn pinch-off point
    x = np.linspace(0, 1, n)
    q = np.zeros(n)
    inside = x <= xp
    k = (x[inside] / xp) * (vov ** 2 / 2)
    v = vov - np.sqrt(np.clip(vov ** 2 - 2 * k, 0, None))
    q[inside] = (vov - v) / vov
    return x, q, xp


def draw(ax, vgs, vds, title, note):
    ax.set_xlim(-0.30, 1.30)
    ax.set_ylim(-0.62, 0.72)
    ax.axis("off")

    # substrate, source, drain
    ax.add_patch(Rectangle((-0.30, -0.62), 1.60, 0.62, fc=SUB, ec="none"))
    ax.add_patch(Rectangle((-0.30, -0.26), 0.30, 0.26, fc=NPLUS, ec="0.4", lw=0.8))
    ax.add_patch(Rectangle((1.00, -0.26), 0.30, 0.26, fc=NPLUS, ec="0.4", lw=0.8))
    ax.text(-0.15, -0.13, "n+", ha="center", va="center", fontsize=9)
    ax.text(1.15, -0.13, "n+", ha="center", va="center", fontsize=9)
    ax.text(0.5, -0.55, "p-type body", ha="center", va="center",
            fontsize=9.5, color="#475569")

    # oxide + gate
    ax.add_patch(Rectangle((0.0, 0.02), 1.0, 0.07, fc=OXIDE, ec="0.5", lw=0.8))
    ax.add_patch(Rectangle((0.0, 0.09), 1.0, 0.20, fc=POLY, ec="0.4", lw=0.9))
    ax.text(0.5, 0.19, "gate", ha="center", va="center", fontsize=9.5)
    ax.text(0.5, 0.055, "oxide", ha="center", va="center", fontsize=7.5,
            color="#92400e")

    # terminals
    ax.plot([-0.15, -0.15], [0.0, 0.42], color="0.25", lw=1.4)
    ax.plot([1.15, 1.15], [0.0, 0.42], color="0.25", lw=1.4)
    ax.plot([0.5, 0.5], [0.29, 0.52], color="0.25", lw=1.4)
    ax.text(-0.15, 0.48, "S", ha="center", fontsize=10, weight="bold")
    ax.text(1.15, 0.48, f"D  $V_{{DS}}$={vds:.2f} V", ha="center", fontsize=9.5,
            weight="bold")
    ax.text(0.5, 0.58, f"G  $V_{{GS}}$={vgs:.2f} V", ha="center", fontsize=9.5,
            weight="bold")

    x, q, xp = channel_profile(vgs, vds)
    if q.max() <= 0:
        ax.text(0.5, -0.10, "no channel", ha="center", va="center",
                fontsize=10.5, color="#b91c1c", style="italic")
    else:
        depth = 0.16 * q
        ax.fill_between(x, 0.0, -depth, color=CHAN, alpha=0.85, lw=0)
        if xp is not None and xp < 1.0:
            ax.fill_between([xp, 1.0], [0, 0], [-0.035, -0.035],
                            color=DEPL, lw=0, hatch="///", ec="#b91c1c")
            ax.annotate("pinched off", xy=((xp + 1) / 2, -0.05),
                        xytext=((xp + 1) / 2, -0.30), ha="center", fontsize=8.5,
                        color="#b91c1c",
                        arrowprops=dict(arrowstyle="->", color="#b91c1c", lw=1.0))

    ax.add_patch(FancyArrowPatch((0.0, -0.34), (1.0, -0.34), arrowstyle="<->",
                                 mutation_scale=9, color="0.45", lw=0.9))
    ax.text(0.5, -0.30, "L", ha="center", fontsize=9.5, color="0.35")

    ax.set_title(title, fontsize=11.5, weight="bold", pad=2)
    ax.text(0.5, -0.72, note, ha="center", va="top", fontsize=9.6,
            transform=ax.transData, color="#334155", wrap=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=str(LAB / "results"))
    args = ap.parse_args()
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)

    panels = [
        (0.30, 0.90, "1. Cutoff",
         "$V_{GS} < V_{TH}$: the gate has not pulled\nan inversion layer out of the body."),
        (1.20, 0.20, "2. Triode",
         "$V_{DS} < V_{GS}-V_{TH}$: a channel end to end,\nthinner at the drain. A resistor."),
        (1.20, 0.61, "3. Edge of saturation",
         "$V_{DS} = V_{GS}-V_{TH}$: the drain end of the\nchannel has just run out of charge."),
        (1.20, 1.60, "4. Saturation",
         "$V_{DS} > V_{GS}-V_{TH}$: the extra volts fall\nacross the pinched-off stretch, not the channel."),
    ]
    fig, axs = plt.subplots(1, 4, figsize=(16.4, 4.3))
    fig.patch.set_facecolor("white")
    for ax, (vg, vd, title, note) in zip(axs, panels):
        draw(ax, vg, vd, title, note)
    fig.subplots_adjust(bottom=0.22, top=0.86, wspace=0.12)
    fig.suptitle("One transistor, four bias points — the regions are what the channel is doing",
                 fontsize=13, y=0.98)
    fig.savefig(out / "ad103-channel-regions.png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"   wrote {out}/ad103-channel-regions.png")


if __name__ == "__main__":
    main()
