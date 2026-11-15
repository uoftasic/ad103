"""Shared look for the course's circuit drawings (schemdraw, textbook style).

Every figure script imports this, draws with schemdraw, and calls save(), which
writes an SVG into docs/assets/img/ with a white background, so the drawing reads
the same on the light and dark site themes and in the PDFs.

    pip install -r scripts/figures/requirements.txt
    python3 scripts/figures/<figure>.py
"""
import os

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["mathtext.fontset"] = "dejavuserif"
import schemdraw  # noqa: E402

schemdraw.use("matplotlib")

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "assets", "img")


def drawing():
    """A schemdraw Drawing with the course style: thin black lines, serif labels."""
    d = schemdraw.Drawing(show=False)
    d.config(unit=2.5, lw=1.3, fontsize=13, font="serif", color="black")
    return d


def save(d, name):
    """Write docs/assets/img/<name>.svg on a white background and return its path."""
    path = os.path.normpath(os.path.join(IMG_DIR, name + ".svg"))
    d.save(path, transparent=False, dpi=150)
    return path
