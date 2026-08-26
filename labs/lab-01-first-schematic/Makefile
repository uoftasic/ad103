# AD103 Lab 01 - your first schematic
#
# Runs in a bare iic-osic-tools:2026.04 container with no environment setup:
# it pins PDK itself, because the image ships with PDK=ihp-sg13g2 and every
# sky130 symbol and model silently disappears if you leave it that way.
#
#   make                prove the toolchain works, end to end, and print a verdict
#   make mine           netlist YOUR schematic, check it, and simulate it
#   make edit           open your schematic in XSchem
#   make wrong-units    the same circuit with W and L in metres - fails on purpose
#   make unconnected    one wire one grid step short - does NOT fail, which is worse
#   make bins           which model bin your device landed in, and what leff really is
#   make clean          delete generated files

export PDK      := sky130A
export PDK_ROOT ?= /foss/pdks

XSCHEM  ?= xschem
NGSPICE ?= ngspice

SCH      := nmos_probe.sch
NETLIST  := xschem/simulation/nmos_probe.spice
LOG      := results/nmos_op.log

.PHONY: all netlist sim check mine edit wrong-units unconnected bins clean

all: check

netlist: $(NETLIST)

$(NETLIST): xschem/$(SCH) xschem/xschemrc
	@echo "== netlisting xschem/$(SCH)"
	@cd xschem && $(XSCHEM) -n -q -x $(SCH) >/dev/null 2>&1
	@echo "   wrote $(NETLIST)"

sim: $(LOG)

$(LOG): spice/nmos_op.spice
	@mkdir -p results
	@echo "== simulating spice/nmos_op.spice"
	@$(NGSPICE) -b spice/nmos_op.spice </dev/null > $(LOG) 2>&1 || true
	@echo "   wrote $(LOG)"

check: netlist sim
	@echo "== checking"
	@python3 src/check.py

mine:
	@mkdir -p results
	@echo "== netlisting xschem/my_probe.sch"
	@cd xschem && $(XSCHEM) -n -q -x my_probe.sch >/dev/null 2>&1 || true
	@test -f xschem/simulation/my_probe.spice || { \
	  echo "   XSchem wrote no netlist. Is xschem/my_probe.sch saved?"; exit 1; }
	@echo "   wrote xschem/simulation/my_probe.spice"
	@python3 src/check_mine.py

edit:
	@cd xschem && $(XSCHEM) my_probe.sch &

unconnected:
	@mkdir -p results
	@echo "== netlisting xschem/broken_probe.sch  (the gate wire is one grid step short)"
	@cd xschem && $(XSCHEM) -n -q -x broken_probe.sch >/dev/null 2>&1 || true
	@echo
	@echo "   XSchem exit status: 0.  No error, no warning.  Here is the device line:"
	@grep '^XM1' xschem/simulation/broken_probe.spice | sed 's/^/     /'
	@echo
	@echo "   The gate is on 'net1'.  XSchem invents a name like that for every"
	@echo "   pin that touches nothing.  Now watch what ngspice does with it:"
	@echo
	@$(NGSPICE) -b spice/nmos_op_unconnected.spice </dev/null \
	  > results/nmos_op_unconnected.log 2>&1 || true
	@grep -E 'gmin stepping|source stepping|Transient op|i\(vds\)|v\(net1\)' \
	  results/nmos_op_unconnected.log | sed 's/^/     /'
	@echo
	@echo "   It did not stop.  It printed an answer: 73.4593 nA, against the"
	@echo "   501.046 uA the working circuit gives.  Wrong by a factor of 6821,"
	@echo "   with no error message anywhere - only three lines of solver"
	@echo "   grumbling that look exactly like the noise you learn to ignore."
	@echo
	@echo "   The reflex check:   grep 'net[0-9]' xschem/simulation/*.spice"
	@echo "   Any hit is a wire you think is connected and is not."

wrong-units:
	@mkdir -p results
	@echo "== simulating spice/nmos_op_wrong_units.spice  (this is supposed to fail)"
	@$(NGSPICE) -b spice/nmos_op_wrong_units.spice </dev/null \
	  > results/nmos_op_wrong_units.log 2>&1 || true
	@echo
	@sed -n '/Error on line/,$$p' results/nmos_op_wrong_units.log | head -20
	@echo
	@echo "That is the whole trap. Diff the two decks to see what changed:"
	@echo "    diff spice/nmos_op.spice spice/nmos_op_wrong_units.spice"

bins:
	@mkdir -p results
	@echo "== spice/bins.spice   which model bin did L=0.15 W=1 land in?"
	@$(NGSPICE) -b spice/bins.spice </dev/null > results/bins.log 2>/dev/null || true
	@grep -E '^ +model xm1|^ +(toxe|vth0|lmin|wmin|l|w|vth|weff|leff) ' results/bins.log
	@echo
	@echo "   Everything above the second 'model' header is the BIN."
	@echo "   Everything below it is YOUR DEVICE."
	@echo "   Full reading: docs/reference/sky130-device-guide.md"

clean:
	@rm -rf results xschem/simulation
	@echo "cleaned"
