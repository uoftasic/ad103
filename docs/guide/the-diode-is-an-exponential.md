# A diode is an exponential

**Question this page answers:** *Why an exponential? Of all the shapes a device could have,
why that one — and why does everyone keep saying "60 millivolts"?*

Because the diode is a **barrier**, current is carriers **climbing** it, and the number of
carriers with enough energy to climb a barrier of height $E$ is proportional to $e^{-E/kT}$.
That last fact is not electronics. It is the same statistics that make a chemical reaction go
faster when you heat it and make the atmosphere thin out with altitude. Put a barrier in front
of a thermal population and you get an exponential, every time.

The rest of this page is that sentence, made into numbers you measured yourself.

## What a junction is

Take one piece of silicon doped so that it has spare electrons to hand out (**n-type**), and
one doped so it has spare vacancies for electrons (**p-type**, and the vacancies are called
**holes**). Push them together. Nothing exotic happens; two things happen, and they fight.

**First, diffusion.** Electrons are thick on the n side and scarce on the p side, so they spill
across, the way a drop of ink spreads through water. Holes spill the other way. Nobody pushed
them. Diffusion is just the statistics of a lot of things moving randomly.

**Second, the bill comes due.** Every electron that leaves the n side leaves behind a positively
charged donor atom, nailed down in the crystal, and arrives on the p side as extra negative
charge. So the spilling builds an **electric field** across the junction, pointing from the n
side to the p side, and that field pushes the next electron back. The region it lives in has
been emptied of mobile carriers, which is why it is called the **depletion region**.

Equilibrium is where the two effects exactly cancel — diffusion pushing carriers across, the
field pushing them back, no net current. The field corresponds to a step in energy: a **built-in
barrier** an electron has to climb to get from the n side to the p side. Nobody applied it; it
built itself.

## Why the barrier gives you an exponential

At any temperature above absolute zero, the carriers are not all sitting at the same energy.
They are shared out over a range, with the number at energy $E$ falling off like $e^{-E/kT}$ —
a lot of carriers with a little energy, exponentially fewer with a lot of it. That is the
Boltzmann distribution and it is the single most reused fact in device physics.

Now apply a forward voltage $V$: plus on the p side, minus on the n side. That voltage opposes
the built-in field, so it **lowers the barrier** by $qV$. The number of carriers that can now
get over is multiplied by

$$
e^{qV/kT}
$$

and the current follows. Two consequences, and they are the whole device:

- **Forward bias is exponential**, because you are exponentially discounting a barrier.
- **Reverse bias saturates.** Reverse voltage makes the barrier *higher*, which stops the
  climbers entirely — but there is a second, much smaller current, made of the few minority
  carriers that thermal energy knocks loose near the junction and the field then sweeps across.
  Those are *falling down* the barrier, not climbing it, and falling costs nothing, so a deeper
  barrier does not produce more of them. Their supply is set by temperature alone, so the
  current is stuck at a tiny constant — which is why it is called the **saturation current**
  $I_0$.

Put the two together and you get the Shockley diode equation:

$$
I \;=\; I_0\left(e^{\,V/nV_T} - 1\right)
\qquad\text{where}\qquad
V_T \;=\; \frac{kT}{q}
$$

$V_T$ is the **thermal voltage**: the voltage whose energy $qV_T$ equals the characteristic
thermal energy $kT$. At the 27 °C ngspice simulates at, $V_T = 25.8649$ mV. The $-1$ makes the equation
give exactly zero at $V = 0$, and it is what produces the reverse saturation floor. The **$n$**
is an experimental fudge, called the **ideality factor**, which lands between 1 and 2 for real
junctions; you will extract it from your own data before the end of this page.

## The number everyone quotes

Rewrite the forward part in terms of *decades* of current instead of $e$-foldings. To multiply
the current by 10 you need $e^{V/nV_T} = 10$, so

$$
\Delta V = n V_T \ln 10
$$

With $n = 1$ and $V_T = 25.8649$ mV that is

$$
\Delta V = 25.8649\ \text{mV} \times 2.302585 = 59.556\ \text{mV}
$$

**That is the famous 60 mV/decade.** It is not a property of silicon, or of doping, or of the
process. It is $kT/q$ times $\ln 10$ — thermodynamics and arithmetic. Nothing you can do to a
diode makes it steeper than that at room temperature, and heating it makes it *worse*.

Real junctions are shallower, by the factor $n$. Your job now is to measure how much shallower
this one is.

## Try this

```bash
cd labs/lab-02-diode-iv
make
```

**What you should see** — the whole lab, in about six seconds. This is an excerpt; the
full 81 lines are in the [lab writeup](labs/lab-02-diode-iv-overview.md):

