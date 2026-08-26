# Four regions, not three

**Question this page answers:** *My textbook gives me cutoff, triode and saturation. What are
the boundaries actually made of, and how do I tell which one I am in?*

You already have the answer from [A MOSFET is a valve](guide/a-mosfet-is-a-valve.md): the
regions are pictures of the channel. This page draws the boundaries on curves you measured
yourself, and then introduces the region your textbook quietly deleted.

## The curves, measured

```bash
cd labs/lab-03-mosfet-regions
make figures
```

![I_D vs V_DS for five gate voltages, with the triode and saturation regions shaded](../assets/img/ad103-id-vds-family.png)

*SKY130 `nfet_01v8`, W = 5 µm, L = 1 µm. Five sweeps of $V_{DS}$, one per gate voltage, from
`spice/id_vds.spice`; drawn by `src/plot_curves.py`. The dashed locus and its dots are
`vdsat` reported by the model itself at each bias, from `spice/op_params.spice` — not a fit,
not a guess, the simulator's own opinion about where the channel pinched off.*

Everything worth knowing about a MOSFET is somewhere in that picture. Take it region by
region, and match each one to a panel of the cross-section figure.

## 1. Cutoff — the gate is not squeezing

**Condition:** $V_{GS} < V_{TH}$.

**What the channel is doing:** nothing. The gate has not pulled enough electrons to the
surface to form a conducting layer, so there is no path between source and drain except two
back-to-back diodes, and one of them is reverse-biased.

**On the plot:** the flat line along the bottom. At $V_{GS} = 0.6$ V the whole sweep from 0 to
1.8 V never gets above **2.005 µA** — on a plot scaled for 700 µA it is indistinguishable
from the axis.

$$I_D \approx 0$$

Keep the "$\approx$". We come back to it.

## 2. Triode — a resistor the gate sets

**Condition:** $V_{GS} > V_{TH}$ **and** $V_{DS} < V_{GS} - V_{TH}$.

**What the channel is doing:** it runs end to end (panel 2 of the cross-section). It is
thinner at the drain, because the drain's own voltage partly cancels the gate's pull there,
but it is continuous. Push harder on the drain and more current flows, in almost the same way
it would through a piece of wire.

**On the plot:** the rising left-hand part of every curve, shaded blue. Near the origin the
curves are nearly straight lines through zero — the signature of a resistor.

$$I_D = \mu_n C_{ox}\frac{W}{L}\left[(V_{GS}-V_{TH})V_{DS} - \frac{V_{DS}^2}{2}\right]$$

Do not memorise that. Read it: a term proportional to $V_{DS}$ (the resistor), minus a term
that grows as $V_{DS}^2$ (the channel thinning out at the drain end and fighting back). At
small $V_{DS}$ the second term vanishes and you are left with Ohm's law, with a conductance
the gate controls:

$$R_{ch} \approx \frac{1}{\mu_n C_{ox}\frac{W}{L}(V_{GS}-V_{TH})}$$

`make extract` measures exactly that, by putting 10 mV across the device and dividing:

| $V_{GS}$ | channel resistance |
|---|---|
| 0.60 V | 26 648.3 Ω |
| 0.90 V | 2 529.2 Ω |
| 1.20 V | 1 288.0 Ω |
| 1.50 V | 907.7 Ω |
| 1.80 V | 736.9 Ω |

**The reflex check for triode:** near the origin, is the curve a straight line through zero?
If yes, you are in triode and you may treat the transistor as a resistor. That check costs one
glance and is right far more often than plugging numbers into the quadratic.

## 3. Saturation — a current source the gate sets

**Condition:** $V_{GS} > V_{TH}$ **and** $V_{DS} > V_{GS} - V_{TH}$.

**What the channel is doing:** the drain end has run out of charge (panel 3) and the
pinch-off point has retreated up the channel (panel 4). The extra drain volts fall across the
pinched-off stretch, not across the channel, so the channel keeps carrying what it was already
carrying.

**On the plot:** the flat right-hand part of every curve, shaded amber. The spacing between
the flat parts is set entirely by $V_{GS}$: 2.005, 63.876, 217.505, 436.080, 696.275 µA. The
drain has stopped mattering; the gate has not.

$$I_D = \frac{1}{2}\mu_n C_{ox}\frac{W}{L}(V_{GS}-V_{TH})^2$$

**The reflex check for saturation:** if you nudge $V_{DS}$ and $I_D$ barely moves, you are in
saturation. That is the definition, and it is also how every bias check in a real design is
done — perturb the drain and see whether the current cares.

## The boundary between them has a name

