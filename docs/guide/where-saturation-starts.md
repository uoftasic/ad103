# Where saturation starts

The textbook boundary between triode and saturation is $V_{DS} = V_{GS} - V_{TH}$. This page
shows why the knee in a measured curve lands somewhere else, and gives the cause a name and a
number.

Along the way you'll meet the two most useful habits in device work: **extract a parameter from a
curve instead of looking it up**, and **compare your extraction with the model's own value** to see
how much your definition mattered.

## Measuring $V_{TH}$

$V_{TH}$ isn't printed on the device. It isn't a single number in the model card either: the BSIM
model computes it from the geometry and the bias, afresh at every operating point. So engineers
*measure* it, and the measurement is a construction on a curve. Here are two common ones.

![Two threshold extractions side by side: linear extrapolation and sqrt(I_D) extrapolation](../assets/img/ad103-vth-extraction.png)

*Both panels: SKY130 `nfet_01v8`, W = 5 µm, L = 1 µm, from `spice/id_vgs.spice` in the Lab 03
package.*

### Method 1: linear extrapolation at small $V_{DS}$

Hold the drain at 0.05 V so the device is clearly a resistor, and sweep the gate. In triode with
small $V_{DS}$, the current is nearly a straight line in $V_{GS}$:

$$I_D \approx \mu_n C_{ox}\frac{W}{L}\left(V_{GS}-V_{TH}-\frac{V_{DS}}{2}\right)V_{DS}$$

Find the steepest point of the measured curve, draw the tangent there, extend it down to
$I_D = 0$, and read the intercept. That intercept is $V_{TH} + V_{DS}/2$, so subtract half the
drain voltage. Lab 03's extraction shows its working:

```
== V_TH by linear extrapolation   (V_DS = 0.05 V)
   steepest point      V_GS = 0.845 V
   tangent slope       66.716 uA/V
   tangent hits zero   V_GS = 0.6266 V
   minus V_DS/2        V_TH = 0.6016 V
```

**0.6016 V**, from four lines of arithmetic on 361 sampled points, with no datasheet involved.

### Method 2: $\sqrt{I_D}$ extrapolation in saturation

The saturation law says $I_D \propto (V_{GS}-V_{TH})^2$, so $\sqrt{I_D}$ should be a straight line
whose x-intercept is $V_{TH}$. Sweep the gate with the drain at 1.8 V, take the square root, fit a
line over a sensible window, and extrapolate:

```
== V_TH by sqrt(I_D) extrapolation   (V_DS = 1.8 V, fit 1.0-1.4 V)
   sqrt(I_D) slope     21.4889 mA^0.5 / V
                       V_TH = 0.5159 V
```

**0.5159 V.**

### Two methods, 86 mV apart

```
== your number vs the model's own number   (device A)
   quantity                              yours    ngspice   diff
   V_TH  (linear extrapolation)         0.6016     0.5895   V   +2.07 %
   V_TH  (sqrt extrapolation)           0.5159     0.5895   V  -12.49 %
```

The `ngspice` column is `@m.xma.msky130_fd_pr__nfet_01v8[vth]`, the threshold BSIM itself reports
at that operating point, from `spice/op_params.spice`. Two reasonable methods on one device give
three answers spread over 86 mV.

None of them is wrong. **$V_{TH}$ is defined by its extraction method**, and the methods disagree
because the square law they both rely on isn't exactly true for this device. Method 1 relies on
it only very near threshold, where it is nearly right, and lands within 2 %. Method 2 relies on it
across a whole volt of overdrive, where it isn't, and is 12 % out.

> **Ask how a threshold was extracted.** "0.52 V" and "0.60 V" can be the same transistor. A
> datasheet threshold with no method beside it has a tolerance you can't see.

For the rest of this course, **$V_{TH} = 0.6016$ V** for this device, because that is what the
linear extrapolation gives, and every prediction below is checked against it.

## The knee comes early

Take the five output curves and find where each one stops rising. Lab 03's `src/mosfit.py` uses one
explicit rule and says so: **the knee is the first $V_{DS}$ at which the slope has fallen to 10 % of
the slope at the origin.** Ten percent is a choice, not a law; what matters is that the same rule
is applied to every curve.

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

