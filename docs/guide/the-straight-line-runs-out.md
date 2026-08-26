# The straight line runs out

**Question this page answers:** *Between ECE110 and AD102 I can already solve any circuit I
have been shown. Why does adding one diode break the method?*

Because the method was never about circuits. It was about **linearity**, and a diode is not
linear.

Here is the thing nobody says out loud in a first circuits course: superposition, Thévenin,
node-voltage with a matrix, the impedance algebra you do in your head — none of those are
facts about wires. They are **theorems**, and every one of them has the same hypothesis at the
top: *every element in this circuit is linear.* You have never had to check the hypothesis,
because until now it was always true.

This page is where it stops being true, and the first thing you should know is that it is not
a small change. It is not "the equations get harder". It is that **the theorem no longer
applies at all**, so its conclusion is not approximately right — it is not right.

## What linear actually promised you

An element is linear if it keeps two promises about the relationship between the voltage
across it and the current through it:

- **Scaling.** Double the voltage, double the current.
- **Additivity.** The response to $v_1 + v_2$ is the response to $v_1$ plus the response
  to $v_2$.

A resistor keeps both, trivially, because $i = v/R$ and division distributes over addition —
including the poly-silicon strips you sized in AD102, which are resistors like any other.
Capacitors and inductors keep both too, because differentiation and integration are linear
operations. Superposition is nothing more than additivity, applied to a whole circuit at once.

So the honest test of a component is: **drive it with A, drive it with B, drive it with A+B,
and see whether the third answer is the first two added up.** That is a measurement, not an
opinion, and [Lab 02](labs/lab-02-diode-iv-overview.md) ships the deck that makes it.

## Try this

```bash
cd labs/lab-02-diode-iv
make line
```

`spice/straight_line.spice` builds six one-ports: a 100 kΩ resistor and a 1 µm² SKY130 diode,
each driven three times — at 0.35 V, at 0.35 V again, and at 0.70 V, which is the sum of the
first two.

**What you should see** (about 2 seconds):

```
== additivity test: a resistor and a diode, driven three ways
--- 100 kohm resistor (amps) ---
    A alone, B alone, then A+B predicted by superposition, then measured
i_r_a = 3.500000e-06
i_r_b = 3.500000e-06
i_r_sum = 7.000000e-06
i_r_ab = 7.000000e-06
--- 1 um^2 diode (amps) ---
    A alone, B alone, then A+B predicted by superposition, then measured
i_d_a = 1.254090e-10
i_d_b = 1.254090e-10
i_d_sum = 2.508180e-10
i_d_ab = 3.917437e-06
```

Read the resistor first. **3.500000 µA + 3.500000 µA = 7.000000 µA**, and the measured answer
is 7.000000 µA. Seven digits, no rounding, no argument. That is what a theorem looks like when
its hypothesis holds.

Now read the diode. Superposition predicts **250.8180 pA**. The circuit delivers
**3.917437 µA**. Not 3 % out. Not 30 % out. Out by a factor of **15,618**.

**Why an engineer cares:** the wrong answer here is not noisy or obviously broken — it is a
clean, confident, plausible-looking number with seven significant figures. Nothing in the
output says "superposition does not apply." You have to know.

> **The reflex check:** before you write down a Thévenin equivalent, a superposition sum, or an
> impedance divider, ask *is every element in this loop linear?* One diode, one transistor, one
> anything with a curve in it, and the answer is no, and the tool you just reached for is the
> wrong tool.

## What the device actually looks like

This is the same diode, swept from −1 V to +0.9 V, plotted the way you have plotted everything
so far — current against voltage, both axes linear.

![Current against voltage for a 1 µm² SKY130 diode on linear axes: a flat line until about 0.6 V, then a near-vertical wall](../assets/img/ad103-diode-iv-linear.png)

*Produced by `src/plot_iv.py` in the Lab 02 package, from the 1901 rows that
`spice/diode_iv.spice` writes.*

A resistor on these axes is a straight line through the origin, and its slope is $1/R$. This is
not that. This is a **flat stretch and a wall**, and the interesting question is what the slope
is — because if the slope is the conductance, then this component's resistance is somewhere
between "infinite" and "almost zero" depending on where you stand on it, and the number 
$R$ has stopped being a property of the part.

Look at the flat stretch honestly. It is not zero current. At −1.000 V the sweep says
**−1.003559 pA**, and at +0.350 V it says **125.4090 pA** — 125 times more current,
which is a huge change, and on this plot both are indistinguishable from the axis. The linear
axes are throwing away the part of the curve that carries most of the physics. Fixing that is
[A diode is an exponential](guide/the-diode-is-an-exponential.md), two pages from here.

## What still works

The panic at this point is usually total, so: **Kirchhoff's laws are fine.**

KCL is charge conservation. KVL is energy conservation. Neither one says anything about what
the elements are made of, so neither one cares that one of them is a diode. Every node equation
you know how to write, you can still write.

| Tool | Still valid with a diode in the loop? |
|---|---|
| KCL, KVL | **Yes.** They are conservation laws, not linearity results. |
| Ohm's law on the *resistors* | **Yes.** The resistors did not stop being resistors. |
| Superposition | **No.** Demonstrated above, off by 15,618×. |
| Thévenin / Norton equivalent | **No** for the part of the circuit containing the diode. Still fine for the linear part around it — which turns out to be the trick. |
| Series/parallel combination | **No** for the diode. There is no $R$ to combine. |
| Solving the system by algebra | **Usually no.** You get an equation with $v$ both inside and outside an exponential, and no rearrangement gets $v$ alone. |

That last row is the real problem, and it is not a problem about diodes. It is a problem about
**equations**. Which is the next page.

## The prior this page is overwriting

You arrived believing that circuit analysis is a *procedure*: identify the topology, apply the
right theorem, turn the crank, get a number. For linear circuits that belief is completely
correct and it will serve you for the rest of your life.

What changes here is that analysis becomes a **search**. You will stop asking "what is the
answer" and start asking "what pair of numbers, one voltage and one current, satisfies both the
element and the circuit at the same time?" There is no crank. There is a target, and a way of
closing in on it.

Next: [The operating point](guide/the-operating-point.md) — how to get an exact number out of
an equation you cannot solve, and what `op` in a SPICE deck has been doing all along.
