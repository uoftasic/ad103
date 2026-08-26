# Capstone — reference answers

**Do not read this first.** Everything below is measurable in a minute with a
copy of a deck you already have. This is a list of things to argue about.

---

## 1. Why is the foundry's own inverter not symmetric?

`sky130_fd_sc_hd__inv_1` is the inverter the digital flow uses. Its two
transistors are in the PDK, in plain text:

```bash
grep -A3 'subckt sky130_fd_sc_hd__inv_1 ' \
  /foss/pdks/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_fd_sc_hd.spice
```

```
.subckt sky130_fd_sc_hd__inv_1 A VGND VNB VPB VPWR Y
X0 VGND A Y VNB sky130_fd_pr__nfet_01v8 w=650000u l=150000u
X1 VPWR A Y VPB sky130_fd_pr__pfet_01v8_hvt w=1e+06u l=150000u
.ends
```

$W_n$ = 0.65 µm, $W_p$ = 1.0 µm, $L$ = 0.15 µm. **A ratio of 1.538**, against
the 2.5 that balances delay and the 3.5 that centres $V_M$. Both of this lab's
answers are wrong about what a real library does.

Build it and measure it. Note the PMOS is `pfet_01v8_hvt` — a *high-threshold*
flavour, not the device this course has been using:

```
XN1 o1 in 0 0     sky130_fd_pr__nfet_01v8     L=0.15 W=0.65
XP1 o1 in vdd vdd sky130_fd_pr__pfet_01v8_hvt L=0.15 W=1.0
```

| inverter | $V_M$ | gain at $V_M$ |
|---|---|---|
| standard-cell sizes, `pfet_01v8_hvt` | **0.790872 V** | −18.5480 |
| the same sizes with plain `pfet_01v8` | 0.853087 V | −12.3578 |
| this lab's $W_p$ = 3.5 µm | 0.899865 V | −11.2590 |

The real cell switches **109 mV below** the middle of the supply, and it does
that on purpose. Three reasons, in the order they matter:

**Area.** Cell height is fixed by the library — every cell in
`sky130_fd_sc_hd` is the same number of tracks tall — so width is what a cell
costs. Going from $W_p$ = 1.0 to $W_p$ = 3.5 makes the pull-up 3.5× wider, and
that cost is paid on every one of the tens of thousands of inverters in a chip.

**Input capacitance.** Whatever drives this gate has to charge $W_n + W_p$ of
gate. A wider pull-up makes *this* inverter's rise faster and the *previous*
stage's job harder. In a chain, past a point, widening stops helping.

**The threshold does not have to be centred.** Look at the gain column: the
standard cell's is **−18.55**, better than either of ours. Noise margins come
from where the unity-gain points are, not from where $V_M$ sits, and a steep
curve with an off-centre $V_M$ can have perfectly good margins on both sides.

The `_hvt` flavour is doing real work here too: it raises the PMOS threshold,
which cuts leakage when the gate is idle — and a standard cell spends almost
all of its life idle.

**Worth arguing about:** we optimised one inverter for one property. A library
optimises a *population* of cells for area, leakage, and the delay of a chain.
Which of this lab's two answers is closer to being useful, and is either?

---

## 2. Size it for delay instead, and check the arithmetic closes

This one is in the main lab (`make extract`, block 4), but the reasoning is
worth writing out because it is the cleanest closure in the course.

Propagation delay is, to a first approximation,

$$t_p \approx \frac{C_L \cdot V_{DD}/2}{I_{\text{drive}}}$$

Same load, same supply, both halves. So making the two drive currents equal is
*exactly* making the two delays equal — no approximation left over.

`spice/drive.spice` measures the ratio: **2.4959**. Set $W_p$ = 2.5 µm and:

| $W_p$ | $t_{pHL}$ | $t_{pLH}$ | ratio |
|---|---|---|---|
| 1 µm | 27.7001 ps | 64.6539 ps | 2.334 |
| **2.5 µm** | **30.2508 ps** | **30.7067 ps** | **1.015** |
| 3.5 µm | 31.7807 ps | 24.1077 ps | 0.759 |

**2.334 against the predicted 2.4959** for the unsized inverter, and 1.015 for
the sized one. The prediction was made from two DC operating points and it
landed inside 7 % on a transient measurement of a different quantity.

Notice also that $t_{pHL}$ *rises* from 27.70 to 31.78 ps as the pull-up gets
wider, even though nothing about the pull-down changed. The wider PMOS is still
partly on while the NMOS is pulling down, and it fights it. That is the same
current that showed up as the 20.0048 µA short-circuit spike in block 6.

---

## 3. How much gain can you get out of two transistors?

Take `spice/vtc_long.spice` and keep going.

| $L$ | $V_M$ | gain at $V_M$ |
|---|---|---|
| 0.15 µm | 0.838027 V | −13.1253 |
| 0.5 µm | 0.714056 V | −116.0341 |
| 2 µm | 0.659120 V | **−247.3836** |

Nearly **250** from two transistors and a wire. That is a real amplifier, and it
is why [The inverter is an amplifier](https://uoftasic.com/ad103/#/guide/the-inverter-is-an-amplifier)
is not a metaphor.

Two things to notice before you get excited.

**$V_M$ marches downward.** 0.838 → 0.714 → 0.659 V. Longer channels raise both
thresholds, but not by the same amount, and the balance point moves. An
amplifier biased at $V_M$ therefore has a bias point that depends on the exact
process corner — which is the entire reason real amplifiers use feedback and
current mirrors instead of being biased by hope.

**A gain of 247 has a bandwidth.** You have not measured one. Gain and speed
trade against each other through the same $g_m$ and the same capacitance, and
every technique in AD201 is a way of spending one to buy the other.

**Worth sitting with:** the $L$ = 2 µm inverter is a better amplifier and a
useless logic gate — 13× the area of the minimum-length one, far slower, and
with a switching threshold 240 mV off centre. Nothing about it is better in
general. It is better at one job.

---

## A note on the wiring mistake in `make broken`

The broken deck moves the PMOS source and body from `vdd` to `0`. Look at what
that produces: the output sits at exactly **0.000000000 V** for all 1801 input
points, and the supply delivers **0.000000 µA**.

There is no error, no warning, and no clue in the log. It is a perfectly valid
circuit — a PMOS with its source grounded is just not a pull-up, so the output
node has nothing holding it high and the NMOS wins at every input.

The reflex check that catches this in one line, on any inverter, is the one
`src/check.py` performs:

```
V_out(0.0 V) = 1.800000 V   V_out(1.8 V) = 2.129252e-07 V
```

**Read both rails before you read anything else.** If the output does not swing
from one supply to the other, nothing further in the measurement means anything,
and no amount of staring at $V_M$ will tell you why.
