# AD103 -- survival-card decks
# The five decks printed on docs/reference/ngspice-errors.md. Every number on
# that page comes out of this directory, so the page cannot drift away from
# what ngspice actually does.
#
# Runs in a bare hpretl/iic-osic-tools:2026.08 container with no environment
# setup: PDK_ROOT is already /foss/pdks inside the image and this file pins it
# anyway. About 14 seconds for all five.
#
#   make          run all five decks and print a verdict
#   make dc       .dc   -- sweep a source
#   make tran     .tran -- the time domain
#   make ac       .ac   -- the frequency domain
#   make parts    the R and the C on their own, so the arithmetic can close
#   make clean    delete results/

export PDK_ROOT ?= /foss/pdks

NGSPICE ?= ngspice
PYTHON  ?= python3

DECKS := dc_id_vgs dc_family tran_rc ac_rc rc_parts
LOGS  := $(addprefix results/,$(addsuffix .log,$(DECKS)))

.PHONY: all dc tran ac parts check clean

all: check

results:
	@mkdir -p results

results/%.log: spice/%.spice | results
	@echo "== $<"
	@$(NGSPICE) -b $< </dev/null > $@ 2>&1 || true
	@grep -E "^(id_|vg_|tau|vfinal|f3db|r|cmim)\s*=|No\. of Data Rows" $@ | sed 's/^/   /'

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
