# Reading a SKY130 device model

**Question this page answers:** *Where do a transistor's numbers actually come from, and why
does `W=1u` break everything?*

You have been writing `sky130_fd_pr__nfet_01v8 L=0.15 W=1` since Lab 01 without being told
what is on the other end of that name. This page opens it. It is also the page that explains
the one error message every AD103 student meets:

```
could not find a valid modelname
```

## Where the models live, and which one you are using

```bash
ls /foss/pdks/sky130A/libs.tech/ngspice/
ls /foss/pdks/sky130A/libs.ref/sky130_fd_pr/spice/ | wc -l
```

| Path | What is in it | You use it |
|---|---|---|
| `libs.tech/ngspice/sky130.lib.spice` | 16 541 bytes — a table of contents. 51 `.lib` sections, one per corner, each pulling in a tree of `.include`s | when you need a corner that has no `.red` file |
| `libs.tech/ngspice/sky130.lib.spice` | 12 176 942 bytes — that whole tree, pre-flattened, for one corner. `tt`, `ff`, `ss`, `sf`, `fs` only | **always**, in AD103. 1.95 s to load instead of 47 s |
| `libs.ref/sky130_fd_pr/spice/` | 675 files, one device family each, human-sized. `sky130_fd_pr__nfet_01v8.pm3.spice`, `sky130_fd_pr__res_high_po.model.spice`, … | when you want to *read* a device rather than simulate it |
| `libs.tech/combined/` | the **continuous** models — the same devices recharacterised so their parameters vary smoothly with size | not directly; this is what XSchem's own `xschemrc` points `SKYWATER_MODELS` at |

That last row is worth a sentence, because it is a genuine fork in the PDK and the foundry's
own README explains it:

> The original devices models were characterized at specific device width and length, and are
> considered "micro-binned"; that is, device models are accurate for devices with width and
> length equal to the devices that were characterized, and can diverge considerably for other
> device sizes. The "continuous" models have been recharacterized to ensure that parameters
> are continuous across device width and length.
>
> — `/foss/pdks/sky130A/libs.tech/combined/README`

AD103's decks name `libs.tech/ngspice/...tt.red` explicitly, so every number in this course
comes from the binned models. Both take `W` and `L` as plain micron numbers.

## Your device line becomes a subcircuit

```spice
XM1 d g 0 0 sky130_fd_pr__nfet_01v8 L=0.15 W=1
```

`X` means "instance of a subcircuit". Find it:

```bash
grep -m1 -n -A3 '^\.subckt  sky130_fd_pr__nfet_01v8 ' \
  /foss/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice
```

```
12:.subckt  sky130_fd_pr__nfet_01v8 d g s b
13:+
14:.param  l = 1 w = 1 nf = 1.0 ad = 0 as = 0 pd = 0 ps = 0 nrd = 0 nrs = 0 sa = 0 sb = 0 sd = 0 mult = 1
15:msky130_fd_pr__nfet_01v8 d g s b sky130_fd_pr__nfet_01v8__model l = {l} w = {w} nf = {nf} ...
```

Four terminals in the order **d g s b**, thirteen parameters with defaults, and inside it one
real MOSFET whose model is called `sky130_fd_pr__nfet_01v8__model`. That trailing `__model`
is the thing bins are attached to, and the reason your `.op` printout is full of names like
`@m.XM1.msky130_fd_pr__nfet_01v8[gm]`.

Not every device is a subcircuit. `sky130_fd_pr__res_generic_m1` and the other metal and
local-interconnect resistors are bare `.model` cards, so they start with `R`, not `X`:

```spice
r7 g 0 sky130_fd_pr__res_generic_m1 w=1 l=1
```

Use `X` on one of those and ngspice says `Error: unknown subckt:`. Use `M` on a transistor and
it says `warning, can't find model 'sky130_fd_pr__nfet_01v8'`. The letter is part of the
device's identity; look at the PDK file before guessing.

## What a bin is

There is no single `nfet_01v8` model. There are **180** of them in the tt corner, each fitted
to a rectangle of the $(W, L)$ plane:

