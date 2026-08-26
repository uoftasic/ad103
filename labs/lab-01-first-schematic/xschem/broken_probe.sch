v {xschem version=3.4.8 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {broken_probe.sch  -  nmos_probe.sch with the gate wire one grid step short.
XSchem netlists it without a word of complaint.} -260 -190 0 0 0.28 0.28 {}
N -40 0 -160 0 { lab=g}
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
W=1
L=0.15
nf=1
mult=1
model=nfet_01v8
spiceprefix=X
}
C {devices/lab_pin.sym} -80 0 0 0 {name=l_g lab=g}
C {devices/lab_pin.sym} 80 -80 0 0 {name=l_d lab=d}
C {devices/vsource.sym} -160 30 0 0 {name=Vgs value=1.8}
C {devices/gnd.sym} -160 90 0 0 {name=g1 lab=0}
C {devices/vsource.sym} 140 -50 0 0 {name=Vds value=1.8}
C {devices/gnd.sym} 140 20 0 0 {name=g2 lab=0}
C {devices/gnd.sym} 20 110 0 0 {name=g3 lab=0}
