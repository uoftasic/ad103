# Lab 03 — The regions of a MOSFET

Writeup: [uoftasic.com/ad103 → Lab 03](https://uoftasic.com/ad103/#/labs/lab-03-mosfet-regions-overview)

Five ngspice sweeps of a SKY130 `nfet_01v8`, a plotting script, and a set of
parameter extractions that turn those sweeps into $V_{TH}$, $g_m$, a subthreshold
slope and a knee voltage — each one arithmetic on your own data, none of them
quoted from a datasheet.

## Run it

```bash
cd labs/lab-03-mosfet-regions
make
```

No environment setup needed. The `Makefile` pins `PDK=sky130A` itself, so this
runs in a bare container even if `.designinit` failed you.

Expected, in **13–22 seconds** (five timed runs on the reference machine):

```
== sweeping spice/id_vds.spice
   wrote results/id_vds.txt
== sweeping spice/id_vgs.spice
   wrote results/id_vgs.txt
== sweeping spice/id_vgs_log.spice
   wrote results/id_vgs_log.txt
== sweeping spice/wl_sweep.spice
   wrote results/wl_sweep.txt
== operating point   spice/op_params.spice
   wrote results/op_params.log
== checking
  YOUR NUMBERS
  ok  I_D  W=5 L=1, V_GS=V_DS=1.8 V        696.2755 uA      (reference 696.2750)
  ok  I_D  W=10 L=1, same bias            1395.3199 uA      (reference 1395.3200)
  ok  I_D  W=5 L=2, same bias              380.7284 uA      (reference 380.7280)
  ok  I_D  W=1 L=0.15, same bias           501.0462 uA      (reference 501.0460)
  ok  V_TH by linear extrapolation           0.6016 V       (reference 0.6016)
  ok  V_TH by sqrt(I_D) extrapolation        0.5159 V       (reference 0.5159)
  ok  g_m at V_GS = 1.8 V                  914.6500 uS      (reference 914.6500)
  ok  subthreshold slope                    85.5629 mV/dec  (reference 85.6000)

PASS  all eight extracted parameters match the reference run
```

## Targets

| Command | What it does |
|---|---|
| `make` | sweep, extract, and print a verdict |
| `make curves` | just the four ngspice sweeps → `results/*.txt` |
| `make op` | just the operating-point parameter dump → `results/op_params.log` |
| `make extract` | print every parameter this lab teaches, with its working |
| `make figures` | redraw the six plots and the channel cross-sections |
| `make vth-l` | the model's `vth` at nine channel lengths |
| `make netlist` | netlist `xschem/nmos_curves.sch`, and warn about unconnected pins |
| `make wrong-units` | the same circuit with `W` and `L` in metres — **fails on purpose** |
| `make clean` | delete `results/` and `xschem/simulation/` |

## Files

| Path | What it is |
|---|---|
| `spice/id_vds.spice` | $I_D$ vs $V_{DS}$, five gate voltages. The output characteristic |
| `spice/id_vgs.spice` | $I_D$ vs $V_{GS}$ at $V_{DS}$ = 0.05 V and 1.8 V. The transfer characteristic |
| `spice/id_vgs_log.spice` | the same saturation sweep, for reading on a log axis |
| `spice/wl_sweep.spice` | four geometries at one bias — the $W/L$ knob |
| `spice/op_params.spice` | what BSIM itself thinks `vth`, `vdsat`, `gm` and `gds` are |
| `spice/vth_vs_l.spice` | `vth` at nine channel lengths, at low $V_{DS}$ |
| `spice/id_vds_wrong_units.spice` | identical to `id_vds.spice` except `L=1u W=5u`. The trap |
| `src/mosfit.py` | reads `wrdata` files; the three extraction functions |
| `src/extract.py` | prints every parameter, showing its working |
| `src/plot_curves.py` | the six figures on the guide pages |
| `src/channel_picture.py` | the four channel cross-sections |
| `src/check.py` | recomputes eight numbers and prints `PASS` or `FAIL` with a reason |
| `xschem/nmos_curves.sch` | the same curve tracer, drawn |
| `xschem/xschemrc` | project-local XSchem config: SKY130 symbols, netlists into `simulation/` |

## The drawn version

![The Lab 03 curve tracer open in XSchem](https://raw.githubusercontent.com/uoftasic/ad103/main/docs/assets/img/ad103-xschem-curve-tracer.png)

```bash
cd xschem
PDK=sky130A xschem nmos_curves.sch &
```

Press **Netlist & Simulate**, then run `python3 src/check.py` from the lab
folder. It should still say `PASS`: the schematic writes into the same
`results/id_vds.txt` the deck does.

**One honest discrepancy.** The schematic's device line comes out as

```
XM1 d g 0 0 sky130_fd_pr__nfet_01v8 L=1 W=5 nf=1 ad=1.45 as=1.45 pd=10.58 ps=10.58 nrd=0.058 nrs=0.058 sa=0 sb=0 sd=0 mult=1
```

while `spice/id_vds.spice` says only `L=1 W=5 nf=1 m=1`. The XSchem symbol
computes the source/drain diffusion geometry from `W` and passes it on;
`nrd`/`nrs` are diffusion resistances in squares, and they put a little series
resistance in the path. The result is **696.226 µA** from the schematic against
**696.275 µA** from the hand deck — 0.007 % apart, well inside `check.py`'s
tolerance. It is not a rounding artefact; it is a real 50 nA, and it is the
first time in this course that the *layout* of a device shows up in its
*electrical* answer. AD104 is where that stops being a footnote.

## What to change

The decks work. That is the starting line, not the finish. Three things worth
doing, in rising order of interest — see
[`solutions/`](solutions/README.md) once you have tried them.

1. Add a $V_{GS} = 1.05$ V curve to `id_vds.spice`. Four edits, and it tells you
   whether you understood how the five columns get written.
2. Do the whole thing for `pfet_01v8` and find out how much of this page is
   about *n*-channel devices specifically.
3. Set device D in `wl_sweep.spice` to `L=0.5` and watch `vth`, `vdsat` and
   $I_D$ move together.

## The one number to know

**696.275 µA** — a SKY130 `nfet_01v8`, W = 5 µm, L = 1 µm, with $V_{GS} = V_{DS}
= 1.8$ V. Every prediction on the AD103 MOSFET pages is checked against it.
