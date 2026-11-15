# Lab 04: Testing the W/L rule

Writeup: [uoftasic.com/ad103 → Lab 04](https://uoftasic.com/ad103/labs/lab-04-wl-knob-overview.html).
The writeup has the steps, the expected output and the explanations; this file is a quick
reference for the package.

The lab is four ngspice runs over seventeen transistors, all at one bias point. Every device sits
at $V_{GS} = V_{DS} = 1.8$ V, so the only thing that changes from one to the next is its shape.
Parts 2 and 3 of the writeup also use three targets in
[`../lab-03-mosfet-regions/`](../lab-03-mosfet-regions/README.md).

## Run it

Fill in `predictions.txt` before you run anything (the writeup explains why), and then:

```bash
cd labs/lab-04-wl-knob
make
make predict
```

You don't need any environment setup first. The `Makefile` sets `PDK=sky130A` itself, so this
runs in a bare container even if `.designinit` failed. `make` takes about 40 seconds and ends
with:

```
PASS  all ten measured values match the reference run
```

## Targets

| Command | What it does |
|---|---|
| `make` | run the four decks and print a verdict |
| `make sweeps` | just the four ngspice runs → `results/*.log` |
| `make predict` | score `predictions.txt` against the measurements |
| `make extract` | every number this lab teaches, with its working shown |
| `make figures` | redraw the three PNGs into `results/` |
| `make broken` | feed the checker a run that is wrong on purpose; **fails deliberately** |
| `make clean` | delete `results/` |

## Files

| Path | What it is |
|---|---|
| `predictions.txt` | six blanks for you to fill in before the first run |
| `spice/w_ladder.spice` | six widths, 1 → 50 µm, all $L$ = 1 µm |
| `spice/l_ladder.spice` | six lengths, 0.15 → 4 µm, all $W$ = 5 µm, with `vth` and `vdsat` |
| `spice/same_ratio.spice` | five devices with $W/L$ = 5 exactly, and their gate capacitance |
| `spice/double_w.spice` | six ways of asking for "twice as wide" |
| `src/wl.py` | log parser and the two bits of shared arithmetic |
| `src/predict.py` | scores your predictions; does not grade them |
| `src/extract.py` | the four tables, with the working shown |
| `src/plot_wl.py` | the three figures on the docs pages |
| `src/check.py` | recomputes ten numbers, prints `PASS` or `FAIL` with a reason |
| `src/bend_it.py` | moves one measured number by 3 %, for `make broken` |
| `solutions/` | reference answers to the three extensions in the writeup |

Every run also leaves a three-line `bsim4v5.out` in the lab folder, written while ngspice runs
`spice/double_w.spice`. It's a BSIM parameter-check note about a negative `Eta0` in one model bin.
It doesn't affect the run, and `make clean` removes it.
