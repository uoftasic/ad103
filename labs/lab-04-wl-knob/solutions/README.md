# Lab 04: reference answers

**Don't read this first.** Every number below is one you can measure in under a minute, and you'll
learn more from measuring it than from reading it here. Treat what follows as a list of things to
argue about rather than a diff to copy.

---

## 1. `W=100`, and then `W=200`

Add two more devices to `spice/w_ladder.spice`, each with its own drain source and its own entry in
the final `print`.

`W=100` works, and continues the trend:

```
i100 = 1.346120e-02          13461.200 uA      134.6120 uA/um
```

For comparison, the rest of the ladder in µA per micron of width:

| $W$ (µm) | 1 | 2 | 5 | 10 | 20 | 50 | 100 |
|---|---|---|---|---|---|---|---|
| $I_D/W$ (µA/µm) | 127.147 | 134.702 | 139.255 | 139.532 | 137.008 | 135.243 | 134.612 |

The curve is a single broad hump. If you widen a narrow device it gets better per micron, and if you
widen a wide one it gets slowly worse. Neither change is large: over a hundredfold range of width
the per-micron current moves by 9.7 %.

`W=200` doesn't work:

```
could not find a valid modelname
    Simulation interrupted due to error!
```

That is the same error message as the `W=1u` trap, even though this time your units are correct.
The SKY130 models are *binned*: each `.model` card covers a range of widths and lengths, and no bin
in `nfet_01v8` reaches 200 µm. A width outside every bin matches no model, so ngspice stops, exactly
as it does for a width with a `u` on it, which is also outside every bin.

The message never mentions `W`, units or bins, so two different mistakes produce the same text. That
is why the habit from [Getting started](https://uoftasic.com/ad103/guide/getting-started.html) is
"look at `W` and `L` first" rather than "read the error".

**If you want a device wider than 100 µm, build it out of several.** You aren't working around the
model by doing that, because it's what the layout of a wide device looks like anyway, so this is
the `nf` story from Part 5 of the lab, now with a reason behind it.

---

## 2. The same ladder in PMOS

Swap `sky130_fd_pr__nfet_01v8` for `sky130_fd_pr__pfet_01v8`, put the source at `vdd` and the gate
at 0 so the device is fully on, and sweep the drain from `vdd` down to 0:

```
XP5 p5 0 vdd vdd sky130_fd_pr__pfet_01v8 L=1 W=5
Vp5 p5 0 0
```

| $W$ (µm) | 1 | 5 | 10 | 50 |
|---|---|---|---|---|
| PMOS $I_D$ (µA) | 23.4954 | 104.1549 | 206.7639 | 1021.990 |
| PMOS $I_D/W$ (µA/µm) | 23.495 | 20.831 | 20.676 | 20.440 |
| NMOS $I_D/W$ (µA/µm) | 127.147 | 139.255 | 139.532 | 135.243 |

There are two things here to argue about.

**The PMOS per-micron number falls at every step**, where the NMOS one rose and then fell. The
process and the bias are the same, and only the device type has changed. So
"current is proportional to $W$" is an approximation whose error depends on which device you picked, rather
than one rule with one set of exceptions.

**At $L$ = 1 µm the NMOS carries 6.685× the PMOS** at the same width (696.2755 / 104.1549). Keep
that number in mind, because [the capstone](https://uoftasic.com/ad103/labs/capstone-inverter-overview.html)
measures the same ratio at $L$ = 0.15 µm and gets 2.496. The ratio between the two device types
isn't set by the process alone, because it also depends on the length you chose. That is because of velocity saturation:
electrons are faster than holes, so shortening the channel costs the electrons more of their
advantage.

An inverter sized from the long-channel ratio would have $W_p = 6.7\,W_n$. At minimum length that is
nearly three times too wide.

---

## 3. The L ladder at low overdrive

Copy `spice/l_ladder.spice`, change the gate source to 0.9 V, and leave every drain at 1.8 V. The
overdrive drops from about 1.2 V to about 0.3 V, so the channel is far from its speed limit.

| $L$ (µm) | 0.15 | 0.5 | 1 | 2 | 4 |
|---|---|---|---|---|---|
| $I_D$ at $V_{GS}$ = 0.9 V (µA) | 328.953 | 106.796 | 63.876 | 38.2696 | 19.8412 |
| $1/L$ rule, from $L$ = 1 (µA) | 425.840 | 127.752 | — | 31.938 | 15.969 |
| rule error | **+29.5 %** | +19.6 % | — | −16.5 % | −19.5 % |
| the same error at $V_{GS}$ = 1.8 V | +75.5 % | +16.4 % | — | −8.6 % | −12.1 % |

**The short-channel over-prediction falls from +75.5 % to +29.5 %.** The velocity-saturation
explanation predicts this, and the run bears it out: take the field away and most of the
short-channel error goes with it.

**The long-channel error gets worse, from −12.1 % to −19.5 %.** The velocity-saturation explanation
does *not* predict that, so this is the more interesting half. At $L$ = 4 µm the threshold is
536.41 mV against the $L$ = 1 µm device's 589.46 mV. That 53 mV difference is small against 1.2 V
of overdrive, but it's a sixth of a 0.3 V one, so as you shrink the overdrive every threshold shift
in the process matters more.

The two ends of the ladder therefore fail for two different reasons, and lowering the gate voltage
fixes one and worsens the other. There is no bias at which $1/L$ is simply correct. That is the honest
form of the lesson, and it's why nobody sizes a real circuit from the square law alone.

---

## An open question

The W ladder humps: per-micron current rises to $W$ = 10 µm and then falls. The model's `vth` falls
at every step (615.2253 mV → 556.5815 mV), so the threshold can't be what turns the curve around: a
cause that only moves one way can't on its own produce an effect that rises and then falls.

Something else must move in the opposite direction and overtake it past $W$ = 10 µm. We don't tell
you what, because we haven't measured it, and a mechanism you can't point to in a run is a story
rather than a result, so in this lab it's a genuinely open question. If you find it (`mobmod`, the binning
boundaries in the model file, or a `print` of some other `@m...[...]` parameter across the ladder
are places to start), bring it to [Discord](https://discord.gg/hrJnP5UsGz).
