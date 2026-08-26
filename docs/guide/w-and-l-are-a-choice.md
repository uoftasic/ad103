# W and L are a choice

**Question this page answers:** *A resistor has a resistance and a capacitor has a
capacitance. What is the number you choose when you place a transistor?*

There isn't one. You choose two lengths.

Every equation on the last three pages carries the factor $W/L$, and it is the only factor in
them that is yours. $\mu_n$, $C_{ox}$ and $V_{TH}$ belong to the foundry and arrive fixed in
the model file. $V_{GS}$ and $V_{DS}$ belong to the rest of the circuit. $W$ and $L$ are two
numbers you type, and they are how a transistor gets designed.

This is the same lesson AD102 taught you about a resistor — [on a chip, a value is a
geometry](https://uoftasic.com/ad102/) — arriving in the device that matters most.

## The knob, turned four ways

`spice/wl_sweep.spice` puts four differently-shaped transistors at identical bias, $V_{GS} =
V_{DS} = 1.8$ V, and sweeps each drain:

| | $W$ | $L$ | $W/L$ | why it is here |
|---|---|---|---|---|
| **A** | 5 µm | 1 µm | 5 | the reference device from the last three pages |
| **B** | 10 µm | 1 µm | 10 | twice as wide |
| **C** | 5 µm | 2 µm | 2.5 | twice as long |
| **D** | 1 µm | 0.15 µm | 6.67 | minimum length — the interesting one |

**Predict before you look.** Current should scale with $W/L$. So relative to A: B should carry
2.00× as much, C should carry 0.50×, and D — whose $W/L$ is 6.67 against A's 5 — should carry
1.33×, or **928 µA**. Write those three numbers down.

```bash
cd labs/lab-03-mosfet-regions
make extract
```

```
== W/L is a knob   (V_GS = 1.8 V, V_DS = 1.8 V)
   device              W/L          I_D  I_D/I_D(A)  (W/L)/(W/L)_A
   A  W=5   L=1       5.00   696.275 uA      1.0000         1.0000
   B  W=10  L=1      10.00  1395.320 uA      2.0040         2.0000
   C  W=5   L=2       2.50   380.728 uA      0.5468         0.5000
   D  W=1   L=0.15    6.67   501.046 uA      0.7196         1.3333
```

![Four device geometries at the same bias, with the W/L prediction for the minimum-length device drawn as a dashed line](../assets/img/ad103-wl-sweep.png)

*From `spice/wl_sweep.spice`, drawn by `src/plot_curves.py`. The dashed line is what $W/L$
alone predicts for device D. The solid red curve is device D.*

Three predictions, one hit and two misses. Take them in order of how badly they missed,
because each miss has a different cause and each cause is worth having.

## B: width is honest — 0.20 % off

Predicted 1 392.551 µA, measured **1 395.320 µA**. Two parts in a thousand.

Width really is a clean multiplier. Doubling $W$ is physically identical to putting two of the
original transistors side by side and wiring them in parallel, which is *literally* how a wide
device is laid out on a real chip — as `nf` fingers of a narrower device. Nothing about the
physics along the channel changes, so nothing about the per-micron current changes.

The 0.20 % that is left over is the source and drain diffusion resistance, which does not
scale quite in step. You will meet it properly in AD104 when you draw one of these.

**The rule you can trust:** current is proportional to $W$. Use it in hand calculations without
apology.

## C: length is not — 9.4 % off

Predicted 348.138 µA, measured **380.728 µA**. The long device carries 9.4 % *more* than
$1/L$ says it should.

Not less — more. That direction is the clue. Go back to [Where saturation
starts](guide/where-saturation-starts.md): a longer channel with the same voltage across it
has a **lower field**, so its carriers are further from their speed limit and each one is
doing more work. Halving the current by doubling $L$ assumes carrier velocity is unaffected by
the field change, and it isn't.

The model agrees, in the parameter it reports: `vdsat` is **0.912 V** for the L = 2 µm device
and **0.779 V** for L = 1 µm — the longer device needs a bigger drain voltage before its
carriers give up, which is another way of saying it was less velocity-limited all along.

**The rule you can trust:** current goes *up* when you shorten the channel, but by less than
$1/L$. For quick reasoning, $1/L$ is the right direction and an optimistic magnitude.

## D: the minimum-length device misses by half — and the arithmetic closes

Predicted 928.367 µA. Measured **501.046 µA**. That is 54 % of the prediction, and it is the
most useful wrong answer in this course.

Your prediction was not bad. It was the answer to a different question — one that assumed
$V_{TH}$ and $\mu_n$ stay put when you change the shape. Neither does. Close the gap in two
steps.

**Step 1 — the threshold moved.** From `spice/op_params.spice`, at the same bias:

| | $L$ | model `vth` |
|---|---|---|
| A | 1 µm | 0.5895 V |
| C | 2 µm | 0.5495 V |
| **D** | **0.15 µm** | **0.7693 V** |

The minimum-length device has a threshold **180 mV higher**. Higher, on a shorter device —
which is the opposite of the "short-channel effect lowers $V_{TH}$" you may have heard, so it
is worth checking that it is real rather than an artefact of that one bias point.
`make vth-l` runs nine lengths at a low drain voltage, so the drain cannot be the cause:

```
== spice/vth_vs_l.spice
   L        model vth
   0.15 um    7.078517e-01 V
   0.2 um     6.872240e-01 V
   0.3 um     6.553824e-01 V
   0.5 um     6.300670e-01 V
   0.8 um     6.003750e-01 V
   1 um       5.894596e-01 V
   1.5 um     5.627056e-01 V
   2 um       5.495175e-01 V
   4 um       5.364102e-01 V
```

**171 mV, monotonically, over the process's whole length range.** It is real. The usual cause
in a modern process is the *halo* (or pocket) implant: extra doping placed near the source and
drain to suppress leakage in short devices. On a long channel those two pockets are a small
fraction of the length and barely register; on a 0.15 µm channel they are most of it, and they
push $V_{TH}$ back up. The effect even has a name — **reverse short-channel effect** — and it
is why `nfet_01v8` at minimum length is deliberately a harder device to turn on.

That eats a lot of the overdrive. Redo the prediction with each device's own threshold and the
square law:

$$\frac{I_D(\mathrm{D})}{I_D(\mathrm{A})} = \frac{(W/L)_\mathrm{D}\,(1.8-0.7693)^2}{(W/L)_\mathrm{A}\,(1.8-0.5895)^2} = \frac{6.667 \times 1.0624}{5 \times 1.4654} = 0.9666$$

$$696.275\ \mu\mathrm{A} \times 0.9666 = 673.06\ \mu\mathrm{A}$$

Better: from 928 down to 673, against a measured 501.

**Step 2 — the carriers hit their speed limit.** 501.046 / 673.06 = **0.744**. The remaining
26 % is velocity saturation, and the model hands you the receipt: `vdsat` for device D is
**0.362 V** while its overdrive $V_{GS} - V_{TH}$ is 1.031 V. That device stopped responding
to drain voltage at barely a third of the overdrive the square law assumed it would use.

So: shrink the transistor by 6.7× in length, and instead of 1.33× the current you get 0.72× —
because you paid 180 mV of threshold and you were already out of carrier velocity.

**Why an engineer cares.** This is the single most common failure mode in a first analog
design: a hand calculation that says the circuit works, a simulation that says it does not,
and a minimum-length device in the middle. Analog designers habitually pick $L$ **two to four
times the minimum**, and now you can see the three reasons at once — the square law still
roughly holds, $V_{TH}$ is closer to nominal, and $r_o$ is 3.3× larger (64.13 kΩ against
19.45 kΩ, from [Where saturation starts](guide/where-saturation-starts.md)). Digital designers
use minimum length for exactly the opposite reason: they want the smallest, fastest switch and
they do not care about $r_o$ at all.

**The reflex check:** whenever a device's measured current disagrees with $W/L$ scaling, look
at the model's `vth` and `vdsat` for that device *before* you look at your algebra. Two `print`
statements settle it.

## What geometry costs

$W/L = 5$ can be built as W = 5 µm, L = 1 µm, or as W = 0.75 µm, L = 0.15 µm. Same ratio,
identical in every equation on these pages, and **forty-four times the area** for the first
one (5 µm² against 0.1125 µm²).

| Device | $W \times L$ | area, relative to D |
|---|---|---|
| A | 5 × 1 | 33.3× |
| B | 10 × 1 | 66.7× |
| C | 5 × 2 | 66.7× |
| D | 1 × 0.15 | 1× |

Area is money. A wafer costs what it costs and you are billed for the square millimetres you
occupy, so every micron of $W$ you spend buying current is a micron you cannot spend on
something else. And $W$ costs more than area: gate capacitance scales with $W \times L$ too —
the 30.56 fF you met on [A MOSFET is a valve](guide/a-mosfet-is-a-valve.md) is for device A —
and every femtofarad of gate has to be charged by whatever drives it, which costs time and
energy somewhere else in the circuit.

That trade — **more current, more area, more capacitance, versus less of all three** — is what
"designing a transistor" means. There is no correct answer, only a chosen one.

## Try this

The lab ships a working sweep. Change it:

1. Open `spice/wl_sweep.spice` and add a fifth device: W = 20 µm, L = 4 µm, so $W/L$ is
   still 5 but every dimension of A is quadrupled. Add its drain source and its `dc` line, add
   a `let`/`wrdata` column, and re-run. **Predict first:** does it carry A's current?
2. Change device D's length from 0.15 to 0.5 and re-run `make extract`. Watch three numbers
   move together — `vth`, `vdsat`, and $I_D$ — and see whether the two-step arithmetic above
   still closes.
3. Set device B to `W=5u L=1u`. Run it. Read the error, and note that it is the *same* error
   you would get from a typo you did not notice. That is why the reflex check exists.

Numbers for all three are in
[`labs/lab-03-mosfet-regions/solutions/`](https://github.com/uoftasic/ad103/tree/main/labs/lab-03-mosfet-regions/solutions).
Try them before you open it — the file is a list of things to argue about, not a diff.

Next: [The inverter is an amplifier](guide/the-inverter-is-an-amplifier.md) — two transistors,
one wire between them, and the moment the digital track and the analog track turn out to be
describing the same circuit.
