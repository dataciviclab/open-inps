"""Fonti dati per la dashboard Open INPS.

Usa lab-connectors per leggere i mart parquet da out/data/mart/.
I loader `require_*` sono il contratto delle pagine: falliscono in chiaro
se un mart manca, invece di restituire DataFrame vuoti silenziosi.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
from lab_connectors.duckdb.queries import load_mart_table
from lab_connectors.formatters import fmt_num

REPO_ROOT = Path(__file__).parent.parent
LOCAL_ROOT = str(REPO_ROOT / "out" / "data")

# Slug del compose multi-dataset (out/data/mart/inps_analisi/)
COMPOSE_SLUG = "inps_analisi"

# ── Formattazione italiana ─────────────────────────────────────────────────


def fmt_it(n: float | int | None) -> str:
    """1234567 → '1.234.567'"""
    if n is None:
        return "–"
    return f"{n:,.0f}".replace(",", ".")


# ── Loader ──────────────────────────────────────────────────────────────────


@st.cache_data(ttl=300, show_spinner=False)
def load_mart(slug: str, table: str, year: int = 2026) -> pd.DataFrame:
    """Carica un singolo mart parquet da out/data/mart/."""
    return load_mart_table(slug, table, year, local_root=LOCAL_ROOT)


def require_mart(slug: str, table: str, year: int = 2026) -> pd.DataFrame:
    """Mart di un dataset singolo. Errore esplicito se assente."""
    df = load_mart(slug, table, year)
    if df is None or df.empty:
        st.error(f"Mart non trovato o vuoto: `{slug}/{table}/{year}`")
        st.stop()
    return df


def require_compose(table: str, year: int = 2026) -> pd.DataFrame:
    """Mart del compose `inps_analisi` (nazionale/territoriale/benchmark/lifecycle)."""
    return require_mart(COMPOSE_SLUG, table, year)


# ── Costanti ────────────────────────────────────────────────────────────────

REGIONI = [
    "Abruzzo",
    "Basilicata",
    "Calabria",
    "Campania",
    "Emilia-Romagna",
    "Friuli Venezia Giulia",
    "Lazio",
    "Liguria",
    "Lombardia",
    "Marche",
    "Molise",
    "Piemonte",
    "Puglia",
    "Sardegna",
    "Sicilia",
    "Toscana",
    "Trentino-Alto Adige",
    "Umbria",
    "Valle d'Aosta",
    "Veneto",
]

ANNI = list(range(2014, 2027))
ALL_YEARS = ANNI

METRICHE = {
    "pensioni_vigenti": "Pensioni in pagamento",
    "pensioni_liquidate": "Pensioni liquidate",
    "pensionamento_flussi": "Nuove pensioni (decorrenza)",
    "rapporti_lavoro": "Assunzioni",
    "cessazioni_lavoro": "Cessazioni",
    "lavoratori_privati": "Lavoratori privati",
    "lavoratori_pa": "Lavoratori pubblici",
    "lavoratori_redditi": "Lavoratori (tutte posizioni)",
    "naspi": "Beneficiari NASpI",
    "dis_coll": "DIS-COLL beneficiari",
    "rdc_nuclei": "Nuclei RdC/PdC",
    "cig_ore": "Ore CIG",
    "assegno_unico": "Figli assegno unico",
    "enti_pubblici": "Enti pubblici",
}

GEOJSON_URL = "https://raw.githubusercontent.com/openpolis/geojson-italian/master/geojson/limits_IT_regions.geojson"

__all__ = [
    "ALL_YEARS",
    "ANNI",
    "COMPOSE_SLUG",
    "GEOJSON_URL",
    "METRICHE",
    "REGIONI",
    "fmt_it",
    "fmt_num",
    "load_mart",
    "require_compose",
    "require_mart",
]
