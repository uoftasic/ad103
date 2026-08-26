# The ngspice survival card

**Question this page answers:** *I have a netlist. What are the five things I can ask ngspice
to do with it, and what does it say when I get it wrong?*

Five analyses cover everything in AD103 and most of second year. Each one below is a
**complete deck that ships in a lab package** — you never have to retype one — and every
output is from that exact file, run in `hpretl/iic-osic-tools:2026.04`, ngspice **46**.

```bash
cd labs/survival-card
make
```

runs all five in about fourteen seconds and checks every number on this page against what
ngspice just said, so the page and the decks cannot drift apart:

```
PASS  every number on the survival card reproduces
```

```bash
ngspice -b mydeck.spice
```

`-b` is batch: run and exit. Without it you land in an interactive prompt and the terminal
looks hung.

## Every deck starts the same way

```spice
.lib $PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice.tt.red tt
```

That one line loads the typical-typical corner of SKY130. Two things about it are worth
knowing before you copy the shorter-looking path from somewhere else.

**Use the `.tt.red` file.** There are two ways to name the tt corner and one of them is
twenty-four times slower, because `sky130.lib.spice` `.include`s a tree of files while
`sky130.lib.spice.tt.red` is that tree already flattened into one 12 MB file:

| `.lib` line | run 1 | run 2 |
|---|---:|---:|
| `sky130.lib.spice.tt.red tt` | 1.951 s | 1.955 s |
| `sky130.lib.spice tt` | 47.583 s | 47.250 s |

Same circuit, same answer, 45 seconds of your life per run. If a deck of yours takes
almost a minute to print one number, this is why.

