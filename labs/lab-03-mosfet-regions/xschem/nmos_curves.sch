v {xschem version=3.4.8 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {AD103 Lab 03  -  MOSFET curve tracer} -180 -230 0 0 0.5 0.5 {}
T {One nfet_01v8, W = 5 um, L = 1 um.  Vds sweeps 0 -> 1.8 V, five times,
once per gate voltage.  Same circuit as spice/id_vds.spice, drawn.

Netlist & Simulate, then run  python3 src/check.py  in the lab folder:
it should still say PASS.  Your schematic and the shipped deck agree.} -180 -195 0 0 0.3 0.3 {}
T {W and L are PLAIN MICRONS.
W=5 means five micrometres.
Never W=5u.} 200 -60 0 0 0.3 0.3 {layer=5}
N -20 0 -160 0 { lab=g}
N 20 -80 20 -30 { lab=d}
N 20 -80 140 -80 { lab=d}
N 20 30 20 80 { lab=0}
N 20 0 60 0 { lab=0}
N 60 0 60 80 { lab=0}
N 20 80 60 80 { lab=0}
N 20 80 20 110 { lab=0}
N -160 60 -160 90 { lab=0}
N 140 -20 140 20 { lab=0}
C {sky130_fd_pr/nfet_01v8.sym} 0 0 0 0 {name=M1
W=5
L=1
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {devices/lab_pin.sym} -80 0 0 0 {name=l_g lab=g}
C {devices/lab_pin.sym} 80 -80 0 0 {name=l_d lab=d}
C {devices/vsource.sym} -160 30 0 0 {name=Vgs value=0}
C {devices/gnd.sym} -160 90 0 0 {name=g1 lab=0}
C {devices/vsource.sym} 140 -50 0 0 {name=Vds value=0}
C {devices/gnd.sym} 140 20 0 0 {name=g2 lab=0}
C {devices/gnd.sym} 20 110 0 0 {name=g3 lab=0}
C {devices/code_shown.sym} -180 185 0 0 {name=MODELS only_toplevel=true value=".lib $PDK_ROOT/sky130A/libs.tech/ngspice/sky130.lib.spice.tt.red tt"}
C {devices/code_shown.sym} -180 250 0 0 {name=CONTROL only_toplevel=true value="
.control
foreach vg 0.6 0.9 1.2 1.5 1.8
  alter Vgs = $vg
  dc Vds 0 1.8 0.01
end
setplot dc1
let id_vgs06 = -dc1.i(vds)
let id_vgs09 = -dc2.i(vds)
let id_vgs12 = -dc3.i(vds)
let id_vgs15 = -dc4.i(vds)
let id_vgs18 = -dc5.i(vds)
wrdata ../../results/id_vds.txt id_vgs06 id_vgs09 id_vgs12 id_vgs15 id_vgs18
.endc
"}
C {devices/launcher.sym} -180 110 0 0 {name=h1 descr="Netlist & Simulate"
tclcommand="xschem save; xschem netlist; xschem simulate"}
