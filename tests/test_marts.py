"""Test: i mart parquet esistono e hanno schema corretto."""

import glob
import os

import pytest

try:
    from lab_connectors.duckdb.core import safe_connect

    HAS_DUCKDB = True
except ImportError:
    HAS_DUCKDB = False

REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
MART_DIR = os.path.join(REPO_ROOT, "out", "data", "mart")

EXPECTED = {
    "inps_pensioni_vigenti": ["mart_vigenti_importo", "mart_vigenti_eta", "mart_vigenti_regione"],
    "inps_pensioni_liquidate": ["mart_liquidate_importo", "mart_liquidate_regione"],
    "inps_rapporti_lavoro": [
        "mart_rapporti_regione",
        "mart_rapporti_provincia",
        "mart_rapporti_eta",
    ],
    "inps_rapporti_cessazioni": [
        "mart_cessazioni_regione",
        "mart_cessazioni_provincia",
        "mart_cessazioni_motivo",
    ],
    "inps_flussi_settore": ["mart_flussi_settore"],
    "inps_pensioni_serie": [
        "mart_pensioni_serie_categoria",
        "mart_pensioni_serie_tipogest",
        "mart_pensioni_serie_regione",
    ],
    "inps_pensionamento_flussi": [
        "mart_pensionamento_regione",
        "mart_pensionamento_gestione",
        "mart_pensionamento_categoria",
    ],
    "inps_retribuzioni": ["mart_retribuzioni_regione", "mart_retribuzioni_eta"],
    "inps_naspi": ["mart_naspi_regione", "mart_naspi_eta", "mart_naspi_durata"],
    "inps_cig": ["mart_cig_regione", "mart_cig_ramo", "mart_cig_mensile"],
    "inps_assegno_unico": ["mart_au_regione", "mart_au_isee"],
    "inps_dipendenti_pubblici": ["mart_dp_regione", "mart_dp_forma_giuridica"],
    "inps_analisi": ["mart_nazionale", "mart_territoriale", "mart_lifecycle", "mart_benchmark"],
}


@pytest.mark.contract
@pytest.mark.parametrize("dataset,tables", EXPECTED.items())
def test_mart_files_exist(dataset, tables):
    for table in tables:
        pattern = os.path.join(MART_DIR, dataset, "2026", f"{table}.parquet")
        assert len(glob.glob(pattern)) > 0, f"Mart mancante: {table} per {dataset}"


@pytest.mark.contract
@pytest.mark.skipif(not HAS_DUCKDB, reason="duckdb non installato")
@pytest.mark.parametrize("dataset,tables", EXPECTED.items())
def test_mart_has_rows(dataset, tables):
    with safe_connect() as con:
        for table in tables:
            pattern = os.path.join(MART_DIR, dataset, "2026", f"{table}.parquet")
            matches = glob.glob(pattern)
            if not matches:
                pytest.skip(f"File non trovato: {table}")
            count = con.execute(f"SELECT count(*) FROM read_parquet('{matches[0]}')").fetchone()[0]
            assert count >= 10, f"{table} ha solo {count} righe (minimo 10)"
