# AD103 -- survival-card decks
# The six decks printed on docs/reference/ngspice-errors.md. Every number those
# decks print on that page is checked against this directory, so the page
# cannot drift away from what ngspice actually does.
#
# Runs in a bare hpretl/iic-osic-tools:2026.08 container with no environment
# setup: PDK_ROOT is already /foss/pdks inside the image and this file pins it
# anyway. About a minute for all six, nearly all of it loading the models.
#
#   make          run all six decks and print a verdict
#   make op       .op   -- one bias point, and the small-signal parameters
#   make dc       .dc   -- sweep a source
#   make tran     .tran -- the time domain
#   make ac       .ac   -- the frequency domain
#   make parts    the R and the C on their own, so the arithmetic can close
#   make clean    delete results/

export PDK_ROOT ?= /foss/pdks

NGSPICE ?= ngspice
PYTHON  ?= python3

DECKS := op_nmos dc_id_vgs dc_family tran_rc ac_rc rc_parts
LOGS  := $(addprefix results/,$(addsuffix .log,$(DECKS)))

.PHONY: all op dc tran ac parts check clean

all: check

results:
	@mkdir -p results

results/%.log: spice/%.spice | results
	@echo "== $<"
	@$(NGSPICE) -b $< </dev/null > $@ 2>&1 || true
	@grep -E "^(id_\w+|vg_\w+|id\[[0-9]+\]|tau|vfinal|f3db|r|cmim|i\(vds\))\s*=|^@m\.|No\. of Data Rows" $@ | sed 's/^/   /'

op:    results/op_nmos.log
dc:    results/dc_id_vgs.log results/dc_family.log
tran:  results/tran_rc.log
ac:    results/ac_rc.log
parts: results/rc_parts.log

check: $(LOGS)
	@echo
	@$(PYTHON) src/check.py

clean:
	@rm -f results/*.log
	@echo "cleaned"
