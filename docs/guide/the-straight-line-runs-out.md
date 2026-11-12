# Linearity and superposition

Between ECE110 and AD102 you learned to solve any circuit you were shown. This page explains why adding
one diode breaks that method, and what still works when it does.

Superposition, Thévenin, node-voltage analysis with a matrix, and the impedance algebra you do in
your head are not facts about wires. They are **theorems**, and every one of them has the same
hypothesis: *every element in this circuit is linear.* You have never had to check that
hypothesis, because until now it was always true. When it fails, the theorem doesn't apply at
all. Its answer isn't approximately right; it's wrong.

## What linear means

An element is **linear** if the relationship between the voltage across it and the current through
it keeps two promises:

- **Scaling.** Double the voltage, double the current.
- **Additivity.** The response to $v_1 + v_2$ is the response to $v_1$ plus the response to
  $v_2$.

A resistor keeps both, because $i = v/R$ and division distributes over addition. That includes
the poly-silicon strips you sized in AD102. Capacitors and inductors keep both too, because
differentiation and integration are linear operations. Superposition is additivity applied to a
whole circuit at once.

So you can test a component directly: drive it with A, drive it with B, drive it with A+B, and see
whether the third answer is the first two added up.

## The additivity test

Lab 02's `spice/straight_line.spice` runs exactly that test. It builds six one-ports: a 100 kΩ resistor and a
1 µm² SKY130 diode, each driven three times, at 0.35 V, at 0.35 V again, and at 0.70 V, which is
the sum of the first two. These are its results:

| | A (0.35 V) | B (0.35 V) | A + B, predicted | A + B, measured at 0.70 V |
|---|---:|---:|---:|---:|
| 100 kΩ resistor | 3.500000 µA | 3.500000 µA | 7.000000 µA | **7.000000 µA** |
| 1 µm² diode | 125.4090 pA | 125.4090 pA | 250.8180 pA | **3.917437 µA** |

For the resistor, 3.500000 µA + 3.500000 µA = 7.000000 µA, and the measured answer is 7.000000 µA,
to seven digits. That is what a theorem looks like when its hypothesis holds.

For the diode, superposition predicts **250.8180 pA**, and the circuit delivers **3.917437 µA**.
That is out by a factor of **15,618**.

The wrong answer is not noisy or obviously broken. It is a clean, plausible-looking number with
seven significant figures, and nothing in the output says "superposition does not apply". You
have to know.

> **Check before you reach for a linear tool.** Before you write down a Thévenin equivalent, a
> superposition sum or an impedance divider, ask whether every element in the loop is linear. One
> diode, one transistor, or anything else with a curve in it, and the answer is no.

You'll run this test yourself in Lab 02, Part 2.

## The diode on linear axes

This is the same diode swept from −1 V to +0.9 V, plotted the way you have plotted everything so
far: current against voltage, both axes linear.

![Current against voltage for a 1 µm² SKY130 diode on linear axes: a flat line until about 0.6 V, then a near-vertical wall](../assets/img/ad103-diode-iv-linear.png)

*Produced by `src/plot_iv.py` in the Lab 02 package, from the 1901 rows that
`spice/diode_iv.spice` writes.*

A resistor on these axes is a straight line through the origin with slope $1/R$. The diode is a
flat stretch and then a wall. If the slope is the conductance, then this component's resistance
is anywhere between "infinite" and "almost zero" depending on where you are on the curve, and $R$
is no longer a property of the part.

The flat stretch is not zero current. At −1.000 V the sweep reads **−1.003559 pA**, and at +0.350 V
it reads **125.4090 pA**: 125 times more current, and on this plot both are indistinguishable from
the axis. Linear axes hide the part of the curve that carries most of the physics.
[The diode equation](guide/the-diode-is-an-exponential.md) shows it on a better axis.

## What still works

**Kirchhoff's laws still hold.** KCL is charge conservation and KVL is energy conservation.
Neither says anything about what the elements are made of, so neither cares that one of them is a
diode. You can still write every node equation you know how to write.

| Tool | Still valid with a diode in the loop? |
|---|---|
| KCL, KVL | **Yes.** They are conservation laws, not linearity results. |
| Ohm's law on the *resistors* | **Yes.** The resistors are still resistors. |
| Superposition | **No.** Off by 15,618× in the test above. |
| Thévenin / Norton equivalent | **No** for the part of the circuit containing the diode. Still fine for the linear part around it, and that turns out to be useful. |
| Series/parallel combination | **No** for the diode. There is no $R$ to combine. |
| Solving the system by algebra | **Usually no.** You get an equation with $v$ both inside and outside an exponential, and no rearrangement gets $v$ alone. |

The last row is the hard one, and it is a problem about equations rather than about diodes.
That's the next page.

## From procedure to search

You arrived treating circuit analysis as a procedure: identify the topology, apply the right
theorem, turn the crank, get a number. For linear circuits that is correct, and it will serve you
for the rest of your career.

With a nonlinear element, analysis becomes a **search**. Instead of "what is the answer?", the
question is "which pair of numbers, one voltage and one current, satisfies both the element and
the rest of the circuit at the same time?" There is no crank to turn. There is a target, and a way
of closing in on it.

## Check yourself

1. A circuit contains only resistors, capacitors and inductors. Can you use superposition on it?
   Why?
2. Using the table above, how would you show that a diode fails the scaling promise as well as the
   additivity one?
3. Why can't you combine a diode in series with a resistor into one equivalent resistance?

Next: [The operating point](guide/the-operating-point.md).
