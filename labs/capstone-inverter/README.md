# Capstone: The CMOS inverter

Writeup: [uoftasic.com/ad103 → Capstone](https://uoftasic.com/ad103/labs/capstone-inverter-overview.html).
That page has the steps, the expected output and the explanations, and this file is a quick
reference.

The inverter is two transistors and one wire between them. You draw it in XSchem, measure its
transfer curve, size it two ways, time it, run it as an amplifier, and finish with the current
mirror that would bias it.

## Run it

```bash
cd labs/capstone-inverter
make
```

You don't need to set up the environment first. The `Makefile` sets `PDK=sky130A` itself, so this
runs in a bare container even if `.designinit` failed. It takes about 55 seconds and ends with:

```
PASS  all twelve measured values match the reference run
```

Then draw your own:

```bash
make edit      # opens xschem/my_inverter.sch
make mine      # netlists it, says what is wrong, and if nothing is, simulates it
```

`xschem/inverter.sch` is the finished version, so open it only after yours works.

## Targets

| Command | What it does |
|---|---|
| `make` | run the five decks and print a verdict |
| `make sweeps` | just the ngspice runs |
| `make extract` | all six blocks of analysis, with the working shown |
| `make figures` | redraw the three PNGs into `results/` |
| `make mine` | netlist and check **your** schematic |
| `make edit` | open `xschem/my_inverter.sch` in XSchem |
| `make mirror` | the current mirror: a 50 µA reference copied four ways |
| `make broken` | an inverter with the PMOS source on the wrong node; it fails on purpose, and without any error message |
| `make clean` | delete `results/` and `xschem/simulation/` |

## Files

| Path | What it is |
|---|---|
| `xschem/my_inverter.sch` | the scaffold: everything but the two transistors |
| `xschem/inverter.sch` | the finished schematic, with its own models and control blocks |
| `xschem/xschemrc` | project-local XSchem config: SKY130 symbols, netlists into `simulation/` |
| `spice/drive.spice` | one NMOS and one PMOS, each fully on: what the two halves can do |
| `spice/vtc.spice` | the transfer curve of the $W_n = W_p$ = 1 µm inverter, and its supply current |
| `spice/vtc_ratio.spice` | five pull-up widths, one input, five switching thresholds |
| `spice/vtc_long.spice` | the same inverter at $L$ = 0.5 µm |
| `spice/gain_op.spice` | the $L$ = 0.5 µm inverter held at its steepest point, 0.712 V: each transistor's $g_m$ and $g_{ds}$ (run by `make extract`) |
| `spice/delay.spice` | a real edge, a 10 fF load, and `.meas` for rise and fall delay |
| `spice/vtc_broken.spice` | `vtc.spice` with the PMOS source and body on `0` |
| `spice/mirror.spice` | a 50 µA reference copied 1:1, 1:2 and 1:4, at several output voltages, and as two unit devices |
| `src/inv.py` | the `wrdata` reader, and the function that turns a VTC into numbers |
| `src/extract.py` | six blocks: the two halves, the naive inverter, sizing, timing, gain, power |
| `src/plot_inv.py` | the three figures on the docs page |
| `src/check.py` | recomputes twelve numbers, prints `PASS` or `FAIL` with a reason |
| `src/check_mine.py` | reads your schematic's netlist and grades it in words |
| `solutions/` | reference answers to the three extensions |
