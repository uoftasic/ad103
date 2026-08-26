# $g_m$ and $r_o$

**Question this page answers:** *Everyone keeps saying a transistor amplifies. Amplifies by how
much, exactly, and what sets the number?*

By $g_m r_o$, and this page is where those two symbols stop being letters.

You have measured a lot of currents. Every one of them was an answer to "what does this device
do at this bias?" An amplifier is not interested in that. An amplifier is interested in **how
much the answer changes when you nudge the input**, which is a slope, not a value — and a
transistor has two slopes that matter, one for each of the terminals you can move.

| Symbol | Name | It is the slope of | In words |
|---|---|---|---|
| $g_m$ | transconductance | $I_D$ vs $V_{GS}$ | how hard the gate pushes |
| $g_{ds}$ | output conductance | $I_D$ vs $V_{DS}$ | how badly the drain leaks through |
| $r_o = 1/g_{ds}$ | output resistance | — | the same thing, upside down |

$g_m$ is in siemens because it is amps per volt, and it is *trans*-conductance because the
volts and the amps are at different terminals. That is the whole reason a transistor can have
gain at all: a two-terminal device's conductance can only ever turn a voltage into the current
through *itself*.

## You already measured $g_m$ — twice

$g_m$ is not a new measurement. It is the slope of the $I_D$ vs $V_{GS}$ curve you swept in
Lab 03, and `make extract` differentiates it for you:

```bash
cd labs/lab-03-mosfet-regions
make extract
```

**What you should see:**

```
== g_m = dI_D/dV_GS   (V_DS = 1.8 V)
   V_GS = 0.90 V   I_D =    63.876 uA   g_m =  376.932 uS   g_m/I_D =   5.90 /V
   V_GS = 1.20 V   I_D =   217.505 uA   g_m =  634.008 uS   g_m/I_D =   2.91 /V
   V_GS = 1.50 V   I_D =   436.080 uA   g_m =  809.693 uS   g_m/I_D =   1.86 /V
   V_GS = 1.80 V   I_D =   696.275 uA   g_m =  914.650 uS   g_m/I_D =   1.31 /V
```

and further down, next to what the model itself thinks:

```
   g_m at V_GS = 1.8 V                914.6500   915.3117  uS   -0.07 %
```

**914.650 µS from your own 361-point sweep against 915.3117 µS from BSIM's analytic
derivative — 0.07 % apart.** Contrast that with the threshold, where two honest methods
disagreed by 86 mV. $g_m$ is a slope of a measured curve, and a slope of a measured curve has
no definitional wiggle room. **Some device parameters are opinions; this one is not.**

## Predict $g_m$ from the square law, and be 27 % wrong

The square law gives you a tidy expression for the slope:

$$I_D = \tfrac{1}{2}\mu_n C_{ox}\tfrac{W}{L}V_{ov}^2 \quad\Longrightarrow\quad
g_m = \frac{2 I_D}{V_{ov}}$$

Use it. At $V_{GS} = 1.8$ V, with your own $V_{TH} = 0.6016$ V from
[Where saturation starts](guide/where-saturation-starts.md), the overdrive is 1.1984 V and
$I_D$ is 696.275 µA:

$$g_m = \frac{2 \times 696.275\ \mu\text{A}}{1.1984\ \text{V}} = 1162.0\ \mu\text{S}$$

Measured: **915.3 µS**. The formula is **27 % high**.

Try it again lower down, at $V_{GS} = 0.9$ V where the overdrive is only 0.2984 V:

$$g_m = \frac{2 \times 63.876\ \mu\text{A}}{0.2984\ \text{V}} = 428.1\ \mu\text{S}$$

Measured: **376.9 µS**. Now it is only **13.6 %** high.

Same failure as the saturation knee, same cause: velocity saturation. Push the overdrive up and
the current stops being quadratic, so its derivative stops being $2I_D/V_{ov}$. The formula
degrades gracefully toward the *other* limit, $g_m = I_D/V_{ov}$, which at 1.8 V would predict
581 µS — 36 % low. The truth is between the two, which is exactly the region no closed form
covers.

**The reflex check:** $2I_D/V_{ov}$ is a sanity bracket, not an answer. If your simulator says
$g_m$ is half or double that, look for a mistake. If it says 27 % less, that is a 130 nm
transistor behaving normally.

## $g_m/I_D$ — the number analog designers actually size with

Look at the last column of that extract output again, and read it upward:

| $V_{GS}$ | $I_D$ | $g_m$ | $g_m/I_D$ |
|---:|---:|---:|---:|
| 0.90 V | 63.876 µA | 376.932 µS | **5.90 /V** |
| 1.20 V | 217.505 µA | 634.008 µS | **2.91 /V** |
| 1.50 V | 436.080 µA | 809.693 µS | **1.86 /V** |
| 1.80 V | 696.275 µA | 914.650 µS | **1.31 /V** |

Between the first row and the last, the current went up by a factor of **10.9** and the gain
you bought with it went up by a factor of only **2.4**. $g_m/I_D$ is the exchange rate — how
many siemens of transconductance one ampere of bias current buys — and it collapses as you push
the gate.

Push the other way and it climbs. `make gm-ro` steps the same device down to $V_{GS} = 0.7$ V:

```bash
make gm-ro
```

```
V_GS = 0.7 V
i(vdc) = -1.06419e-05
@m.xmc.msky130_fd_pr__nfet_01v8[gm] = 1.437123e-04
```

143.7123 µS on 10.6419 µA is **13.50 /V** — ten times the efficiency of the 1.8 V bias, on a
sixty-fifth of the current.

