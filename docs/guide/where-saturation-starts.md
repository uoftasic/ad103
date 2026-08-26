# Where saturation starts

**Question this page answers:** *I have the boundary condition $V_{DS} = V_{GS} - V_{TH}$.
Why does my own measured knee land somewhere else?*

Because the textbook boundary is the answer to a slightly different question, and the
difference has a name, a cause, and a number you can read off your own sweep.

This is also the page where you meet the two most useful habits in device work: **extract a
parameter from a curve rather than looking it up**, and **compare your extraction against the
model's own opinion** to find out how much your definition mattered.

## First: you need $V_{TH}$, and nobody will give it to you

$V_{TH}$ is not printed on the device. It is not a single number in the model card either —
BSIM computes it from the geometry and the bias, freshly, every operating point. So an
engineer *measures* it, and the measurement is a construction on a curve.

```bash
cd labs/lab-03-mosfet-regions
make figures
```

![Two threshold extractions side by side: linear extrapolation and sqrt(I_D) extrapolation](../assets/img/ad103-vth-extraction.png)

*Both panels: SKY130 `nfet_01v8`, W = 5 µm, L = 1 µm, from `spice/id_vgs.spice`.*

### Method 1 — linear extrapolation, at small $V_{DS}$

Hold the drain at 0.05 V so the device is unambiguously a resistor, and sweep the gate. In
triode with $V_{DS}$ small, the current is nearly a straight line in $V_{GS}$:

$$I_D \approx \mu_n C_{ox}\frac{W}{L}\left(V_{GS}-V_{TH}-\frac{V_{DS}}{2}\right)V_{DS}$$

So: find the steepest point of the measured curve, draw the tangent there, run it down to
$I_D = 0$, and read the intercept. That intercept is $V_{TH} + V_{DS}/2$, so subtract half the
drain voltage you used. `make extract` does exactly this and shows its working:

```
== V_TH by linear extrapolation   (V_DS = 0.05 V)
   steepest point      V_GS = 0.845 V
   tangent slope       66.716 uA/V
   tangent hits zero   V_GS = 0.6266 V
   minus V_DS/2        V_TH = 0.6016 V
```

**0.6016 V.** Four lines of arithmetic on 361 sampled points, no datasheet involved.

### Method 2 — $\sqrt{I_D}$ extrapolation, in saturation

The saturation law says $I_D \propto (V_{GS}-V_{TH})^2$, so $\sqrt{I_D}$ should be a straight
line whose x-intercept is $V_{TH}$. Sweep the gate with the drain at 1.8 V, take the square
root, fit a line over a sensible window, extrapolate:

```
== V_TH by sqrt(I_D) extrapolation   (V_DS = 1.8 V, fit 1.0-1.4 V)
   sqrt(I_D) slope     21.4889 mA^0.5 / V
                       V_TH = 0.5159 V
```

**0.5159 V.**

### They disagree by 86 mV, and that is the lesson

```
== your number vs the model's own number   (device A)
   quantity                              yours    ngspice   diff
   V_TH  (linear extrapolation)         0.6016     0.5895   V   +2.07 %
   V_TH  (sqrt extrapolation)           0.5159     0.5895   V  -12.49 %
```

The `ngspice` column is `@m.xma.msky130_fd_pr__nfet_01v8[vth]` — what BSIM itself thinks the
threshold is at that operating point, from `spice/op_params.spice`. Two honest methods, one
device, three answers spread over 86 mV.

Nobody is wrong. **$V_{TH}$ is defined by its extraction method**, and the methods disagree
because the square law they both lean on is not exactly true for this device. Method 1 leans
on it only very near threshold, where it is nearly right, and lands within 2 %. Method 2 leans
on it hard, over a whole volt of overdrive, where it is not — and pays 12 % for it.

**The reflex check:** any time someone quotes you a threshold voltage, ask *how it was
extracted*. "0.52 V" and "0.60 V" can be the same transistor. If a number in a datasheet has
no method beside it, it has a tolerance you cannot see.

For the rest of this course, **$V_{TH} = 0.6016$ V** for this device, because that is the
number your own linear extrapolation produced and it is the one every prediction below is
checked against.

## Now the knee — and why it is early

Take the five output curves and find where each one stops rising. `src/mosfit.py` uses one
explicit, arbitrary rule, and says so: **the knee is the first $V_{DS}$ at which the slope has
fallen to 10 % of the slope at the origin.** Ten percent is a choice, not a law; what matters
is that the same rule is applied to every curve.

