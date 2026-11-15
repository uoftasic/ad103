# Capstone: reference answers

**Don't read this first.** You can measure everything below in a minute with a copy of a deck you
already have, so think of this page as a list of things to argue about.

---

## 1. Why isn't the foundry's own inverter symmetric?

`sky130_fd_sc_hd__inv_1` is the inverter the digital flow uses, and its two transistors are written
out in plain text in the PDK:

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

That's $W_n$ = 0.65 µm, $W_p$ = 1.0 µm and $L$ = 0.15 µm, a ratio of 1.538, against the 2.5 that
balances delay and the 3.5 that centres $V_M$. A real library uses neither of the lab's answers.

Build it and measure it. When you do, note that the PMOS is `pfet_01v8_hvt`, a high-threshold
flavour, not the `pfet_01v8` this course has been using:

```
XN1 o1 in 0 0     sky130_fd_pr__nfet_01v8     L=0.15 W=0.65
XP1 o1 in vdd vdd sky130_fd_pr__pfet_01v8_hvt L=0.15 W=1.0
```

| inverter | $V_M$ | gain at $V_M$ |
|---|---|---|
| standard-cell sizes, `pfet_01v8_hvt` | **0.790872 V** | −18.5480 |
| the same sizes with plain `pfet_01v8` | 0.853087 V | −12.3578 |
| the lab's $W_p$ = 3.5 µm | 0.899865 V | −11.2590 |

The real cell switches 109 mV below the middle of the supply, and it does so on purpose. There are
three reasons, given here in the order they matter:

**Area.** Cell height is fixed by the library (every cell in `sky130_fd_sc_hd` is the same number of
tracks tall), so width is what a cell costs. Going from $W_p$ = 1.0 to $W_p$ = 3.5 makes the pull-up
3.5× wider, and that cost is paid on every one of the tens of thousands of inverters in a chip.

**Input capacitance.** Whatever drives this gate has to charge $W_n + W_p$ worth of gate. A wider
pull-up makes *this* inverter's rise faster and the *previous* stage's job harder, so in a chain of
inverters, widening the pull-up stops helping past a certain point.

**The threshold doesn't have to be centred.** In the gain column, the standard cell's gain is
−18.55, better than either of the lab's. Noise margins come from where the unity-gain points
are, not from where $V_M$ sits, and a steep curve with an off-centre $V_M$ can have good margins on
both sides.

The `_hvt` flavour is doing real work too. It raises the PMOS threshold, which cuts leakage while
the gate is idle, and a standard cell spends almost all of its life idle.

**To argue about:** the lab optimised one inverter for one property. A library optimises a
*population* of cells for area, leakage, and the delay of a chain. Which of the lab's two answers is
closer to being useful, and is either?

---

## 2. Size it for delay, and check the arithmetic closes

This one is in the lab itself (`make extract`, block 4), but the reasoning is worth writing out,
because it's the cleanest match between a prediction and a measurement in the course.

Propagation delay is, to a first approximation,

$$t_p \approx \frac{C_L \cdot V_{DD}/2}{I_{\text{drive}}}$$

The load and supply are the same for both halves, so within this formula, making the two drive
currents equal is exactly the same as making the two delays equal, with no further approximation.

`spice/drive.spice` measures the ratio of the two drive currents as 2.4959. Setting $W_p$ = 2.5 µm
gives:

| $W_p$ | $t_{pHL}$ | $t_{pLH}$ | ratio |
|---|---|---|---|
| 1 µm | 27.7001 ps | 64.6539 ps | 2.334 |
| **2.5 µm** | **30.2508 ps** | **30.7067 ps** | **1.015** |
| 3.5 µm | 31.7807 ps | 24.1077 ps | 0.759 |

The unsized inverter's delay ratio is 2.334 against the predicted 2.4959, and the sized one's is
1.015. The prediction came from two DC operating points, and it landed within 7 % on a transient
measurement of a different quantity.

Notice also that $t_{pHL}$ *rises* from 27.70 to 31.78 ps as the pull-up gets wider, even though
nothing about the pull-down changed. The wider PMOS is still partly on while the NMOS pulls down,
and it fights the NMOS. That's the same current that shows up as the 20.0048 µA short-circuit peak in
block 6.

---

## 3. How much gain can two transistors give?

Take `spice/vtc_long.spice` and keep making $L$ longer.

| $L$ | $V_M$ | gain at $V_M$ |
|---|---|---|
| 0.15 µm | 0.838027 V | −13.1253 |
| 0.5 µm | 0.714056 V | −116.0341 |
| 2 µm | 0.659120 V | **−247.3836** |

That's a gain of nearly 250 from two transistors and a wire, which makes it a real amplifier, and
it's why [The CMOS inverter](https://uoftasic.com/ad103/guide/the-inverter-is-an-amplifier.html)
treats the inverter as one.

Two things to notice before you get excited.

**$V_M$ moves down**, from 0.838 to 0.714 to 0.659 V. Longer channels raise both thresholds, but not by the
same amount, so the balance point moves. An amplifier biased at $V_M$ therefore has a bias point that
depends on the exact process corner, which is why real amplifiers use feedback and current mirrors
instead of hoping the bias lands in the right place.

**A gain of 247 comes with a bandwidth**, and you haven't measured it. Gain and speed trade against each other
through the same $g_m$ and the same capacitance, and every technique in AD201 is a way of spending
one to buy the other.

**To think about:** the $L$ = 2 µm inverter is a better amplifier and a useless logic gate: 13× the
area of the minimum-length one, far slower, and with a switching threshold 240 mV off centre.
It's better at one job, and nothing about it is better in general.

---

## The wiring mistake in `make broken`

The broken deck moves the PMOS source and body from `vdd` to `0`. The output sits at exactly
**0.000000000 V** for all 1801 input points, and the supply delivers **0.000000 µA**.

There is no error, no warning and no clue in the log, because the circuit is valid: a PMOS with its
source grounded just isn't a pull-up, so nothing holds the output node high and the NMOS wins at
every input.

The check that catches this in one line, on any inverter, is the one `src/check.py` does first:

```
V_out(0.0 V) = 1.800000 V   V_out(1.8 V) = 2.129252e-07 V
```

**Read both rails before anything else.** If the output doesn't swing from one supply to the other,
nothing further in the measurement means anything, and no amount of staring at $V_M$ will tell you
why.
