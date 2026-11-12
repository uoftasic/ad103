# Transconductance and output resistance

Everyone says a transistor amplifies. This page puts a number on how much, and shows what sets it:
the product $g_m r_o$.

So far you've measured currents, each one an answer to "what does this device do at this bias?".
An amplifier cares about something else: **how much the answer changes when you nudge the input.**
That is a slope, not a value, and a transistor has two slopes that matter, one for each terminal
you can move.

| Symbol | Name | It is the slope of | In words |
|---|---|---|---|
| $g_m$ | **transconductance** | $I_D$ vs $V_{GS}$ | how hard the gate pushes |
| $g_{ds}$ | **output conductance** | $I_D$ vs $V_{DS}$ | how much the drain leaks through |
| $r_o = 1/g_{ds}$ | **output resistance** | — | the same thing, upside down |

$g_m$ is in siemens because it is amps per volt, and it is *trans*-conductance because the volts
and the amps are at different terminals. That is the reason a transistor can have gain at all: a
two-terminal device's conductance can only turn a voltage into the current through *itself*.

## Measuring $g_m$

$g_m$ is the slope of the $I_D$ vs $V_{GS}$ curve you swept in Lab 03, Part 5. Differentiating that
sweep gave:

```
== g_m = dI_D/dV_GS   (V_DS = 1.8 V)
   V_GS = 0.90 V   I_D =    63.876 uA   g_m =  376.932 uS   g_m/I_D =   5.90 /V
   V_GS = 1.20 V   I_D =   217.505 uA   g_m =  634.008 uS   g_m/I_D =   2.91 /V
   V_GS = 1.50 V   I_D =   436.080 uA   g_m =  809.693 uS   g_m/I_D =   1.86 /V
   V_GS = 1.80 V   I_D =   696.275 uA   g_m =  914.650 uS   g_m/I_D =   1.31 /V
```

and, next to the model's own value:

```
   g_m at V_GS = 1.8 V                914.6500   915.3117  uS   -0.07 %
```

**914.650 µS from your 361-point sweep against 915.3117 µS from BSIM's analytic derivative, 0.07 %
apart.** Compare that with the threshold, where two reasonable methods disagreed by 86 mV. $g_m$ is
the slope of a measured curve, so there is no choice of definition to argue about.

## The square-law estimate

The square law gives a tidy expression for the slope:

$$I_D = \tfrac{1}{2}\mu_n C_{ox}\tfrac{W}{L}V_{ov}^2 \quad\Longrightarrow\quad
g_m = \frac{2 I_D}{V_{ov}}$$

At $V_{GS} = 1.8$ V, with $V_{TH} = 0.6016$ V from
[Where saturation starts](guide/where-saturation-starts.md), the overdrive is 1.1984 V and $I_D$ is
696.275 µA:

$$g_m = \frac{2 \times 696.275\ \mu\text{A}}{1.1984\ \text{V}} = 1162.0\ \mu\text{S}$$

The model gives **915.3 µS**, so the formula is **27 % high**.

Lower down, at $V_{GS} = 0.9$ V where the overdrive is only 0.2984 V:

$$g_m = \frac{2 \times 63.876\ \mu\text{A}}{0.2984\ \text{V}} = 428.1\ \mu\text{S}$$

Measured: **376.9 µS**. Now the formula is only **13.6 %** high.

This is the same failure as the saturation knee, with the same cause: velocity saturation. Push
the overdrive up and the current stops being quadratic, so its derivative stops being
$2I_D/V_{ov}$. At the fully velocity-saturated limit, $g_m = I_D/V_{ov}$, which at 1.8 V would
predict 581 µS, 36 % low. The truth lies between the two limits, in the region no closed-form
formula covers.

> **Use $2I_D/V_{ov}$ as a sanity bracket, not an answer.** If your simulator says $g_m$ is half
> or double that, look for a mistake. If it says 27 % less, that is a 130 nm transistor behaving
> normally.

## $g_m/I_D$: how designers size devices

Read the last column of the $g_m$ table again, from the bottom up:

| $V_{GS}$ | $I_D$ | $g_m$ | $g_m/I_D$ |
|---:|---:|---:|---:|
| 0.90 V | 63.876 µA | 376.932 µS | **5.90 /V** |
| 1.20 V | 217.505 µA | 634.008 µS | **2.91 /V** |
| 1.50 V | 436.080 µA | 809.693 µS | **1.86 /V** |
| 1.80 V | 696.275 µA | 914.650 µS | **1.31 /V** |

Between the first row and the last, the current goes up by a factor of **10.9** and the $g_m$ you
bought with it goes up by a factor of only **2.4**. $g_m/I_D$ is the exchange rate, how much
transconductance one ampere of bias current buys, and it collapses as you push the gate harder.

Go the other way and it climbs. The Lab 03 deck `spice/gm_ro.spice` steps the same device down to
$V_{GS} = 0.7$ V:

```
V_GS = 0.7 V
i(vdc) = -1.06419e-05
@m.xmc.msky130_fd_pr__nfet_01v8[gm] = 1.437123e-04
```

