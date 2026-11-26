"""Regressioni semantiche per inps_pensionamento_flussi.

Proteggono due contratti visti rompersi con il refresh INPS del 2026-11-26:
- `eta_media_decorrenza` deve essere numerica (non NULL) anche con
  `read.all_varchar`;
- i mart devono contenere solo il dettaglio, senza la gerarchia di totali
  (trimestre/dimensione/sesso) che la fonte include.

Saltano in CI quando i parquet locali non sono presenti.
"""

from __future__ import annotations

import os

import pytest

try:
    from lab_connectors.duckdb.core import safe_connect

    HAS_DUCKDB = True
except ImportError:
    HAS_DUCKDB = False

REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
CLEAN = os.path.join(
    REPO_ROOT,
    "out",
    "data",
    "clean",
    "inps_pensionamento_flussi",
    "2026",
    "inps_pensionamento_flussi_2026_clean.parquet",
)
MART_DIR = os.path.join(
    REPO_ROOT, "out", "data", "mart", "inps_pensionamento_flussi", "2026"
)
MART_SPECS = {
    "regione": (os.path.join(MART_DIR, "mart_pensionamento_regione.parquet"), "regione"),
    "gestione": (os.path.join(MART_DIR, "mart_pensionamento_gestione.parquet"), "gestione"),
    "categoria": (os.path.join(MART_DIR, "mart_pensionamento_categoria.parquet"), "categoria"),
}
SOMMA_DETTAGLIO = 5_343_223  # 2021-2026, dettaglio (senza totali)

pytestmark = [
    pytest.mark.skipif(not HAS_DUCKDB, reason="duckdb non installato"),
    pytest.mark.skipif(not os.path.isfile(CLEAN), reason="clean locale assente (CI)"),
]


def test_clean_eta_media_non_null() -> None:
    with safe_connect() as con:
        nulli, totale, minima = con.execute(
            f"""
            SELECT
                count(*) FILTER (WHERE eta_media_decorrenza IS NULL),
                count(*),
                min(eta_media_decorrenza)
            FROM read_parquet('{CLEAN}')
            """
        ).fetchone()
    assert totale > 0
    assert nulli == 0, "eta_media_decorrenza NULL: cast fallito sul formato italiano"
    assert minima is not None and minima > 0


def test_clean_flag_totale_esplicito() -> None:
    with safe_connect() as con:
        righe = con.execute(
            f"""
            SELECT is_totale, count(*)
            FROM read_parquet('{CLEAN}')
            GROUP BY 1 ORDER BY 1
            """
        ).fetchall()
    valori = dict(righe)
    assert None not in valori, "is_totale non deve essere NULL"
    assert valori.get(True, 0) > 0, "la fonte include totali: il flag deve marcarli"
    assert valori.get(False, 0) > 0, "manca il dettaglio"


@pytest.mark.parametrize("nome", list(MART_SPECS))
def test_mart_esclude_totali(nome: str) -> None:
    percorso, colonna = MART_SPECS[nome]
    if not os.path.isfile(percorso):
        pytest.skip("mart locale assente (CI)")
    with safe_connect() as con:
        totali_trimestre, totali_dimensione, eta_nulle = con.execute(
            f"""
            SELECT
                count(*) FILTER (WHERE trimestre = 'Totale'),
                count(*) FILTER (WHERE "{colonna}" = 'Totale'),
                count(*) FILTER (WHERE eta_media_decorrenza IS NULL)
            FROM read_parquet('{percorso}')
            """
        ).fetchone()
    assert totali_trimestre == 0, f"{nome}: mart include righe trimestre=Totale"
    assert totali_dimensione == 0, f"{nome}: mart include la dimensione Totale"
    assert eta_nulle == 0, f"{nome}: eta_media_decorrenza NULL"


@pytest.mark.parametrize("nome", list(MART_SPECS))
def test_mart_somma_dettaglio(nome: str) -> None:
    percorso, _colonna = MART_SPECS[nome]
    if not os.path.isfile(percorso):
        pytest.skip("mart locale assente (CI)")
    with safe_connect() as con:
        somma = con.execute(
            f"SELECT sum(n_pensioni) FROM read_parquet('{percorso}')"
        ).fetchone()[0]
    assert somma == SOMMA_DETTAGLIO, (
        f"{nome}: somma {somma} diversa dal dettaglio atteso {SOMMA_DETTAGLIO} "
        "(probabili totali inclusi)"
    )
