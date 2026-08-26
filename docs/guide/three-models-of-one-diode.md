# Three models of one diode

**Question this page answers:** *Everyone tells me a diode drops 0.7 V. The last page said it
is an exponential with no fixed voltage at all. Which one am I supposed to use?*

Both. On purpose, knowing which, and knowing what it costs you. A model is not a claim about
what a device *is* — it is a deliberate simplification with a stated error bar, and choosing one
is an engineering decision you make several times a day.

Here are the three you will actually use, from crudest to exact.

## Model 1 — the ideal switch

*Forward: a wire, 0 V. Reverse: an open circuit.*

This is the model you use in your head while reading a schematic, to answer "which way does the
current go?". It has no voltage in it and no current in it, and it is right about the only thing
it claims: **direction**.

## Model 2 — the constant drop

*Forward: a 0.7 V battery. Reverse: an open circuit.*

This is the one everybody quotes, and the reason it works is the number you measured:
**77.04 mV per decade**. Take it straight off the lab's own decade table: from 1 nA to 1 µA is
a factor of a **thousand** in current, and the voltage goes from **0.419503 V** to
**0.651480 V**. A thousand times the current, for 232 mV.

A device whose current can change by three orders of magnitude while its voltage changes by less
than a quarter of a volt is, from a certain distance, a battery. That distance is Model 2.

## Model 3 — the exponential

*$I = I_0\left(e^{V/nV_T}-1\right)$, solved together with the rest of the circuit.*

Exact, and the equation cannot be solved by rearrangement, so this model always comes with a
numerical method attached — either your own [three lines of
iteration](guide/the-operating-point.md) or SPICE's.

## What each one costs, in numbers you can check

One resistor from 1.8 V into one 1 µm² diode. Model 1 says the current is $1.8/R$. Model 2 says
$(1.8-0.7)/R$. Model 3 is what `make op` reported.

| $R$ | Model 1: switch | Model 2: 0.7 V | Model 3: measured | Model 1 error | Model 2 error |
|---|---|---|---|---|---|
| 10 kΩ | 180.00 µA | 110.00 µA | **90.94642 µA** | +97.9 % | +20.9 % |
| 100 kΩ | 18.000 µA | 11.000 µA | **10.60153 µA** | +69.8 % | +3.8 % |
| 1 MΩ | 1.8000 µA | 1.1000 µA | **1.143884 µA** | +57.4 % | −3.8 % |

Three things worth noticing, and none of them is "Model 2 is good".

**Model 2's error changes sign.** It is 3.8 % high at 10 µA and 3.8 % low at 1 µA, because 0.7 V
is simply where this junction happens to sit at a few microamps — above that the real voltage is
higher, below it lower. The constant-drop model is a *tangent point*, not a bound. Pick a diode
running at 100 µA and 0.7 V is a bad guess; pick one at 1 nA and it is a terrible one, because
[the sweep says](guide/the-diode-is-an-exponential.md) that diode is sitting at 0.419503 V.

**Model 2 degrades where you least expect.** It is *worst* at the largest current, where the
series resistance you extracted (979.1 Ω) has begun adding its own drop on top of the junction's.
At 10 kΩ it is out by a fifth.

**Model 1 is never better than 57 % wrong** in this circuit and is still the right model for
reading a schematic, because it is not answering this question.

## Which one to use

| You are asking | Use |
|---|---|
| which way does current flow; is this branch on or off | **Model 1** |
| roughly what current, roughly what headroom, on the back of an envelope | **Model 2**, and say "about" out loud |
| what does this actually do; will it still work at 0 °C; how much does it drift | **Model 3**, in a simulator |

> **The reflex check:** if a hand calculation used 0.7 V, and the answer it produced matters to
> better than about 10 %, redo it in the simulator. If you find yourself defending a
> two-significant-figure result that came out of a one-significant-figure model, you have
> stopped doing engineering.

## The fourth model you will meet next

There is one more, and it is the most useful of all: **replace the diode with a resistor whose
value is the slope of the curve at the operating point**. That is the small-signal model, it is
only valid for changes small enough that the curve looks straight, and it is how every amplifier
in this course is analysed. You have already computed one — 30.3 kΩ at the 1 MΩ operating point,
on [the operating point page](guide/the-operating-point.md).

## Making the diode bigger buys less than you think

One last thing before the MOSFET, because it is the thread running through this whole track. In
AD102 a resistor's value turned out to be a **geometry** — so many squares of doped silicon, and
the value followed. A diode is drawn the same way, out of the same kind of shapes, so the
obvious question is what the shape buys you here.

```bash
cd labs/lab-02-diode-iv
make area
```

```
--- Part 1: forward current at 0.500 V vs junction area (amps) ---
    area = 1, 4, 16, 100 um^2
i_1um = 1.109698e-08
i_4um = 3.457181e-08
i_16um = 1.186544e-07
i_100um = 6.679656e-07
```

Four square junctions — 1×1, 2×2, 4×4 and 10×10 µm — at the same 0.500 V.

**Predict before you read on.** A hundred times the area ought to be a hundred times the
current. It is **60.19** times.

Here is where the missing factor went. Divide each current by its own area, in nanoamps per
square micron, and put it next to the junction's perimeter-to-area ratio:

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

Now use it to predict the two rows you did not use. At $P/A = 2$ it gives **8.642917**, against
a measured 8.6429525. At $P/A = 1$ it gives **7.415882**, against a measured 7.415900. **Five
significant figures, on data the fit never saw.**

The diode is two devices in parallel: a **face**, whose current is proportional to area, and an
**edge**, whose current is proportional to perimeter. SkyWater says so directly on the model
card — `js` in amps per unit area, `jsw` in amps per unit length — and your four measurements
just reconstructed both terms without being told either one.

And the consequence is a fabrication fact worth carrying: **a small junction leaks more per
square micron than a big one**, because perimeter shrinks with the linear dimension while area
shrinks with its square. Two diodes of the same total area do not behave identically if one is
drawn as a long thin strip and the other as a square.

**Why an engineer cares:** run that 60.19× the other way round. At a *fixed current*, the
hundred-times-bigger diode sits lower by $77.04 \times \log_{10}(60.19) = 137$ mV. That is what
a junction a hundred times the size buys you: **a seventh of a volt**. Area is an
extraordinarily expensive way to move a diode's voltage, and every analog designer learns it
once, usually by drawing something enormous and getting almost nothing for it.

Next: [A MOSFET is a valve](guide/a-mosfet-is-a-valve.md) — a device with the same exponential
hiding inside it, plus a third terminal that lets you control the barrier from outside.
