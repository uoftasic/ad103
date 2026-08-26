v {xschem version=3.4.8 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {*** BUILD YOUR INVERTER HERE ***} -900 -300 0 0 0.45 0.45 {layer=5}
T {Everything except the two transistors is drawn and wired
for you: the supply, the input source, ground, and the four
named nets.  Do not rename them - src/check_mine.py looks
for exactly these four:

    vdd   the supply rail, 1.8 V
    in    the input, driven by Vin
    out   where the two drains meet
    0     ground

Add two devices.  Shift-I opens the symbol chooser; click
the sky130A line in the left pane, open sky130_fd_pr, and
put this in the Search box:

    pfet_01v8*.sym        then        nfet_01v8*.sym

Press q on each one and set  W=1  and  L=0.15.
PLAIN MICRONS - never W=1u.  Then wire them:

    PMOS   drain -> out   gate -> in   source -> vdd   body -> vdd
    NMOS   drain -> out   gate -> in   source -> 0     body -> 0

Every pin except the gate is on the RIGHT edge of the
symbol.  The body is the middle one of those three, and it
is the pin everybody forgets.  Use Shift-W rather than w
for a wire that has to land on a pin - it snaps.

Ctrl-S to save.  Then, in the lab folder:    make mine} -900 -258 0 0 0.28 0.28 {}
T {put the PMOS here} 60 -175 0 0 0.3 0.3 {layer=5}
T {put the NMOS here} 60 85 0 0 0.3 0.3 {layer=5}
T {the two drains
meet on this net} 115 -55 0 0 0.28 0.28 {layer=5}
N 20 -230 20 -195 { lab=vdd}
N 20 -30 100 -30 { lab=out}
N 20 135 20 170 { lab=0}
N -80 -30 -150 -30 { lab=in}
C {devices/lab_pin.sym} 20 -230 0 0 {name=l_vdd lab=vdd}
C {devices/lab_pin.sym} 20 170 0 0 {name=l_gnd lab=0}
C {devices/lab_pin.sym} -150 -30 0 0 {name=l_in lab=in}
C {devices/lab_pin.sym} 100 -30 0 0 {name=l_out lab=out}
C {devices/vsource.sym} -300 -30 0 0 {name=Vdd value=1.8}
C {devices/lab_pin.sym} -300 -60 0 0 {name=l_vdd2 lab=vdd}
C {devices/gnd.sym} -300 0 0 0 {name=g1 lab=0}
C {devices/vsource.sym} -400 -30 0 0 {name=Vin value=0}
C {devices/lab_pin.sym} -400 -60 0 0 {name=l_in2 lab=in}
C {devices/gnd.sym} -400 0 0 0 {name=g2 lab=0}
