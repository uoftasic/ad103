# The operating point

If you can't use superposition and you can't solve the equation by hand, the number has to come
from a search. You can run that search yourself on paper in about ninety seconds, and it is worth
doing once, because it is what every SPICE simulation you launch does underneath.

## A resistor and a diode in series

One supply, one resistor, one diode:

```
   1.8 V ───[ 100 kΩ ]───┬───▶|───┐
                         │        │
                       v_node     ⏚
```

There is one unknown, `v_node`, and KCL at that node gives one equation: the current down through
the resistor equals the current through the diode.

$$
\frac{1.8 - v}{100\,\text{k}\Omega} \;=\; I_{\text{diode}}(v)
$$

The left side is a straight line in $v$. The right side is the diode's curve, which
[the next page](../guide/the-diode-is-an-exponential.md) shows is an exponential in $v$. So the
equation is

$$
\frac{1.8 - v}{100\,000} \;=\; I_0\!\left(e^{v/nV_T} - 1\right)
$$

with $v$ both outside an exponential and inside one. **No rearrangement of this equation leaves $v$
alone on one side.** That isn't a gap in your algebra; it is a property of the equation, which
mathematicians call **transcendental**. The usual response is to stop trying to be exact and
start getting close, then closer.

## Load lines

Plot the diode's curve, then plot the resistor's equation on the same axes. The resistor's
equation, $i = (1.8 - v)/R$, is a straight line with intercept $1.8/R$ and slope $-1/R$. It is
called the **load line**, and drawing it is still the fastest way to *see* what a circuit like this
will do.

![The diode's measured curve with two resistor load lines, crossing at marked operating points](../assets/img/ad103-diode-load-line.png)

*Produced by `src/plot_iv.py` in the Lab 02 package. The blue curve is the same 1901 rows as every
other diode plot in this course.*

Anywhere on the blue curve, the diode's equation is satisfied. Anywhere on an orange line, the
resistor and the supply are satisfied. Only where they cross is everything satisfied at once, and
that crossing, one voltage and one current together, is the **operating point**.

Two things follow from the picture:

- Changing the resistor moves the operating point **along the diode's curve**, not off it. Going
  from 1 MΩ to 100 kΩ multiplies the current by 9.27 and moves the voltage by 83.7 mV: ten times
  the current for less than a tenth of a volt.
- The diode's curve is so steep near 0.7 V that a large change in the load line produces a small
  change in voltage. That is where the "a diode drops 0.7 V" rule of thumb comes from, and
  [Three diode models](../guide/three-models-of-one-diode.md) puts a number on how good it is.

## Worked example: guess, correct, repeat

You can also find the operating point numerically, with a calculator and two facts from the
measured curve. Start from the folk rule, and use one measured anchor: the diode carries
**3.917437 µA at 0.700 V**, and its current rises one decade per **77.04 mV**.

1. **Guess** $v = 0.700$ V. The resistor then delivers $(1.8 - 0.700)/100\,\text{k}\Omega =
   11.000\ \mu\text{A}$.
2. **Correct.** At 11.000 µA the diode doesn't want 0.700 V. It wants
   $0.700 + 0.07704\log_{10}(11.000/3.917437) = 0.7345$ V.
3. **Repeat.** At 0.7345 V the resistor delivers only 10.655 µA, which the diode holds at
   0.7335 V, which gives 10.665 µA, which gives 0.7335 V again. It has stopped moving.

The hand answer is **0.7335 V and 10.665 µA**, after three rounds of arithmetic.

## What ngspice gets

ngspice's operating-point analysis, `op`, solves the same circuit by iterating until the answer
stops moving. For three resistor values it gives:

| $R$ | diode voltage | current |
|---|---:|---:|
| 10 kΩ | 0.8905358 V | 90.94642 µA |
| 100 kΩ | **0.7398473 V** | **10.60153 µA** |
| 1 MΩ | 0.6561163 V | 1.143884 µA |

Against the hand answer of 0.7335 V and 10.665 µA, you were **6.3 mV** and **0.60 %** away, from
three lines of arithmetic and one measured anchor.

The 0.60 % comes from a real property of the device. You used a constant 77.04 mV per decade, and
above about 0.7 V the diode's curve has already started to bend away from that straight line.
Lab 02 measures where the bend starts, **0.699 V**, and [the next
page](../guide/the-diode-is-an-exponential.md) explains why it happens. If you redo the three steps
with 86 mV per decade instead (the measured local value up there), you land on **0.7373 V and
10.627 µA**: 2.6 mV and 0.24 % out, less than half the error.

## Two independent calculations

`op` and a DC sweep (`.dc`) are different computations. `op` solves the nonlinear circuit once, by
iterating. The diode sweep is 1901 separate solves of a *different* circuit: a lone diode driven by
a voltage source, with no resistor at all. They should agree only because they describe the same
device.

So find, in the sweep data, the voltage where the diode's current equals the 100 kΩ load line's
current. Interpolating between the two sweep rows that bracket the crossing gives
**0.739846 V and 1.060154e-05 A**. `op` said 7.398473e-01 V and 1.060153e-05 A. The two agree to
six digits, from two calculations that share nothing but the device model. When two independent
routes to a number agree that far, the number is not an artifact of either route. You'll do this
comparison in Lab 02, Part 5.

Every amplifier, current mirror and logic gate is designed by first choosing an operating point
and then arranging for the circuit to sit there. The back half of this course
([transconductance](../guide/gm-and-ro.md), [the CMOS inverter](../guide/the-inverter-is-an-amplifier.md),
[the current mirror](../guide/the-current-mirror.md)) is about picking that point on purpose instead
of discovering it afterwards.

## Small-signal resistance

Zoom in far enough on any smooth curve and it looks like a straight line. Near the 1 MΩ operating
point, the diode's own sweep gives $\Delta V = 2$ mV between the rows at 0.655 V and 0.657 V, and
$\Delta I = 65.98$ nA across the same two rows: a slope of **30.3 kΩ**. To a small wiggle riding on
that operating point, the diode behaves as a 30.3 kΩ resistor, and superposition works again, for
the wiggle.

That is the idea behind every analog circuit you have used: be nonlinear enough to set a bias
point, then treat everything small that happens near it as linear. Move the operating point and
the resistance moves with it. At the 100 kΩ point the same measurement gives 4.12 kΩ, seven times
smaller, because the current there is ten times larger.

> **A small-signal resistance needs an operating point.** If someone quotes you the resistance of
> a diode without telling you the current through it, they haven't told you anything.

## Check yourself

1. In the worked example, why does the iteration converge instead of running away? (Think about
   the slopes of the two curves at the crossing.)
2. With $R$ = 1 MΩ, the load line is ten times flatter. Without calculating, would you expect the
   operating-point voltage to be higher or lower than with 100 kΩ? Check against the table.
3. The small-signal resistance is 30.3 kΩ at the 1 MΩ point and 4.12 kΩ at the 100 kΩ point. What
   does that tell you about how the slope of the curve changes with current?

Next: [The diode equation](../guide/the-diode-is-an-exponential.md).
