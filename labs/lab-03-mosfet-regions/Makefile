# AD103 Lab 03 - the regions of a MOSFET
#
# Runs in a bare iic-osic-tools:2026.08 container with no environment setup.
# It pins PDK itself, because the image ships with PDK=ihp-sg13g2 and every
# sky130 model silently disappears if you leave it that way.
#
#   make               sweep, extract, plot, and print a verdict
#   make curves        just the four ngspice sweeps
#   make op            just the operating-point parameter dump
#   make vth-l         print the model's vth for nine channel lengths
#   make vth-body      print the model's vth for five source-to-bulk voltages
#   make gm-ro         gm, ro and the gain one transistor can give you
#   make extract       print the parameters pulled out of the sweeps
#   make figures       redraw the six PNGs (plus the channel cross-sections)
#   make netlist       netlist xschem/nmos_curves.sch (the drawn version)
#   make wrong-units   the same circuit with W and L in metres - fails on purpose
#   make clean         delete results/ and xschem/simulation/

export PDK      := sky130A
export PDK_ROOT ?= /foss/pdks

NGSPICE ?= ngspice
PYTHON  ?= python3

SWEEPS  := id_vds id_vgs id_vgs_log wl_sweep
DATA    := $(addprefix results/,$(addsuffix .txt,$(SWEEPS)))
OPLOG   := results/op_params.log

.PHONY: all curves op extract figures check netlist vth-l vth-body gm-ro wrong-units clean

all: check

results:
	@mkdir -p results

results/%.txt: spice/%.spice | results
	@echo "== sweeping $<"
	@cd spice && $(NGSPICE) -b $*.spice </dev/null > ../results/$*.log 2>&1 || true
	@test -s $@ || { echo "   NO DATA - read results/$*.log"; \
	  sed -n '/Error/,$$p' results/$*.log | head -12; exit 1; }
	@echo "   wrote $@"

curves: $(DATA)

op: $(OPLOG)

$(OPLOG): spice/op_params.spice | results
	@echo "== operating point   spice/op_params.spice"
	@$(NGSPICE) -b spice/op_params.spice </dev/null > $(OPLOG) 2>&1 || true
	@echo "   wrote $(OPLOG)"

extract: curves op
	@$(PYTHON) src/extract.py

figures: curves op
	@echo "== drawing figures"
	@$(PYTHON) src/plot_curves.py
	@$(PYTHON) src/channel_picture.py

check: curves op
	@echo "== checking"
	@$(PYTHON) src/check.py

vth-l: | results
	@echo "== spice/vth_vs_l.spice"
	@$(NGSPICE) -b spice/vth_vs_l.spice </dev/null > results/vth_vs_l.log 2>&1 || true
	@echo "   L        model vth"
	@awk '/^L = /{l=$$0; next} /\[vth\]/{split($$0,a,"= "); \
	  printf "   %-10s %s V\n", substr(l,5), a[2]}' results/vth_vs_l.log

netlist:
	@echo "== netlisting xschem/nmos_curves.sch"
	@cd xschem && xschem -n -q -x nmos_curves.sch >/dev/null 2>&1
	@echo "   wrote xschem/simulation/nmos_curves.spice"
	@grep -c 'net[0-9]' xschem/simulation/nmos_curves.spice >/dev/null 2>&1 \
	  && echo "   WARNING: the netlist contains net<N> names - some pin is unconnected" \
	  || echo "   no invented net names - every pin is wired"

vth-body: | results
	@echo "== spice/vth_body.spice"
	@$(NGSPICE) -b spice/vth_body.spice </dev/null > results/vth_body.log 2>&1 || true
	@sed -n '/--- vth and I_D/,$$p' results/vth_body.log \
	  | grep -vE '^$$|Note:|Reference value|Doing analysis|SPARSE|Data Rows'

gm-ro: | results
	@echo "== spice/gm_ro.spice"
	@$(NGSPICE) -b spice/gm_ro.spice </dev/null > results/gm_ro.log 2>&1 || true
	@sed -n '/--- W = 5 um/,$$p' results/gm_ro.log \
	  | grep -vE '^$$|Note:|Reference value|Doing analysis|SPARSE|Data Rows'

wrong-units: | results
	@echo "== simulating spice/id_vds_wrong_units.spice  (this is supposed to fail)"
	@$(NGSPICE) -b spice/id_vds_wrong_units.spice </dev/null \
	  > results/id_vds_wrong_units.log 2>&1 || true
	@echo
	@sed -n '/Error on line/,$$p' results/id_vds_wrong_units.log | head -14
	@echo
	@echo "That is the whole trap. Two characters:"
	@echo "    diff spice/id_vds.spice spice/id_vds_wrong_units.spice"

clean:
	@rm -rf results xschem/simulation
	@mkdir -p results && touch results/.gitkeep
	@echo "cleaned"