**`$PDK_ROOT` is already set** to `/foss/pdks` inside the image, so the line works with no
setup. `$PDK` is *not* what you want it to be — see
[the XSchem cheat sheet](reference/xschem-cheatsheet.md#the-wrong-pdk-is-silent) — but this
line does not use it.

## 1. `.op` — one bias point

*"With these DC voltages applied, what is every node and every current?"*

**`labs/lab-01-first-schematic/spice/nmos_op.spice`** — this one you have already run; it is
the deck Lab 01's `make` uses, minus the `nf=1 m=1` that XSchem writes:

```spice
* .op -- one bias point of one NMOS
.lib $PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice.tt.red tt
XM1 d g 0 0 sky130_fd_pr__nfet_01v8 L=0.15 W=1
Vgs g 0 1.8
Vds d 0 1.8
.control
op
print i(Vds)
.endc
.end
```

```
i(vds) = -5.01046e-04
```

501.046 µA, and it is **negative** because SPICE measures current *into* a voltage source's
positive terminal — current leaving `Vds` and going down through the transistor comes back
in the other way. Every drain current you print through a supply will be negative. This is
not a bug and it is the single most common "my answer has the wrong sign" in first year.

The same circuit ships as `labs/lab-01-first-schematic/spice/nmos_op.spice` (with `nf=1 m=1`
spelled out), and `make` in that lab prints:

```
  drain current : 501.046 uA  (reference 501.046 uA)

PASS  netlist and operating point match the reference run
```

`.op` also gives you the small-signal parameters that AD103's Movement IV is about:

```spice
print @m.XM1.msky130_fd_pr__nfet_01v8[vth] @m.XM1.msky130_fd_pr__nfet_01v8[gm] @m.XM1.msky130_fd_pr__nfet_01v8[gds] @m.XM1.msky130_fd_pr__nfet_01v8[cgg]
```

```
@m.xm1.msky130_fd_pr__nfet_01v8[vth] = 7.692674e-01
@m.xm1.msky130_fd_pr__nfet_01v8[gm]  = 5.322242e-04
@m.xm1.msky130_fd_pr__nfet_01v8[gds] = 5.141539e-05
@m.xm1.msky130_fd_pr__nfet_01v8[cgg] = 8.568632e-16
```

The name is ugly and it is not optional. `XM1` is *your* instance; inside it the PDK's
subcircuit builds a real MOSFET called `msky130_fd_pr__nfet_01v8`, and `@m.XM1.<that>[...]`
is the path to it. Get it wrong and ngspice says `Error: no such vector`.

## 2. `.dc` — sweep a source

*"Sweep this voltage and give me a curve."*

**`labs/survival-card/spice/dc_id_vgs.spice`** — `make dc`:

```spice
* AD103 survival card, analysis 2 -- .dc, sweep a source
.lib $PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice.tt.red tt
XM1 d g 0 0 sky130_fd_pr__nfet_01v8 L=1 W=5
Vgs g 0 0
Vds d 0 1.8
.control
dc Vgs 0 1.8 0.01
let id = -i(Vds)
meas dc id_1v8 find id at=1.8
meas dc id_0v9 find id at=0.9
meas dc vg_at_1ua when id=1u rise=1
.endc
.end
```

```
No. of Data Rows : 181
id_1v8              =  6.96275e-04
id_0v9              =  6.38760e-05
vg_at_1ua           =  5.65815e-01
```

181 rows because 0 to 1.8 in steps of 0.01 is 181 points, ends included. Count them; if the
row count is not what you expect, your sweep is not what you think it is.

The `dc` command takes `source start stop step`. Add four more arguments for a second, outer
sweep and you get a family of curves in one run:

```spice
dc Vds 0 1.8 0.01 Vgs 0.6 1.8 0.3
```

(`labs/survival-card/spice/dc_family.spice`, also run by `make dc`.)

```
No. of Data Rows : 905
id[180] = 2.005399e-06
id[181] = 1.881519e-42
```

905 rows is $5 \times 181$ — five gate voltages, each a full $V_{DS}$ sweep, laid end to end
in **one** vector. Index 180 is the last point of the first curve and index 181 is the first
point of the second, back at $V_{DS} = 0$. That is why
`labs/lab-03-mosfet-regions/spice/id_vds.spice` uses `foreach` and `alter` instead: five
separate `dc` commands give you five separate plots, addressable as `dc1.i(vds)` …
`dc5.i(vds)`, which is what you want when each curve becomes its own column in a file.

To get data out of ngspice and into a plot, `wrdata`:

```spice
wrdata ../results/id_vds.txt id_vgs06 id_vgs09 id_vgs12 id_vgs15 id_vgs18
```

Plain text, one **x,y pair per vector** on every row — five vectors give ten columns, and
the x column is repeated five times. Verified against the file that command writes:

```
 0.00000000e+00  1.78502380e-42  0.00000000e+00  1.88151889e-42  0.00000000e+00  1.97801397e-42  ...
 1.00000000e-02  3.75258957e-07  1.00000000e-02  3.95382562e-06  1.00000000e-02  7.76418855e-06  ...
```

**`let` first, then `meas`.** Write `-i(Vds)` directly inside `print` or `meas` and:

```
Error: no such vector as -i(vds).
 meas dc id_at_1v8 find -i(vds) at=1.8 failed!
```

`i(Vds)` is a vector; `-i(Vds)` is an *expression*, and `meas` wants a vector name. Make the
vector yourself with `let id = -i(Vds)` and hand `meas` the name `id`.

## 3. `.tran` — the time domain

*"Step the input and watch the output move."*

**`labs/survival-card/spice/tran_rc.spice`** — `make tran`:

```spice
* AD103 survival card, analysis 3 -- .tran, the time domain
.lib $PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice.tt.red tt
Vin in 0 pulse(0 1.8 1n 10p 10p 50n 100n)
XR1 in out sky130_fd_pr__res_generic_po W=1 L=200
XC1 out 0 sky130_fd_pr__cap_mim_m3_1 W=10 L=10 MF=1 m=1
.control
tran 5p 40n
meas tran tau when v(out)=1.1376 rise=1
meas tran vfinal find v(out) at=39n
.endc
.end
```

```
No. of Data Rows : 8014
tau                 =  3.10826e-09
vfinal              =  1.80000e+00
```

`tran <step> <stop>` — the step is a *hint*, not a promise; ngspice takes smaller steps
where the waveform is moving, which is why 40 ns at 5 ps produced 8014 rows and not 8000.

`pulse(v1 v2 delay risetime falltime width period)`. Here the edge starts at **1 ns**.

**`meas ... when` returns an absolute time, not an interval.** 1.1376 V is
$0.632 \times 1.8$, so `tau` should be one time constant — and 3.10826 ns is one time
constant *after the edge at 1 ns*. The time constant is $3.10826 - 1 = 2.10826$ ns. Forget
to subtract the delay and your RC is 47 % too big.

## 4. `.ac` — the frequency domain

*"Same circuit. Where does it stop responding?"*

**`labs/survival-card/spice/ac_rc.spice`** — `make ac`. Same two devices as the `.tran` deck:

```spice
* AD103 survival card, analysis 4 -- .ac, the frequency domain
.lib $PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice.tt.red tt
Vin in 0 dc 0 ac 1
XR1 in out sky130_fd_pr__res_generic_po W=1 L=200
XC1 out 0 sky130_fd_pr__cap_mim_m3_1 W=10 L=10 MF=1 m=1
.control
ac dec 200 10k 1G
meas ac f3db when vdb(out)=-3.0103 fall=1
.endc
.end
```

```
No. of Data Rows : 1001
f3db                =  7.56449e+07
```

`ac dec <points-per-decade> <fstart> <fstop>`. Five decades at 200 points each is 1001 rows.
The source needs `ac 1` on it — `dc 0` alone gives you a silent zero everywhere and a flat
line at $-\infty$ dB.

`vdb(out)` is $20\log_{10}|v(\text{out})|$. Half power is $-3.0103$ dB, not $-3$; using $-3$
shifts your answer by about 0.1 %, which is fine until you compare against arithmetic.

### The two analyses have to agree — check that they do

The resistor and the capacitor in those two decks can be measured on their own —
**`labs/survival-card/spice/rc_parts.spice`**, `make parts`:

```
r = 1.018463e+04
cmim = 2.065822e-13
```

$$RC = 10184.63 \times 206.5822\times10^{-15} = 2.10396\ \text{ns}$$

$$f_{-3\text{dB}} = \frac{1}{2\pi RC} = 75.6453\ \text{MHz}$$

`.ac` measured **75.6449 MHz** — 0.0005 % from the arithmetic. `.tran` measured
**2.10826 ns** — 0.20 % from the arithmetic, and high rather than random, because a 5 ps
step cannot land exactly on the crossing. Two analyses and a hand calculation agreeing to
four figures is what "the deck is right" looks like. Make this check a habit: whenever you
have an RC, one of the three numbers is free. `make` in that package prints exactly this
comparison at the end, so you can see it close.

## 5. `.meas` — get a number out instead of a picture

`meas` is not a fifth analysis; it is how the other four stop being pictures. It runs
*after* an analysis, in the same `.control` block, and prints one line.

| Form | Means |
|---|---|
| `meas dc  <name> find <vec> at=<x>` | the value of `<vec>` at sweep point `<x>` |
| `meas tran <name> find <vec> at=<t>` | the value at time `<t>` |
| `meas tran <name> when <vec>=<val> rise=1` | the **time** of the first rising crossing |
| `meas ac  <name> when vdb(out)=-3.0103 fall=1` | the **frequency** of the first falling crossing |
| `meas tran <name> avg <vec> from=<t1> to=<t2>` | the average over a window |
| `meas tran <name> trig v(a) val=0.9 rise=1 targ v(b) val=0.9 fall=1` | a propagation delay |

Three rules that cost people an evening each:

1. The analysis type in `meas dc` / `meas tran` / `meas ac` must match the analysis you just
   ran, or the measurement silently fails.
2. `when` gives you the x-axis value (time, or frequency, or the swept voltage); `find`
   gives you the y-axis value.
3. A failed `meas` prints ` meas <name> ... failed!` and **ngspice keeps going and exits 0**.
   Read the output; do not trust the exit code.

## Output that looks like trouble and is not

### The four `Error:` lines that open every single run

Before ngspice has read one character of your circuit:

```
Error opening osdi lib "/foss/pdks/sky130A/libs.tech/ngspice/osdi/psp103.osdi": No such file or directory!
Error: Library /foss/pdks/sky130A/libs.tech/ngspice/osdi/psp103.osdi couldn't be loaded!
Error opening osdi lib "/foss/pdks/sky130A/libs.tech/ngspice/osdi/psp103_nqs.osdi": No such file or directory!
Error: Library /foss/pdks/sky130A/libs.tech/ngspice/osdi/psp103_nqs.osdi couldn't be loaded!
Error opening osdi lib "/foss/pdks/sky130A/libs.tech/ngspice/osdi/r3_cmc.osdi": No such file or directory!
Error: Library /foss/pdks/sky130A/libs.tech/ngspice/osdi/r3_cmc.osdi couldn't be loaded!
Error opening osdi lib "/foss/pdks/sky130A/libs.tech/ngspice/osdi/mosvar.osdi": No such file or directory!
Error: Library /foss/pdks/sky130A/libs.tech/ngspice/osdi/mosvar.osdi couldn't be loaded!
Warning: OSDI libs have not been loaded successfully.
    Any of the following steps may fail, if Verilog A models are involved!.
```

**This is the most alarming output in the course and it means nothing.** Every MOSFET run on
this page produced it, including the ones whose numbers are quoted to six figures.

OSDI is ngspice's plug-in interface for compiled Verilog-A models. SKY130's `nfet_01v8`,
`pfet_01v8`, resistors and diodes are all *built-in* BSIM and diode models, so none of those
four libraries is ever needed. The image simply does not ship them.

Note what this does to the rule at the bottom of this page: these lines say `Error` and are
**not** followed by `Simulation interrupted due to error!`, and the run exits `0`. That is
precisely the distinction — `Error:` on its own is not enough. Look for the pair.

Every AD103 `Makefile` redirects this to a log, so you will first meet it the day you type
`ngspice -b` yourself.

### The warning block every resistor and diode prints

Run anything against this PDK and stderr fills with warnings. They are scenery. This is the
complete stderr of a deck that instantiates eight resistors and a capacitor and gets every
number right — 18 lines:

```
Warning: Model issue on line 4842 :
  .model xr2:rhead_model r sw_et=0 isnoisy=0 rsh=    3.458312000000000e+02 ...
unrecognized parameter (sw_et) - ignored
unrecognized parameter (isnoisy) - ignored
unrecognized parameter (p2) - ignored
unrecognized parameter (q2) - ignored
...
Warning: sky130_fd_pr__model__parasitic__diode_ps2nw: IKR too small - model effect disabled!
Warning: sky130_fd_pr__diode_pw2nd_05v5: IKR too small - model effect disabled!
```

- **`unrecognized parameter (sw_et) - ignored`** (10 of them) — the PDK's resistor model
  cards carry parameters written for a different simulator. ngspice drops them and models
  the resistor correctly anyway.
- **`IKR too small - model effect disabled!`** (2) — a high-injection knee current the
  models set to zero. Not your circuit; it appears whenever a junction diode is in the deck,
  which is always.
- **`Note: No compatibility mode selected!`** — prints on every single run, including
  perfect ones.

**Warnings go to stderr, results go to stdout.** `ngspice -b deck.spice > results.log` gives
you a clean log and leaves the noise on your terminal. The rule for telling scenery from a
real problem: a real problem says `Error` and is followed by
`Simulation interrupted due to error!`.

## Error messages, with the exact text

| ngspice says | You did |
|---|---|
| `could not find a valid modelname` | put a `u` on `W` or `L`, or asked for a size no bin covers. Full explanation: [Reading a SKY130 device model](reference/sky130-device-guide.md). |
| `Error: no such vector as -i(vds).` | put an expression where `print`/`meas` wanted a vector. `let id = -i(Vds)` first. |
| `Error: unknown subckt: xr6 f 0 sky130_fd_pr__res_generic_l1 w=1 l=1` | started the line with `X` for a device that is a plain `.model`, not a `.subckt`. `res_generic_l1` and the metal resistors are `R` lines: `r6 f 0 sky130_fd_pr__res_generic_l1 w=1 l=1`. |
| `warning, can't find model 'sky130_fd_pr__nfet_01v8' from line` | started the line with `M` for a device that *is* a `.subckt`. Transistors are `X` lines. |
| `Too many parameters for subcircuit type "sky130_fd_pr__res_generic_po" (instance: xxr1)` | passed `mult=1` to a device whose subcircuit has no `mult`. Not every resistor takes the same parameters. |
| `Too few parameters for subcircuit type "sky130_fd_pr__cap_var_lvt" (instance: xxcv)` | gave the wrong number of *nodes*. The varactor has three terminals, not two. |
| `Error: incomplete or empty netlist` / `no simulations run!` | nothing on its own. It is the second message; the real error is a few lines above it. |
| `Error: Library …/osdi/psp103.osdi couldn't be loaded!` | nothing at all. Four of these open every run on this image; see [above](reference/ngspice-errors.md#the-four-error-lines-that-open-every-single-run). |

## Exit codes

Measured, on the decks on this page:

| Deck | exit |
|---|---:|
| a correct `.op` | `0` |
| `W=1u` — `could not find a valid modelname` | `1` |
| a deck whose `meas` failed | `0` |
| a deck with no `.control` block at all | `0` |
| any of the above, with the four OSDI `Error:` lines | unchanged |

So `$?` catches a deck that would not build, and catches nothing else. Every AD103 lab
`Makefile` therefore reads the log and prints its own `PASS` or `FAIL` rather than trusting
ngspice's status — and so should any script of yours.

---

Next: [Reading a SKY130 device model](reference/sky130-device-guide.md), which is where
`could not find a valid modelname` gets its full explanation.
