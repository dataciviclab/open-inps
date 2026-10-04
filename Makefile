# CLI toolkit del Lab. La memoria DuckDB è controllata da safe_connect
# (lab-connectors) via env DUCKDB_MEMORY_LIMIT (default 2GB); nei runner CI
# con RAM ridotta il pipeline imposta limiti conservativi.
TOOLKIT = toolkit

DATASETS := $(shell find datasets -name dataset.yml 2>/dev/null | sort)
COMPOSE  := $(shell find compose -name dataset.yml 2>/dev/null | sort)

# --- Compose (eseguire dopo i dataset singoli) ------------------------------

.PHONY: compose
compose:
	@for f in $(COMPOSE); do \
		echo "=== $$f ==="; \
		TOOLKIT_ALLOW_SCRIPT_SOURCE=1 $(TOOLKIT) run --config "$$f" || exit 1; \
	done

# --- Dataset principali ------------------------------------------------------

.PHONY: run
run:
	@for f in $(DATASETS); do \
		echo "=== $$f ==="; \
		TOOLKIT_ALLOW_SCRIPT_SOURCE=1 $(TOOLKIT) run --config "$$f" || exit 1; \
	done

# CI post-merge e dispatch: dataset + compose (come pipeline.yml)
.PHONY: run-all
run-all: run compose

# Alias documentato in README/CONTRIBUTING
.PHONY: all
all: run-all test

# --- Validazione config -------------------------------------------------------

.PHONY: check
check:
	@for f in $(DATASETS) $(COMPOSE); do \
		echo "-> $$f"; \
		TOOLKIT_ALLOW_SCRIPT_SOURCE=1 $(TOOLKIT) run preflight --config "$$f" > /dev/null 2>&1 || exit 1; \
	done
	@echo "✅ All configs valid"

# --- Pulizia -----------------------------------------------------------------

.PHONY: clean
clean:
	rm -rf out/data/_runs out/data/probe out/data/raw out/data/clean out/data/mart out/data/cross .tmp/

.PHONY: clean-runs
clean-runs:
	rm -rf out/data/_runs/

# --- Registry (artifact catalogo — dry-run di default) -----------------------

.PHONY: registry registry-write
registry:
	TOOLKIT_ALLOW_SCRIPT_SOURCE=1 $(TOOLKIT) registry build --prefix open-inps

registry-write:
	TOOLKIT_ALLOW_SCRIPT_SOURCE=1 $(TOOLKIT) registry build --prefix open-inps --write

# --- Test --------------------------------------------------------------------

.PHONY: test
test:
	pytest tests/ -v

# --- Dashboard ---------------------------------------------------------------
# Richiede: pip install -e ".[dashboard]"

.PHONY: dashboard
dashboard:
	cd dashboard && streamlit run app.py --server.headless=true

# --- Help --------------------------------------------------------------------

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:' Makefile | sort