143.7123 µS on 10.6419 µA is **13.50 /V**: ten times the efficiency of the 1.8 V bias, on a
sixty-fifth of the current.

There is a ceiling. Deep below threshold the drain current is exponential in $V_{GS}$, and the
derivative of an exponential is proportional to itself, so $g_m/I_D$ levels off at

$$\left.\frac{g_m}{I_D}\right|_{\max} = \frac{1}{n V_T}$$

$V_T = kT/q = 25.8649$ mV at 27 °C, and $n$ comes from the subthreshold slope you measured in
Lab 03: **85.6 mV/decade**, so $n = 85.6/(2.3026 \times 25.8649) = 1.437$. The ceiling for this
device is

$$\frac{1}{1.437 \times 0.0258649} = 26.9\ /\text{V}$$

At $V_{GS} = 0.7$ V you are at 13.50, **half the ceiling**. That is the textbook definition of
**moderate inversion**: the region between the square law and the exponential, where most low-power
analog circuits live and where neither hand formula works.

This one number captures the whole design trade. Bias hard and you get speed, small devices and
poor current efficiency. Bias softly and you get more $g_m$ per microamp, at the cost of area and
bandwidth. Professional analog designers choose $g_m/I_D$ **first** (10 to 15 /V for a low-noise
amplifier, 5 for something that has to be fast) and let the geometry follow from it.

## $r_o$ and intrinsic gain

$g_m$ tells you how much signal current you get. To turn current back into voltage you have to
push it through a resistance, and the largest one available is the transistor's own $r_o$: the
slope of the "flat" saturation region that
[Where saturation starts](guide/where-saturation-starts.md#the-saturation-region-slopes-upward)
showed isn't flat.

Multiply the two and the current cancels:

$$A_{v,\max} = g_m r_o = \frac{g_m}{g_{ds}}$$

This is the **intrinsic gain**: the most voltage gain one transistor can ever produce, whatever you
build around it, because it assumes you loaded the transistor with something infinitely better than
itself. `spice/gm_ro.spice` measures it at four lengths, each at $V_{GS} = V_{DS}$ = 1.8 V:

| $L$ | $I_D$ | $g_m$ | $r_o = 1/g_{ds}$ | $g_m r_o$ | in dB |
|---:|---:|---:|---:|---:|---:|
| 0.15 µm | 2644.190 µA | 2468.806 µS | 3.588 kΩ | **8.86** | 18.9 dB |
| 0.5 µm | 1196.020 µA | 1460.824 µS | 24.008 kΩ | **35.07** | 30.9 dB |
| 1 µm | 696.275 µA | 915.312 µS | 64.130 kΩ | **58.70** | 35.4 dB |
| 4 µm | 197.974 µA | 274.342 µS | 386.764 kΩ | **106.11** | 40.5 dB |

Compare the two ends. The minimum-length device has **9.0× the transconductance** of the 4 µm one
and still gives **one twelfth of the gain**, because its output resistance is 108 times lower.
Channel-length modulation explains it: for a short channel, getting slightly shorter is a *large*
fractional change, so $g_{ds}$ is large.

**This is the most important trade in analog IC design, and it runs opposite to digital.** The
digital track, DD101 through DD104, wants every transistor as short as the process allows, because
short is fast. An analog designer who needs gain deliberately draws long devices and pays for them
in area and speed. Same process, same transistor, opposite instinct, and when the two teams share a
die, this is what they argue about.

> **Intrinsic gain in the tens is normal** for a modern process. If a hand analysis promises a
> gain of 500 from one transistor, it used a $\lambda$ from a textbook written when channels were
> microns long.

You'll run `spice/gm_ro.spice` yourself in Lab 04, Part 3.

## Where these numbers go next

**The inverter.** Take an NMOS and a PMOS, tie their gates together and their drains together, and
you have two transconductances driving one node, loaded by two output resistances in parallel:

$$A_v = -\left(g_{mn} + g_{mp}\right)\left(r_{on} \parallel r_{op}\right)$$

Both devices push, so their $g_m$ values add. That is why
[the CMOS inverter](guide/the-inverter-is-an-amplifier.md) measures a gain of **−116.0341** at
L = 0.5 µm, well above the 35.07 a single L = 0.5 µm device could manage alone.

**The mirror.** A saturated transistor is very nearly a current source, and $r_o$ measures how
nearly. An L = 1 µm device holding 50 µA changes its current by **1.46 %** when its drain moves from
0.9 V to 1.2 V. That is [the current mirror](guide/the-current-mirror.md), and its error budget is
this page's $r_o$ column.

## Check yourself

1. Why can a transistor have voltage gain when a resistor can't?
2. At $V_{GS}$ = 1.2 V, what does $2I_D/V_{ov}$ predict for $g_m$, using $V_{TH}$ = 0.6016 V? Is the
   measured value above or below it?
3. You need a $g_m$ of 1 mS from as little current as possible. Should you bias near threshold or
   with a large overdrive? What do you give up?
4. Going from L = 0.15 µm to L = 4 µm, $g_m$ falls and $g_m r_o$ rises. Explain both with one
   sentence each.

Next: [Sizing with W and L](guide/w-and-l-are-a-choice.md).
