"""Regressioni semantiche per inps_retribuzioni.

Proteggono il contratto pubblico: `retribuzione_totale` è in euro, settimane
e giornate sono quantità, e le sezioni ATECO sono mappate. Saltano in CI
quando i parquet locali non sono presenti.
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
    "inps_retribuzioni",
    "2026",
    "inps_retribuzioni_2026_clean.parquet",
)
MART_SETTORE = os.path.join(
    REPO_ROOT,
    "out",
    "data",
    "mart",
    "inps_retribuzioni",
    "2026",
    "mart_retribuzioni_settore.parquet",
)

pytestmark = [
    pytest.mark.skipif(not HAS_DUCKDB, reason="duckdb non installato"),
    pytest.mark.skipif(not os.path.isfile(CLEAN), reason="clean locale assente (CI)"),
]


def test_clean_has_correct_wage_columns() -> None:
    with safe_connect() as con:
        cols = [
            d[0]
            for d in con.execute(
                f"SELECT * FROM read_parquet('{CLEAN}') LIMIT 0"
            ).description
        ]
    assert "retribuzione_totale" in cols
    assert "settimane_retribuite" in cols
    assert "settimane_utili" in cols
    assert "giornate_retribuite" in cols
    assert "somma_retribuzioni" not in cols
    assert "unita_lavorative" not in cols


def test_clean_units_are_plausible() -> None:
    with safe_connect() as con:
        row = con.execute(
            f"""
            SELECT
                count(*) AS n,
                sum(
                    CASE
                        WHEN n_lavoratori > 0
                         AND (retribuzione_totale IS NULL OR retribuzione_totale <= 0)
                        THEN 1 ELSE 0
                    END
                ) AS bad_wage,
                min(
                    CASE WHEN n_lavoratori > 0
                         THEN retribuzione_totale / n_lavoratori END
                ) AS min_avg,
                max(
                    CASE WHEN n_lavoratori > 0
                         THEN retribuzione_totale / n_lavoratori END
                ) AS max_avg,
                max(
                    CASE WHEN n_lavoratori > 0
                         THEN settimane_retribuite / n_lavoratori END
                ) AS max_weeks,
                max(
                    CASE WHEN n_lavoratori > 0
                         THEN giornate_retribuite / n_lavoratori END
                ) AS max_days
            FROM read_parquet('{CLEAN}')
            """
        ).fetchone()

    n, bad_wage, min_avg, max_avg, max_weeks, max_days = row
    assert n > 0
    assert bad_wage == 0
    assert 1_000 <= min_avg <= max_avg <= 200_000
    assert max_weeks <= 60
    assert max_days <= 400


def test_settore_mapping_is_complete() -> None:
    with safe_connect() as con:
        row = con.execute(
            f"""
            SELECT
                count(*) FILTER (
                    WHERE dimensione = 'anno_settore' AND settore_codice IS NOT NULL
                ) AS mapped,
                count(*) FILTER (
                    WHERE dimensione = 'anno_settore'
                      AND settore_codice IS NULL
                      AND settore_label IS NOT NULL
                      AND settore_label NOT ILIKE '%totale%'
                ) AS unmapped
            FROM read_parquet('{CLEAN}')
            """
        ).fetchone()

    mapped, unmapped = row
    assert mapped > 0
    assert unmapped == 0


@pytest.mark.skipif(not os.path.isfile(MART_SETTORE), reason="mart settore locale assente (CI)")
def test_mart_settore_has_euro_wages() -> None:
    with safe_connect() as con:
        row = con.execute(
            f"""
            SELECT count(*), min(retribuzione_media), max(retribuzione_media)
            FROM read_parquet('{MART_SETTORE}')
            """
        ).fetchone()

    n, min_avg, max_avg = row
    assert n > 0
    assert 1_000 <= min_avg <= max_avg <= 200_000
