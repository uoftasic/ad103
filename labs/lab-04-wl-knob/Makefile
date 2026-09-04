# AD103 Lab 04 - W/L is a knob
#
# Runs in a bare hpretl/iic-osic-tools:2026.08 container with no environment
# setup: it pins PDK itself, because the image ships with PDK=ihp-sg13g2 and
# every sky130 model silently disappears if you leave it that way.
#
#   make            run the four sweeps and print a verdict   (about 9 s)
#   make sweeps     just the four ngspice runs
#   make predict    score the predictions you wrote in predictions.txt
#   make extract    every number this lab teaches, with its working
#   make figures    redraw the three PNGs
#   make broken     hand the checker a sweep that is wrong on purpose
#   make clean      delete results/

export PDK      := sky130A
export PDK_ROOT ?= /foss/pdks

NGSPICE ?= ngspice
PYTHON  ?= python3

DECKS := w_ladder l_ladder same_ratio double_w
LOGS  := $(addprefix results/,$(addsuffix .log,$(DECKS)))

.PHONY: all sweeps predict extract figures check broken clean

all: check

results:
	@mkdir -p results

results/%.log: spice/%.spice | results
	@echo "== $<"
	@command -v $(NGSPICE) >/dev/null 2>&1 || { \
	  echo "   FAILED - $(NGSPICE) is not on your PATH."; \
	  echo "   You are running on the host. Open a terminal inside the workbench"; \
	  echo "   container and try again."; \
	  exit 1; }
	@$(NGSPICE) -b $< </dev/null > $@ 2>&1 || true
	@grep -q 'could not find a valid modelname' $@ && { \
	  echo "   FAILED - 'could not find a valid modelname'."; \
	  echo "   That is a unit suffix on W or L. They are plain microns: W=5, not W=5u."; \
	  exit 1; } || true
	@grep -qE '^[^ ]+ *= *[-0-9.]' $@ || { \
	  echo "   FAILED - $@ contains no measurements. ngspice ran but printed"; \
	  echo "   nothing this lab can read. The last few lines of the log were:"; \
	  tail -5 $@ | sed 's/^/     /'; \
	  exit 1; }
	@echo "   wrote $@"

sweeps: $(LOGS)

predict: $(LOGS)
	@$(PYTHON) src/predict.py

extract: $(LOGS)
	@$(PYTHON) src/extract.py

figures: $(LOGS)
	@echo "== drawing figures"
	@MPLCONFIGDIR=/tmp $(PYTHON) src/plot_wl.py

check: $(LOGS)
	@echo "== checking"
	@$(PYTHON) src/check.py

broken: $(LOGS)
	@echo "== handing the checker a W ladder with one number changed"
	@$(PYTHON) src/bend_it.py
	@echo
	@$(PYTHON) src/check.py --w-log results/w_ladder_bent.log || true
	@echo
	@echo "That FAIL is the one you caused. Read what it says about WHICH"
	@echo "number moved and by how much, then run 'make' again."

clean:
	@rm -rf results bsim4v5.out spice/bsim4v5.out
	@echo "cleaned"
