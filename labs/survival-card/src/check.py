#!/usr/bin/env python3
"""Verdict for the AD103 survival-card decks.

Every number the reference page prints comes out of these five decks. This
checks each one against the value written on the page, so the page and the
decks cannot drift apart.

Usage:  python3 src/check.py
"""
import math
import re
import sys
from pathlib import Path

R = Path("results")

# (log file, regex for the value, label, page value, tolerance as a fraction)
CHECKS = [
    ("dc_id_vgs.log", r"No\. of Data Rows\s*:\s*(\d+)",      "dc rows",            181,        0),
    ("dc_id_vgs.log", r"id_1v8\s*=\s*([\d.eE+-]+)",          "id_1v8 (A)",         6.96275e-04, 2e-5),
    ("dc_id_vgs.log", r"id_0v9\s*=\s*([\d.eE+-]+)",          "id_0v9 (A)",         6.38760e-05, 2e-5),
    ("dc_id_vgs.log", r"vg_at_1ua\s*=\s*([\d.eE+-]+)",       "vg_at_1ua (V)",      5.65815e-01, 2e-5),
    ("dc_family.log", r"No\. of Data Rows\s*:\s*(\d+)",      "dc family rows",     905,        0),
    ("dc_family.log", r"id\[180\]\s*=\s*([\d.eE+-]+)",       "id[180] (A)",        2.005399e-06, 2e-5),
    ("tran_rc.log",   r"tau\s*=\s*([\d.eE+-]+)",             "tran tau (s)",       3.10826e-09, 2e-5),
    ("tran_rc.log",   r"vfinal\s*=\s*([\d.eE+-]+)",          "tran vfinal (V)",    1.80000e+00, 2e-5),
    ("ac_rc.log",     r"No\. of Data Rows\s*:\s*(\d+)",      "ac rows",            1001,       0),
    ("ac_rc.log",     r"f3db\s*=\s*([\d.eE+-]+)",            "ac f3db (Hz)",       7.56449e+07, 2e-5),
    ("rc_parts.log",  r"^r\s*=\s*([\d.eE+-]+)",              "R (ohm)",            1.018463e+04, 2e-5),
    ("rc_parts.log",  r"^cmim\s*=\s*([\d.eE+-]+)",           "C_mim (F)",          2.065822e-13, 2e-5),
]

print("== checking the five survival-card decks against the reference page")
bad = []
got = {}
for logname, pat, label, want, tol in CHECKS:
    p = R / logname
    if not p.exists():
        bad.append(f"{label}: {p} is missing -- run `make`"); continue
    m = re.search(pat, p.read_text(), re.M | re.I)
    if not m:
        bad.append(f"{label}: no match for /{pat}/ in {p}"); continue
    v = float(m.group(1)); got[label] = v
    ok = (v == want) if tol == 0 else (abs(v - want) <= tol * abs(want))
    flag = "ok " if ok else "BAD"
    if isinstance(want, int) and tol == 0:
        print(f"  {flag} {label:<22} {int(v):>14}   (page {want})")
    else:
        print(f"  {flag} {label:<22} {v:>14.6e}   (page {want:.6e})")
    if not ok:
        bad.append(f"{label}: got {v!r}, the page says {want!r}")

# The point of the page: three independent numbers must close.
if "R (ohm)" in got and "C_mim (F)" in got:
    r, c = got["R (ohm)"], got["C_mim (F)"]
    rc = r * c
    f_arith = 1.0 / (2 * math.pi * rc)
    print()
    print(f"  R x C                    = {rc*1e9:.5f} ns   (arithmetic)")
    print(f"  1 / (2 pi R C)           = {f_arith/1e6:.4f} MHz (arithmetic)")
    if "ac f3db (Hz)" in got:
        f_ac = got["ac f3db (Hz)"]
        print(f"  .ac measured             = {f_ac/1e6:.4f} MHz  "
              f"({(f_ac/f_arith-1)*100:+.4f} % from the arithmetic)")
    if "tran tau (s)" in got:
        tau = got["tran tau (s)"] - 1e-9      # the edge is at 1 ns
        print(f"  .tran measured, minus the 1 ns edge = {tau*1e9:.5f} ns  "
              f"({(tau/rc-1)*100:+.3f} % from the arithmetic)")

print()
if bad:
    print("FAIL")
    for b in bad:
        print("    -", b)
    sys.exit(1)
print("PASS  every number on the survival card reproduces")
