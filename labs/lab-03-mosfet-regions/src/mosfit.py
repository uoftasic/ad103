#!/usr/bin/env python3
"""Shared helpers for AD103 Lab 03.

Three jobs: read ngspice's `wrdata` files, work out which bias each column of
one was swept at by reading the deck that wrote it, and do the three
extractions this lab is about (threshold, transconductance, subthreshold
slope). Nothing here is clever - it is arithmetic on two columns of numbers,
which is the point.
"""
import re
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parent.parent
RESULTS = LAB / "results"
SPICE   = LAB / "spice"


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


def deck_gate_voltages(deck):
    """The V_GS behind each COLUMN of the wrdata file this deck writes.

    You cannot get this from the `foreach` line alone, and assuming you can is
    the single most expensive mistake in this lab. Three separate lines have to
    be read together:

        foreach vg 0.6 1.05 0.9 ...    run order. dc1 is 0.6, dc2 is 1.05
        let id_vgs105 = -dc2.i(vds)    ties a vector name to a RUN
        wrdata <file> id_vgs06 ...     column order, by NAME

    `dcN` is a run counter, not a bias label, and `wrdata` writes columns in
    whatever order you name them - which need not be either the run order or
    ascending gate voltage. Insert a sixth curve in its natural place in the
    foreach list and all three orders come apart.

    Returns the gate voltage of each column, in column order.
    """
    text = Path(deck).read_text()

    m = re.search(r"^\s*foreach\s+vg\s+(.+)$", text, re.M)
    if not m:
        raise ValueError(f"{deck}: no 'foreach vg ...' line to read gate voltages from")
    run_gate = [float(t) for t in m.group(1).split()]

    run_of = {}
    for name, n in re.findall(r"^\s*let\s+(\w+)\s*=\s*-?\s*dc(\d+)\.i\(",
                              text, re.M):
        run_of[name] = int(n)

    w = re.search(r"^\s*wrdata\s+\S+\s+(.+)$", text, re.M)
    if not w:
        raise ValueError(f"{deck}: no 'wrdata' line to read the column order from")

    gates = []
    for name in w.group(1).split():
        if name not in run_of:
            raise ValueError(
                f"{deck}: wrdata writes '{name}', but no 'let {name} = -dcN.i(vds)' "
                f"line says which sweep that is")
        n = run_of[name]
        if not 1 <= n <= len(run_gate):
            raise ValueError(
                f"{deck}: '{name}' reads dc{n}, but the foreach line only runs "
                f"{len(run_gate)} sweeps (dc1..dc{len(run_gate)})")
        gates.append(run_gate[n - 1])
    return gates


def deck_geometries(deck):
    """The (W, L) behind each COLUMN of a one-device-per-drain-source deck.

    spice/wl_sweep.spice gives every transistor its own drain source so each
    can be swept alone, which means a column is three hops away from a
    geometry:

        wrdata <file> id_a id_b ...     column order, by name
        let id_a = -dc1.i(vda)          name -> the source it measures
        Vda da 0 0                      source -> the node it drives
        XMA da g 0 0 ... L=1 W=5        node   -> the device, and its shape

    Edit any one of those four lines - extension 3 asks you to edit the last -
    and the labels have to follow. Reading them is four regexes; assuming them
    is a wrong label on a right number.

    Returns [(W, L), ...] in column order.
    """
    text = Path(deck).read_text()

    src_of = {n: s.lower() for n, s in
              re.findall(r"^\s*let\s+(\w+)\s*=\s*-?\s*dc\d+\.i\((\w+)\)",
                         text, re.M)}
    node_of = {f"v{n}".lower(): d for n, d in
               re.findall(r"^\s*V(\w+)\s+(\w+)\s+\w+", text, re.M)}
    shape_of = {}
    for node, params in re.findall(r"^\s*X\w+\s+(\w+)\s+.*?nfet_01v8\s+(.*)$",
                                   text, re.M):
        w = re.search(r"\bW\s*=\s*([\d.]+)", params)
        l = re.search(r"\bL\s*=\s*([\d.]+)", params)
        if w and l:
            shape_of[node] = (float(w.group(1)), float(l.group(1)))

    w = re.search(r"^\s*wrdata\s+\S+\s+(.+)$", text, re.M)
    if not w:
        raise ValueError(f"{deck}: no 'wrdata' line to read the column order from")

    out = []
    for name in w.group(1).split():
        try:
            out.append(shape_of[node_of[src_of[name]]])
        except KeyError as exc:
            raise ValueError(
                f"{deck}: cannot trace column '{name}' back to a device "
                f"(stuck at {exc}). Check its 'let', its V source and its "
                f"XM line all still name the same node.") from None
    return out


def labelled_columns(deck, path):
    """read_wrdata(path), with each column's V_GS read out of the deck.

    Returns (x, [(v_gs, column), ...]). Refuses to guess: if the deck and the
    data file disagree about how many curves there are, that is a stale results
    file, and pairing them off anyway would print one curve's current under
    another curve's label.
    """
    x, ys = read_wrdata(path)
    gates = deck_gate_voltages(deck)
    if len(gates) != len(ys):
        raise ValueError(
            f"{Path(deck).name} writes {len(gates)} curves but "
            f"{Path(path).name} holds {len(ys)} - the results file is stale. "
            f"Run 'make clean && make'.")
    return x, list(zip(gates, ys))


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
