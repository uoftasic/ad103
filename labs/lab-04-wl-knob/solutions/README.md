# Lab 04 — reference answers

**Do not read this first.** Every number below is one you can measure in under
a minute, and measuring it yourself is worth more than reading it. This file is
a list of things to argue about, not a diff.

---

## 1. `W=100`, and then `W=200`

Add two more devices to `spice/w_ladder.spice`, each with its own drain source
and its own line in the final `print`.

`W=100` works, and continues the trend:

```
i100 = 1.346120e-02          13461.200 uA      134.6120 uA/um
```

For comparison the rest of the ladder, in µA per micron of width:

| $W$ (µm) | 1 | 2 | 5 | 10 | 20 | 50 | 100 |
|---|---|---|---|---|---|---|---|
| $I_D/W$ (µA/µm) | 127.147 | 134.702 | 139.255 | 139.532 | 137.008 | 135.243 | 134.612 |

A single broad hump. Widen a narrow device and it gets better per micron;
widen a wide one and it gets slowly worse. Neither end is dramatic — over a
hundredfold range of width the per-micron current moves by 9.7 %.

`W=200` does not work:

```
could not find a valid modelname
    Simulation interrupted due to error!
```

**That is the same error message as the `W=1u` trap**, and this time your units
are perfect. The SKY130 models are *binned*: each `.model` card covers a range
of widths and lengths, and no bin in `nfet_01v8` reaches 200 µm. A width outside
every bin matches no model, so ngspice stops — exactly as it does for a width
in metres, because a width in metres is also outside every bin.

Worth sitting with: **the message never mentions `W`, or units, or bins.** It is
the same three words for two completely different mistakes. That is why the
reflex check in [Getting started](https://uoftasic.com/ad103/#/guide/getting-started)
is *"look at `W` and `L` first"* rather than *"read the error"*.

**If you want a device wider than 100 µm, you build it out of several.** That is
not a workaround; it is what a layout of a wide device actually looks like, and
it is the `nf` story from Part 2 arriving with a reason.

---

## 2. The same ladder in PMOS

Swap `sky130_fd_pr__nfet_01v8` for `sky130_fd_pr__pfet_01v8`, put the source at
`vdd` and the gate at 0 so the device is fully on, and sweep the drain from
`vdd` down to 0:

```
XP5 p5 0 vdd vdd sky130_fd_pr__pfet_01v8 L=1 W=5
Vp5 p5 0 0
```

| $W$ (µm) | 1 | 5 | 10 | 50 |
|---|---|---|---|---|
| PMOS $I_D$ (µA) | 23.4954 | 104.1549 | 206.7639 | 1021.990 |
| PMOS $I_D/W$ (µA/µm) | 23.495 | 20.831 | 20.676 | 20.440 |
| NMOS $I_D/W$ (µA/µm) | 127.147 | 139.255 | 139.532 | 135.243 |

Two things to argue about.

**The PMOS per-micron number falls monotonically** where the NMOS one humped.
Same process, same bias, different device — so "current is proportional to $W$"
is not one rule with one set of exceptions. It is an approximation whose error
depends on which device you picked.

**At $L$ = 1 µm the NMOS carries 6.685× the PMOS** at the same width
(696.2755 / 104.1549). Hold on to that number, because
[the capstone](https://uoftasic.com/ad103/#/labs/capstone-inverter-overview)
measures the same ratio at $L$ = 0.15 µm and gets **2.496**. The ratio between
the two device types is not a property of the process. It is a property of the
process *and the length you chose*, and the reason is velocity saturation:
electrons are faster than holes, so shortening the channel costs the electrons
more of their advantage.

An inverter sized from the long-channel ratio would want $W_p = 6.7\,W_n$. At
minimum length that is nearly three times too wide.

---

## 3. The L ladder at low overdrive

Copy `spice/l_ladder.spice`, change the gate source to 0.9 V, leave every drain
at 1.8 V. Overdrive drops from about 1.2 V to about 0.3 V, so the channel is far
from its speed limit.

| $L$ (µm) | 0.15 | 0.5 | 1 | 2 | 4 |
|---|---|---|---|---|---|
| $I_D$ at $V_{GS}$ = 0.9 V (µA) | 328.953 | 106.796 | 63.876 | 38.2696 | 19.8412 |
| $1/L$ rule, from $L$ = 1 (µA) | 425.840 | 127.752 | — | 31.938 | 15.969 |
| rule error | **+29.5 %** | +19.6 % | — | −16.5 % | −19.5 % |
| the same error at $V_{GS}$ = 1.8 V | +75.5 % | +16.4 % | — | −8.6 % | −12.1 % |

**The short-channel over-prediction collapses from +75.5 % to +29.5 %.** That is
the prediction the velocity-saturation story makes, and it holds: take the field
away and most of the short-channel error goes with it.

**The long-channel error gets worse, from −12.1 % to −19.5 %.** That is the
prediction the velocity-saturation story does *not* make, and it is the more
interesting half. At $L$ = 4 µm the threshold is 536.41 mV against the $L$ = 1 µm
device's 589.46 mV — 53 mV of difference, which is a rounding error against 1.2 V
of overdrive and a sixth of a 0.3 V one. Shrink the overdrive and every
threshold shift in the process gets louder.

So the two ends of the ladder fail for two different reasons, and lowering the
gate voltage fixes one and worsens the other. **There is no bias at which $1/L$
is simply correct**, which is the honest form of the lesson and the reason nobody
sizes a real circuit from the square law alone.

---

## A question with no answer here

The W ladder humps: per-micron current rises to $W$ = 10 µm and then falls. The
model's `vth` falls monotonically the whole way (615.2253 mV → 556.5815 mV), so
the threshold cannot be what turns the curve around — a monotonic cause does not
produce a non-monotonic effect on its own.

Something else is moving in the opposite direction and overtaking it past
$W$ = 10 µm. This course does not tell you what, because we have not measured it,
and a mechanism you cannot point at in a run is a story rather than a result.
If you find it — `mobmod`, the binning boundaries in the model file, a `print`
of some other `@m...[...]` parameter across the ladder — bring it to
[Discord](https://discord.gg/hrJnP5UsGz). That is a genuinely open question in
this lab, not a rhetorical one.