```bash
L=/foss/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice
sed -n '/^\.lib tt$/,/^\.endl tt$/p' $L | grep -c '^\.model sky130_fd_pr__nfet_01v8__model\.'
```

```
180
```

The `sed` is not decoration. `sky130.lib.spice` holds **two** `.lib` sections — `tt`
and `tt_mm`, the mismatch-enabled twin — so a plain `grep -c` over the whole file answers
`360` and every count you take from it is doubled. Slice the section first. (`-m1` on the
`.subckt` grep above is there for the same reason.)

Each one carries its own patch of the plane on its first line. This is the one that will win
for `L=0.15 W=1`:

```
.model sky130_fd_pr__nfet_01v8__model.71 nmos
+ lmin = 1.5e-07 lmax = 1.8e-07 wmin = 8.4e-07 wmax = 1.0e-6
```

Sorting all 180, the ladder the foundry actually characterised is:

| axis | edges (µm) |
|---|---|
| **L** | 0.15, 0.18, 0.25, 0.5, 1, 2, 4, 8, 20, 100 |
| **W** | 0.36, 0.39, 0.42, 0.52, 0.54, 0.55, 0.58, 0.60, 0.61, 0.64, 0.65, 0.74, 0.84, 1.0, 1.26, 1.68, 2.0, 3.0, 5.0, 7.0, 100 |

Ten L edges is nine bands; twenty-one W edges is twenty bands; $9 \times 20 = 180$, which is
the bin count exactly. So a SKY130 NMOS is defined for **L from 0.15 µm to 100 µm and W from
0.36 µm to 100 µm**, and nowhere else. Ask for anything outside that and there is no model to
run.

Other devices, same corner, same command with the device name swapped:

| device | bins |
|---|---:|
| `sky130_fd_pr__nfet_01v8` | 180 |
| `sky130_fd_pr__pfet_01v8` | 108 |
| `sky130_fd_pr__pfet_01v8_hvt` | 198 |
| `sky130_fd_pr__nfet_01v8_lvt` | 88 |
| `sky130_fd_pr__pfet_01v8_lvt` | 48 |
| `sky130_fd_pr__nfet_g5v0d10v5` | 88 |
| `sky130_fd_pr__pfet_g5v0d10v5` | 88 |

## The units, and why they look wrong

Look again at that bin:

```
+ lmin = 1.5e-07 lmax = 1.8e-07 wmin = 8.4e-07 wmax = 1.0e-6
```

Those are metres. And you wrote `L=0.15 W=1`. They cannot be compared — unless something
converts, and something does. Every bin also carries:

```
+ binunit = 2.0
```

`binunit = 2` tells ngspice that the *instance's* `L` and `W` are micron numbers, so it scales
them before choosing a bin. `L=0.15` becomes $1.5\times10^{-7}$ m, which is exactly `lmin`.

**Demonstrate it, don't take my word.** Lab 01 ships the deck that shows you:
`labs/lab-01-first-schematic/spice/bins.spice`. It is the same transistor as `nmos_op.spice`
with one deliberate difference — **no `.control` block at all**, which makes batch ngspice
dump the whole operating point, including the model card it chose and the geometry it used,
rather than only what you asked it to print.

That dump is several hundred lines, so `make bins` pulls out the eleven that matter:

```bash
cd labs/lab-01-first-schematic
make bins
```

```
      model xm1:sky130_fd_pr__nfe
       toxe             4.148e-09
       vth0              0.411231
       lmin               1.5e-07
       wmin               8.4e-07
      model xm1:sky130_fd_pr__nfe
          l               1.5e-07
          w                 1e-06
        vth              0.769267
       weff           9.56282e-07
       leff           1.26136e-07
```

(The `make bins` target is four lines of `grep`; if you would rather run it yourself, it is
`ngspice -b spice/bins.spice 2>/dev/null | grep -E '^ +model xm1|^ +(toxe|vth0|lmin|wmin|l|w|vth|weff|leff) '`.)

