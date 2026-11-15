"""Shared look for the course's circuit drawings (schemdraw, textbook style).

Every figure script imports this, draws with schemdraw, and calls save(), which
writes an SVG into docs/assets/img/ with a white background, so the drawing reads
the same on the light and dark site themes and in the PDFs.

    pip install -r scripts/figures/requirements.txt
    python3 scripts/figures/<figure>.py

With the versions pinned in requirements.txt, rerunning a script reproduces its
committed SVG byte for byte: save() fixes the SVG id salt and leaves out the date
matplotlib would otherwise stamp in. (Another matplotlib version draws the same
figure with slightly different SVG.)
Labels may contain "&" (for example "P&R"); schemdraw 0.23 would otherwise fail
to measure them.
"""
import os

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["mathtext.fontset"] = "dejavuserif"
matplotlib.rcParams["svg.hashsalt"] = "uoftasic-figures"
import schemdraw  # noqa: E402
from schemdraw.backends import svg as _svg  # noqa: E402

schemdraw.use("matplotlib")

# schemdraw sizes label text by parsing it as XML (through ziamath when that is
# installed, through its own estimate otherwise), so a bare "&" stops it. Every
# size estimate goes through svg.text_size, so escaping there covers both.
_text_size = _svg.text_size
_svg.text_size = lambda text, *a, **k: _text_size(text.replace("&", "&amp;"), *a, **k)

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "assets", "img")


def drawing():
    """A schemdraw Drawing with the course style: thin black lines, serif labels."""
    d = schemdraw.Drawing(show=False)
    d.config(unit=2.5, lw=1.3, fontsize=13, font="serif", color="black")
    return d


def save(d, name):
    """Write docs/assets/img/<name>.svg on a white background and return its path."""
    path = os.path.normpath(os.path.join(IMG_DIR, name + ".svg"))
    d.draw()
    fig = d.fig  # schemdraw's matplotlib figure; same savefig call as its own save()
    fig.fig.savefig(path, format="svg", transparent=False, dpi=150, bbox_inches="tight",
                    bbox_extra_artists=fig.ax.get_default_bbox_extra_artists(), pad_inches=0,
                    metadata={"Date": None})
    return path
