"""Regressioni semantiche per mart_rg_incentivi.

Proteggono il totale e la voce dominante del 2024: se il capitolo
dell'esonero generalizzato sparisse o venisse rinominato, il totale
crollerebbe di metà. Saltano quando i parquet locali non sono presenti.
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
MART = os.path.join(
    REPO_ROOT,
    "out",
    "data",
    "mart",
    "inps_bilancio_gestionale",
    "2026",
    "mart_rg_incentivi.parquet",
)

pytestmark = [
    pytest.mark.skipif(not HAS_DUCKDB, reason="duckdb non installato"),
    pytest.mark.skipif(not os.path.isfile(MART), reason="mart locale assente (CI)"),
]


def test_totale_2024_e_voce_dominante() -> None:
    """2024: ~33,6 mld di uscite, con l'esonero generalizzato a ~17,2 mld."""
    with safe_connect() as con:
        totale, generalizzato = con.execute(
            f"""
            SELECT
                SUM(importo_esercizio_eur),
                SUM(CASE WHEN famiglia = 'Esonero generalizzato'
                         THEN importo_esercizio_eur END)
            FROM read_parquet('{MART}')
            WHERE anno = 2024
            """
        ).fetchone()

    assert totale == pytest.approx(33.62e9, rel=0.02)
    assert generalizzato == pytest.approx(17.21e9, rel=0.02)


def test_famiglie_presenti() -> None:
    """Le famiglie principali restano popolate, senza valori vuoti."""
    with safe_connect() as con:
        famiglie, vuote = con.execute(
            f"""
            SELECT COUNT(DISTINCT famiglia),
                   COUNT(*) FILTER (WHERE famiglia IS NULL OR famiglia = '')
            FROM read_parquet('{MART}')
            WHERE anno = 2024
            """
        ).fetchone()

    assert famiglie >= 9
    assert vuote == 0
