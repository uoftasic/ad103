# What moves the threshold

In Lab 03 you extracted $V_{TH} = 0.6016$ V for the W = 5 µm, L = 1 µm transistor. A second
method gave 0.5159 V, and BSIM's own value was 0.5895 V, which showed that **$V_{TH}$ is defined by
its extraction method**.

This page covers the other half: even with the method fixed, the *same transistor* has a
different threshold depending on three things you have been holding still. They are the voltage
between source and bulk, the length you drew, and the temperature.

## The fourth terminal

Look at any device line in this course:

```
XM1 d g 0 0 sky130_fd_pr__nfet_01v8 L=1 W=5
```

Four nodes: **drain, gate, source, bulk**. You have wired the last two to the same place, node 0,
on every deck since Lab 01, so the voltage between them has always been zero.

The **bulk** (also called the *body* or *substrate*) is the silicon the transistor is built in.
For an NMOS in this process that is the p-type wafer itself, shared with every other NMOS on the
chip. You don't usually get to choose its voltage: it is tied to ground.

What you *can* change, sometimes without meaning to, is the **source** voltage. Stack two NMOS
transistors in series, as in the bottom half of a two-input NAND gate, and the upper one's source
sits on the lower one's drain, somewhere above ground. Its bulk is still at 0, so $V_{SB} > 0$.

## Body effect

The Lab 03 deck `spice/vth_body.spice` uses the same W = 5 µm, L = 1 µm device with the source
lifted onto its own node. $V_{GS}$ and $V_{DS}$ are held fixed *relative to the source*
($V_{GS}$ = 1.8 V, $V_{DS}$ = 0.05 V), so the only thing that changes is $V_{SB}$:

| $V_{SB}$ | $V_{TH}$ | shift | $I_D$ |
|---:|---:|---:|---:|
| 0 V | 0.5894596 V | — | 66.3374 µA |
| 0.3 V | 0.6607482 V | **+71.289 mV** | 61.6210 µA |
| 0.6 V | 0.7213725 V | **+131.913 mV** | 57.7533 µA |
| 0.9 V | 0.7745817 V | **+185.122 mV** | 54.4634 µA |
| 1.2 V | 0.8222507 V | **+232.791 mV** | 51.5967 µA |

Lifting the source 1.2 V above the bulk moved the threshold by **232.791 mV**, nearly a quarter of
a volt on a supply that is only 1.8 V, and cost **22.2 %** of the drain current at the same gate
drive. Nothing was rewired and no dimension changed.

This is the **body effect**. It is why a two-input NAND gate is slower than an inverter by more
than the extra transistor's capacitance accounts for: the upper device in the stack works against a
threshold a hundred-odd millivolts higher than the one on its datasheet, because its source isn't
at ground.

## The body-effect formula

This is the standard formula, the one your device-physics course will give you:

$$V_{TH}(V_{SB}) = V_{TH0} + \gamma\left(\sqrt{2\phi_F + V_{SB}} - \sqrt{2\phi_F}\right)$$

$\gamma$ is the **body-effect coefficient**, in $\sqrt{\text{V}}$, and $2\phi_F$ is roughly twice the
Fermi potential of the substrate. Both are set by how heavily the silicon is doped, and neither is
printed anywhere easy to read. So fit them to the five measured points and see whether the formula
is any good.

Take $V_{TH0} = 0.5894596$ V from the $V_{SB} = 0$ row, then least-squares fit the other four for
$\gamma$ and $2\phi_F$:

$$\gamma = 0.4108\ \sqrt{\text{V}} \qquad 2\phi_F = 0.600\ \text{V}$$

| $V_{SB}$ | measured | formula | difference |
|---:|---:|---:|---:|
| 0 V | 0.5895 V | 0.5895 V | — |
| 0.3 V | 0.6607 V | 0.6610 V | **−0.23 mV** |
| 0.6 V | 0.7214 V | 0.7213 V | **+0.11 mV** |
| 0.9 V | 0.7746 V | 0.7744 V | **+0.20 mV** |
| 1.2 V | 0.8223 V | 0.8224 V | **−0.15 mV** |

Two parameters, five points, and a worst error of **0.23 mV**: four significant figures of
agreement between a formula from the 1960s and a BSIM4 model with several hundred parameters.

