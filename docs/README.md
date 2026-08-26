# AD103 — Nonlinear Circuits

Draw a transistor, ask it a question, and believe the answer. This is where the
analog track stops using formulas that assume everything is a straight line.

Part of the **UofT ASIC Team** education materials. Published at **https://uoftasic.com/ad103/**.
Labs run inside the shared **workspace** you set up in [IC101](https://uoftasic.com/ic101/).

## At a glance

| | |
|---|---|
| **Track** | Analog |
| **Prerequisites** | [IC101](https://uoftasic.com/ic101/) → [AD101](https://uoftasic.com/ad101/) → [AD102](https://uoftasic.com/ad102/), in that order |
| **Main tool** | **XSchem** — the schematic editor. You have not used it before; [Getting started](guide/getting-started.md) assumes that. |
| **Also** | ngspice 46, and the SKY130 device models, both already in the workbench |
| **Math level** | Algebra, exponentials, logarithms. One square root. No calculus required. |
| **Time** | 14–18 hours, self-paced |

> **This course is pinned to the workbench image `hpretl/iic-osic-tools:2026.04`**, which ships
> **XSchem 3.4.8RC** and **ngspice-46**. Check yours with `xschem --version`.
>
> The image's default PDK is **not** SKY130. Launch XSchem without fixing that and you get a
> German 130 nm process instead, with none of the symbols this course names — and no error
> message. [Getting started](guide/getting-started.md) shows you the two-second check.

> **If your environment setup fails, run `make` anyway.** Every lab package pins its own PDK
> and model paths, so the labs run to completion in a bare container with no setup at all, and
> each one ends in `PASS` or `FAIL` with a reason.

## What this course is about

AD101 taught you to read a signal. AD102 taught you that a resistor is a doped strip of
silicon whose value is a **shape**. Both of those live in a world where doubling the input
doubles the output.

The diode and the MOSFET do not live in that world, and almost everything interesting about a
chip happens because they don't. A transistor is useful *because* its response bends. Amplify
with it and the bend is the gain; switch with it and the bend is the on/off. Push it too far
either way and the bend is the distortion.

You cannot solve these circuits with the algebra AD102 gave you. So you learn the other
skill: **ask a simulator, and know enough to tell a plausible answer from a wrong one.**

## What you'll do

1. Draw a schematic in **XSchem** from an empty canvas, and read the SPICE netlist it writes
2. Sweep a real SKY130 diode and find out how far the textbook's **60 mV per decade** is from
   what silicon actually does
3. Map the **four regions** of a MOSFET — including the one most textbooks skip
4. Extract a threshold voltage from your own curve, two different ways, and explain why the two
   answers differ by 86 mV
5. Find out what $W$ and $L$ really buy you, and where the $W/L$ rule stops being true —
   five devices with identical $W/L$ carrying five different currents
6. Build a **CMOS inverter** from two transistors, measure the voltage at which it switches,
   and discover that sizing it for equal delay and sizing it for a centred threshold are two
   different jobs

## Path

| Part | Guide | Lab |
|------|-------|-----|
| 0 | [Getting started](guide/getting-started.md) | [Lab 01 — Your first schematic](labs/lab-01-first-schematic-overview.md) |
| I — Where the straight line ends | [The straight line runs out](guide/the-straight-line-runs-out.md) · [The operating point](guide/the-operating-point.md) | — |
| II — The diode | [A diode is an exponential](guide/the-diode-is-an-exponential.md) · [Three models of one diode](guide/three-models-of-one-diode.md) | [Lab 02 — The diode I–V curve](labs/lab-02-diode-iv-overview.md) |
| III — The MOSFET | [A MOSFET is a valve](guide/a-mosfet-is-a-valve.md) · [Four regions, not three](guide/four-regions-not-three.md) · [Where saturation starts](guide/where-saturation-starts.md) | [Lab 03 — The regions of a MOSFET](labs/lab-03-mosfet-regions-overview.md) |
| IV — The parameters | [Threshold is not a constant](guide/threshold-is-not-a-constant.md) · [$g_m$ and $r_o$](guide/gm-and-ro.md) · [W and L are a choice](guide/w-and-l-are-a-choice.md) | [Lab 04 — $W/L$ is a knob](labs/lab-04-wl-knob-overview.md) |
| Capstone | [The inverter is an amplifier](guide/the-inverter-is-an-amplifier.md) · [The current mirror](guide/the-current-mirror.md) | [Capstone — The CMOS inverter](labs/capstone-inverter-overview.md) |

Reference: [XSchem cheat sheet](reference/xschem-cheatsheet.md) ·
[The ngspice survival card](reference/ngspice-errors.md) ·
[Reading a SKY130 device model](reference/sky130-device-guide.md)

**Stuck?** Ask in the [team Discord](https://discord.gg/hrJnP5UsGz). Nobody expects you to work
this out alone at 2 a.m. — see [Getting help](guide/getting-started.md#getting-help).

## Quick start

```bash
# in the noVNC desktop, after IC101
. /foss/designs/common/.designinit
echo $PDK                      # must say sky130A, not ihp-sg13g2
mod add ad103                  # first time only
mod ad103
xschem --version               # expect: XSCHEM V3.4.8RC
cd labs/lab-01-first-schematic && make
```

That last command should print `PASS` and the number **501.046 µA** in about
two and a half seconds. If it does, your toolchain is fine and any problem after
this is a drawing problem, which is a much better problem to have.

## What you'll have at the end

A schematic you drew, a set of measured device curves you can defend, and the habit that makes
the rest of the analog track possible: **predict the number, run the sim, and go find out which
one of you was wrong.**

## Next courses

- **[AD104](https://uoftasic.com/ad104/)** — Layout: draw those transistors as geometry in Magic, DRC and LVS clean
- **AD201** — Analog Signal Processing · **AD202** — Mixed Signal
