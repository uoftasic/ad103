# Lab 03 — reference answers

**Do not read this first.** Every deck here is four to six lines away from one that
already ships and already works, and the whole value of the exercise is in the
four lines. Try it, run it, be surprised by something, *then* come here.

What follows is not a diff. It is the list of things worth arguing about once
your version runs.

Run any of them with:

```bash
cd labs/lab-03-mosfet-regions
ngspice -b solutions/pfet_op.spice
```

---

## 1. `id_vds_six.spice` — a sixth curve at $V_{GS} = 1.05$ V

**The answer:** $I_D$ = **131.053 µA** at $V_{DS}$ = 1.8 V, which sits between the
63.876 µA of the 0.9 V curve and the 217.505 µA of the 1.2 V curve, roughly where
a squared law puts it.

**The thing to argue about is not the current.** Look at what happened to the
plot names. In the shipped deck, `foreach vg 0.6 0.9 1.2 1.5 1.8` produces plots
`dc1`…`dc5` **in the order the sweeps ran**, and the `let` lines below assume
that order. Insert `1.05` in its natural place — second — and every plot after it
shifts by one:

```
foreach vg 0.6 1.05 0.9 1.2 1.5 1.8
...
let id_vgs105 = -dc2.i(vds)      <- the new one is dc2
let id_vgs09  = -dc3.i(vds)      <- 0.9 V was dc2, now it is dc3
```

If you appended `1.05` to the end of the list instead, nothing shifted and your
deck worked first try — and you also did not find out that `dcN` is a *run
counter*, not a bias label. That distinction will cost somebody an afternoon in
Lab 04; better it costs you four lines here.

**A question worth sitting with:** the `wrdata` line writes the columns in
whatever order you name them, which need not be the order they were simulated.
The shipped solution writes them in ascending gate voltage. What breaks in
`src/plot_curves.py` if you don't?

---

## 2. `pfet_op.spice` — the same measurement on a PMOS

Same W, same L, same 1.8 V of gate drive and 1.8 V of drain-source. Everything
that can be held constant is.

| | `nfet_01v8` | `pfet_01v8` |
|---|---|---|
| $\lvert I_D\rvert$ | 696.275 µA | **104.155 µA** |
| model `vth` | 0.5895 V | **1.0219 V** |
| `vdsat` | 0.7795 V | 0.6691 V |
| `gm` | 915.312 µS | 236.903 µS |
| `gds` | 15.593 µS | **1.568 µS** |
| $r_o = 1/g_{ds}$ | 64.13 kΩ | **637.6 kΩ** |
| $g_m r_o$ | 58.7 | **151.0** |

**Argue about all three of the bold rows.**

*The current is 6.685× lower.* Everyone is taught "a PMOS is two or three times
weaker because holes are slower than electrons," and that is not enough to
explain 6.685. Close the gap the same way [W and L are a
choice](https://uoftasic.com/ad103/#/guide/w-and-l-are-a-choice) closes it: the
PMOS threshold is 432 mV higher, so at the same 1.8 V of gate drive it has far
less overdrive. Square-law that away —

$$\left(\frac{1.8-0.5895}{1.8-1.0219}\right)^2 = 2.421$$

— and $6.685 / 2.421 = \mathbf{2.76}$ is left over. *That* is the mobility ratio,
and it is the two-to-three you were taught. The rest was threshold, hiding.

*The PMOS threshold really is that high.* `pfet_01v8` with 1.8 V on it has 0.78 V
of overdrive against the NMOS's 1.21 V. Any circuit that wants matched pull-up
and pull-down strength has to buy the difference with $W$ — which is why the
PMOS in a standard-cell inverter is drawn wider than the NMOS, and why the ratio
is not the 2–3 that the mobility argument alone would suggest.

*The PMOS output resistance is ten times higher.* 637.6 kΩ against 64.13 kΩ, so
its intrinsic gain $g_m r_o$ is 151 against 58.7 — **more than twice the gain of
the NMOS**, from a device that carries a seventh of the current. If your instinct
was "the PMOS is the weak one, use NMOS for everything," this is the number that
should complicate it. Amplifier input stages are very often PMOS, and this row is
a large part of why.

---

## 3. `wl_sweep_L05.spice` — device D lengthened to 0.5 µm

One character changed: `L=0.15` becomes `L=0.5`.

| device D | $L$ = 0.15 µm | $L$ = 0.5 µm |
|---|---|---|
| $I_D$ | 501.046 µA | **225.514 µA** |
| model `vth` | 0.7693 V | **0.6339 V** |
| `vdsat` | 0.3622 V | **0.6346 V** |
| $r_o$ | 19.45 kΩ | **109.6 kΩ** |

Three numbers moved, and all three moved the way the guide page said they would:
threshold came *down* 135 mV as the halo implants stopped dominating the channel,
`vdsat` came *up* because the field along a longer channel is lower, and $r_o$
went up by 5.6× because the pinch-off region is now a small fraction of the
channel instead of a large one.

**Check that the two-step arithmetic still closes.** $W/L$ is now 2, so against
device A:

- $W/L$ alone predicts $696.275 \times 2/5 = 278.510$ µA. Measured 225.514 —
  **81.0 %** of the prediction.
- Correct for the threshold: $\dfrac{2 \times (1.8-0.6339)^2}{5 \times (1.8-0.5895)^2} = 0.3712$,
  so 258.42 µA. Measured 225.514 — **87.3 %**.

Compare with the minimum-length device, where the same two steps left 54.0 % and
then 74.4 %. Both corrections are still doing work, and both are doing *less* of
it. The square law is not wrong; it is an approximation that gets better as you
back away from the process minimum, and you can now say by how much.

**The design question this is really asking:** device D at L = 0.5 µm carries 45 %
of the current for 3.3× the area, and gets 5.6× the output resistance. When is
that a good trade, and when is it a terrible one? The honest answer is "digital
says terrible, analog says obviously good," and knowing which conversation you
are in is most of what makes an analog designer.

---

## What none of these change

The extraction code. `src/mosfit.py` never mentions a device, a width, or a
threshold value — it takes two columns of numbers and does arithmetic. That is
deliberate: point it at the PMOS sweep, or a sweep of something you draw in
AD104, and it still works. Parameter extraction is a skill you own, not a script
that belongs to this lab.
