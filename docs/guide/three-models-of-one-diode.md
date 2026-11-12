# Three diode models

Everyone tells you a diode drops 0.7 V. The last page showed it is an exponential with no fixed
voltage at all. You'll use both descriptions, deliberately, knowing what each one costs. A model is
a simplification with an error bar, and choosing one is an engineering decision you make several
times a day.

These are the three you'll use, from crudest to exact.

## Model 1: the ideal switch

*Forward: a wire, 0 V. Reverse: an open circuit.*

This is the model you use in your head while reading a schematic, to answer "which way does the
current go?". It has no voltage and no current in it, and it is right about the only thing it
claims: **direction**.

## Model 2: the constant drop

*Forward: a 0.7 V battery. Reverse: an open circuit.*

This is the one everybody quotes, and it works because of the number you saw on the last page:
**77.04 mV per decade**. From the decade table, going from 1 nA to 1 µA is a factor of a
**thousand** in current, and the voltage goes from **0.419503 V** to **0.651480 V**. A thousand
times the current for 232 mV.

A device whose current can change by three orders of magnitude while its voltage changes by less
than a quarter of a volt looks, from far enough away, like a battery. Model 2 is that view.

## Model 3: the exponential

*$I = I_0\left(e^{V/nV_T}-1\right)$, solved together with the rest of the circuit.*

This one is exact, and it can't be solved by rearrangement, so it always comes with a numerical
method: either your own [three lines of iteration](guide/the-operating-point.md) or SPICE's.

## What each model costs

Take one resistor from 1.8 V into one 1 µm² diode. Model 1 says the current is $1.8/R$. Model 2
says $(1.8-0.7)/R$. Model 3 is ngspice's operating point, from
[The operating point](guide/the-operating-point.md).

| $R$ | Model 1: switch | Model 2: 0.7 V | Model 3: ngspice | Model 1 error | Model 2 error |
|---|---|---|---|---|---|
| 10 kΩ | 180.00 µA | 110.00 µA | **90.94642 µA** | +97.9 % | +20.9 % |
| 100 kΩ | 18.000 µA | 11.000 µA | **10.60153 µA** | +69.8 % | +3.8 % |
| 1 MΩ | 1.8000 µA | 1.1000 µA | **1.143884 µA** | +57.4 % | −3.8 % |

Three things to notice, and none of them is "Model 2 is good".

**Model 2's error changes sign.** It is 3.8 % high at 10 µA and 3.8 % low at 1 µA, because 0.7 V
is simply where this junction happens to sit at a few microamps. Above that current the real
voltage is higher; below it, lower. The constant-drop model is a tangent point, not a bound. For a
diode running at 100 µA, 0.7 V is a bad guess; for one at 1 nA it is a terrible one, because the
[decade table](guide/the-diode-is-an-exponential.md#what-the-sky130-diode-measures) puts that
diode at 0.419503 V.

**Model 2 is worst at the largest current.** There, the series resistance (979.1 Ω) adds its own
drop on top of the junction's. At 10 kΩ the model is out by a fifth.

**Model 1 is never better than 57 % wrong** in this circuit, and it is still the right model for
reading a schematic, because it isn't trying to answer this question.

## Which one to use

| You are asking | Use |
|---|---|
| which way does current flow; is this branch on or off | **Model 1** |
| roughly what current, roughly what headroom, on the back of an envelope | **Model 2**, and say "about" out loud |
| what does this actually do; will it still work at 0 °C; how much does it drift | **Model 3**, in a simulator |

> **When to stop using 0.7 V.** If a hand calculation used 0.7 V and its answer matters to better
> than about 10 %, redo it in the simulator. A two-significant-figure result that came out of a
> one-significant-figure model isn't worth defending.

## The small-signal model

There is a fourth model, and it is the most useful of all: replace the diode with a resistor whose
value is the slope of the curve at the operating point. That is the **small-signal model**. It is
valid only for changes small enough that the curve looks straight, and it is how every amplifier
in this course is analysed. You've already seen one: 30.3 kΩ at the 1 MΩ operating point, on
[The operating point](guide/the-operating-point.md#small-signal-resistance).

## What junction area buys

In AD102 a resistor's value turned out to be a matter of geometry: so many squares of doped
silicon. A diode is drawn the same way, out of the same kinds of shapes, so the obvious question is
what the shape buys you here.

Lab 02 puts four square junctions (1×1, 2×2, 4×4 and 10×10 µm) at the same 0.500 V:

| area (µm²) | current at 0.500 V |
|---:|---:|
| 1 | 11.09698 nA |
| 4 | 34.57181 nA |
| 16 | 118.6544 nA |
| 100 | 667.9656 nA |

A hundred times the area ought to give a hundred times the current. It gives **60.19** times.

To find the missing factor, divide each current by its own area and put it next to the junction's
perimeter-to-area ratio:

| area (µm²) | perim (µm) | perim / area | current / area (nA/µm²) |
|---|---|---|---|
| 1 | 4 | 4.0 | 11.09698 |
| 4 | 8 | 2.0 | 8.6429525 |
| 16 | 16 | 1.0 | 7.415900 |
| 100 | 40 | 0.4 | 6.679656 |

Take **only the first and last rows** and fit a straight line through them:

$$
\frac{I}{A} \;=\; 6.188848 + 1.2270344 \times \frac{P}{A}\ \ \text{nA/µm}^2
$$

Now use it to predict the two rows you didn't use. At $P/A = 2$ it gives **8.642917**, against a
measured 8.6429525. At $P/A = 1$ it gives **7.415882**, against a measured 7.415900. That is five
significant figures on data the fit never saw.

So the diode is two devices in parallel: a **face**, whose current is proportional to area, and an
**edge**, whose current is proportional to perimeter. SkyWater's model card says so directly, with
`js` in amps per unit area and `jsw` in amps per unit length, and these four measurements
reconstruct both terms without being told either one.

That gives a fabrication fact worth remembering: **a small junction leaks more per square micron
than a big one**, because perimeter shrinks with the linear dimension while area shrinks with its
square. Two diodes of the same total area don't behave identically if one is a long thin strip and
the other a square.

Run the 60.19× the other way. At a *fixed current*, the diode with a hundred times the area sits
lower by $77.04 \times \log_{10}(60.19) = 137$ mV. A junction a hundred times the size buys you
**about a seventh of a volt**. Area is a very expensive way to move a diode's voltage, and most
analog designers learn this once, by drawing something enormous and getting almost nothing for it.

You'll run this measurement, and three ways of getting a diode's size silently wrong, in Lab 02,
Part 7.

## Check yourself

1. A diode carries 100 µA. Is Model 2's 0.7 V likely to be too high or too low? Use the decade
   table to justify your answer.
2. Using the fitted line above, what would the current per µm² be for a junction with
   $P/A = 0.1$?
3. You need to lower a diode's voltage by 77 mV at fixed current. Roughly how much bigger must the
   junction be, if area alone set the current? Why is the real answer bigger still?

Next: [Lab 02: The diode I–V curve](labs/lab-02-diode-iv-overview.md).
