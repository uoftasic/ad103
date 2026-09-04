v {xschem version=3.4.8 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {AD103 Lab 02  -  the diode I-V bench} -180 -230 0 0 0.5 0.5 {}
T {One sky130_fd_pr__diode_pw2nd_05v5, area = 1 um^2, perim = 4 um.
Vd sweeps -1 V to +0.9 V.  Same circuit as spice/diode_iv.spice, drawn.

Netlist & Simulate, then run  python3 src/check.py  in the lab folder:
it should still say PASS.  Your schematic and the shipped deck agree.} -180 -195 0 0 0.3 0.3 {}
T {area is in SQUARE MICRONS, perim is in MICRONS.
area=1 perim=4 is a 1 um x 1 um junction.
The symbol ships with area=1e12 perim=4e6 -
a junction one metre square.  Change both.} 260 -40 0 0 0.3 0.3 {layer=5}
N 140 -30 140 -80 { lab=anode}
N -180 -80 140 -80 { lab=anode}
N -180 -80 -180 -30 { lab=anode}
N -180 30 -180 60 { lab=0}
N 140 30 140 80 { lab=0}
C {sky130_fd_pr/diode.sym} 140 0 2 0 {name=D1
model=diode_pw2nd_05v5
area=1
perim=4
spiceprefix=X
}
C {devices/lab_pin.sym} -20 -80 0 0 {name=l_a lab=anode}
C {devices/vsource.sym} -180 0 0 0 {name=Vd value=0}
C {devices/gnd.sym} -180 60 0 0 {name=g1 lab=0}
C {devices/gnd.sym} 140 80 0 0 {name=g2 lab=0}
C {devices/code_shown.sym} -180 130 0 0 {name=MODELS only_toplevel=true value=".lib $PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice tt"}
C {devices/code_shown.sym} -180 195 0 0 {name=CONTROL only_toplevel=true value="
.control
dc Vd -1 0.9 0.001
let id = -i(Vd)
wrdata ../../results/diode_iv.txt id
write diode_tb.raw
.endc
"}
C {devices/launcher.sym} -180 55 0 0 {name=h1 descr="Netlist & Simulate"
tclcommand="xschem save; xschem netlist; xschem simulate"}
