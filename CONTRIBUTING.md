# Contributing — Open INPS

## Setup

```bash
pip install -e ".[dev,pipeline,dashboard]"
```

Le dipendenze vivono in `pyproject.toml` (standard Lab). `dashboard/requirements.txt`
è solo export pin per Streamlit Cloud.

## Pipeline

```bash
make check    # valida config
make run      # esegui tutti i dataset
make clean    # pulisci output
make registry # genera registry.json
```

## Aggiungere un dataset

1. Crea `datasets/<slug>/dataset.yml`
2. Aggiungi `scripts/extract_<slug>.py` (usa `scripts/common.py`)
3. Aggiungi `sql/clean.sql` e `sql/mart_*.sql`
4. Esegui `make run` e verifica
5. Aggiorna `registry.json`

## Regole

- Segui gli standard del Lab: `analysis/lab-ops/standards/`
- `clean.sql` legge solo da `raw_input`
- `mart*.sql` legge solo da `clean_input`
- Ogni `mart*.sql` produce **1 tabella** dichiarata in `mart.tables`
- Numeri italiani: usa `remove_dot_thousands()` o `normalize_italian_number()`
- Non committare output (`out/`, `*.parquet`, `*.csv` generati)
