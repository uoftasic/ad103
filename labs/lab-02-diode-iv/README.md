# AD103 Lab 02: The diode I–V curve

Writeup: [`docs/labs/lab-02-diode-iv-overview.md`](../../docs/labs/lab-02-diode-iv-overview.md),
published at <https://uoftasic.com/ad103/#/labs/lab-02-diode-iv-overview>. The steps and expected
output are there; this file is a quick reference.

## Run it

Inside the workbench container (`hpretl/iic-osic-tools:2026.08`):

```bash
cd labs/lab-02-diode-iv
make
```

It takes about 25 seconds and ends in `PASS` or `FAIL`. No environment setup is required: no
`.designinit`, no `mod`, no `PDK`. The decks find the models through `PDK_ROOT`, which the image
already sets to `/foss/pdks`, and the `Makefile` sets it anyway. The XSchem bench in `xschem/`
resolves its symbols through `PDK`, so `xschem/xschemrc` sets that to `sky130A` itself.

## Targets

| Target | What it does |
|---|---|
| `make` | DC sweep + additivity test + three plots + verdict |
| `make sweep` | just the 1901-point DC sweep |
| `make line` | print the additivity test again |
| `make plots` | just the plots, from `results/diode_iv.txt` |
| `make area` | what junction area buys you, and three silent unit mistakes |
| `make floor` | what the flat reverse line on the log plot really is |
| `make op` | one resistor and one diode in series, three times |
| `make broken` | hands the checker a 5 %-wrong sweep, on purpose |
| `make clean` | delete `results/` |

## Files

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
xschem/diode_tb.sch         the same bench as spice/diode_iv.spice, drawn
xschem/xschemrc             project-local XSchem config; sets PDK=sky130A for this bench
```

Every deck loads the typical corner with `.lib $PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice tt`.

`area` is in square microns and `perim` in microns, and neither takes a unit suffix:
`area=1 perim=4` is a 1 µm × 1 µm junction.
