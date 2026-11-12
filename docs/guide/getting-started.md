# Getting started

AD103's main tool is **XSchem**, a schematic editor. You draw a circuit, XSchem writes the SPICE
netlist, and ngspice simulates it:

$$\text{schematic} \;\longrightarrow\; \text{netlist} \;\longrightarrow\; \text{ngspice}
\;\longrightarrow\; \text{a number}$$

You have almost certainly never used XSchem. This page explains how it fits together and the
handful of traps that cost new users the most time. Nothing here installs anything: AD103 needs
one Docker image and a browser, and you already have both from
[IC101](https://uoftasic.com/ic101/). You'll set up and draw your first schematic in
[Lab 01](labs/lab-01-first-schematic-overview.md).

## The PDK setting

The workbench image can simulate more than one process. The environment variable `PDK` picks
which one, and the image's default is `ihp-sg13g2`, a real 130 nm process from IHP in Germany.
AD103 uses **SKY130** for everything.

This matters more in AD103 than anywhere else in the curriculum, because **XSchem reads `$PDK`
at launch to decide which device library to load**, and it does not tell you which one it
picked. If you launch it with the default, you get a healthy-looking editor showing this:

![XSchem started with the image's default PDK — note IHP in the menu bar](../assets/img/xschem-wrong-pdk.png)

*The menu bar says **IHP**. The tab says `start_page.sch`. The page offers to load "IHP SG13G2
spice models". There is no error and no warning.*

Every `sky130_fd_pr/...` symbol this course names will be missing. If you draw anyway, the
netlist says `IS MISSING !!!!` next to your transistor, and XSchem still exits successfully.

The fix is a setup script from the workspace repo, `/foss/designs/common/.designinit`, which sets
`PDK=sky130A`. You load it with a leading `.`, which is the shell's `source` command: it runs the
file in your current shell, and that is the only way a script can change your environment.
Because it changes only the current shell, you have to load it again in every new terminal.

The check takes two seconds: `echo $PDK` should print `sky130A`, and XSchem's menu bar should
say **SKY130**. Lab 01, Part 1 has you do it.

## Where XSchem starts

XSchem reads a settings file called `xschemrc` from the directory you launch it in. Each AD103
lab has one in its `xschem/` folder. It makes the SKY130 symbols resolve and puts your netlists
somewhere you can find them. Three habits follow from that:

- **Launch XSchem from a terminal, not from a desktop icon.** Some of its messages go to the
  terminal it was started from. Started from a menu, those messages go nowhere, and the program
  seems to silently do nothing.
- **Launch it from the directory your schematics are in**, so it reads that directory's
  `xschemrc`. If symbols vanish after working yesterday, you probably started it somewhere else.
- **Name the file you want to open**, as in `xschem nmos_probe.sch &`. With no filename, XSchem
  opens whatever its settings call the start page.

### The PDK start page

Every AD103 lab sets the start page to a blank `untitled.sch` in the lab directory, so inside a
lab folder a bare `xschem &` is harmless. Anywhere else, such as a scratch folder of your own
with no `xschemrc`, you get the SKY130 PDK's own start page:

![The SKY130 start page XSchem opens on when no filename is given](../assets/img/xschem-start-page.png)

*The menu bar reads **SKY130**. The canvas is a live schematic: those NFET, PFET, RES, MIM and
VARACTOR rows are real symbols. It looks exactly like a page you could work on, but you can't.*

That page is a real file at `/foss/pdks/sky130A/libs.tech/xschem/sky130_tests/top.sch`, inside
the PDK, which is read-only. Two things go wrong there, and neither explains itself:

- `Ctrl-S` cannot write the file. XSchem asks `save file?`, you say **Yes**, and it answers with
  a box reading **`file opening for write failed!`**. The tab still shows its `*` and the file
  on disk is untouched. Nothing appears in the terminal.
- **Netlist** writes the netlist next to the schematic, so it tries to create a `simulation/`
  folder inside the PDK and stops with this box:

![XSchem's error box: can't create directory "/foss/pdks/sky130A/libs.tech/xschem/sky130_tests/simulation": permission denied](../assets/img/xschem-netlist-permission-denied.png)

```
can't create directory
"/foss/pdks/sky130A/libs.tech/xschem/sky130_tests/simulation": permission denied
```

Nothing is wrong with your install, your PDK or your drawing. You are in a read-only folder.
Open a schematic that lives in your own directory and the error goes away. If you have already
drawn something there, **File → Save as** into your own folder rescues it.

## `W=1`, never `W=1u`

On a SKY130 transistor, **`W` and `L` are plain micron numbers with no unit suffix.** `W=1`
means one micrometre. This is the most common mistake anyone makes with SKY130, and nearly
everyone makes it at least once.

Everywhere else in SPICE you would write `1u` for a micron, so `W=1u` looks right. But the
SKY130 models already treat the number as microns, so `W=1u` becomes a millionth of a micron.
XSchem accepts it without a murmur and writes this device line:

```
XM1 d g 0 0 sky130_fd_pr__nfet_01v8 L=0.15u W=1u nf=1 ad=2.9e-07 as=2.9e-07 pd=0.580002 ps=0.580002 nrd=290000 nrs=290000 sa=0 sb=0
+ sd=0 mult=1
```

The symbol computes the diffusion areas and resistances from `W`, so the `u` spreads: `nrd` went
from `0.29` to `290000` and `ad` from `0.29` to `2.9e-07`. Two characters changed six more
numbers, and XSchem reported none of it.

ngspice is the one that objects:

```
could not find a valid modelname
    Simulation interrupted due to error!

Error: incomplete or empty netlist
       or no ".plot", ".print", or ".fourier" lines in batch mode;
no simulations run!
```

**`could not find a valid modelname` almost always means a unit suffix on `W` or `L`.** The
SKY130 models are **binned**: each `.model` card covers a range of widths and lengths, and a
device has to fall inside one of those ranges. A width of a millionth of a micron falls outside
every bin, so no model matches and ngspice stops. The message names neither `W` nor units, which
is why the habit to build is "check `W` and `L` first" rather than "read the error".
[Reading a SKY130 device model](reference/sky130-device-guide.md) has the full explanation.

You'll cause this error on purpose in Lab 01, Part 6, so you recognise it later.

## How wires connect

A wire in XSchem connects only where one of its **endpoints** lands on a pin or on another wire.
Two wires that cross do not connect. XSchem draws a small solid dot at a real junction and draws
nothing where two wires pass over each other:

![Two pairs of XSchem wires side by side: on the left they cross with nothing drawn at the crossing, on the right they meet at a small solid dot](../assets/img/xschem-wire-junction.png)

*The same picture twice. On the left, one wire runs over another and XSchem draws nothing at the
crossing: two separate nets that happen to overlap on screen. On the right, four wire ends land
on the same grid point and XSchem draws the dot: one net. The dot is the only difference, and
it is a few pixels wide, so zoom in on every junction before you netlist.*

Every click lands on the snap grid. A wire that ends one grid step short of a pin looks
connected at normal zoom and is not.

For long connections you don't draw a wire at all. You **name the net** instead: place a net
label (`lab_pin.sym`) on each end and give both the same name. Two labels with the same name are
the same net, wherever they are on the page. Every supply and ground connection in this course
is made that way.

Here is the reference schematic from Lab 01, the one you'll netlist first:

![nmos_probe.sch: one NMOS, two supplies, two named nets](../assets/img/xschem-nmos-probe.png)

*One `nfet_01v8` with `W=1`, `L=0.15`. `Vgs` drives the gate through a net labelled `g`; `Vds`
drives the drain through `d`. Source and body both go to ground; the filled cyan dot is a real
junction. The status bar reads `SNAP: 10  GRID: 20  MODE: spice`: snap is why your wires land
exactly on pins instead of near them.*

XSchem annotates each device with its size: `nfet_01v8`, `nf=1`, and `1 x 1 / 0.15`, which is
`mult × W / L`. You can check a page of transistors at a glance.

## The netlist

When you click **Netlist**, XSchem writes a SPICE file and says almost nothing about it.

**Where it goes.** By default the netlist lands in `~/.xschem/simulations/`, a folder inside
the container, which is deleted along with the container. Your schematic is on your own disk;
the netlist is not. The setting **Simulation → Use 'simulation' dir in schematic dir** fixes
this: netlists then land in a `simulation/` folder next to the `.sch` file. Each lab's
`xschemrc` turns it on with `set local_netlist_dir 1`. A scratch directory of your own won't
have it.

![The XSchem Simulation menu open, with the radio bullet on "Use 'simulation' dir in schematic dir"](../assets/img/xschem-simulation-menu.png)

*The three netlist-directory entries are radio buttons, and exactly one is on. Here the bullet
is on the middle one, which is what `set local_netlist_dir 1` in a lab's `xschemrc` selects.*

**What it contains.** This is the netlist of `nmos_probe.sch`:

```
** sch_path: /foss/designs/modules/ad103/labs/lab-01-first-schematic/xschem/nmos_probe.sch
**.subckt nmos_probe
XM1 d g 0 0 sky130_fd_pr__nfet_01v8 L=0.15 W=1 nf=1 ad=0.29 as=0.29 pd=2.58 ps=2.58 nrd=0.29 nrs=0.29 sa=0 sb=0 sd=0 mult=1
Vgs g 0 1.8
Vds d 0 1.8
**.ends
.end
```

Your whole drawing is in those seven lines. `XM1 d g 0 0` is the transistor and its four terminals
in order: **drain, gate, source, body**. The names are the labels you placed, and `0` is ground,
which SPICE has always called zero.

There are no models and no analysis command. A netlist is only the circuit. The `.lib` line that
loads the SKY130 models and the `.control` block that says what to measure live in the
testbench, and Lab 02 is where you meet one.

![XSchem showing the generated netlist in its own window, over the schematic it came from](../assets/img/xschem-netlist-window.png)

*With **Simulation → Show netlist after netlist command** (`Shift-A`) ticked, every press of
**Netlist** pops the file up in a window, with the schematic still behind it.*

### Invented net names

Read the four node names on the device line. They should be exactly the nets you labelled. If
the gate wire stops one grid step short of the gate pin, XSchem writes this, with no error, no
warning, and exit status 0:

```
XM1 d net1 0 0 sky130_fd_pr__nfet_01v8 L=0.15 W=1 nf=1 ...
```

`g` became `net1`. XSchem invents a name for every pin that isn't connected to anything, and the
invented names all look like `net` followed by a number. So after every netlist, search for
them with `grep 'net[0-9]' simulation/*.spice`. Any hit is a wire you think is connected and
isn't. This is faster and more reliable than squinting at the canvas, and it finds nine out of
ten wiring mistakes in this course. Lab 01, Part 7 shows you what ngspice does with a circuit
like this.

## Simulation time

Every SPICE deck in this course loads the SKY130 models with this line:

```
.lib $PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice tt
```

`tt` picks the typical corner. Loading the model library is slow: a single-deck run such as
Lab 01's `make` takes about ten seconds, and the terminal stays silent while ngspice reads the
models. That is not a hang, so don't press `Ctrl-C`.

## Getting help

The course is self-paced, but you don't have to work alone.

- **Ask in the [team Discord](https://discord.gg/hrJnP5UsGz).** No question is too basic. Most
  of what looks like your mistake in an EDA tool is the tool being unhelpful, and XSchem in
  particular fails quietly.
- **Quote the exact error, and say where it appeared.** Some of XSchem's messages go to the
  terminal it was launched from, and some, including every one on this page, appear only as a
  box in the window while the terminal stays silent. Paste the text either way, along with the
  command you ran and what `xschem --version` says.
- **Post a screenshot of the schematic.** A wiring problem is obvious in a screenshot and very
  hard to describe in words.
- **If a command on these pages does not do what the page says, that is a bug in the course.**
  Report it. Every command here was run before it was written down and every number was copied
  from a real run, so a mismatch means something has changed, and we want to know.

## Check yourself

Answer these on paper before you start Lab 01.

1. XSchem's menu bar says **IHP**. What is wrong, and what two checks tell you it's fixed?
2. You typed `W=2u` on a transistor. Which tool complains, and with what message?
3. Two wires cross on the canvas with no dot at the crossing. Are they connected?
4. A device line reads `XM1 d net3 0 0 ...`. Which terminal is unconnected?
5. You netlisted a schematic in a folder with no `xschemrc`. Where did the netlist go, and what
   happens to it when the container is removed?

Next: [Lab 01: Your first schematic](labs/lab-01-first-schematic-overview.md).