Compare that with the last two pages. The square law missed the saturation knee by 34 %, and the
$\sqrt{I_D}$ extraction missed the threshold by 12 %. Here a formula from the same era lands within
a fifth of a millivolt. Simple models aren't uniformly wrong. They are wrong about the things
short channels broke and right about the things short channels didn't touch. The depletion charge
under the channel doesn't depend on how long the channel is, so the square-root law survived where
the square law didn't.

> **When a hand formula disagrees with a simulator,** ask which assumption of the formula the
> device violates. If you can't name one, suspect your arithmetic.

## Threshold and drawn length

Shortening a device raises its current. It also moves its threshold, in a direction few people
predict. The Lab 03 deck `spice/vth_vs_l.spice` has nine copies of the same W = 5 µm transistor at
nine lengths, all at $V_{DS}$ = 50 mV so that the drain doesn't influence the answer:

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

Most textbooks introduce **threshold roll-off**: as a channel gets shorter, the source and drain
depletion regions take over some of the charge the gate would otherwise have to support, the
gate's job gets easier, and $V_{TH}$ **falls**. These nine go the other way. The threshold rises
monotonically, from **0.5364102 V** at L = 4 µm to **0.7078517 V** at L = 0.15 µm, a span of
**171.44 mV**, and the shortest device has the *highest* threshold.

This is the **reverse short-channel effect**, and it comes from a manufacturing decision rather
than from unavoidable physics. Processes at this node implant extra p-type dopant in pockets right
beside the source and drain, called **halo** or **pocket** implants, specifically to fight
roll-off, because a short device whose threshold collapses is a short device that leaks. In SKY130
the halo over-corrects: the average doping under a short channel ends up *higher* than under a long
one, so the gate has more charge to support, not less.

Two practical consequences. First, you can't shorten a transistor and keep its bias point: 171 mV
of threshold is most of an overdrive voltage. Second, analog designers who need two transistors to
behave identically give them **the same length**, always, even when the equations say only $W/L$
matters. In Lab 04 you'll see five devices with identical $W/L$ carry five different currents, and
this is one of the reasons.

## Threshold and temperature

The same `vth_body.spice` run ends with the device at $V_{SB} = 0$ at three temperatures, the
automotive range that real parts are specified over:

| $T$ | $V_{TH}$ | $I_D$ |
|---:|---:|---:|
| −40 °C | 0.6499250 V | 93.8168 µA |
| 27 °C | 0.5894596 V | 66.3374 µA |
| 125 °C | 0.5010177 V | 45.0650 µA |

$V_{TH}$ falls by **148.9 mV** across the range, a slope of **−0.9025 mV/°C**. That is close enough
to the −1 mV/°C rule of thumb that you can just remember the rule of thumb.

Before you read the current column, predict its direction. A lower threshold means more overdrive
at the same gate voltage, so the hot device ought to carry *more* current.

It carries **32.1 % less**. Cold, it carries **41.4 % more**.

Temperature moves more than the threshold. Carrier **mobility** falls as the lattice heats up and
scatters carriers more, roughly as $T^{-1.5}$, and at this overdrive the mobility effect wins
comfortably. The two effects have opposite signs, and which one dominates depends on the bias. At
very low overdrive, near threshold, the threshold term wins and the current goes *up* with
temperature. The gate voltage at which the two cancel is called the **zero-temperature-coefficient
point**, and circuits that must not drift are sometimes deliberately biased there.

> **"Does this get better or worse when it's hot?"** has no general answer for a MOSFET. Simulate
> both ends. This is the corner discipline [AD102](https://uoftasic.com/ad102/) drilled into you
> with resistors, and it matters more here, because a resistor's temperature coefficient doesn't
> change sign on you.

You'll run `vth_body.spice` and `vth_vs_l.spice` yourself in Lab 04, Part 2.

## Check yourself

1. In a stack of two NMOS transistors, which one sees $V_{SB} > 0$, and does that make it stronger
   or weaker?
2. Using $\gamma$ = 0.4108 √V and $2\phi_F$ = 0.600 V, estimate the threshold shift at
   $V_{SB}$ = 0.6 V and compare it with the table.
3. Why does the halo implant raise the threshold of a short device more than a long one?
4. At this overdrive, the drain current falls when the device heats up even though $V_{TH}$ falls.
   Which effect wins, and would the answer be the same just above threshold?

Next: [Transconductance and output resistance](guide/gm-and-ro.md).
