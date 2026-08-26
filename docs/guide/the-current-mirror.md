# The current mirror

**Question this page answers:** *[The inverter](guide/the-inverter-is-an-amplifier.md) needs its
input held at 0.712 V, on a cliff with a gain of 116. What holds it there?*

Not a voltage. A **current**.

This is the last idea AD103 owes you, and it is the one that turns everything on the previous
nine pages into a circuit you could actually build. It is also, satisfyingly, an idea you
already met in [AD102](https://uoftasic.com/ad102/) wearing different clothes.

## Why voltages are the wrong thing to distribute

You need every amplifier on a chip biased at the right point. The obvious plan is to generate
one good voltage and wire it everywhere.

Count what that voltage has to survive, using numbers you measured yourself:

| It has to survive | and you measured |
|---|---|
| threshold moving with temperature | **−0.9025 mV/°C**, 148.9 mV across the automotive range |
| threshold moving with channel length | **171.44 mV** from L = 4 µm to L = 0.15 µm |
| threshold moving with source-to-bulk | **232.791 mV** at $V_{SB}$ = 1.2 V |
| process corners | AD102 Lab 04's whole subject |

A gate voltage that is 100 mV wrong on a device with $g_m$ = 334 µS is **33 µA** wrong. The
plan does not survive contact with a real die.

But look at what AD102's Lab 04 concluded, and what
[W and L are a choice](guide/w-and-l-are-a-choice.md) concluded: **absolute values wander;
ratios hold.** Two devices side by side on the same die are at the same temperature, in the
same corner, with the same threshold. Whatever moved one moved the other.

So do not distribute a voltage. Distribute a *current*, by building a circuit whose output is a
**ratio** of its input.

## The circuit is two transistors and a shorted terminal

Take a transistor and tie its gate to its drain. It is now a two-terminal device, and it is
forced into saturation for free: $V_{DS} = V_{GS}$, so $V_{DS}$ always exceeds
$V_{GS} - V_{TH}$. This is a **diode-connected** transistor.

Push a known current into it. It settles at whatever gate voltage carries that current — the
device solves the equation for you, because you do not know $\mu_n C_{ox}$ and it does.

Now wire a second transistor's gate to the same node. Same $V_{GS}$, same silicon, same
temperature. Same current.

```bash
cd labs/capstone-inverter
make mirror
```

**What you should see, first block:**

```
--- part 1: the reference branch sets a gate voltage ---
v(ng) = 8.672678e-01
@m.xmref.msky130_fd_pr__nfet_01v8[vdsat] = 2.336319e-01
```

50 µA was forced into the reference branch, and the diode-connected device chose
**0.8672678 V** to carry it. Nobody computed that. It is the transistor's own answer, and if
the die is hot, or slow, or the threshold moved, the number moves with it — which is exactly
the point.

And the copy, at $V_{out} = 0.9$ V:

```
i(vo2) = -5.00878e-05
```

**50.0878 µA against a 50 µA reference — 0.176 % error**, from a circuit with no resistors, no
feedback, and no trimming. That is what "ratios hold" buys you.

## First honest limit: the copy needs headroom

A saturated transistor is very nearly a current source. Drop it out of saturation and it is a
resistor. Part 3 sweeps the output node to find out where that happens:

```
--- part 3: the same 1:1 copy at several output voltages ---
V_out = 0.1 V
i(vo1) = -2.84076e-05
V_out = 0.2 V
i(vo1) = -4.27022e-05
V_out = 0.4 V
i(vo1) = -4.81163e-05
V_out = 0.6 V
i(vo1) = -4.91572e-05
V_out = 0.9 V
i(vo1) = -5.00878e-05
V_out = 1.2 V
i(vo1) = -5.08174e-05
V_out = 1.8 V
i(vo1) = -5.20797e-05
```

| $V_{out}$ | $I_{out}$ | error vs 50 µA |
|---:|---:|---:|
| 0.1 V | 28.4076 µA | **−43.18 %** |
| 0.2 V | 42.7022 µA | −14.60 % |
| 0.4 V | 48.1163 µA | −3.77 % |
| 0.6 V | 49.1572 µA | −1.69 % |
| 0.9 V | 50.0878 µA | +0.18 % |
| 1.2 V | 50.8174 µA | +1.63 % |
| 1.8 V | 52.0797 µA | +4.16 % |

Two separate things are visible in that column, and telling them apart is the skill.

**Below about 0.25 V the copy collapses.** Part 1 printed the reason:
`vdsat = 2.336319e-01`. Below **0.2336 V** of drain voltage the output device is in triode, not
saturation, and a triode device's current depends on its drain. Every current mirror has a
minimum output voltage, called its **compliance**, and it is $V_{DSAT}$ — about 234 mV here.
This is why a 1.8 V supply feels tight: every stacked current source spends a quarter of a volt
just existing.

**Above it, the copy drifts upward by about 1.6 % per 0.3 V.** That is not a failure, that is
$r_o$ — [the finite slope of saturation](guide/gm-and-ro.md). Take the two clean rows:

$$r_o \approx \frac{1.8 - 0.6}{(52.0797 - 49.1572)\ \mu\text{A}} = 410.6\ \text{k}\Omega$$

A "current source" with 410 kΩ across it. Real, finite, and the reason the next circuit in
every analog textbook is the **cascode** — a second transistor stacked on top to shield the
first one from the output swing, which buys back a factor of $g_m r_o$ of output resistance and
costs you another $V_{DSAT}$ of compliance.

**The reflex check:** before you call a mirror broken, ask what $V_{out}$ was. Half the current
missing is almost always a device in triode, not a wiring error.

## Second honest limit: the ratio you drew is not the ratio you get

Now the useful part. Widen the output device and the copy scales — a mirror is a *multiplier*.
Part 2 draws 1:1, 1:2 and 1:4 by width:

```
--- part 2: one gate voltage, three widths, V_out = 0.9 V ---
i(vo2) = -5.00878e-05
i(vo3) = -1.12313e-04
i(vo4) = -2.39347e-04
```

**Predict before you read the table.** $W = 5$, 10 and 20 µm on one gate voltage should give
1×, 2× and 4×.

| drawn | $W$ | $I_{out}$ | actual ratio | error |
|---|---:|---:|---:|---:|
| 1× | 5 µm | 50.0878 µA | 1.0000 | — |
| 2× | 10 µm | 112.313 µA | **2.2423** | **+12.12 %** |
| 4× | 20 µm | 239.347 µA | **4.7785** | **+19.46 %** |

Twelve percent, from a circuit whose entire selling point is that ratios are exact. The deck
prints the cause on the next two lines:

```
  and why the ratio is not what you drew:
@m.xmw1.msky130_fd_pr__nfet_01v8[vth] = 5.894596e-01
@m.xmw2.msky130_fd_pr__nfet_01v8[vth] = 5.766246e-01
@m.xmw1.msky130_fd_pr__nfet_01v8[gm]  = 3.340839e-04
@m.xmw2.msky130_fd_pr__nfet_01v8[gm]  = 7.187672e-04
```

The W = 10 µm device has a threshold **12.835 mV lower** than the W = 5 µm one. (Lab 04
measured the same shift independently: `vth(W=10) - vth(W=5) = -12.8354 mV`. Two decks, five
figures.) It is the **narrow-width effect** — the edges of a channel behave differently from
its middle, and a wider device is proportionally less edge.

Does 12.8 mV explain 12 %? Close the arithmetic. The wide device's $g_m$ is 718.7672 µS, so a
threshold 12.835 mV lower is worth about

$$\Delta I \approx g_m \Delta V_{TH} = 718.7672\ \mu\text{S} \times 12.835\ \text{mV}
= 9.23\ \mu\text{A}$$

on a branch that should have carried $2 \times 50.0878 = 100.1756$ µA. Measured excess:
**12.14 µA**. Same size, same sign; the straight-line estimate under-reads because at
$g_m/I_D$ = 6.40 /V (718.7672 µS on 112.313 µA) this device is in moderate inversion, where
current rises faster than linearly with gate voltage. **The mechanism is confirmed even
though the linearisation is loose** — and knowing which of those two statements you have
proved is the whole skill.

## The fix is the habit AD102 already gave you

[Matching beats accuracy](https://uoftasic.com/ad102/#/guide/matching-beats-accuracy) stated a
reflex, about resistors:

> *if you need a ratio, build both sides out of the same unit device*

A 4:1 resistor ratio is four identical units and one unit, never a long strip beside a short
one, because the ends do not scale. The identical claim is true of transistors, for the
identical reason: **the edges do not scale.**

So do not draw one W = 10 µm device. Draw **two W = 5 µm devices in parallel** — same total
width, same total area, same current in theory.

```
--- part 4: one W=10 device vs two W=5 devices in parallel ---
i(vo3) = -1.12313e-04
i(vo5) = -1.00176e-04
```

| output branch | $I_{out}$ | ideal $2\times$ | error |
|---|---:|---:|---:|
| one W = 10 µm device | 112.313 µA | 100.1756 µA | **+12.12 %** |
| two W = 5 µm devices in parallel | **100.176 µA** | 100.1756 µA | **+0.0004 %** |

**Six figures.** Two copies of the unit device carry exactly twice the unit device's current,
because they *are* two copies of the unit device — same width, same edges, same threshold,
nothing left to differ.

This is why real analog layout is full of arrays of identical transistors with their sources
and drains strapped together, and why a schematic that says `m=4` means "four of these", not
"one four times as wide". It is the same rule AD102 proved on resistors, the same rule that
made a 3:1 divider land at 1.350000 V instead of 1.309327 V, arrived at from a completely
different direction.

**The reflex check:** any time a schematic asks for a ratio of two devices, ask whether both
sides are built from the same unit. If they are not, the ratio has a systematic error in it
that no amount of care will remove.

## What to take away

- Distribute currents, not voltages. A diode-connected transistor turns a current into whatever
  gate voltage carries it — **0.8672678 V** for 50 µA here — and that voltage tracks temperature
  and corner for free.
- A 1:1 copy is good to **0.176 %**. That is what matching buys.
- The copy needs **$V_{DSAT}$ = 234 mV** of output headroom, and above it drifts at the rate
  $r_o$ = 410.6 kΩ allows. Both are honest limits with names, and the cascode is the answer to
  the second one.
- A ratio drawn as one wide device is **12 %** wrong. The same ratio drawn as parallel unit
  devices is **0.0004 %** wrong. AD102 told you this about resistors; it was never about
  resistors.

## Where AD103 ends, and what AD104 does with it

You arrived able to read a signal and size a resistor. You leave able to look at a
three-terminal device, name the region it is in, predict which way a number will move, and find
out by asking a simulator a question you designed.

The [capstone](labs/capstone-inverter-overview.md) is the CMOS inverter, and it is the bridge —
deliberately. It is the smallest circuit that is simultaneously a logic gate the digital track
would recognise and an amplifier this course would. When you finish it you will have
`xschem/my_inverter.sch`: a schematic you drew, sized against a criterion you chose, verified
against a simulation to six digits.

**AD104 — Layout takes that exact file and asks you to build
it.** Every transistor becomes a rectangle of diffusion under a stripe of poly. Every net
becomes metal with a width and a spacing. Then Magic runs **DRC** to check that a fab could
make what you drew, and netgen runs **LVS** to prove that what you drew is the same circuit as
the schematic on this page — not similar, *the same*, node for node and device for device.

Three things from AD103 will be waiting for you there, and now you know why they matter:

- **$W$ and $L$ are geometry**, and in Magic you will be drawing them with a mouse rather than
  typing them. The `W=1` versus `W=1u` trap disappears, because there is no longer a number to
  put a unit on.
- **`nf=2`** — the multi-finger device from
  [Lab 04](labs/lab-04-wl-knob-overview.md) that changed the current by 4.5 % with no change to
  $W$ or $L$ — stops being a mysterious parameter and becomes a picture: two gate stripes
  sharing a drain.
- **Unit devices in an array**, from this page. AD104 is where you find out what a mirror
  actually looks like when it is drawn properly, dummies and all.

And [SiliWiz](https://tinytapeout.com/siliwiz/), which AD102 used to look at a resistor in
cross-section, is worth one more visit before you go: draw an NMOS in it, sweep the gate, and
watch the channel you have been calculating about for five labs appear underneath the oxide.

**Stuck, or want to argue about any of this?** The team Discord is at
<https://discord.gg/hrJnP5UsGz>. Bring the number you got and the number you expected.