```
== DC sweep: 1901 points, -1.000 V to +0.900 V
   (about 2 s, model library included)
   wrote results/diode_iv.txt
...
  current      forward V     mV since previous decade
     1e-12 A   0.181962 V           -
     1e-11 A   0.264643 V       82.68
     1e-10 A   0.342408 V       77.77
     1e-09 A   0.419503 V       77.09
     1e-08 A   0.496518 V       77.02
     1e-07 A   0.573602 V       77.08
     1e-06 A   0.651480 V       77.88

  fit over 154 points from 1e-09 A to 1e-07 A:
    slope           : 77.037 mV/decade
    thermal voltage : 25.8649 mV  (27 degC)
    ideality n      : 1.2935
    I0 (V=0 intercept): 3.5864 fA
    leaves the line : 0.699 V, 3.8136 uA (line says 4.2487 uA)
```

**Read the middle column of that table before anything else.** Every step from 100 pA to 1 µA
costs between **77.02 and 77.88 mV**, four decades running. The device is charging you a fixed
toll per factor of ten, and that is what "exponential" means when you say it in millivolts.

**Why an engineer cares:** 77 mV per decade is the sentence that governs analog design. It says
you cannot get a big current change out of a small voltage change *or* a small current change
out of a big one — the exchange rate is fixed by physics. Every bias network, every reference,
every "why is this circuit so sensitive" question comes back to it.

## Reading the plot

![The same sweep with a logarithmic vertical axis: six decades of straight line, with a fitted 77.0 mV/decade line](../assets/img/ad103-diode-iv-log.png)

*Produced by `src/plot_iv.py` in the Lab 02 package.*

Same 1901 rows as the flat-and-a-wall picture in [The straight line runs
out](guide/the-straight-line-runs-out.md). One axis changed.

A **log axis** does not label equal *distances* with equal *differences*. It labels them with
equal **ratios**. Between $10^{-9}$ and $10^{-8}$ is the same vertical distance as between
$10^{-8}$ and $10^{-7}$, even though the second gap is ten times bigger in amps. Three
consequences you should internalise now, because every analog plot you meet for the rest of
your life uses this axis:

1. **A straight line on a log-y plot is an exponential**, and only an exponential. Its
   steepness is the exponent's rate — here, mV per decade.
2. **There is no zero.** Zero is infinitely far down, and a negative number cannot be drawn at
   all — which is why this plot shows only the forward half. Anything you want to see on both
   sides of zero needs either two plots or the *magnitude* of the current.
3. **Small features at the bottom are not small.** The wiggle near $10^{-13}$ spans as much
   real information as the wall at $10^{-4}$. Linear axes hide six decades of this device;
   this one hides nothing.

Read a value off it the way you read the table: find the gridline below your point, count how
far up towards the next one you are — **halfway up a decade is $\times 3.16$, not $\times 5$**
— and multiply.

## Extract the ideality factor yourself

You have a slope. Divide out the physics you already know:

$$
n \;=\; \frac{\text{measured mV/decade}}{V_T \ln 10}
   \;=\; \frac{77.0367}{59.556} \;=\; 1.2935
$$

Now open SKY130's own model card and look at what SkyWater wrote:

```bash
grep -m1 -A20 'model sky130_fd_pr__diode_pw2nd_05v5 d' \
  /foss/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice \
  | grep -E '^\+ (js|jsw|n|rs) '
```

```
+ js = 2.75e-015 ; Units: amper/meter^2
+ jsw = 6e-016 ; Units: amper/meter
+ n = 1.2928
+ rs = 981 ; Units: ohm (ohm/meter^2 if area defined)
```

(The `-m1` matters: that model card appears **twice** in the flattened corner file, so without
it every line comes out doubled and it looks like you found two different diodes.)

**1.2935 measured, 1.2928 declared.** You pulled a foundry parameter out of the slope of a
graph, and it agrees to five parts in ten thousand. That is what parameter extraction *is*, and
it is most of what a device engineer does for a living: not reading the number off a card, but
proving you can get it back out of a measurement.

> **The reflex check:** any time you have a straight run on a log-current plot, its slope in
> mV/decade divided by 59.6 is an ideality factor, and an ideality factor between 1 and 2 means
> "this is a junction". You will use this exact reflex on a MOSFET in
> [Four regions, not three](guide/four-regions-not-three.md) — that device's line comes out at
> 85.6 mV/decade, and it is not a coincidence that the number is in the same range.

## Both ends of the line are lies, and you should know whose

The straight part runs from about 0.3 V to about 0.7 V. Outside that it bends, at both ends,
and the two bends have completely different causes. One is the diode. One is the simulator.

### The bottom: that floor is ngspice, not silicon

At the bottom left the curve flattens into a floor near a picoamp. It is tempting to call that
the saturation current. It is not.

```bash
cd labs/lab-02-diode-iv
make floor
```

