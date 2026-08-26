v {xschem version=3.4.8 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {*** DRAW YOUR FIRST TRANSISTOR HERE ***} -900 -240 0 0 0.45 0.45 {layer=5}
T {Two voltage sources, two named nets and a ground are already
placed.  Do not rename the nets - src/check_mine.py wants
exactly these two:

    g   the gate net, driven by Vgs at 1.8 V
    d   the drain net, driven by Vds at 1.8 V

Add ONE transistor:

    Shift-I  ->  sky130A  ->  sky130_fd_pr
             ->  Search box:  nfet_01v8*.sym
             ->  nfet_01v8.sym, OK, click to drop it

Press q on it and set     W=2     L=0.15
PLAIN MICRONS - W=2u means two METRES.

Then wire four pins.  Every pin except the gate is on the
RIGHT edge of the symbol: drain, body, source, top to bottom.

    gate -> g      drain -> d
    source -> ground      body -> ground

Shift-W snaps a wire to the nearest pin.  Space while drawing
straightens a diagonal one.

Ctrl-S, then in the lab folder:      make mine} -900 -190 0 0 0.28 0.28 {}
T {put the NMOS here} 50 -145 0 0 0.3 0.3 {layer=5}
T {source and body
both go to ground} 50 95 0 0 0.28 0.28 {layer=5}
N -150 0 -80 0 { lab=g}
N 100 -80 20 -80 { lab=d}
C {devices/lab_pin.sym} -150 0 0 0 {name=l_g lab=g}
C {devices/lab_pin.sym} 100 -80 0 0 {name=l_d lab=d}
C {devices/gnd.sym} 20 130 0 0 {name=g3 lab=0}
C {devices/vsource.sym} -420 -30 0 0 {name=Vgs value=1.8}
C {devices/lab_pin.sym} -420 -60 0 0 {name=l_g2 lab=g}
C {devices/gnd.sym} -420 0 0 0 {name=g1 lab=0}
C {devices/vsource.sym} -320 -30 0 0 {name=Vds value=1.8}
C {devices/lab_pin.sym} -320 -60 0 0 {name=l_d2 lab=d}
C {devices/gnd.sym} -320 0 0 0 {name=g2 lab=0}
