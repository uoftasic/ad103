#!/usr/bin/env python3
"""Shared helpers for the AD103 capstone.

Everything the capstone measures comes out of one voltage transfer curve, so
this file is mostly one function: given (V_in, V_out), hand back the four
numbers that describe an inverter.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parent.parent
RESULTS = LAB / "results"

VDD = 1.8


def read_wrdata(path: Path | str) -> np.ndarray:
    """Read an ngspice `wrdata` file.

    wrdata writes an x column in front of EVERY y column, so a file with three
    vectors has six columns: x y1 x y2 x y3. The x columns are identical, so
    take the first and every odd column after it.
    """
    path = Path(path)
    if not path.exists():
        raise SystemExit(f"no {path} - run 'make sweeps' first")
    raw = np.loadtxt(path)
    return np.column_stack([raw[:, 0]] + [raw[:, i] for i in range(1, raw.shape[1], 2)])


@dataclass
class VTC:
    """Everything one transfer curve has to say."""
    vin: np.ndarray
    vout: np.ndarray
    vm: float           # switching threshold: where V_out = V_in
    gain: float         # steepest slope, dV_out/dV_in (negative)
    vin_at_gain: float  # where that slope happens
    vil: float          # input low: the first place the slope reaches -1
    vih: float          # input high: the last place it does
    vol: float          # output low, measured at V_IH
    voh: float          # output high, measured at V_IL
    nmh: float          # noise margin high: V_OH - V_IH
    nml: float          # noise margin low:  V_IL - V_OL


def analyse(vin: np.ndarray, vout: np.ndarray) -> VTC:
    # --- the switching threshold: the one input that comes out unchanged ----
    # V_out - V_in crosses zero exactly once on a working inverter. Find the
    # crossing and interpolate between the two samples either side of it, so
    # the answer is not quantised to the sweep step.
    f = vout - vin
    sign_change = np.where(np.diff(np.sign(f)))[0]
    if len(sign_change) == 0:
        raise SystemExit("this curve never crosses V_out = V_in - it is not "
                         "inverting. Check that the PMOS source is on vdd and "
                         "the NMOS source is on ground.")
    k = sign_change[0]
    vm = vin[k] + (vin[k + 1] - vin[k]) * (-f[k]) / (f[k + 1] - f[k])

    # --- the gain: the steepest part of the curve ---------------------------
    slope = np.gradient(vout, vin)
    gain = float(slope.min())
    vin_at_gain = float(vin[int(np.argmin(slope))])

    # --- the unity-gain points, which is what V_IL and V_IH actually mean ---
    steep = np.where(slope < -1.0)[0]
    if len(steep) == 0:
        raise SystemExit(
            f"this curve never gets steeper than -1. Its steepest slope is "
            f"{gain:.3e}, which means the output barely responds to the input "
            f"at all. A circuit with no gain above 1 cannot restore a logic "
            f"level, so it is not a usable inverter whatever else it is.")
    vil, vih = float(vin[steep[0]]), float(vin[steep[-1]])
    voh = float(np.interp(vil, vin, vout))
    vol = float(np.interp(vih, vin, vout))

    return VTC(vin=vin, vout=vout, vm=float(vm), gain=gain,
               vin_at_gain=vin_at_gain, vil=vil, vih=vih, vol=vol, voh=voh,
               nmh=voh - vih, nml=vil - vol)


def load(name: str, col: int = 1) -> VTC:
    d = read_wrdata(RESULTS / name)
    return analyse(d[:, 0], d[:, col])