```
   knee of each curve vs the model's vdsat
     V_GS  V_GS - V_TH  your knee     vdsat
     0.60       -0.002       0.09     0.065
     0.90        0.298       0.29     0.256
     1.20        0.598       0.50     0.442
     1.50        0.898       0.70     0.612
     1.80        1.198       0.89     0.779
```

Read the second and third columns together, top to bottom.

At $V_{GS} = 0.9$ V the textbook boundary predicts a knee at 0.298 V and your curve knees at
**0.29 V**. That is a hit, and it is worth pausing on — the simple theory works, to two
digits, in its own back yard.

At $V_{GS} = 1.8$ V the boundary predicts 1.198 V and your curve knees at **0.89 V**. The
theory is 34 % high. It did not fail gently; it failed progressively, and the further you push
the gate the worse it gets.

## The cause has a name: velocity saturation

The square law contains an assumption nobody states out loud: that electron drift velocity is
proportional to electric field, forever. Double the field, double the speed.

Silicon does not do that. Above roughly $10^4$ V/cm the carriers stop speeding up — they are
scattering off the lattice as fast as the field can accelerate them — and settle at a
saturation velocity of about $10^7$ cm/s. Once the carriers in your channel are moving as fast
as they can move, adding drain voltage adds nothing.

So the channel does not need to wait for $V_{DS}$ to reach $V_{ov}$ before the current stops
responding. It stops responding as soon as the field along the channel is high enough, which
for $L = 1\ \mu\mathrm{m}$ and a volt of overdrive is *earlier*. The model reports the true
value as **`vdsat`**, and `vdsat` is below $V_{ov}$ at every one of the five bias points above.

Two consequences you will use constantly:

- **A short device saturates earlier.** The same overdrive across a shorter channel is a
  higher field. Compare the two extremes at $V_{GS} = 1.8$ V, both from
  `spice/op_params.spice`: L = 2 µm gives `vdsat = 0.912` V; L = 0.15 µm gives **`vdsat =
  0.362` V**. The minimum-length device pinches off at less than a third of the drain voltage
  the long one needs.
- **The square law degrades toward a straight line.** Fully velocity-saturated, $I_D$ becomes
  proportional to $V_{ov}$, not $V_{ov}^2$. That is exactly why Method 2 above under-read the
  threshold by 12 %: it fitted a square root to something that is drifting toward linear.

**The reflex check:** if a hand calculation with the square law is out by tens of percent on a
modern short device, the square law is the suspect, not your arithmetic. Simulate, then use
the hand calculation for *direction* — "wider means more current" — and the simulator for
*magnitude*.

## Saturation is not flat either

One more comfortable lie to retire. Look hard at the right-hand end of the $V_{GS} = 1.8$ V
curve. It is not horizontal. It rises from **682.502 µA** at $V_{DS} = 1.2$ V to **696.275 µA**
at 1.8 V — 2.0 % more current for 0.6 V more drain.

The reason is in panel 4 of the [channel cross-section](guide/a-mosfet-is-a-valve.md): as
$V_{DS}$ grows, the pinch-off point retreats further from the drain, so the *conducting* part
of the channel gets slightly **shorter**. Shorter channel, more current. This is **channel
length modulation**, and it is what the $(1 + \lambda V_{DS})$ factor in your textbook is
patching.

The slope has a name — output conductance $g_{ds}$ — and its reciprocal is the output
resistance $r_o$:

| Device | $g_{ds}$ at $V_{GS}=V_{DS}=1.8$ V | $r_o = 1/g_{ds}$ |
|---|---|---|
| W = 5 µm, **L = 1 µm** | 15.593 µS | **64.13 kΩ** |
| W = 1 µm, **L = 0.15 µm** | 51.415 µS | **19.45 kΩ** |

Both from `spice/op_params.spice`. A transistor in saturation is not a current source; it is a
current source with 64 kΩ across it — and if you use the minimum-length device, 19 kΩ.

That number decides how much voltage gain you can get out of one transistor, and it is the
first thing [$g_m$ and $r_o$](guide/gm-and-ro.md) does with it.

## What to take away

- $V_{TH}$ is an extracted number, not a property. Always ask by which method.
- The boundary $V_{DS} = V_{GS} - V_{TH}$ is a *long-channel, low-field* answer. Real
  saturation starts earlier, and the model will tell you where if you ask it for `vdsat`.
- Saturation slopes upward. The slope is $g_{ds}$, its reciprocal is $r_o$, and $r_o$ is
  smaller on shorter devices.
- Every one of those statements is a number in `results/`, produced by a deck you can read.

Next: [Threshold is not a constant](guide/threshold-is-not-a-constant.md) — you extracted a
$V_{TH}$ and pinned it down. Now watch it move when you touch a terminal you have been
ignoring.
