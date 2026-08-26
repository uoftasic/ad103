# AD103 Lab 02 — The diode I–V curve

Runnable package. The writeup that goes with it is
[`docs/labs/lab-02-diode-iv-overview.md`](../../docs/labs/lab-02-diode-iv-overview.md),
published at <https://uoftasic.com/ad103/#/labs/lab-02-diode-iv-overview>.

## Run it

Inside the workbench container (`hpretl/iic-osic-tools:2026.04`):

```bash
cd labs/lab-02-diode-iv
make
```

About six seconds, and it ends in `PASS` or `FAIL`. **No environment setup is required** — not
`.designinit`, not `mod`, not `PDK`. The decks find the models through `PDK_ROOT`, which the
image already sets to `/foss/pdks`, and the `Makefile` pins it anyway. The XSchem bench in
`xschem/` resolves its symbols through `PDK`, so `xschem/xschemrc` pins that to `sky130A`
itself; on the image's default IHP process the same bench would netlist to
`D1 - diode IS MISSING !!!!` and simulate a column of zeros without complaining.

| Target | What it does |
|---|---|
| `make` | DC sweep + additivity test + three plots + verdict |
| `make sweep` | just the 1901-point DC sweep |
| `make plots` | just the plots, from `results/diode_iv.txt` |
| `make area` | what junction area buys you, and three silent unit traps |
| `make floor` | what the flat reverse line on the log plot really is |
| `make op` | one resistor and one diode in series, three times |
| `make broken` | hands the checker a 5 %-wrong sweep, on purpose |
| `make clean` | delete `results/` |

## What is in here

```
spice/diode_iv.spice        the DC sweep: -1.000 V to +0.900 V, 1 mV steps
spice/straight_line.spice   a resistor and a diode, each driven A, B, and A+B
spice/load_line.spice       R + diode from 1.8 V, for three values of R
spice/diode_area.spice      four junction sizes, and three ways to write a size wrong
spice/reverse_floor.spice   the same reverse points at two different GMIN
src/iv.py                   reading and fitting helpers, shared by the two scripts below
src/plot_iv.py              draws the three figures and prints every number on them
src/check.py                the verdict
src/bend_it.py              makes the deliberately wrong sweep for `make broken`
```

Every deck loads `sky130.lib.spice.tt.red`, the pre-flattened typical corner. It gives a
**byte-identical** sweep to the unflattened `sky130.lib.spice` and reads about 30× faster —
2.4 s instead of 74 s, per deck, per run.

## The two numbers this lab exists to produce

| | measured here | SkyWater's model card |
|---|---|---|
| ideality factor $n$ | **1.29351** | `n = 1.2928` |
| series resistance | **979.1 Ω** | `rs = 981` |

Both were extracted from the shape of a graph, not read off the card.

## Units, once

`area` is in **square microns**, `perim` is in **microns**, and neither takes a unit suffix —
the same rule as `W` and `L` on a MOSFET. `area=1 perim=4` is a 1 µm × 1 µm junction.
`area=1u` is a millionth of a square micron and ngspice will simulate it without complaint.
