# AD103 Lab 02 - the diode's I-V curve
#
# Runs in a bare hpretl/iic-osic-tools:2026.04 container with no environment
# setup. PDK_ROOT is already /foss/pdks inside the image, and this file pins it
# anyway, so nothing here depends on PDK, .designinit, or which directory you
# started in.
#
#   make            sweep, additivity test, plots, verdict   (about 6 s)
#   make sweep      just the DC sweep
#   make plots      just the plots (needs results/diode_iv.txt)
#   make area       what junction area buys you, and three silent unit traps
#   make floor      what the flat reverse line on the log plot really is
#   make op         a resistor and a diode in series: the operating point
#   make broken     feed the checker a deliberately wrong sweep
#   make clean      delete everything under results/
#
# Every deck loads sky130.lib.spice.tt.red, the pre-flattened typical corner:
# same numbers as sky130.lib.spice, about 30x faster to read. See getting-started section 12.

export PDK_ROOT ?= /foss/pdks

NGSPICE ?= ngspice
PYTHON  ?= python3

R := results

.PHONY: all sweep line plots check area floor op broken clean

all: check

$(R)/diode_iv.txt: spice/diode_iv.spice
	@mkdir -p $(R)
	@echo "== DC sweep: 1901 points, -1.000 V to +0.900 V"
	@echo "   (about 2 s, model library included)"
	@$(NGSPICE) -b spice/diode_iv.spice </dev/null > $(R)/diode_iv.log 2>&1 || true
	@echo "   wrote $(R)/diode_iv.txt"

sweep: $(R)/diode_iv.txt

$(R)/straight_line.log: spice/straight_line.spice
	@mkdir -p $(R)
	@echo "== additivity test: a resistor and a diode, driven three ways"
	@$(NGSPICE) -b spice/straight_line.spice </dev/null > $(R)/straight_line.log 2>&1 || true
	@sed -n '/--- 100 kohm/,/Note:/p' $(R)/straight_line.log | grep -v '^Note:'

# 'make line' is the entry point the guide page 'The straight line runs out' names,
# so it has to print the block EVERY time - not only on the run that happens to
# build the log. Without the rm, a second 'make line' says 'Nothing to be done'.
line:
	@rm -f $(R)/straight_line.log
	@$(MAKE) --no-print-directory $(R)/straight_line.log

plots: $(R)/diode_iv.txt
	@echo "== plots"
	@$(PYTHON) src/plot_iv.py

check: $(R)/diode_iv.txt $(R)/straight_line.log plots
	@echo "== checking"
	@$(PYTHON) src/check.py

area:
	@mkdir -p $(R)
	@echo "== junction area, and three lines that all claim to be 1 um^2"
	@$(NGSPICE) -b spice/diode_area.spice </dev/null > $(R)/diode_area.log 2>&1 || true
	@sed -n '/--- Part 1/,/Note:/p' $(R)/diode_area.log | grep -v '^Note:'
	@echo "ngspice printed no error for any of the four lines in Part 2."
	@echo "Compare them yourself:   grep -n '^X' spice/diode_area.spice"

floor:
	@mkdir -p $(R)
	@echo "== the reverse current, measured twice with two different GMIN"
	@$(NGSPICE) -b spice/reverse_floor.spice </dev/null > $(R)/reverse_floor.log 2>&1 || true
	@sed -n '/--- default GMIN/,/Note:/p' $(R)/reverse_floor.log | grep -v '^Note:'

op: $(R)/load_line.log
	@sed -n '/--- diode voltage/,/Note:/p' $(R)/load_line.log | grep -v '^Note:'

$(R)/load_line.log: spice/load_line.spice
	@mkdir -p $(R)
	@echo "== one resistor and one diode in series, three times"
	@$(NGSPICE) -b spice/load_line.spice </dev/null > $(R)/load_line.log 2>&1 || true

broken: $(R)/diode_iv.txt
	@mkdir -p $(R)
	@echo "== feeding the checker a sweep that is 5 % off, on purpose"
	@$(PYTHON) src/bend_it.py
	@echo
	@$(PYTHON) src/check.py --data $(R)/diode_iv_bent.txt || true
	@echo
	@echo "That FAIL is the one you caused. Read it, then run 'make' again."

clean:
	@rm -f $(R)/*.txt $(R)/*.log $(R)/*.png
	@echo "cleaned"