The two conditions above meet where $V_{DS} = V_{GS} - V_{TH}$. That quantity, $V_{GS} -
V_{TH}$, is called the **overdrive voltage** $V_{ov}$, and it is the number an analog designer
actually thinks in. It is not "how far above threshold you are" as a piece of trivia — it *is*
the drain voltage at which the device changes character, and it is the headroom the device
demands before it will behave as a current source.

Where that boundary really sits, and why the answer your curve gives is 26 % lower than
$V_{ov}$ at high gate voltage, is the whole of [Where saturation
starts](guide/where-saturation-starts.md).

## 4. The fourth region — the one that is not in your textbook

Go back to §1 and look at the "$\approx$" again.

**Predict before you scroll.** The threshold of this device is about 0.59 V. At $V_{GS} =
0.30$ V — half the threshold, comfortably "off" — how much current flows through a 1.8 V
drain? Write down an order of magnitude. Zero is an acceptable answer; commit to it.

Now put the same sweep on a log axis:

![I_D vs V_GS on a log axis, showing six decades of current below threshold](../assets/img/ad103-subthreshold.png)

*From `spice/id_vgs_log.spice`. Same device, same $V_{DS} = 1.8$ V, the only change is the
y-axis.*

```
== below threshold   (V_DS = 1.8 V)
   V_GS = 0.00 V   I_D = 2.1853e-12 A
   V_GS = 0.30 V   I_D = 1.3645e-09 A
   V_GS = 0.60 V   I_D = 2.0054e-06 A
   decades from 0.0 V to 0.6 V : 5.96
   subthreshold slope          : 85.6 mV/decade
```

**1.36 nanoamps.** Not zero, and not noise — a smooth, repeatable, exponential function of
gate voltage. On the linear plot this entire region is a flat line sitting on the axis. On the
log plot it is a **straight line six decades tall**, which is what an exponential looks like.

This is **subthreshold conduction**, or weak inversion. The gate has not made a proper
channel, but it has bent the energy bands enough that some electrons make it across by thermal
agitation — and the number that do is exponential in the barrier height, exactly like the
diode you swept in [Lab 02](labs/lab-02-diode-iv-overview.md). It is the same physics. A
MOSFET below threshold *is* a diode.

The slope of that line is the parameter everyone quotes: **85.6 mV per decade** on this
device. It takes 85.6 mV of gate to change the drain current by a factor of ten. There is a
hard floor of about 60 mV/decade at room temperature that no conventional MOSFET can beat —
the same $kT/q \ln 10 = 59.6$ mV you met on the diode page — and real devices land above it.

**Why an engineer cares, in one arithmetic step.** Suppose you build a chip with ten million
of these transistors and switch it off — every gate at ground:

$$10^7 \times 2.1853\ \mathrm{pA} = 21.9\ \mu\mathrm{A}$$

Tolerable. Now suppose your threshold came out 0.3 V lower than you designed for, which is
well within the spread of a real process. In subthreshold the current depends on $V_{GS} -
V_{TH}$ and not on either one alone, so a device with $V_{TH}$ lowered by 0.3 V and its gate
at ground carries exactly what this device carries with its gate at 0.3 V — the number two
rows up:

$$10^7 \times 1.3645\ \mathrm{nA} = 13.6\ \mathrm{mA}$$

**Six hundred times more, from a shift of 0.3 V in one parameter,** on a chip that is doing
nothing. This is why threshold voltage is guarded so jealously, why "low power" and "high
speed" pull in opposite directions — a low $V_{TH}$ gives you speed and leakage together — and
why subthreshold slope has its own line in every process datasheet.

**The reflex check:** a MOSFET is never off. Any time you hear "the transistor is off",
translate it to "the transistor is passing a current I have decided to ignore", and then ask
how many of them there are.

## The four regions, on one card

| Region | Condition | Channel | $I_D$ behaves like |
|---|---|---|---|
| **Subthreshold** | $V_{GS} < V_{TH}$ | none, but carriers get over the barrier | an exponential in $V_{GS}$ |
| **Cutoff** | $V_{GS} \ll V_{TH}$ | none | zero, for accounting purposes |
| **Triode** | $V_{GS} > V_{TH}$, $V_{DS} < V_{ov}$ | continuous, thinner at the drain | a resistor $R(V_{GS})$ |
| **Saturation** | $V_{GS} > V_{TH}$, $V_{DS} > V_{ov}$ | pinched off at the drain end | a current source $I(V_{GS})$ |

Cutoff and subthreshold are the same region seen on two different axes, which is precisely why
textbooks collapse them. Keep them apart: one is where you do digital arithmetic, the other is
where you do power budgets.

Next: [Where saturation starts](guide/where-saturation-starts.md) — you now have a boundary
condition, $V_{DS} = V_{GS} - V_{TH}$. Your own measured curves disagree with it, by a
predictable amount, for a reason with a name.
