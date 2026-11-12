# Lab 01: Your first schematic

Writeup: [uoftasic.com/ad103 → Lab 01](https://uoftasic.com/ad103/#/labs/lab-01-first-schematic-overview).
The steps, expected output and explanations are there; this file is a quick reference.

## Run it

```bash
cd labs/lab-01-first-schematic
make
```

No environment setup is needed. The `Makefile` sets `PDK=sky130A` itself, so this runs in a bare
container even if `.designinit` failed. It takes about ten seconds and ends with:

```
PASS  netlist and operating point match the reference run
```

and a drain current of **501.046 µA**. If you get that, the toolchain works and any later
problem is in a drawing.

## Targets

| Command | What it does |
|---|---|
| `make` | netlist the reference schematic, simulate, print a verdict |
| `make edit` | open `xschem/my_probe.sch` in XSchem |
| `make mine` | netlist and check **your** schematic, then simulate it |
| `make wrong-units` | the same circuit with `W` and `L` written in metres; **fails on purpose** |
| `make unconnected` | one wire one grid step short; does **not** fail, and gives a wrong answer |
| `make bins` | which model bin `L=0.15 W=1` landed in, and what `leff` really is |
| `make clean` | delete `results/` and `xschem/simulation/` |

## Files

| Path | What it is |
|---|---|
| `xschem/my_probe.sch` | **yours.** Everything but the transistor |
| `xschem/nmos_probe.sch` | the reference schematic: one NMOS, two supplies, nets `g` and `d`. Don't save over it |
| `xschem/broken_probe.sch` | the same drawing with the gate wire one grid step short |
| `xschem/xschemrc` | project-local XSchem config: loads the SKY130 symbols, and puts netlists in `simulation/` next to the schematic instead of inside the container |
| `spice/nmos_op.spice` | the same circuit as a hand-written deck: models, devices, sources, analysis, `.end` |
| `spice/nmos_op_wrong_units.spice` | identical except `L=0.15u W=1u` |
| `spice/nmos_op_unconnected.spice` | identical except the gate is on `net1` |
| `spice/bins.spice` | identical except it has **no `.control` block**, so batch ngspice dumps the whole operating point; `make bins` reads the model bin and `leff` out of it |
| `src/check.py` | reads the netlist and the log, prints `PASS` or `FAIL` and why |
| `src/check_mine.py` | reads **your** netlist and grades it in words before simulating |
