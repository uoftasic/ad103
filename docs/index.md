# AD103 — Nonlinear Circuits

In this course you draw transistors in XSchem, simulate them with real SKY130 models, and
learn to tell a believable answer from a wrong one. It is the third course in the analog
track, and the first one where the circuits stop being linear.

AD103 is part of the **UofT ASIC Team** education materials, and it's published at
**https://uoftasic.com/ad103/**. The labs run inside the shared **workspace** you set up in
[IC101](https://uoftasic.com/ic101/).

## At a glance

| | |
|---|---|
| **Who it's for** | 2nd–3rd year ECE students on the analog track |
| **Track** | Analog |
| **Prerequisites** | [IC101](https://uoftasic.com/ic101/) → [AD101](https://uoftasic.com/ad101/) → [AD102](https://uoftasic.com/ad102/), in that order |
| **Main tool** | **XSchem**, the schematic editor. Lab 01 assumes you have never used it before. |
| **Also** | ngspice 47 and the SKY130 device models, both already in the workbench |
| **Math level** | Algebra, exponentials, logarithms, and one square root. You won't need calculus. |
| **Time** | About 16.5 hours, self-paced |

## Course path

Work down this table in order. A **Read** row is one or more guide pages: concepts, figures and
worked examples, with nothing to run. A **Do** row is one lab, where you run every command
yourself. Each lab lists the pages to read before you start it.

| # | | What | Time |
|---|---|---|---|
| 1 | Read | [Getting started](guide/getting-started.md) | 30 min |
| 2 | Do | [Lab 01: Your first schematic](labs/lab-01-first-schematic-overview.md). Draw one NMOS in XSchem, simulate it, and break it twice on purpose. | 2 h |
| 3 | Read | [Linearity and superposition](guide/the-straight-line-runs-out.md) · [The operating point](guide/the-operating-point.md) · [The diode equation](guide/the-diode-is-an-exponential.md) · [Three diode models](guide/three-models-of-one-diode.md) | 1.5 h |
| 4 | Do | [Lab 02: The diode I–V curve](labs/lab-02-diode-iv-overview.md). Sweep a SKY130 diode, extract two of its model parameters, and heat it to 100 °C. | 1.75 h |
| 5 | Read | [How a MOSFET works](guide/a-mosfet-is-a-valve.md) · [The four regions](guide/four-regions-not-three.md) · [Where saturation starts](guide/where-saturation-starts.md) | 1.5 h |
| 6 | Do | [Lab 03: MOSFET regions](labs/lab-03-mosfet-regions-overview.md). Find the four regions on your own NMOS curves, extract its threshold two ways, and add a curve to the SPICE deck. | 2.25 h |
| 7 | Read | [What moves the threshold](guide/threshold-is-not-a-constant.md) · [Transconductance and output resistance](guide/gm-and-ro.md) · [Sizing with W and L](guide/w-and-l-are-a-choice.md) | 1.5 h |
| 8 | Do | [Lab 04: Testing the W/L rule](labs/lab-04-wl-knob-overview.md). Predict six currents from $W/L$, then measure where the rule holds and where it breaks. | 2 h |
| 9 | Read | [The CMOS inverter](guide/the-inverter-is-an-amplifier.md) · [The current mirror](guide/the-current-mirror.md) | 1 h |
| 10 | Do | [Capstone: The CMOS inverter](labs/capstone-inverter-overview.md). Draw and size your own inverter, time it, run it as an amplifier, and measure a current mirror. | 2.5 h |

The times are estimates. Your first lab will probably take longest, because you are learning
XSchem at the same time.

Keep these open while you work: [XSchem cheat sheet](reference/xschem-cheatsheet.md) ·
[The ngspice survival card](reference/ngspice-errors.md) ·
[Reading a SKY130 device model](reference/sky130-device-guide.md)

**Stuck?** Ask in the [team Discord](https://discord.gg/hrJnP5UsGz). Nobody expects you to work
this out alone at 2 a.m. See [Getting help](guide/getting-started.md#getting-help) for what to
include in your question.

## The workbench

This course is pinned to the workbench image **`hpretl/iic-osic-tools:2026.08`**, which ships
**XSchem 3.4.8RC** and **ngspice-47**, and Lab 01 has you check both versions.

> **Warning:** the image's default PDK is not SKY130. If you launch XSchem without changing it,
> you get IHP's 130 nm process instead, which has none of the symbols this course uses, and
> XSchem gives you no error message. [Getting started](guide/getting-started.md) explains what to look for, and Lab 01
> has you check it.

The warning applies when you start XSchem yourself. The lab `make` targets don't depend on the
PDK setting, because every lab package pins its own PDK and model paths. Even if Lab 01, Part 1 can't load the course
environment for you, `make` in a lab folder still runs to completion in a bare container, and each
lab ends in `PASS` or `FAIL` with a reason.

## What this course is about

AD101 taught you to read a signal. AD102 taught you that a resistor is a doped strip of silicon
whose value is set by its shape. In both, doubling the input doubled the output.

The diode and the MOSFET don't behave that way, and most of what makes a chip work depends on
that: a transistor is useful because its response bends. When you amplify with it, the bend
gives you gain, and when you switch with it, the bend gives you on and off. If you push it too
far either way, the same bend becomes distortion.

The algebra from AD102 can't solve these circuits, so in this course you learn to ask a
simulator instead, and to know enough to spot a wrong answer when it gives you one.

## What you'll learn

1. Draw a schematic in XSchem from an empty canvas, and read the SPICE netlist it writes
2. Sweep a real SKY130 diode and measure how far it is from the textbook's **60 mV per decade**
3. Map the **four regions** of a MOSFET, including the one most textbooks skip
4. Extract a threshold voltage from your own curve two different ways, and explain why the two
   answers differ by 86 mV
5. Find out what $W$ and $L$ buy you, and where the $W/L$ rule breaks: five devices with
   identical $W/L$ carry five different currents
6. Build a **CMOS inverter** from two transistors, measure the voltage at which it switches, and
   see that sizing it for equal delay and sizing it for a centred threshold give different
   answers

By the end you'll have a schematic you drew, a set of measured device curves you can defend,
and a habit the rest of the analog track depends on: predict the number, run the simulation,
and work out which of the two was wrong.

## Next courses

- **[AD104](https://uoftasic.com/ad104/)** — Layout: you draw those transistors as geometry in Magic, and make them pass DRC and LVS
- **AD201** — Analog Signal Processing · **AD202** — Mixed Signal
