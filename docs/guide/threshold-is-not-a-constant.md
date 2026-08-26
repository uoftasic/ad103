# Threshold is not a constant

**Question this page answers:** *I extracted $V_{TH} = 0.6016$ V for my transistor. Is that
its threshold voltage, or was it just its threshold voltage on Tuesday?*

On [Where saturation starts](guide/where-saturation-starts.md) you pinned a number down. You
drew a tangent, ran it to zero, subtracted half the drain voltage, and got 0.6016 V. Then you
found that a second honest method gave 0.5159 V, and BSIM's own opinion was 0.5895 V, and the
lesson was that **$V_{TH}$ is defined by its extraction method**.

That was the easy half. This page is the hard half: even with the method fixed, the *same
transistor* has a different threshold depending on three things you have been quietly holding
still. One of them is a terminal you have not touched yet.

## The terminal you have been ignoring

Look at any device line in this course:

```
XM1 d g 0 0 sky130_fd_pr__nfet_01v8 L=1 W=5
```

Four nodes: **drain, gate, source, bulk**. You have been wiring the last two to the same place
— node 0 — on every deck since Lab 01, so the difference between them has been exactly zero
and invisible.

The **bulk** (or *body*, or *substrate*) is the silicon the transistor is built *in*. For an
NMOS in this process that is the p-type wafer itself, and it is shared with every other NMOS on
the chip. You do not usually get to choose its voltage; it is tied to ground and that is that.

What you *do* get to choose, sometimes without meaning to, is the **source** voltage. Stack two
NMOS transistors in series — which is what the bottom half of a two-input NAND gate is — and
the upper one's source sits on the lower one's drain, somewhere above ground. Its bulk is still
at 0. So $V_{SB} > 0$, and the two terminals you have been treating as one are no longer one.

## Try this — lift the source and watch the threshold move

```bash
cd labs/lab-03-mosfet-regions
make vth-body
```

The deck is `spice/vth_body.spice`. It is the same W = 5 µm, L = 1 µm device this lab has used
throughout, with the source lifted onto its own node and $V_{GS}$ and $V_{DS}$ held fixed
*relative to the source*, so the only thing changing is $V_{SB}$.

**What you should see:**

```
--- vth and I_D vs V_SB, W = 5 um, L = 1 um, V_GS = 1.8 V, V_DS = 0.05 V ---
V_SB = 0 V
@m.xm1.msky130_fd_pr__nfet_01v8[vth] = 5.894596e-01
i(vds) = -6.63374e-05
V_SB = 0.3 V
@m.xm1.msky130_fd_pr__nfet_01v8[vth] = 6.607482e-01
i(vds) = -6.16210e-05
V_SB = 0.6 V
@m.xm1.msky130_fd_pr__nfet_01v8[vth] = 7.213725e-01
i(vds) = -5.77533e-05
V_SB = 0.9 V
@m.xm1.msky130_fd_pr__nfet_01v8[vth] = 7.745817e-01
i(vds) = -5.44634e-05
V_SB = 1.2 V
@m.xm1.msky130_fd_pr__nfet_01v8[vth] = 8.222507e-01
i(vds) = -5.15967e-05
```

| $V_{SB}$ | $V_{TH}$ | shift | $I_D$ |
|---:|---:|---:|---:|
| 0 V | 0.5894596 V | — | 66.3374 µA |
| 0.3 V | 0.6607482 V | **+71.289 mV** | 61.6210 µA |
| 0.6 V | 0.7213725 V | **+131.913 mV** | 57.7533 µA |
| 0.9 V | 0.7745817 V | **+185.122 mV** | 54.4634 µA |
| 1.2 V | 0.8222507 V | **+232.791 mV** | 51.5967 µA |

**232.791 mV.** Lifting the source 1.2 V above the bulk moved the threshold by nearly a quarter
of a volt, on a supply that is only 1.8 V total, and cost **22.2 %** of the drain current at
the same gate drive. Nothing was rewired and no dimension changed.

**Why an engineer cares:** this is the **body effect**, and it is why a two-input NAND gate is
slower than an inverter by more than the extra transistor's capacitance accounts for. The upper
device in the stack is fighting a threshold that is a hundred-odd millivolts higher than the
one on its datasheet, purely because its source is not at ground.

## Predict it — and this time the textbook is right

Here is the standard formula, the one your device-physics course will give you:

$$V_{TH}(V_{SB}) = V_{TH0} + \gamma\left(\sqrt{2\phi_F + V_{SB}} - \sqrt{2\phi_F}\right)$$

$\gamma$ is the **body-effect coefficient**, in $\sqrt{\text{V}}$, and $2\phi_F$ is roughly
twice the Fermi potential of the substrate — both set by how heavily the silicon is doped.
Neither is printed on anything you can easily read, so **fit them to your own five points** and
find out whether the formula is any good.

Take $V_{TH0} = 0.5894596$ V from the $V_{SB} = 0$ row, then least-squares the remaining four
for $\gamma$ and $2\phi_F$:

$$\gamma = 0.4108\ \sqrt{\text{V}} \qquad 2\phi_F = 0.600\ \text{V}$$

| $V_{SB}$ | measured | formula | difference |
|---:|---:|---:|---:|
| 0 V | 0.5895 V | 0.5895 V | — |
| 0.3 V | 0.6607 V | 0.6610 V | **−0.23 mV** |
| 0.6 V | 0.7214 V | 0.7213 V | **+0.11 mV** |
| 0.9 V | 0.7746 V | 0.7744 V | **+0.20 mV** |
| 1.2 V | 0.8223 V | 0.8224 V | **−0.15 mV** |

