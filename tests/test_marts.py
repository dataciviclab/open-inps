"""Test: i mart parquet esistono e hanno schema corretto."""
import pytest
import glob
import os

try:
    import duckdb
    HAS_DUCKDB = True
except ImportError:
    HAS_DUCKDB = False

REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
MART_DIR = os.path.join(REPO_ROOT, "out", "data", "mart")

# Expected mart tables per dataset
EXPECTED = {
    "inps_pensioni_vigenti": ["mart_vigenti_importo", "mart_vigenti_eta", "mart_vigenti_regione"],
    "inps_pensioni_liquidate": ["mart_liquidate_importo", "mart_liquidate_regione"],
    "inps_rapporti_lavoro": ["mart_rapporti_regione", "mart_rapporti_provincia", "mart_rapporti_eta"],
    "inps_retribuzioni": ["mart_retribuzioni_regione", "mart_retribuzioni_eta"],
    "inps_naspi": ["mart_naspi_regione", "mart_naspi_eta", "mart_naspi_durata"],
    "inps_cig": ["mart_cig_regione", "mart_cig_ramo", "mart_cig_mensile"],
    "inps_assegno_unico": ["mart_au_regione", "mart_au_isee"],
    "inps_dipendenti_pubblici": ["mart_dp_regione", "mart_dp_forma_giuridica"],
}


@pytest.mark.contract
@pytest.mark.parametrize("dataset,tables", EXPECTED.items())
def test_mart_files_exist(dataset, tables):
    """Ogni dataset deve avere i mart parquet dichiarati."""
    for table in tables:
        pattern = os.path.join(MART_DIR, dataset, "2026", f"{table}.parquet")
        matches = glob.glob(pattern)
        assert len(matches) > 0, f"Mart mancante: {table} per {dataset}"


@pytest.mark.contract
@pytest.mark.skipif(not HAS_DUCKDB, reason="duckdb non installato")
@pytest.mark.parametrize("dataset,tables", EXPECTED.items())
def test_mart_has_rows(dataset, tables):
    """Ogni mart deve avere almeno 10 righe."""
    con = duckdb.connect()
    for table in tables:
        pattern = os.path.join(MART_DIR, dataset, "2026", f"{table}.parquet")
        matches = glob.glob(pattern)
        if not matches:
            pytest.skip(f"File non trovato: {table}")
        count = con.execute(f"SELECT count(*) FROM read_parquet('{matches[0]}')").fetchone()[0]
        assert count >= 10, f"{table} ha solo {count} righe (minimo 10)"


@pytest.mark.contract
@pytest.mark.skipif(not HAS_DUCKDB, reason="duckdb non installato")
def test_compose_mart_exists():
    """Il compose deve produrre mart_nazionale e mart_territoriale."""
    con = duckdb.connect()
    for table in ["mart_nazionale", "mart_territoriale"]:
        pattern = os.path.join(MART_DIR, "inps_analisi", "2026", f"{table}.parquet")
        matches = glob.glob(pattern)
        assert len(matches) > 0, f"Compose mart mancante: {table}"
        count = con.execute(f"SELECT count(*) FROM read_parquet('{matches[0]}')").fetchone()[0]
        assert count >= 10, f"Compose {table} ha solo {count} righe"
