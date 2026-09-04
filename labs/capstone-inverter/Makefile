# AD103 capstone - the CMOS inverter
#
# Runs in a bare hpretl/iic-osic-tools:2026.08 container with no environment
# setup: it pins PDK itself, because the image ships with PDK=ihp-sg13g2 and
# every sky130 model silently disappears if you leave it that way.
#
#   make            run the five decks and print a verdict   (about 13 s)
#   make sweeps     just the ngspice runs
#   make extract    every number this capstone teaches, with its working
#   make figures    redraw the three PNGs
#   make mine       netlist YOUR schematic, simulate it, and check it
#   make edit       open your schematic in XSchem
#   make mirror     the current mirror: what a copied current really costs
#   make broken     what an inverter with both sources on ground does
#   make clean      delete results/ and xschem/simulation/

export PDK      := sky130A
export PDK_ROOT ?= /foss/pdks

NGSPICE ?= ngspice
XSCHEM  ?= xschem
PYTHON  ?= python3

DATA := results/vtc.txt results/vtc_ratio.txt results/vtc_long.txt
LOGS := results/drive.log results/delay.log

.PHONY: all sweeps extract figures check mine edit mirror broken clean

all: check

results:
	@mkdir -p results

results/%.txt: spice/%.spice | results
	@echo "== $<"
	@$(NGSPICE) -b $< </dev/null > results/$*.log 2>&1 || true
	@test -s $@ || { echo "   NO DATA - read results/$*.log"; \
	  sed -n '/^Error on line/,$$p' results/$*.log | head -12; exit 1; }
	@echo "   wrote $@"

results/drive.log: spice/drive.spice | results
	@echo "== $<"
	@$(NGSPICE) -b $< </dev/null > $@ 2>&1 || true
	@echo "   wrote $@"

results/delay.log: spice/delay.spice | results
	@echo "== $<"
	@$(NGSPICE) -b $< </dev/null > $@ 2>&1 || true
	@echo "   wrote $@"

sweeps: $(DATA) $(LOGS)

extract: $(DATA) $(LOGS)
	@$(PYTHON) src/extract.py

figures: $(DATA) $(LOGS)
	@echo "== drawing figures"
	@MPLCONFIGDIR=/tmp $(PYTHON) src/plot_inv.py

check: $(DATA) $(LOGS)
	@echo "== checking"
	@$(PYTHON) src/check.py

# ---------------------------------------------------------------- your turn
mine: | results
	@echo "== netlisting xschem/my_inverter.sch"
	@cd xschem && $(XSCHEM) -n -q -x my_inverter.sch >/dev/null 2>&1 || true
	@test -f xschem/simulation/my_inverter.spice || { \
	  echo "   XSchem wrote no netlist. Is xschem/my_inverter.sch saved?"; exit 1; }
	@echo "   wrote xschem/simulation/my_inverter.spice"
	@$(PYTHON) src/check_mine.py

edit:
	@cd xschem && $(XSCHEM) my_inverter.sch &

mirror: | results
	@echo "== spice/mirror.spice   a 50 uA reference, copied four ways"
	@$(NGSPICE) -b spice/mirror.spice </dev/null > results/mirror.log 2>&1 || true
	@sed -n '/--- part 1/,$$p' results/mirror.log \
	  | grep -vE '^$$|Note:|Doing analysis|SPARSE|Data Rows|Reference value'

broken: | results
	@echo "== an inverter with the PMOS source wired to ground instead of vdd"
	@$(NGSPICE) -b spice/vtc_broken.spice </dev/null > results/vtc_broken.log 2>&1 || true
	@$(PYTHON) src/check.py --vtc results/vtc_broken.txt || true
	@echo
	@echo "That FAIL is the one you caused. Nothing errored, nothing warned,"
	@echo "and ngspice produced 1801 perfectly good rows of a circuit that is"
	@echo "not an inverter. Diff the two decks:"
	@echo "    diff spice/vtc.spice spice/vtc_broken.spice"

clean:
	@rm -rf results xschem/simulation
	@echo "cleaned"