```
--- default GMIN = 1e-12 S (amps; negative = current flowing backwards) ---
    at -1.000 V, at -0.500 V, at +0.100 V
i_m1v0 = -1.00356e-12
i_m0v5 = -5.03558e-13
i_p0v1 = 1.672571e-13
--- GMIN = 1e-15 S: the same diode, a thousand times less simulator ---
    at -1.000 V, at -0.500 V, at +0.100 V
j_m1v0 = -4.55885e-15
j_m0v5 = -4.05763e-15
j_p0v1 = 6.735706e-14
```

Every SPICE puts a conductance called **GMIN** across every junction, because a perfectly
non-conducting branch makes the matrix it solves singular and the simulation fails to converge.
ngspice's default is $10^{-12}$ S — one picoamp per volt.

Do the arithmetic on the top row. At −1.000 V the current is 1.00356 pA and at −0.500 V it is
0.503558 pA. The **difference is 0.500002 pA across 0.5 V**, which is a conductance of
$1.000\times10^{-12}$ S, to six digits. That is not a diode. Diodes do not have a constant
resistance; that is GMIN, and it is the entire floor.

Subtract it and what is left is constant, which is what a saturation current is supposed to be:

| $V$ | current | minus GMIN$\times V$ | |
|---|---|---|---|
| −1.000 V | 1.00356 pA | **3.56 fA** | |
| −0.500 V | 0.503558 pA | **3.558 fA** | |
| −1.000 V, GMIN = 1e-15 | 4.55885 fA | **3.559 fA** | |
| −0.500 V, GMIN = 1e-15 | 4.05763 fA | **3.558 fA** | |

**3.558 fA**, four ways. Now look back at what the fit to the *forward* curve reported for the
$V = 0$ intercept: **3.5864 fA**. Two ends of the plot, two completely different pieces of
arithmetic, agreeing to 0.8 %. That is $I_0$, and it is femtoamps — about **22,000 electrons per
second**, which is the entire reverse current of this device.

One more, to close it properly. With GMIN out of the way, the forward point at +0.100 V reads
**67.357 fA**. The equation, using only the two numbers you extracted from the straight part of
the graph, predicts

$$
I_0\left(10^{\,V/77.0367\,\text{mV}} - 1\right)
 = 3.5864\ \text{fA} \times (19.858 - 1) = 67.63\ \text{fA}
$$

**Within 0.4 %** — and note that you needed the $-1$ to get there. At 0.1 V the $-1$ term is
still worth 5 % of the answer. That term is not decoration.

### The top: that bend is the diode, and it is a resistor

Above about 0.7 V the measured curve falls **below** the straight line and keeps falling. The
lab reports where: **0.699 V, 3.8136 µA, against 4.2487 µA on the line.**

That is not the junction failing. It is the **series resistance** of everything the current has
to get through *besides* the junction — the neutral silicon on either side, the contacts, the
metal. And you can extract it the same way you extracted $n$: the lab does, in the block right
below the fit.

```
  series resistance, from the top of the curve:
    at 0.900 V the diode carries 98.0354 uA
    the straight line needs only 0.804011 V for that current
    so 95.989 mV is dropped outside the junction
    rs = 95.989 mV / 98.0354 uA = 979.1 ohm
```

The junction only ever wanted 0.804011 V. The other **95.989 mV** was spent getting there. Look
at the model card you grepped a moment ago: **`rs = 981`**. You extracted 979.1 Ω
from the shape of a graph, and it agrees with the foundry's number to **0.2 %**.

That is why the top bends. As the current climbs, the wasted `I·rs` climbs with it, and it
climbs *linearly* while the junction's own requirement climbs only logarithmically — so it
wins. The lab's local-slope table shows the takeover happening (arrows added here):

```
   0.450  2.4887e-09       77.01     <- pure junction
   0.600  2.1945e-07       77.50
   0.700  3.9174e-06       85.92     <- rs starting to cost you
   0.800  3.3105e-05      151.64
   0.850  6.2443e-05      217.80     <- mostly a resistor now
```

**Why an engineer cares:** the useful exponential range of a real diode is finite at both ends,
and *the bottom end may be your simulator rather than your circuit*. A student who reports "my
diode's reverse leakage is 1 pA" has reported ngspice's default setting.

## The part that trips people up

Everything above says the diode's *voltage* is set by its current, not the other way around.
That inversion is the hardest habit to build, because for two years you have been told a
component is a thing you put a voltage across.

Try it the other way. Ask "what voltage does this diode sit at?" and the answer is "at what
current?". Ask "what happens if I put 0.900 V across it" and the sweep answers **98.0354 µA** —
**25 times** the current at 0.700 V, for 200 mV more drive. There is no such thing as *slightly*
too much voltage on a diode, which is the real reason every diode in every circuit you will ever
see has something current-limiting in series with it. Drive it with a current and it picks a
sensible voltage. Drive it with a voltage and you had better be right.

Next: [Three models of one diode](guide/three-models-of-one-diode.md) — when you are allowed to
say "0.7 volts and move on", and exactly how wrong it makes you.
