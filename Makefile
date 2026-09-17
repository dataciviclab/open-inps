# DataCivicLab — Open INPS
# Dati INPS: pensioni, lavoro, CIG, NASpI
TOOLKIT = toolkit

DATASETS := $(shell find datasets -name dataset.yml 2>/dev/null | sort)

.PHONY: check run run-all clean registry registry-write extract help

check:
	@for f in $(DATASETS); do \
		echo "-> $$f"; \
		TOOLKIT_ALLOW_SCRIPT_SOURCE=1 $(TOOLKIT) run preflight --config "$$f" > /dev/null 2>&1 || exit 1; \
	done
	@echo "✅ All configs valid"

run:
	@for f in $(DATASETS); do \
		echo "=== $$f ==="; \
		TOOLKIT_ALLOW_SCRIPT_SOURCE=1 $(TOOLKIT) run --config "$$f" || exit 1; \
	done

run-all: run

registry:
	TOOLKIT_ALLOW_SCRIPT_SOURCE=1 $(TOOLKIT) registry build --prefix open_inps

registry-write:
	TOOLKIT_ALLOW_SCRIPT_SOURCE=1 $(TOOLKIT) registry build --prefix open_inps --write

clean:
	rm -rf out/data/_runs out/data/probe out/data/raw out/data/clean out/data/mart .tmp/

clean-runs:
	rm -rf out/data/_runs/

extract:
	@for f in $(DATASETS); do \
		dir=$$(dirname "$$f"); \
		if [ -f "$$dir/extract.py" ]; then \
			echo "=== $$dir ==="; \
			python3 "$$dir/extract.py" "out/raw_$$(basename $$dir).csv" || exit 1; \
		fi; \
	done

help:
	@grep -E '^[a-zA-Z_-]+:' Makefile | sort
