# The operating point

**Question this page answers:** *If I cannot use superposition, and I cannot solve the equation
by hand, where does the number come from?*

From a search. And you can run the search yourself, on paper, in about ninety seconds — which
is worth doing once, because it is exactly what every SPICE simulation you will ever launch is
doing underneath.

## The smallest circuit that defeats algebra

One supply, one resistor, one diode:

```
   1.8 V ───[ 100 kΩ ]───┬───▶|───┐
                         │        │
                       v_node     ⏚
```

There is one unknown, `v_node`, and KCL at that node gives you one equation. The current down
through the resistor equals the current through the diode:

$$
\frac{1.8 - v}{100\,\text{k}\Omega} \;=\; I_{\text{diode}}(v)
$$

The left side is a straight line in $v$. The right side is the diode's curve, and — as the next
page shows — it is an exponential in $v$. So the equation you have to solve looks like

$$
\frac{1.8 - v}{100\,000} \;=\; I_0\!\left(e^{v/nV_T} - 1\right)
$$

with $v$ both outside an exponential and inside one. **There is no rearrangement of that
equation that ends with $v$ alone on the left.** This is not a gap in your algebra; it is a
property of the equation. Mathematicians call this kind transcendental, and the usual response
is to stop trying to be exact and start being *close, then closer*.

## Two ways to be close

### Draw both sides and look for the crossing

Plot the diode's curve, then plot the resistor's equation on the same axes. The resistor's
equation, $i = (1.8 - v)/R$, is a straight line with intercept $1.8/R$ and slope $-1/R$ — it is
called the **load line**, and drawing it is a hundred-year-old habit that is still the fastest
way to *see* what a circuit is going to do.

![The diode's measured curve with two resistor load lines, crossing at marked operating points](../assets/img/ad103-diode-load-line.png)

*Produced by `src/plot_iv.py` in the Lab 02 package. The blue curve is the same 1901 rows as
every other diode plot in this course.*

Anywhere on the blue curve, the diode is satisfied. Anywhere on an orange line, the resistor
and the supply are satisfied. **Only where they cross is everything satisfied at once**, and
that crossing point — one voltage and one current, together — is the **operating point**.

Two things fall straight out of the picture:

- Change the resistor and the operating point moves **along the diode's curve**, not off it.
  Going from 1 MΩ to 100 kΩ multiplies the current by 9.27 and moves the voltage by 83.7 mV.
  Ten times the current, less than a tenth of a volt.
- The diode's curve is so steep near 0.7 V that a huge change in the load line produces a small
  change in the voltage. That single observation is where the "a diode drops 0.7 V" rule of
  thumb comes from, and it is the subject of
  [Three models of one diode](guide/three-models-of-one-diode.md).

### Guess, correct, repeat

You can also do it numerically, with the curve you measured and a calculator. Start from the
folk rule, and use one measured anchor from your own sweep: the diode carries **3.917437 µA at
0.700 V**, and the curve climbs one decade of current per **77.04 mV**.

1. **Guess** $v = 0.700$ V. Then the resistor delivers $(1.8 - 0.700)/100\,\text{k}\Omega =
   11.000\ \mu\text{A}$.
2. **Correct.** At 11.000 µA the diode does not want 0.700 V, it wants
   $0.700 + 0.07704\log_{10}(11.000/3.917437) = 0.7345$ V.
3. **Repeat.** At 0.7345 V the resistor only delivers 10.655 µA, which the diode holds at
   0.7335 V, which gives 10.665 µA, which gives 0.7335 V again. **It has stopped moving.**

Your hand answer: **0.7335 V and 10.665 µA**. Three rounds of arithmetic.

## Now let ngspice do it

```bash
cd labs/lab-02-diode-iv
make op
```

**What you should see** (about 2 seconds):

```
== one resistor and one diode in series, three times
--- diode voltage at the operating point (volts) ---
    R = 10 kohm, 100 kohm, 1 Mohm
v(n1) = 8.905358e-01
v(n2) = 7.398473e-01
v(n3) = 6.561163e-01
--- and the current through it (amps) ---
i_10k = 9.094642e-05
i_100k = 1.060153e-05
i_1meg = 1.143884e-06
```

**0.7398473 V and 10.60153 µA**, against your hand answer of 0.7335 V and 10.665 µA. You were
**6.3 mV** and **0.60 %** away, from three lines of arithmetic and one measured anchor.

The 0.60 % is not sloppiness, and it is worth chasing, because the reason is a real property of
the device: you used a constant 77.04 mV/decade, and above about 0.7 V the diode's curve has
already started to bend away from that straight line. The lab measures exactly where it starts
to bend — **0.699 V** — and [the next page](guide/the-diode-is-an-exponential.md) explains why.
Run the same three lines with 86 mV/decade instead — the local value up there, measured — and
you land on **0.7373 V and 10.627 µA**: 2.6 mV and 0.24 % out, less than half the error.

## Check it against a completely different calculation

`op` and `.dc` are not the same computation. `op` solves the nonlinear system once, by
iterating. The sweep in `results/diode_iv.txt` is 1901 separate solves of a *different* circuit
— a lone diode driven by a voltage source, with no resistor anywhere. There is no reason the
two should agree except that they describe the same device.

Find, in the sweep file, the voltage where the diode's current equals the load line's:

```bash
cd labs/lab-02-diode-iv
python3 -c "
import sys; sys.path.insert(0,'src')
from iv import read_iv
v, i = read_iv()
prev = None
for a, b in zip(v, i):
    f = b - (1.8 - a)/1e5
    if prev and prev[1] < 0 <= f:
        v0, f0 = prev
        vx = v0 + (0 - f0)/(f - f0)*(a - v0)
        print(f'{vx:.6f} V   {(1.8 - vx)/1e5:.6e} A'); break
    prev = (a, f)
"
```

```
0.739846 V   1.060154e-05 A
```

`op` said `7.398473e-01` and `1.060153e-05`. **Six digits, from two calculations that share
nothing but the device.** When two independent routes to a number agree that far, the number is
not an artifact of either route.

**Why an engineer cares:** every amplifier, every current mirror, every logic gate is designed
by first choosing an operating point and then arranging for the circuit to sit there. The whole
back half of this course — [transconductance](guide/gm-and-ro.md),
[the inverter as an amplifier](guide/the-inverter-is-an-amplifier.md),
[the current mirror](guide/the-current-mirror.md) — is about picking that point on purpose
instead of discovering it afterwards.

## The slope at that point is a resistance

One preview, because it is the reason operating points matter at all.

Zoom in far enough on any curve and it looks like a straight line. Near the 1 MΩ operating
point above, the diode's own sweep gives $\Delta V = 2$ mV between the rows at 0.655 V and
0.657 V, and $\Delta I = 65.98$ nA across the same two rows — a slope of **30.3 kΩ**. To a small
wiggle riding on top of that operating point, the diode simply *is* a 30.3 kΩ resistor, and
superposition works again, for the wiggle.

That is the entire trick behind every analog circuit you have ever used: **be nonlinear enough
to set a bias point, then be linear about everything small that happens near it.** Move the
operating point and the resistance moves with it — at the 100 kΩ point the same measurement
gives 4.12 kΩ, seven times smaller, because you are ten times further up the curve.

> **The reflex check:** a small-signal resistance is only meaningful *at a stated operating
> point*. If someone quotes you the resistance of a diode without telling you the current
> through it, they have not told you anything.

Next: [A diode is an exponential](guide/the-diode-is-an-exponential.md) — where that curve comes
from, why it has to be an exponential, and how to read the plot that finally shows it.
