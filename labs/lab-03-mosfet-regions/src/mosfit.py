#!/usr/bin/env python3
"""Shared helpers for AD103 Lab 03.

Two jobs: read ngspice's `wrdata` files, and do the three extractions this lab
is about (threshold, transconductance, subthreshold slope). Nothing here is
clever - it is arithmetic on two columns of numbers, which is the point.
"""
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parent.parent
RESULTS = LAB / "results"


def read_wrdata(path):
    """Read an ngspice `wrdata` file into (x, [y0, y1, ...]).

    wrdata writes an x column in front of EVERY vector, so a file with five
    saved vectors has ten columns: x y0 x y1 x y2 x y3 x y4. The x columns are
    identical copies. This drops the duplicates and hands back one x and a list
    of y's. If you were expecting six columns, that is why you got ten.
    """
    raw = np.loadtxt(path)
    if raw.ndim == 1:
        raw = raw.reshape(1, -1)
    if raw.shape[1] % 2:
        raise ValueError(f"{path}: expected an even column count, got {raw.shape[1]}")
    x = raw[:, 0]
    ys = [raw[:, 2 * i + 1] for i in range(raw.shape[1] // 2)]
    return x, ys


def derivative(y, x):
    """dy/dx on a uniformly-or-not-uniformly sampled curve, same length as x."""
    return np.gradient(y, x)


def vth_linear_extrapolation(vgs, id_, vds_used):
    """Threshold by the constant-current-free method every fab uses.

    In the linear region (small V_DS) the square law collapses to

        I_D = k' (W/L) (V_GS - V_TH - V_DS/2) V_DS

    which is a straight line in V_GS. Find the steepest point of the measured
    curve, run the tangent there down to I_D = 0, and read the intercept. That
    intercept is V_TH + V_DS/2, so subtract half the drain voltage you used.

    Returns (vth, vgs_at_max_slope, slope, intercept_of_tangent).
    """
    gm = derivative(id_, vgs)
    i = int(np.argmax(gm))
    slope = gm[i]
    x0, y0 = vgs[i], id_[i]
    x_intercept = x0 - y0 / slope
    return x_intercept - vds_used / 2.0, x0, slope, x_intercept


def vth_sqrt_extrapolation(vgs, id_, fit_lo=1.0, fit_hi=1.4):
    """Threshold from the SATURATION sweep, via sqrt(I_D).

    In saturation the square law says I_D = (k'/2)(W/L)(V_GS - V_TH)^2, so
    sqrt(I_D) is a straight line whose x-intercept is V_TH. Fit it over a
    window of V_GS that is well above threshold but below where the curve
    flattens out - the default window is 1.0 V to 1.4 V.

    Returns (vth, slope, mask_used).
    """
    root = np.sqrt(np.clip(id_, 0, None))
    m = (vgs >= fit_lo) & (vgs <= fit_hi)
    slope, offset = np.polyfit(vgs[m], root[m], 1)
    return -offset / slope, slope, m


def subthreshold_slope(vgs, id_, dec_lo=-10.0, dec_hi=-8.0):
    """Millivolts of gate needed to change I_D by a factor of ten.

    Fits log10(I_D) against V_GS over a current window given in decades
    (default 1e-10 A to 1e-8 A, comfortably below threshold and comfortably
    above the numerical floor). Returns (mV_per_decade, mask_used).
    """
    with np.errstate(divide="ignore"):
        logi = np.log10(np.clip(id_, 1e-30, None))
    m = (logi >= dec_lo) & (logi <= dec_hi)
    slope, _ = np.polyfit(vgs[m], logi[m], 1)   # decades per volt
    return 1000.0 / slope, m


def knee_voltage(vds, id_, frac=0.10):
    """Where the output curve stops rising and starts being flat.

    Definition used here, and it is a choice, not a law: the knee is the first
    V_DS at which the slope dI_D/dV_DS has fallen to `frac` of the slope the
    curve had at the origin. Ten percent is arbitrary; what matters is that
    you apply the SAME definition to every curve, then compare the answers to
    V_GS - V_TH and see how well they track.
    """
    g = derivative(id_, vds)
    g0 = np.max(g[:5])
    if g0 <= 0:
        return float("nan")
    below = np.where(g <= frac * g0)[0]
    below = below[below > 2]
    return float(vds[below[0]]) if below.size else float("nan")
