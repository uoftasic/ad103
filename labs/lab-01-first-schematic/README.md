# Lab 01 — Your first schematic

Writeup: [uoftasic.com/ad103 → Lab 01](https://uoftasic.com/ad103/#/labs/lab-01-first-schematic-overview)

Draw one transistor. Turn it into SPICE. Ask a simulator what current flows
through it. That is the whole lab, and every other lab in this course is that
same chain with a bigger circuit on the front.

It also does something the rest of the course depends on: it gives you a
**known-good reference** you can run at any time. When a page later seems to be
lying to you, come back here and type `make`. A `PASS` means the toolchain is
fine and the problem is in your drawing, which is a far better problem to have.

## Run it

```bash
cd labs/lab-01-first-schematic
make
```

No environment setup needed. The `Makefile` pins `PDK=sky130A` itself, so this
runs in a bare container even if `.designinit` failed you.

Expected, in about **2.5 seconds**:

```
== netlisting xschem/nmos_probe.sch
   wrote xschem/simulation/nmos_probe.spice
== simulating spice/nmos_op.spice
   wrote results/nmos_op.log
== checking
  device line : XM1 d g 0 0 sky130_fd_pr__nfet_01v8 L=0.15 W=1 nf=1 ad=0.29 as=0.29 pd=2.58 ps=2.58 nrd=0.29 nrs=0.29 sa=0 sb=0 sd=0 mult=1
  drain current : 501.046 uA  (reference 501.046 uA)

PASS  netlist and operating point match the reference run
```

**501.046 µA.** A real SKY130 NMOS, one micrometre wide and 150 nanometres long,
with 1.8 V on the gate and 1.8 V on the drain.

## Then draw your own

`xschem/my_probe.sch` has the two supplies, the two named nets and the ground
already placed. It is missing exactly one thing.

```bash
make edit      # opens it in XSchem
```

![xschem/my_probe.sch — everything but the transistor](https://raw.githubusercontent.com/uoftasic/ad103/main/docs/assets/img/ad103-xschem-my-probe.png)

Add one `nfet_01v8`, set `W=2` and `L=0.15`, wire its four pins, save, and:

```bash
make mine
```

It netlists what you drew and checks it before it simulates anything, because a
schematic can be wrong in five ways that all look identical in the window:

```
  WHAT YOU DREW
    XM1 d g 0 0 sky130_fd_pr__nfet_01v8 L=0.15 W=2 nf=1 ad=0.58 as=0.58 pd=4.58 ps=4.58 nrd=0.145 nrs=0.145 sa=0 sb=0 sd=0 mult=1

  Wired correctly. Simulating it.

  YOUR TRANSISTOR
    W = 2 um, L = 0.15 um, V_GS = V_DS = 1.8 V
    drain current    1030.4200 uA
    reference        1030.4200 uA

PASS  you drew a transistor, XSchem turned it into SPICE, and ngspice
      answered 1030.4200 uA. That is the whole chain, and it is the
      chain every other lab in this course runs on.
```

If it is wrong, it says which of the five and what to do about it — a missing
device, a unit suffix on `W`, a `net7` where a wire did not land, the source on
the wrong node, the body left floating. In words, not as a stack trace.

## Targets

| Command | What it does |
|---|---|
| `make` | netlist the reference schematic, simulate, print a verdict |
| `make edit` | open `xschem/my_probe.sch` in XSchem |
| `make mine` | netlist and check **your** schematic, then simulate it |
| `make wrong-units` | the same circuit with `W` and `L` in metres — **fails on purpose, loudly** |
| `make unconnected` | one wire one grid step short — **does not fail, which is worse** |
| `make bins` | which model bin `L=0.15 W=1` landed in, and what `leff` really is |
| `make clean` | delete `results/` and `xschem/simulation/` |

## The two failures worth causing on purpose

Run both of these before you need them. They are the two ways a schematic goes
wrong in this course, and they fail in opposite ways.

**`make wrong-units`** — `W=1u` instead of `W=1`. ngspice stops dead with
`could not find a valid modelname`, which names neither `W` nor units. Loud,
unhelpful, and impossible to miss.

**`make unconnected`** — the gate wire ends one grid step short of the gate pin.
XSchem netlists it with **exit status 0**, invents a net name, and ngspice
returns an answer:

```
   XSchem exit status: 0.  No error, no warning.  Here is the device line:
     XM1 d net1 0 0 sky130_fd_pr__nfet_01v8 L=0.15 W=1 ...

     Warning: Dynamic gmin stepping failed
     Warning: True gmin stepping failed
     Warning: source stepping failed
     Note: Transient op finished successfully
     i(vds) = -7.34593e-08
     v(net1) = 5.017472e-01
```

**73.4593 nA against 501.046 µA — wrong by a factor of 6821, with no error
anywhere.** The gate settled at 0.5017472 V because nothing was driving it.
The only clue is three lines of solver grumbling that look exactly like the
noise you learn to scroll past.

The reflex check, and use it after every netlist for the rest of this course:

```bash
grep 'net[0-9]' xschem/simulation/*.spice
```

Any hit is a wire you believe is connected and is not.

## Files

| Path | What it is |
|---|---|
| `xschem/my_probe.sch` | **yours.** Everything but the transistor |
| `xschem/nmos_probe.sch` | the reference schematic — one NMOS, two supplies, nets `g` and `d` |
| `xschem/broken_probe.sch` | the same drawing with the gate wire one grid step short |
| `xschem/xschemrc` | project-local XSchem config: loads the SKY130 symbols, and puts netlists in `simulation/` next to the schematic instead of inside the container |
| `spice/nmos_op.spice` | the same circuit as a hand-written deck. Five parts: models, devices, sources, analysis, `.end` |
| `spice/nmos_op_wrong_units.spice` | identical except `L=0.15u W=1u`. The loud trap |
| `spice/nmos_op_unconnected.spice` | identical except the gate is on `net1`. The quiet one |
| `spice/bins.spice` | identical except it has **no `.control` block**, so batch ngspice dumps the whole operating point. `make bins` shows which model bin your device landed in, and that `leff` is 16 % shorter than the `L` you drew |
| `src/check.py` | reads the netlist and the log, prints `PASS` or `FAIL` and why |
| `src/check_mine.py` | reads **your** netlist and grades it in words before simulating |

## Two numbers to take with you

`make` gives **501.046 µA** for the reference $W$ = 1 µm device. `make mine`
gives **1030.4200 µA** for your $W$ = 2 µm one.

Twice 500.941 — the reference number as the XSchem netlist produces it, with the
diffusion parasitics the symbol adds — is 1001.882. You measured 1030.42, which
is **2.85 % more**. Doubling the width did slightly better than doubling the
current.

That is not noise and it is not a mistake. It is a real property of the device,
and [Lab 04](../lab-04-wl-knob/README.md) is entirely about it.

Also note the sign: `i(vds) = -5.01046e-04` in the log. ngspice reports current
*into* the positive terminal of a source, and this source is pushing current
out. From [Lab 02](../lab-02-diode-iv/README.md) onward that convention stops
surprising you.
