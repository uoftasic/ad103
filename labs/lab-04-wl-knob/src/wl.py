#!/usr/bin/env python3
"""Shared helpers for AD103 Lab 04.

The ngspice logs this lab produces are plain text: one `name = value` per
line, in the order the deck printed them. Nothing here is clever - it is a
parser for that, plus the two bits of arithmetic every part of this lab does.
"""
from __future__ import annotations

from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
RESULTS = LAB / "results"


def read_log(name: str) -> dict[str, float]:
    """Pull every `key = number` line out of an ngspice log.

    Keys are lower-cased. The long `@m.xw5.msky130_fd_pr__nfet_01v8[vth]`
    names survive intact, because that is what the deck printed and matching
    the deck is more useful than a tidier name.
    """
    path = RESULTS / name
    if not path.exists():
        raise SystemExit(f"no {path} - run 'make sweeps' first")
    out: dict[str, float] = {}
    for line in path.read_text().splitlines():
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip().lower()
        if not key or " " in key:
            continue
        try:
            out[key] = float(val.strip().split()[0])
        except (ValueError, IndexError):
            continue
    if not out:
        raise SystemExit(
            f"{path} has no 'key = number' lines in it. ngspice produced no\n"
            f"measurements - the usual cause is that it never ran. First line of\n"
            f"the log: {path.read_text().splitlines()[0] if path.read_text().strip() else '(empty)'}")
    return out


def vth(log: dict[str, float], inst: str) -> float:
    """The model's own threshold for one instance, in volts."""
    return log[f"@m.{inst}.msky130_fd_pr__nfet_01v8[vth]"]


def vdsat(log: dict[str, float], inst: str) -> float:
    return log[f"@m.{inst}.msky130_fd_pr__nfet_01v8[vdsat]"]


def cgg(log: dict[str, float], inst: str) -> float:
    return log[f"@m.{inst}.msky130_fd_pr__nfet_01v8[cgg]"]


def gds(log: dict[str, float], inst: str) -> float:
    return log[f"@m.{inst}.msky130_fd_pr__nfet_01v8[gds]"]


def pct(got: float, ref: float) -> float:
    """Signed percentage error of `got` against `ref`."""
    return 100.0 * (got - ref) / ref


# The reference device, used as the anchor for every prediction in this lab.
# It is the same device Lab 03 swept: W = 5 um, L = 1 um, V_GS = V_DS = 1.8 V.
REF_W = 5.0
REF_L = 1.0
