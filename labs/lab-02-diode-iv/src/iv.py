"""Shared reading / fitting helpers for AD103 Lab 02.

Both plot_iv.py and check.py import this, so the number on the plot and the
number in the verdict can never disagree.
"""
import math
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent

# Boltzmann / electron charge, and the temperature ngspice ran at.
K_B = 1.380649e-23      # J/K   (exact, SI 2019)
Q_E = 1.602176634e-19   # C     (exact, SI 2019)
T_SIM = 300.15          # K     = 27 degC, ngspice's default TEMP
VT = K_B * T_SIM / Q_E  # thermal voltage, volts
DEC = math.log(10.0)    # 2.302585..., "one decade" in natural logs

# The decades printed in the table: the whole usable range of the curve.
TABLE_DECADES = [1e-12, 1e-11, 1e-10, 1e-9, 1e-8, 1e-7, 1e-6]

# The window the slope is fitted over: 1 nA to 100 nA. High enough that the
# simulator's GMIN floor is long gone, low enough that the diode's series
# resistance has not started bending the curve down. Between those two the
# local slope is constant to better than 0.1 mV/decade.
FIT_LO, FIT_HI = 1e-9, 1e-7


def read_iv(path=None):
    """Read the two-column wrdata file ngspice wrote: volts, amps."""
    path = Path(path) if path else LAB / "results" / "diode_iv.txt"
    v, i = [], []
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        v.append(float(parts[0]))
        i.append(float(parts[1]))
    return v, i


def v_at_current(v, i, target):
    """Interpolate the forward voltage at which the current equals target.

    Linear interpolation in (V, log I), which is the right thing to do on a
    curve that is a straight line in exactly those coordinates.
    """
    for k in range(1, len(v)):
        if i[k - 1] < target <= i[k]:
            l0, l1 = math.log(i[k - 1]), math.log(i[k])
            f = (math.log(target) - l0) / (l1 - l0)
            return v[k - 1] + f * (v[k] - v[k - 1])
    return None


def decade_table(v, i, decades=None):
    """[(current, voltage, mV since the previous decade), ...]"""
    decades = decades or TABLE_DECADES
    rows, prev = [], None
    for d in decades:
        vd = v_at_current(v, i, d)
        if vd is None:
            continue
        step = None if prev is None else (vd - prev) * 1e3
        rows.append((d, vd, step))
        prev = vd
    return rows


def fit_exponential(v, i, lo=FIT_LO, hi=FIT_HI):
    """Least-squares fit of ln(I) = ln(I0) + V/(n*VT) over [lo, hi] amps.

    Returns (mV_per_decade, n, I0_amps, npoints).
    """
    xs = [(vv, math.log(ii)) for vv, ii in zip(v, i) if lo <= ii <= hi]
    n_pts = len(xs)
    if n_pts < 2:
        # Nothing to fit. A sweep that never gets between lo and hi amps is
        # almost always a sweep with no diode in it: the netlist said
        # "IS MISSING", ngspice solved it anyway, and every current is zero.
        raise ValueError(
            f"the curve has no points between {lo:.0e} A and {hi:.0e} A, so "
            f"there is no exponential to fit. A sweep that is flat at zero "
            f"means the model never loaded - check that the netlist has no "
            f"'IS MISSING' line and that PDK is sky130A")
    mx = sum(p[0] for p in xs) / n_pts
    my = sum(p[1] for p in xs) / n_pts
    sxy = sum((p[0] - mx) * (p[1] - my) for p in xs)
    sxx = sum((p[0] - mx) ** 2 for p in xs)
    slope = sxy / sxx                      # d(ln I)/dV  = 1/(n*VT)
    intercept = my - slope * mx            # ln(I0)
    mv_per_decade = DEC / slope * 1e3
    n_ideality = 1.0 / (slope * VT)
    return mv_per_decade, n_ideality, math.exp(intercept), n_pts


def fit_line(v, mv_per_decade, i0):
    """The fitted straight line, evaluated at a voltage, in amps."""
    return i0 * 10.0 ** (v / (mv_per_decade * 1e-3))


def series_resistance(v, i, mv_per_decade, i0, at=0.900):
    """Extract the series resistance from the top of the curve.

    At a high current the junction still obeys the straight line - it is just
    that some of the voltage you applied is being dropped across the silicon
    and the contacts before it ever reaches the junction. So: find the voltage
    the straight line says this current needs, subtract it from the voltage
    actually applied, and divide the leftover by the current.

    Returns (v_applied, i_measured, v_junction, dv, rs_ohms).
    """
    i_at = None
    for vv, ii in zip(v, i):
        if abs(vv - at) < 1e-9:
            i_at = ii
            break
    if i_at is None or i_at <= 0:
        return None
    v_junction = mv_per_decade * 1e-3 * math.log10(i_at / i0)
    dv = at - v_junction
    return at, i_at, v_junction, dv, dv / i_at


def local_slope(v, i, lo=0.050, hi=0.880, step=0.050, half=0.010):
    """[(V, I, local mV/decade), ...] - the slope measured over +-half volts."""
    out = []
    idx = {round(a, 3): k for k, a in enumerate(v)}
    n = int(round((hi - lo) / step)) + 1
    for m in range(n):
        target = round(lo + m * step, 3)
        k = idx.get(target)
        if k is None:
            continue
        k0, k1 = k - int(round(half / 0.001)), k + int(round(half / 0.001))
        if k0 < 0 or k1 >= len(v) or i[k0] <= 0 or i[k1] <= 0:
            continue
        dec = (math.log10(i[k1]) - math.log10(i[k0])) / (v[k1] - v[k0])
        out.append((v[k], i[k], 1000.0 / dec))
    return out


def rs_departure(v, i, mv_per_decade, i0, frac=0.10):
    """First forward point where the data falls `frac` below the fitted line."""
    for vv, ii in zip(v, i):
        if ii <= 0 or vv <= 0:
            continue
        line = fit_line(vv, mv_per_decade, i0)
        if line > 1e-12 and ii < line * (1.0 - frac):
            return vv, ii, line
    return None
