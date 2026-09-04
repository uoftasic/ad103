v {xschem version=3.4.8 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {AD103 capstone  -  the CMOS inverter} -420 -320 0 0 0.5 0.5 {}
T {One PMOS pulling up, one NMOS pulling down,
gates tied together.  Both W = 1 um, L = 0.15 um.
The same circuit as spice/vtc.spice, drawn.

Press "Netlist & Simulate", then run
  python3 src/check.py
in the lab folder.  It should still say PASS.} -420 -285 0 0 0.3 0.3 {}
T {source AND body
both go to vdd} 95 -220 0 0 0.28 0.28 {layer=5}
T {source AND body
both go to ground} 95 120 0 0 0.28 0.28 {layer=5}
T {the two drains meet here:
that net is the output} 115 -55 0 0 0.28 0.28 {layer=5}
T {W and L are PLAIN MICRONS.
W=1 means one micrometre.
Never W=1u.} -420 60 0 0 0.3 0.3 {layer=5}
N 20 -230 20 -190 { lab=vdd}
N 20 -160 60 -160 { lab=vdd}
N 60 -190 60 -160 { lab=vdd}
N 20 -190 60 -190 { lab=vdd}
N 20 -130 20 -30 { lab=out}
N 20 -30 20 70 { lab=out}
N 20 -30 100 -30 { lab=out}
N 20 100 60 100 { lab=0}
N 60 100 60 130 { lab=0}
N 20 130 60 130 { lab=0}
N 20 130 20 170 { lab=0}
N -20 -160 -80 -160 { lab=in}
N -80 -160 -80 -30 { lab=in}
N -80 -30 -80 100 { lab=in}
N -20 100 -80 100 { lab=in}
N -80 -30 -150 -30 { lab=in}
C {sky130_fd_pr/pfet_01v8.sym} 0 -160 0 0 {name=MP
W=1
L=0.15
nf=1
mult=1
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 0 100 0 0 {name=MN
W=1
L=0.15
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
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
C {devices/code_shown.sym} -420 215 0 0 {name=MODELS only_toplevel=true value=".lib $PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice tt"}
C {devices/code_shown.sym} -420 280 0 0 {name=CONTROL only_toplevel=true value="
.control
dc Vin 0 1.8 0.001
let idd = -i(Vdd)
wrdata ../../results/vtc.txt v(out) idd
.endc
"}
C {devices/launcher.sym} -420 160 0 0 {name=h1 descr="Netlist & Simulate"
tclcommand="xschem save; xschem netlist; xschem simulate"}
