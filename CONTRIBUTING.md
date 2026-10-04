# Contributing — Open INPS

## Setup

```bash
pip install -e ".[dev,pipeline,dashboard]"
```

Le dipendenze vivono in `pyproject.toml` (standard Lab). `dashboard/requirements.txt`
è solo export pin per Streamlit Cloud.

## Pipeline

```bash
make check          # preflight su tutti i dataset.yml + compose
make run            # dataset singoli
make compose        # compose inps-analisi (dopo make run)
make run-all        # run + compose (come CI post-merge)
make test           # pytest
make dashboard      # Streamlit (richiede extra dashboard)
make registry-write # scrivi registry.json
make clean          # pulisci output
```

## Aggiungere un dataset

1. Crea `datasets/<slug>/dataset.yml`
2. Crea `datasets/<slug>/extract.py` (usa `scripts/common.py` per l'API INPS)
3. Aggiungi `datasets/<slug>/sql/clean.sql` e `sql/mart_*.sql`
4. Esegui `TOOLKIT_ALLOW_SCRIPT_SOURCE=1 toolkit run --config datasets/<slug>/dataset.yml`
5. Verifica con `make check` e `make test`
6. Se il dataset entra nel compose: aggiungilo in `compose/inps-analisi/dataset.yml` (support + clean.sql)
7. Aggiorna `registry/registry.json` (`make registry-write`) e il README

## Regole

- Segui gli standard del Lab: `infra/lab-ops/standards/`
- `clean.sql` legge solo da `raw_input` (e `read_parquet` dei support nel compose)
- `mart*.sql` legge solo da `clean_input`
- Ogni `mart*.sql` produce **1 tabella** dichiarata in `mart.tables`
- Numeri italiani: `remove_dot_thousands()` / `normalize_italian_number()` — se `read.decimal=','` è già parsato da DuckDB, usa `CAST AS DOUBLE` (contratto toolkit)
- Le selections API usano i **field id** della struttura (es. `anno`, `sesso`, `COD_NACE_REV2`), non le label display
- Non committare output (`out/`, `*.parquet`, `*.csv` generati)
- Ogni nuovo dataset documenta limiti/definizioni nel README se le metriche non sono additive

## CI

- `check.yml` (PR + push main): pytest + preflight su `datasets/` e `compose/`
- `pipeline.yml` (merge PR, schedule, dispatch): `make run-all` con detect su `datasets compose`