There is a ceiling. Deep below threshold the drain current is exponential in $V_{GS}$, and the
derivative of an exponential is proportional to itself, so $g_m/I_D$ flattens out at

$$\left.\frac{g_m}{I_D}\right|_{\max} = \frac{1}{n V_T}$$

$V_T = kT/q = 25.8649$ mV at 27 °C, and $n$ comes straight from the subthreshold slope you
already measured — **85.6 mV/decade**, and $n = 85.6/(2.3026 \times 25.8649) = 1.437$. So the
ceiling for this device is

$$\frac{1}{1.437 \times 0.0258649} = 26.9\ /\text{V}$$

At $V_{GS} = 0.7$ V you measured 13.50 — **half the ceiling**, which is the textbook definition
of *moderate inversion*, the region between the square law and the exponential where most
low-power analog circuits actually live and where neither hand formula works.

**Why an engineer cares:** this is the whole design trade in one number. Bias hard and you get
speed, small devices, and terrible current efficiency. Bias softly and you get gain per
microamp, at the cost of area and bandwidth. Professional analog design is done by choosing
$g_m/I_D$ **first** — 10 to 15 /V for a low-noise amplifier, 5 for something that has to be
fast — and letting the geometry fall out of it.

## The other slope: $r_o$, and the gain ceiling

$g_m$ tells you how much current your signal makes. To turn current back into voltage you have
to push it through a resistance, and the largest resistance available is the transistor's own
$r_o$ — the finite slope of "flat" saturation that
[Where saturation starts](guide/where-saturation-starts.md) refused to let you call flat.

Multiply the two and the current cancels:

$$A_{v,\max} = g_m r_o = \frac{g_m}{g_{ds}}$$

This is the **intrinsic gain**: the most voltage gain one transistor can produce, ever,
regardless of what you build around it, because it assumes you loaded it with something
infinitely better than itself. `make gm-ro` measures it at four lengths:

```
--- W = 5 um, V_GS = V_DS = 1.8 V, four channel lengths ---
L = 0.15 um
i(vda) = -2.64419e-03
@m.xma.msky130_fd_pr__nfet_01v8[gm] = 2.468806e-03
@m.xma.msky130_fd_pr__nfet_01v8[gds] = 2.787163e-04
```

| $L$ | $I_D$ | $g_m$ | $r_o = 1/g_{ds}$ | $g_m r_o$ | in dB |
|---:|---:|---:|---:|---:|---:|
| 0.15 µm | 2644.190 µA | 2468.806 µS | 3.588 kΩ | **8.86** | 18.9 dB |
| 0.5 µm | 1196.020 µA | 1460.824 µS | 24.008 kΩ | **35.07** | 30.9 dB |
| 1 µm | 696.275 µA | 915.312 µS | 64.130 kΩ | **58.70** | 35.4 dB |
| 4 µm | 197.974 µA | 274.342 µS | 386.764 kΩ | **106.11** | 40.5 dB |

Read the two ends against each other. The minimum-length device has **2.7× the
transconductance** of the 4 µm one and still gives **one twelfth the gain**, because its output
resistance is 108 times worse. Channel-length modulation eats it alive: a short channel that
gets slightly shorter is a *large* fractional change, so $g_{ds}$ is large.

**This is the single most important trade in analog IC design, and it runs opposite to
digital.** The digital track spends DD101 through DD104 wanting every transistor as short as
the process allows, because short is fast. An analog designer who needs gain deliberately draws
long devices and pays for them in area and speed. Same PDK, same transistor, opposite instinct —
and when the two teams share a die, this is what they argue about.

**The reflex check:** intrinsic gain in the tens is normal for a modern process. If a hand
analysis promises you a gain of 500 from one transistor, you have used a $\lambda$ from a
textbook written when channels were microns long.

## Where the numbers meet the circuit

Two previews you will cash in shortly.

**The inverter.** Take an NMOS and a PMOS, tie their gates together, tie their drains together,
and you have two transconductances driving one node loaded by two output resistances in
parallel:

$$A_v = -\left(g_{mn} + g_{mp}\right)\left(r_{on} \parallel r_{op}\right)$$

Both devices push, so the gains *add* — which is why
[the inverter](guide/the-inverter-is-an-amplifier.md) measures a gain of **−116.0341** at
L = 0.5 µm, comfortably more than the 35.07 a single L = 0.5 µm device could manage alone.

**The mirror.** A transistor in saturation is very nearly a current source, and "very nearly"
is measured in $r_o$: an L = 1 µm device holding 50 µA changes its mind by **1.46 %** when its
drain moves from 0.9 V to 1.2 V. That is [the current mirror](guide/the-current-mirror.md), and its error budget
is this page's second column.

## What to take away

- $g_m$ is a slope you can measure from your own sweep, and your answer will agree with the
  model's to a fraction of a percent. Unlike $V_{TH}$, it is not a matter of method.
- $2I_D/V_{ov}$ over-predicts $g_m$ by 27 % at full overdrive and 14 % at low overdrive. Use it
  for direction, not magnitude.
- $g_m/I_D$ is the efficiency of your bias current, it runs from about 1.3 /V at full overdrive
  to a ceiling of 26.9 /V deep in subthreshold, and choosing it is how professionals start a
  design.
- $g_m r_o$ is the gain ceiling of one transistor: **8.86** at minimum length, **106.11** at
  L = 4 µm. Long devices for gain, short devices for speed, and you cannot have both.

Next: [W and L are a choice](guide/w-and-l-are-a-choice.md) — you now have every parameter that
$W$ and $L$ move. Time to move them on purpose and watch the $W/L$ rule you were taught fall
apart.