The name is truncated to `sky130_fd_pr__nfe` by ngspice's own column width, and the header
appears twice because ngspice prints the model card first and the instance second. Everything
above the second header is the **bin**; everything below it is **your device**.

Read that block slowly, because four separate lessons are in it.

- `l = 1.5e-07`, `w = 1e-06`. Your plain `0.15` and `1` arrived as metres. The conversion is real.
- `lmin = 1.5e-07`, `wmin = 8.4e-07`. This is bin 71, the one that won. Your device sits on
  its **lower** L edge (0.15 µm) and its **upper** W edge (1.0 µm) — one nudge in either
  direction and a different model card, with different fitted parameters, takes over.
- `vth0 = 0.411231` is the model card's threshold parameter; `vth = 0.769267` is what this
  device actually has at this bias. They are not the same number and they are not supposed to
  be — see [Threshold is not a constant](guide/threshold-is-not-a-constant.md).
- `weff = 9.56282e-07`, `leff = 1.26136e-07`. **You drew 1 µm and got 0.956 µm; you drew
  0.15 µm and got 0.126 µm.** The gate is 16 % shorter than the mask, because the source and
  drain diffuse sideways underneath it. Nothing comes out the size you drew.

## The trap: `W=1` versus `W=1u`

Everywhere else in SPICE, a bare number is metres and you write `1u` for a micron. On a
SKY130 device you write **`W=1`**, and `W=1u` fails. Two decks, one character apart —
both ship in `labs/lab-01-first-schematic/spice/`:

```spice
XM1 d g 0 0 sky130_fd_pr__nfet_01v8 L=0.15 W=1 nf=1 m=1     ← nmos_op.spice
XM1 d g 0 0 sky130_fd_pr__nfet_01v8 L=0.15u W=1u nf=1 m=1   ← nmos_op_wrong_units.spice
```

```bash
make wrong-units
```

```
Error on line 13 or its substitute:
  m.xm1.msky130_fd_pr__nfet_01v8 d g 0 0 xm1:sky130_fd_pr__nfet_01v8__model l=    1.500000000000000e-07     w=    1.000000000000000e-06     nf=    1.000000000000000e+00     ad= ...
could not find a valid modelname
    Simulation interrupted due to error!

Error: incomplete or empty netlist
       or no ".plot", ".print", or ".fourier" lines in batch mode;
no simulations run!
```

Exit status `1`.

**Now look at what makes this trap cruel.** The error prints
`l = 1.500000000000000e-07`, which is 150 nm — the number you wanted. It looks correct.
Students stare at that line and conclude the problem is somewhere else.

It is not correct, because that is the value *before* `binunit` scaling. ngspice is about to
multiply it by $10^{-6}$ again: `0.15u` = $1.5\times10^{-7}$ → $1.5\times10^{-13}$ m
= 0.00000015 µm, which is below `lmin` in all 180 bins. The error message shows you the
halfway house.

**The reflex:** `could not find a valid modelname` on a line that looks fine means look for a
`u`. Then compare the two `l=` values — the good deck's `.op` shows `l 1.5e-07` *after*
scaling; the failing deck's error shows `l= 1.5e-07` *before* it.

## The same error, a different cause

```spice
XM1 d g 0 0 sky130_fd_pr__nfet_01v8 L=0.1 W=1
```

```
Error on line 13 or its substitute:
  m.xm1.msky130_fd_pr__nfet_01v8 d g 0 0 xm1:sky130_fd_pr__nfet_01v8__model l=    1.000000000000000e-01     w=    1.000000000000000e+00 ...
could not find a valid modelname
```

Identical message. No `u` anywhere. The cause is that SKY130's shortest characterised gate is
**0.15 µm** and you asked for 0.1 µm, so again no bin claims it. The expanded line is what
separates the two cases: `l= 1.0e-01` is a plain micron number that is simply too small,
while `l= 1.5e-07` is a metres value that should have been microns.

So the message has two readings:

| the expanded `l=` shows | what happened |
|---|---|
| a number that looks like microns (`1.0e-01`, `5.0e+00`) | the size is outside the ladder. Check it against the L and W edges above. |
| a number that looks like metres (`1.5e-07`, `1.0e-06`) | you wrote `u`. Delete it. |

## Every other device takes plain micron numbers too

The rule is not special to transistors. Nothing in the SKY130 PDK takes a unit suffix on a
geometry.

| Device | Line | Parameters | Units |
|---|---|---|---|
| MOSFET | `XM1 d g s b sky130_fd_pr__nfet_01v8 W=1 L=0.15 nf=1 m=1` | `W`, `L`, `nf`, `m` | µm |
| Precision resistor | `XR1 r0 r1 b sky130_fd_pr__res_high_po W=1 L=10 mult=1` | `W`, `L`, `mult` | µm |
| Generic poly / diffusion resistor | `XR1 t1 t2 sky130_fd_pr__res_generic_po W=1 L=200` | `W`, `L` — **no `mult`** | µm |
| Metal / li resistor | `r1 a b sky130_fd_pr__res_generic_m1 w=1 l=1` | `R` line, not `X` | µm |
| MIM capacitor | `XC1 c0 c1 sky130_fd_pr__cap_mim_m3_1 W=10 L=10 MF=1 m=1` | `W`, `L`, `MF` | µm |
| Varactor | `XCV c0 c1 b sky130_fd_pr__cap_var_lvt W=10 L=10 VM=1` | three terminals | µm |
| Diode | `XD1 n p sky130_fd_pr__diode_pw2nd_05v5 area=1 perim=4` | `area`, `perim` | µm², µm |

Two of those rows are their own trap. Passing `mult=1` to `res_generic_po`, which has no such
parameter, gives
`Too many parameters for subcircuit type "sky130_fd_pr__res_generic_po" (instance: xxr1)`.
Giving the varactor two nodes instead of three gives
`Too few parameters for subcircuit type "sky130_fd_pr__cap_var_lvt" (instance: xxcv)`.
When in doubt, read the `.subckt` line — it is one `grep` away and it lists both the terminals
and the parameters:

```bash
grep -m1 -A2 'subckt.*sky130_fd_pr__res_high_po ' \
  /foss/pdks/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__res_high_po.model.spice
```

The diode's `area` and `perim` deserve their own warning, because getting them wrong produces
no error at all — see the deliberate failures in
[Lab 02 — The diode I–V curve](labs/lab-02-diode-iv-overview.md).

## Corners

`tt` is the second word on the `.lib` line, and it is one of 51:

```
tt  sf  ff  ss  fs  ll  hh  hl  lh  sf_ll  sf_hh  …  tt_mm  …  mc
```

- The first pair is the **transistors**: `tt` typical, `ff` fast-fast, `ss` slow-slow, and the
  mixed `sf` / `fs`.
- `ll`, `hh`, `hl`, `lh` are the **passives** — resistor and capacitor low/high. AD102's
  corner decks use these.
- `_mm` adds mismatch, `mc` is Monte Carlo. Both need extra setup; AD103 does not use them.

Only `tt`, `ff`, `ss`, `sf` and `fs` have a flattened `.red` file. Everything else has to come
from `sky130.lib.spice`, and pays the 47-second parse.

## Three reflex checks

1. **Before you believe a simulation**, check the geometry landed where you meant: run a bare
   `.op` and read `l`, `w`, `weff`, `leff`.
2. **On `could not find a valid modelname`**, read the expanded `l=` in the error before
   changing anything. Metres-looking → delete a `u`. Micron-looking → your size is off the
   ladder.
3. **When a device behaves oddly across a size sweep**, remember you may have crossed a bin
   edge. The parameters change discontinuously there; that is what "micro-binned" costs you,
   and it is why the continuous models exist.

---

Next: [W and L are a choice](guide/w-and-l-are-a-choice.md), which is what to do with the two
numbers now that you know what happens to them. For the passive side of the same PDK, AD102's
[SKY130 passive quick-reference](https://uoftasic.com/ad102/#/reference/sky130-passive-catalogue).
