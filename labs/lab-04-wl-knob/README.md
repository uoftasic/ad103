# Lab 04 — $W/L$ is a knob

Writeup: [uoftasic.com/ad103 → Lab 04](https://uoftasic.com/ad103/#/labs/lab-04-wl-knob-overview)

Four ngspice runs, seventeen transistors, one bias point. Every device in this
lab sits at $V_{GS} = V_{DS} = 1.8$ V, wide open and saturated, and the only
thing that ever changes is its **shape**. You write six predictions down before
you run anything, and then you find out how the $W/L$ rule does.

Short version: it does very well on $W$ and very badly on $L$, and the five
devices in Part 4 all have $W/L$ = 5.000 and carry five different currents.

## Run it

```bash
cd labs/lab-04-wl-knob
make
```

No environment setup needed. The `Makefile` pins `PDK=sky130A` itself, so this
runs in a bare container even if `.designinit` failed you.

Expected, in about **9 seconds** (8.82 s and 8.76 s on two timed clean runs):

```
== spice/w_ladder.spice
   wrote results/w_ladder.log
== spice/l_ladder.spice
   wrote results/l_ladder.log
== spice/same_ratio.spice
   wrote results/same_ratio.log
== spice/double_w.spice
   wrote results/double_w.log
== checking
  YOUR NUMBERS
  ok  I_D  W=1  L=1                  127.1470 uA  (reference 127.1470)
  ok  I_D  W=5  L=1                  696.2755 uA  (reference 696.2755)
  ok  I_D  W=10 L=1                 1395.3200 uA  (reference 1395.3200)
  ok  I_D  W=50 L=1                 6762.1370 uA  (reference 6762.1370)
  ok  I_D  W=5  L=0.15              2644.1910 uA  (reference 2644.1910)
  ok  I_D  W=5  L=4                  197.9738 uA  (reference 197.9738)
  ok  I_D  W=0.75 L=0.15             364.9284 uA  (reference 364.9284)
  ok  I_D  W=20 L=4                  798.0193 uA  (reference 798.0193)
  ok  two W=5 in parallel           1392.5510 uA  (reference 1392.5510)
  ok  vth(W=10) - vth(W=5)           -12.8354 mV  (reference -12.8354)

  2 x I_D(W=5)           =    1392.5510 uA
  two W=5 in parallel    =    1392.5510 uA   (difference +0.000000 uA)

PASS  all ten measured values match the reference run
```

That last pair is the point of the whole lab. Two 5 µm transistors wired in
parallel carry **exactly** twice one of them — the difference is zero to every
digit ngspice prints. One 10 µm transistor does not.

## Do this before you run anything else

Open `predictions.txt` and fill in the six blanks. It takes ninety seconds and
it is the only part of this lab you cannot get back afterwards.

```bash
make predict
```

```
  device            W/L    the W/L rule       measured       rule err   your guess    your err
  ------------------------------------------------------------------------------------------------
  W=10   L=1      10.00    1392.551 uA   1395.3200 uA     -0.2 %           --         --
  W=50   L=1      50.00    6962.755 uA   6762.1370 uA     +3.0 %           --         --
  W=5    L=2       2.50     348.138 uA    380.7284 uA     -8.6 %           --         --
  W=5    L=0.15   33.33    4641.837 uA   2644.1910 uA    +75.5 %           --         --
  W=0.75 L=0.15    5.00     696.275 uA    364.9284 uA    +90.8 %           --         --
  W=20   L=4       5.00     696.275 uA    798.0193 uA    -12.7 %           --         --
```

Six predictions from one rule. Two land, four miss, and the four miss in a
pattern you can read off the sign column.

## Targets

| Command | What it does |
|---|---|
| `make` | run the four decks and print a verdict |
| `make sweeps` | just the four ngspice runs → `results/*.log` |
| `make predict` | score `predictions.txt` against what actually happened |
| `make extract` | every number this lab teaches, with its working shown |
| `make figures` | redraw the three PNGs into `results/` |
| `make broken` | feed the checker a run that is wrong on purpose — **fails deliberately** |
| `make clean` | delete `results/` |

## Files

| Path | What it is |
|---|---|
| `predictions.txt` | six blanks. Fill them in first |
| `spice/w_ladder.spice` | six widths, 1 → 50 µm, all $L$ = 1 µm |
| `spice/l_ladder.spice` | six lengths, 0.15 → 4 µm, all $W$ = 5 µm, with `vth` and `vdsat` |
| `spice/same_ratio.spice` | five devices with $W/L$ = 5 exactly, and their gate capacitance |
| `spice/double_w.spice` | six ways of asking for "twice as wide". Two of them lie |
| `src/wl.py` | log parser and the two bits of shared arithmetic |
| `src/predict.py` | scores your predictions; does not grade them |
| `src/extract.py` | the four tables, with the working shown |
| `src/plot_wl.py` | the three figures on the docs pages |
| `src/check.py` | recomputes ten numbers, prints `PASS` or `FAIL` with a reason |
| `src/bend_it.py` | moves one measured number by 3 %, for `make broken` |

## The three results worth carrying out of here

**1. Width is a multiplier. Length is not.** Over the ladder, $I_D$ per micron
of width moves by 9.7 % between $W$ = 1 and $W$ = 10 and then back down 3.1 % by
$W$ = 50 — call it flat. $I_D \times L$, which $1/L$ says should be constant,
runs from **396.63** at $L$ = 0.15 µm to **791.90** at $L$ = 4 µm. It doubles.

**2. `mult=2` does nothing, silently.** The sky130 subcircuit declares a
parameter called `mult` and then never uses it, so a hand-written line reading
`W=5 mult=2` simulates as a single 5 µm device and ngspice says nothing at all.
`m=2` is the one that works. XSchem's symbol writes **both** onto every device
line — look at any netlist from Lab 01 and you will see `mult=1 m=1` — which is
why the schematic path gets this right and the copy-the-device-line path does
not.

**3. `nf` is not in $W/L$ and it changes the answer by 4.5 %.** `W=10 nf=2`
carries 1458.136 µA against `W=10 nf=1`'s 1395.320 µA. Same width, same length,
same bias. The difference is that two 5 µm fingers share a drain diffusion, and
that is a fact about the *layout*, not the schematic. AD104 is where you draw it.

> **A dead end worth knowing about.** Do not push `nf` up to see how far the
> effect goes. On this device, `W=10 nf=5` aborts the whole run with
> `Fatal: Drout = -1.76308 is negative` and
> `doAnalyses: no such parameter on this device` — a BSIM parameter check
> failing inside a model bin, not a mistake you made. Two fingers is the
> demonstration; five is a bug report.

## A file you did not ask for

Every run of this lab leaves a three-line `bsim4v5.out` in the lab folder:

```
Checking parameters for BSIM 4.5 model xf:sky130_fd_pr__nfet_01v8__model.5
Warning: Eta0 = -0.0310679 is negative.
```

`spice/double_w.spice` is the one that writes it, and `xf` is the `nf=2` device. BSIM's
parameter checker dumps a file whenever a model card has a value it wants to comment on, and
SkyWater's `nfet_01v8` bin 5 has a negative `Eta0`, which is legal and intentional. Nothing is
wrong, the run is not affected, and `make clean` removes it.

## Extensions

Three, with reference answers in [`solutions/`](solutions/README.md). Predict
first, then run, then read.

1. Add `W=100` to the W ladder. Then add `W=200`. One of them tells you where
   the model stops.
2. Build the same W ladder out of `pfet_01v8` and compare the two per-micron
   numbers. The ratio is not what the capstone will lead you to expect.
3. Re-run the L ladder with $V_{GS}$ = 0.9 V instead of 1.8 V. If velocity
   saturation is really what breaks $1/L$, the short-channel error should shrink.
   Check whether it does — and check what happens at the long end.