**Two parameters, five points, worst error 0.23 mV.** That is four significant figures of
agreement between a formula from the 1960s and a BSIM4 model with several hundred parameters in
it.

Stop and notice how different this feels from the last two pages. The square law missed the
saturation knee by 34 %. The $\sqrt{I_D}$ extraction missed the threshold by 12 %. And here the
same era of textbook physics lands within a fifth of a millivolt. **Simple models are not
uniformly wrong** — they are wrong about the things short channels broke and right about the
things short channels did not touch. The depletion charge under the channel does not care how
long the channel is, so the square-root law survived where the square law did not.

**The reflex check:** when a hand formula disagrees with a simulator, ask *which assumption of
the formula the device violates.* If you cannot name one, suspect your arithmetic instead.

## Second: the threshold depends on the length you drew

You already know that shortening a device raises its current. It also moves its threshold, and
in the direction almost nobody predicts.

```bash
make vth-l
```

`spice/vth_vs_l.spice` is nine copies of the same W = 5 µm transistor at nine lengths, all at
$V_{DS} = 50$ mV so the drain is not influencing the answer.

**What you should see:**

```
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

**Predict before you read on.** Most textbooks introduce *threshold roll-off*: as a channel
gets shorter, the source and drain depletion regions eat into the charge the gate has to
support, the gate's job gets easier, and $V_{TH}$ **falls**. Which way did these nine go?

Up. Monotonically. From **0.5364102 V** at L = 4 µm to **0.7078517 V** at L = 0.15 µm — a span
of **171.44 mV**, and the shortest device has the *highest* threshold, which is the opposite of
roll-off.

This is the **reverse short-channel effect**, and it is a manufacturing decision rather than a
physical inevitability. Processes at this node implant extra p-type dopant in pockets right
beside the source and drain — **halo** or **pocket** implants — specifically to fight roll-off,
because a short device whose threshold collapses is a short device that leaks. In SKY130 the
halo wins, and it over-corrects: the average doping under a short channel ends up *higher* than
under a long one, so the gate has more charge to support, not less.

**Why an engineer cares:** two things. First, you cannot shorten a transistor and keep its bias
point — 171 mV of threshold is most of an overdrive voltage. Second, and more usefully: this is
why analog designers who need two transistors to behave identically make them **the same
length**, always, without exception, even when the equations say only $W/L$ matters. Lab 04
already showed you five devices with identical $W/L$ carrying five different currents; this is
one of the reasons.

## Third: the threshold depends on how warm the chip is

The same `make vth-body` run ends with the same device at three temperatures — the automotive
range every real part is specified over.

**What you should see:**

```
--- and the same device, V_SB = 0, at three temperatures ---
T = -40 C
@m.xm1.msky130_fd_pr__nfet_01v8[vth] = 6.499250e-01
i(vds) = -9.38168e-05
T = 27 C
@m.xm1.msky130_fd_pr__nfet_01v8[vth] = 5.894596e-01
i(vds) = -6.63374e-05
T = 125 C
@m.xm1.msky130_fd_pr__nfet_01v8[vth] = 5.010177e-01
i(vds) = -4.50650e-05
```

| $T$ | $V_{TH}$ | $I_D$ |
|---:|---:|---:|
| −40 °C | 0.6499250 V | 93.8168 µA |
| 27 °C | 0.5894596 V | 66.3374 µA |
| 125 °C | 0.5010177 V | 45.0650 µA |

$V_{TH}$ falls by **148.9 mV** across the range — a slope of **−0.9025 mV/°C**, which is close
enough to the −1 mV/°C rule of thumb that you should just remember the rule of thumb.

Now look at the current column and predict the sign before you read the next sentence. A lower
threshold means more overdrive at the same gate voltage, so the hot device should carry *more*
current.

It carries **32.1 % less**. Cold, it carries **41.4 % more**.

The threshold is not the only thing temperature moves. Carrier **mobility** falls as the
lattice heats up and phonon scattering gets worse, roughly as $T^{-1.5}$, and at this
overdrive mobility wins the argument comfortably. Two effects, opposite signs, and which one
dominates depends on where you are biased — at very low overdrive, near threshold, the
threshold term wins instead and current goes *up* with temperature. The gate voltage at which
they cancel is called the **zero-temperature-coefficient point**, and circuits that must not
drift are sometimes deliberately biased there.

**The reflex check:** "does this get better or worse when it is hot?" has no general answer
for a MOSFET. Simulate both ends. This is exactly the corner discipline
[AD102](https://uoftasic.com/ad102/) drilled you on with resistors, and it matters more here,
because a resistor's temperature coefficient does not change sign on you.

## What to take away

- A transistor has four terminals. If you have never varied the fourth, you have never seen
  what it does — and it is worth 232.791 mV.
- The body-effect formula is *accurate*: two fitted parameters, worst error 0.23 mV. Not every
  simple model is a lie; the ones that survived short channels survived for a reason.
- Threshold rises as you shorten the device in this process, not falls. Halo implants, not
  physics — which means the direction is a property of *this* PDK, and you check it rather than
  assume it.
- Threshold moves about −0.9 mV per °C, and the current still goes down when you heat it,
  because mobility moves further.
- Every one of those numbers came out of two decks you can read:
  `spice/vth_body.spice` and `spice/vth_vs_l.spice`.

Next: [$g_m$ and $r_o$](guide/gm-and-ro.md) — you have spent three pages finding out how much
the current moves. Now put a name and a number on *how much it moves per volt*, which is the
one parameter every amplifier in your future is built out of.
