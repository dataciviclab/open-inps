TOOLKIT = toolkit

DATASETS := $(shell find datasets -name dataset.yml 2>/dev/null | sort)

.PHONY: check run run-all clean extract help

check:
	@for f in $(DATASETS); do \
		echo "-> $$f"; \
		TOOLKIT_ALLOW_SCRIPT_SOURCE=1 $(TOOLKIT) run preflight --config "$$f" > /dev/null 2>&1 || exit 1; \
	done
	@echo "All configs valid"

run:
	@for f in $(DATASETS); do \
		echo "=== $$f ==="; \
		TOOLKIT_ALLOW_SCRIPT_SOURCE=1 $(TOOLKIT) run --config "$$f" || exit 1; \
	done

run-all: run

extract:
	python3 datasets/inps-pensioni-vigenti/extract.py out/raw_vigenti.csv
	python3 datasets/inps-pensioni-liquidate/extract.py out/raw_liquidate.csv

clean:
	rm -rf out/

help:
	@grep -E '^[a-zA-Z_-]+:' Makefile | sort
