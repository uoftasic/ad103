# The inverter is an amplifier

**Question this page answers:** *The digital track keeps drawing this circuit and calling it a
NOT gate. Why is it in the analog course?*

Because it is not a NOT gate. It is an amplifier that the digital track has agreed to only ever
look at from the two ends.

Two transistors, gates tied together, drains tied together. An NMOS pulling down, a PMOS
pulling up. In [DD101](https://uoftasic.com/dd101/) this is the smallest thing that computes;
in this course it is the smallest thing with gain — and this page is where those two
descriptions turn out to be one circuit.

## Everything you need is already measured

You have all four ingredients, from three earlier pages:

- A MOSFET is a valve, and it is **off** below threshold and **on** above it —
  [A MOSFET is a valve](guide/a-mosfet-is-a-valve.md)
- In between there are four regions, and the interesting one is saturation —
  [Four regions, not three](guide/four-regions-not-three.md)
- In saturation the gate moves the current by $g_m$, and the drain leaks it back through
  $r_o$ — [$g_m$ and $r_o$](guide/gm-and-ro.md)
- Electrons are more mobile than holes, so the same shape drawn p-type is weaker —
  [W and L are a choice](guide/w-and-l-are-a-choice.md)

Put them together and the inverter's whole behaviour falls out without a single new idea.

## The one number that starts everything: 2.4959

```bash
cd labs/capstone-inverter
make extract
```

**What you should see, first block:**

```
== 1. What each transistor can do on its own   W = 1 um, L = 0.15 um
   NMOS, gate and drain at 1.8 V          501.0462 uA
   PMOS, gate and drain at 0 V            200.7478 uA
   NMOS / PMOS                              2.4959
```

**501.0462 µA** should stop you. That is the same number Lab 01's `make` printed on your very
first day of this course, from a deck with one transistor in it. Nothing has drifted.

The PMOS, drawn exactly the same size and driven exactly as hard, carries **200.7478 µA** —
**2.4959 times less**. Holes drift more slowly through silicon than electrons do, by roughly
that factor in this process, and there is nothing a designer can do about it except draw the
PMOS wider. Every asymmetry on the rest of this page is that one ratio propagating.

## The transfer curve, and the part in the middle

Sweep the input from 0 to 1.8 V and plot the output.

![The voltage transfer characteristic of a CMOS inverter: flat at 1.8 V, a near-vertical drop near 0.84 V, flat at 0 V](../assets/img/ad103-inverter-vtc.png)

*`spice/vtc.spice`, $W_n = W_p = 1$ µm, $L = 0.15$ µm, SKY130 tt corner.*

Three parts, and the digital track only ever uses two of them:

- **Input low.** The NMOS is below threshold, the PMOS is fully on. Output sits at
  **1.7506 V**, and the circuit is a closed switch to $V_{DD}$.
- **Input high.** The mirror image. Output **0.0684 V**.
- **In between.** Both transistors are on, both are in *saturation*, and the output falls off a
  cliff.

That cliff is the amplifier. Its slope is the voltage gain, and `make extract` measures it:

```
   switching threshold V_M       0.838027 V   (V_DD/2 would be 0.900000)
   steepest slope                -13.1253     at V_in = 0.814 V
```

**A gain of −13.1253.** Wiggle the input by 1 mV near 0.814 V and the output wiggles by 13.1 mV
the other way. That is a real amplifier — a poor one, but the circuit does not know it is
supposed to be a logic gate.

**Why an engineer cares:** the reason digital logic works *at all* is that this gain is bigger
than one. A gate whose gain was 0.9 would shrink every signal a little on each hop and a chain
of them would fade to grey. Gain greater than unity is what makes a logic level *restore* — a
slightly degraded 1.6 V in comes out as a clean 1.7506 V. Digital design is analog design with
enough gain that nobody has to think about it.

## $V_M$ is not a threshold voltage

The **switching threshold** $V_M$ is the input at which output equals input — the point the
curve crosses the 45° line. Here it is **0.838027 V**, and $V_{DD}/2$ would be 0.900000 V, so
it sits **62.0 mV low**.

Predict why before reading on. Then note what $V_M$ is *not*:

```
   Note what V_M is not: it is not a threshold voltage of either device
   (those are 769.27 mV and 510.03 mV), and it is not their average.
   It is the input at which the two currents happen to be equal.
```

Neither 0.76927 V nor 0.51003 V, and their average (0.6396 V) is not it either. $V_M$ is a
*circuit* property: the input voltage at which the NMOS's current and the PMOS's current are
equal, both devices being in saturation. Since the NMOS is 2.4959× stronger, the currents
balance at an input **below** midpoint — it takes less gate voltage than you would expect to
let the pull-down win.

## Two sizings, two different jobs — and this is the trap

The obvious fix: make the PMOS 2.4959× wider so the two are equally strong. Try it, and watch
it not quite work.

```
   Wp (um)   Wp/Wn        V_M        error vs 0.9 V      gain
   1          1.00    0.838027 V      -61.97 mV     -13.1253
   2          2.00    0.869826 V      -30.17 mV     -12.8834
   2.5        2.50    0.882739 V      -17.26 mV     -11.8856
   3.5        3.50    0.899865 V       -0.13 mV     -11.2590
   4          4.00    0.905807 V       +5.81 mV     -11.2846
```

$W_p = 2.5$ µm — the ratio the current measurement told you to use — leaves **17.26 mV** of
error. Two thirds of the problem gone and a third of it stubbornly there. The ratio that
actually centres $V_M$ is **3.5**.

The reason is worth more than the number. Part 1 measured each device with its gate at the
*full* supply. But at $V_M$ the input is $V_M$, so the NMOS sees $V_{GS} = 0.9$ V and the PMOS
sees $V_{SG} = 0.9$ V — neither is anywhere near full drive, and the two devices' currents do
not scale with overdrive in the same way down there. **Matching currents at 1.8 V is a
different condition from matching them at 0.9 V**, and the first one is not the question you
asked.

Now time all three, into 10 fF:

```
   Wp (um)      t_pHL         t_pLH      pull-up / pull-down
   1          27.7001 ps    64.6539 ps         2.334
   2.5        30.2508 ps    30.7067 ps         1.015
   3.5        31.7807 ps    24.1077 ps         0.759
```

**The two sizings are answers to two different questions, and neither is wrong:**

| You want | Draw | You get |
|---|---|---|
| equal rise and fall time | $W_p = 2.5$ µm | 30.2508 / 30.7067 ps — 1.5 % apart |
| equal noise margins ($V_M$ centred) | $W_p = 3.5$ µm | $V_M$ = 0.899865 V, 0.13 mV out |

The $W_p = 3.5$ inverter rises **24 % faster than it falls**. The $W_p = 2.5$ inverter has its
switching point 17 mV low. There is no width that does both, and choosing between them is a
design decision that depends on whether your worry is timing or noise.

**The reflex check:** when two reasonable criteria give two different answers, you have found a
trade, not a mistake. Name both criteria out loud before you pick.

## Make it a real amplifier: change one letter

The gain was −13.1253 with $L = 0.15$ µm, the process minimum. [$g_m$ and
$r_o$](guide/gm-and-ro.md) says gain is $g_m$ times an output resistance, and $r_o$ grows
sharply with length. So lengthen both devices and change nothing else:

```
   L = 0.15 um, Wn = Wp = 1 um    gain  -13.1253 at V_in = 0.814 V
   L = 0.5  um, Wn = Wp = 1 um    gain -116.0341 at V_in = 0.712 V
                                  V_M   0.714056 V
```

**8.84× the gain for 3.33× the length.** Same two transistors, same supply, same schematic —
one number in one field.

![Two transfer curves overlaid: the L = 0.15 µm inverter and the much steeper L = 0.5 µm one](../assets/img/ad103-inverter-gain.png)

Check it against the previous page before you believe it. The intrinsic gain $g_m r_o$ of a
single $L = 0.5$ µm device measured **35.07**. The inverter gets **116.03**, more than three
times that — is the circuit cheating?

No: **both** transistors are amplifying. The gates are tied together, so a wiggle on the input
moves the NMOS current *and* the PMOS current, in the same direction through the output node.
The transconductances add and the output resistances parallel:

$$A_v = -\left(g_{mn} + g_{mp}\right)\left(r_{on} \parallel r_{op}\right)$$

Two devices pushing into one node is the cheapest gain in analog design, and this arrangement
has a name you will meet in AD201 — the **CMOS inverting amplifier**, or the push-pull stage.
It is the same schematic your logic library calls `inv_1`.

> **The bias problem, named now so it does not surprise you later.** To use this as an
> amplifier you have to hold the input at 0.712 V — on a cliff whose slope is 116, which means
> a 10 mV drift in bias moves the output by 1.16 V and slams it into a rail. A real amplifier
> spends most of its transistor count on *holding the operating point still*, and the first
> tool for that is [the current mirror](guide/the-current-mirror.md). That is the next page,
> and it is the last idea AD103 owes you.

## What the switch costs while it is switching

One more measurement, because it explains a thing you have felt with your hands.

```
   supply current at V_in = 0 V             0.000002 uA
   supply current at V_in = 1.8 V           0.000320 uA
   peak supply current                       20.0048 uA   at V_in = 0.891 V
```

At either end, one transistor is off and the gate draws **two picoamps**. That is why CMOS beat
every logic family before it: a gate that is not switching costs essentially nothing.

Halfway through a transition, both devices are on at once and **20.0048 µA** flows straight
from $V_{DD}$ to ground doing no useful work whatsoever. This is **short-circuit current**, and
it is one of the two reasons a chip warms up when it computes (the other is charging all that
gate capacitance). Multiply by a hundred million gates switching a billion times a second and
you have the entire thermal design of a processor.

**Why an engineer cares:** it also explains a rule the digital track states without proof —
*never leave an input floating.* A floating gate drifts to somewhere near $V_M$, parks the
inverter in the middle of that cliff, and burns 20 µA forever in a gate that is doing nothing.

## What to take away

- An inverter is an amplifier with a gain of **−13.1253** at minimum length, and digital logic
  works because that number is bigger than one.
- $V_M$ = **0.838027 V**, not $V_{DD}/2$, and not a threshold voltage of either device. It is
  where the two currents cross.
- Sizing for equal delay ($W_p = 2.5$) and sizing for a centred $V_M$ ($W_p = 3.5$) are
  different jobs with different answers.
- Lengthening both channels to 0.5 µm takes the gain to **−116.0341**, and the gains of the two
  devices add because their gates are tied together.
- Both devices on at once costs **20.0048 µA** of short-circuit current, which is why floating
  inputs are forbidden.

Next: [The current mirror](guide/the-current-mirror.md) — the circuit that holds an operating
point still, built out of the one habit
[AD102](https://uoftasic.com/ad102/) spent a whole lab teaching you.
