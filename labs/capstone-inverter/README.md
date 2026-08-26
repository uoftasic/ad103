# Capstone — The CMOS inverter

Writeup: [uoftasic.com/ad103 → Capstone](https://uoftasic.com/ad103/#/labs/capstone-inverter-overview)

Two transistors. One wire between them. It is the smallest circuit in this
course and the only one you will meet again in every course after it.

You draw it in XSchem, measure its voltage transfer curve, extract the voltage
at which it switches, discover that the number is not the one you predicted,
and then find out that your prediction was the right answer to a question you
were not asking.

## Run it

```bash
cd labs/capstone-inverter
make
```

No environment setup needed. The `Makefile` pins `PDK=sky130A` itself, so this
runs in a bare container even if `.designinit` failed you.

Expected, in about **13 seconds** (13.29 s and 13.19 s on two timed clean runs):

```
== spice/vtc.spice
   wrote results/vtc.txt
== spice/vtc_ratio.spice
   wrote results/vtc_ratio.txt
== spice/vtc_long.spice
   wrote results/vtc_long.txt
== spice/drive.spice
   wrote results/drive.log
== spice/delay.spice
   wrote results/delay.log
== checking
  YOUR NUMBERS
  ok  I_D  NMOS W=1 L=0.15         501.0462 uA  (reference 501.0462)
  ok  I_D  PMOS W=1 L=0.15         200.7478 uA  (reference 200.7478)
  ok  NMOS / PMOS drive ratio        2.4959     (reference 2.4959)
  ok  V_M   Wn = Wp = 1              0.8380 V   (reference 0.8380)
  ok  gain at V_M, L = 0.15        -13.1253     (reference -13.1253)
  ok  V_M   Wp = 2.5                 0.8827 V   (reference 0.8827)
  ok  V_M   Wp = 3.5                 0.8999 V   (reference 0.8999)
  ok  V_M   L = 0.5, Wn = Wp         0.7141 V   (reference 0.7141)
  ok  gain at V_M, L = 0.5        -116.0341     (reference -116.0341)
  ok  t_pHL  Wp = 2.5               30.2508 ps  (reference 30.2508)
  ok  t_pLH  Wp = 2.5               30.7067 ps  (reference 30.7067)
  ok  t_pLH / t_pHL  Wp = 1          2.3341     (reference 2.3341)

  V_out(0.0 V) = 1.800000 V   V_out(1.8 V) = 2.129252e-07 V

PASS  all twelve measured values match the reference run
```

## Draw it yourself — this is the point of the capstone

`xschem/my_inverter.sch` has everything except the two transistors: the supply,
the input source, ground, and the four named nets. Add a `pfet_01v8` and an
`nfet_01v8`, wire them, save, and run:

```bash
make edit      # opens your schematic
make mine      # netlists it, tells you what is wrong, and if nothing is, simulates it
```

`make mine` reads the netlist XSchem writes and checks the things a first
inverter actually gets wrong — a missing device, a unit suffix on `W`, an
invented `net7` where a wire did not land, the PMOS body left on ground. Each
one is reported in words, not as a stack trace. When the wiring is right it
builds a testbench around **your** device lines, simulates it, and puts your
switching threshold next to the reference:

```
  YOUR INVERTER
    V_out(0.0 V)              1.800000 V
    V_out(1.8 V)          2.131046e-07 V
    switching threshold       0.838029 V
    gain at V_M               -13.1252
    noise margins H / L     0.8106 / 0.6376 V

PASS  Wn = Wp = 1 um, and your V_M is 0.838029 V against the
      reference 0.838027 V. You drew the same inverter the
      shipped deck describes, and it behaves identically.
```

**0.838029 against 0.838027 — two microvolts.** Your drawing and the shipped
hand-written deck are the same circuit, and now you have proof rather than a
promise.

`xschem/inverter.sch` is the finished version, if you want something to compare
against. Open it only after yours works.

## Targets

| Command | What it does |
|---|---|
| `make` | run the five decks and print a verdict |
| `make sweeps` | just the ngspice runs |
| `make extract` | all six blocks of analysis, with the working shown |
| `make figures` | redraw the three PNGs into `results/` |
| `make mine` | netlist and check **your** schematic |
| `make edit` | open `xschem/my_inverter.sch` in XSchem |
| `make broken` | an inverter with the PMOS source on the wrong node — **fails deliberately, and silently** |
| `make clean` | delete `results/` and `xschem/simulation/` |

## Files

| Path | What it is |
|---|---|
| `xschem/my_inverter.sch` | the scaffold. Everything but the two transistors |
| `xschem/inverter.sch` | the finished schematic, with its own models and control blocks |
| `xschem/xschemrc` | project-local XSchem config: SKY130 symbols, netlists into `simulation/` |
| `spice/drive.spice` | one NMOS and one PMOS, each fully on. What the two halves can do |
| `spice/vtc.spice` | the transfer curve of the $W_n = W_p$ = 1 µm inverter, and its supply current |
| `spice/vtc_ratio.spice` | five pull-up widths, one input, five switching thresholds |
| `spice/vtc_long.spice` | the same inverter at $L$ = 0.5 µm |
| `spice/delay.spice` | a real edge, a 10 fF load, and `.meas` for rise and fall delay |
| `spice/vtc_broken.spice` | `vtc.spice` with one node name changed. It is the trap |
| `src/inv.py` | the `wrdata` reader, and the one function that turns a VTC into numbers |
| `src/extract.py` | six blocks: the two halves, the naive inverter, sizing, timing, gain, power |
| `src/plot_inv.py` | the three figures on the docs page |
| `src/check.py` | recomputes twelve numbers, prints `PASS` or `FAIL` with a reason |
| `src/check_mine.py` | reads your schematic's netlist and grades it in words |

## The thing worth carrying out of here

An inverter with $W_p = W_n$ switches at **0.838027 V**, not at 0.900 V. Fixing
that has two different right answers:

| you want | set $W_p$ to | and you get |
|---|---|---|
| equal rise and fall delay | **2.5 µm** | 30.2508 ps down, 30.7067 ps up — 1.5 % apart |
| a switching threshold at $V_{DD}/2$ | **3.5 µm** | $V_M$ = 0.899865 V, 0.13 mV out |

2.4959 is the ratio of the two saturation currents, straight out of
`spice/drive.spice`. It is not a failed attempt at centring $V_M$ — it is the
exact answer to a different question, because delay is charge over current and
equal currents give equal delays.

A real standard-cell library picks neither. `sky130_fd_sc_hd__inv_1`, the
inverter LibreLane drops into your digital designs, is $W_n$ = 0.65 µm,
$W_p$ = 1.0 µm — a ratio of **1.54** — and you can read that straight out of
`/foss/pdks/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_fd_sc_hd.spice`.
Why a foundry would deliberately ship an asymmetric inverter is the first
extension in [`solutions/`](solutions/README.md).

## Where this goes next

You now have a schematic of a real logic gate, sized by you, verified against a
simulation. **AD104** takes exactly this file and asks you to draw it as
geometry in Magic — every transistor becomes a rectangle of diffusion under a
stripe of poly — then run DRC and LVS until the layout and this netlist agree.

The `nf=2` result from [Lab 04](../lab-04-wl-knob/README.md) is the first thing
that will make sense once you do.