At $V_{GS} = 0.9$ V the textbook boundary predicts a knee at 0.298 V, and the curve knees at
**0.29 V**. The simple theory works to two digits at low overdrive.

At $V_{GS} = 1.8$ V the boundary predicts 1.198 V and the curve knees at **0.89 V**. The theory is
34 % high. The error grows steadily the harder you drive the gate.

## Velocity saturation

The square law contains an assumption that is rarely stated: that electron drift velocity is
proportional to electric field, without limit. Double the field, double the speed.

Silicon doesn't do that. Above roughly $10^4$ V/cm the carriers stop speeding up, because they
scatter off the crystal lattice as fast as the field can accelerate them, and they settle at a
**saturation velocity** of about $10^7$ cm/s. Once the carriers in the channel are moving as fast as
they can, more drain voltage adds nothing. This is **velocity saturation**.

So the current doesn't wait for $V_{DS}$ to reach $V_{ov}$ before it stops responding. It stops as
soon as the field along the channel is high enough, and for $L = 1\ \mu\mathrm{m}$ and a volt of
overdrive, that happens *earlier*. The model reports the actual value as **`vdsat`**, and `vdsat`
is below $V_{ov}$ at every one of the five bias points above.

Two consequences you'll use constantly:

- **A short device saturates earlier.** The same overdrive across a shorter channel is a higher
  field. At $V_{GS} = 1.8$ V, both from `spice/op_params.spice`: L = 2 µm gives `vdsat = 0.912` V,
  and L = 0.15 µm gives **`vdsat = 0.362` V**. The minimum-length device pinches off at less than a
  third of the drain voltage the long one needs.
- **The square law drifts toward a straight line.** When fully velocity-saturated, $I_D$ becomes
  proportional to $V_{ov}$, not $V_{ov}^2$. That is why Method 2 under-read the threshold by 12 %:
  it fitted a square root to something drifting toward linear.

> **When a square-law calculation is tens of percent out** on a short modern device, suspect the
> square law before your arithmetic. Simulate, and use the hand calculation for *direction*
> ("wider means more current") and the simulator for *magnitude*.

## The saturation region slopes upward

The right-hand end of the $V_{GS} = 1.8$ V curve isn't horizontal. It rises from **682.502 µA** at
$V_{DS} = 1.2$ V to **696.275 µA** at 1.8 V: 2.0 % more current for 0.6 V more drain.

The reason is in panel 4 of the [channel cross-section](guide/a-mosfet-is-a-valve.md#the-channel-at-four-bias-points).
As $V_{DS}$ grows, the pinch-off point moves further from the drain, so the conducting part of the
channel gets slightly **shorter**, and a shorter channel carries more current. This is
**channel-length modulation**, and it is what the $(1 + \lambda V_{DS})$ factor in your textbook
approximates.

The slope is called the **output conductance** $g_{ds}$, and its reciprocal is the **output
resistance** $r_o$:

| Device | $g_{ds}$ at $V_{GS}=V_{DS}=1.8$ V | $r_o = 1/g_{ds}$ |
|---|---|---|
| W = 5 µm, **L = 1 µm** | 15.593 µS | **64.13 kΩ** |
| W = 1 µm, **L = 0.15 µm** | 51.415 µS | **19.45 kΩ** |

Both are from `spice/op_params.spice`. A saturated transistor is not an ideal current source; it is
a current source with 64 kΩ in parallel, or 19 kΩ if you use the minimum-length device.

That number sets how much voltage gain one transistor can give, and it is the first thing
[Transconductance and output resistance](guide/gm-and-ro.md) uses.

You'll reproduce every number on this page in Lab 03, Parts 2 and 3.

## Check yourself

1. Method 1 subtracts $V_{DS}/2$ from the tangent's intercept. Where does that term come from?
2. Why does Method 2 give a lower $V_{TH}$ than Method 1 on this device?
3. At $V_{GS}$ = 1.5 V, how far is the measured knee below $V_{GS} - V_{TH}$, in percent?
4. You shorten a device from L = 1 µm to L = 0.15 µm at the same bias. Does `vdsat` go up or down,
   and does $r_o$ go up or down?

Next: [Lab 03 — MOSFET regions](labs/lab-03-mosfet-regions-overview.md).
