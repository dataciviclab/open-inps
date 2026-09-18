"""Data sources — tutto derivato dal registry.

Anni, slug e anni-per-dataset vengono da registry.json.
Niente hardcoding di anni o slug nelle funzioni.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
from lab_connectors.dashboard import require_data
from lab_connectors.dashboard.sources import detect_local_root, years_for_slug
from lab_connectors.duckdb.queries import load_mart_table
from lab_connectors.formatters import fmt_num
from lab_connectors.registry import load_registry

# ── Init ────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent
LOCAL_ROOT = detect_local_root(ROOT)

_registry = load_registry(ROOT / "registry" / "registry.json")

# Anni disponibili per il compose
ALL_YEARS = years_for_slug(_registry, "inps_analisi") or list(range(2014, 2027))
LATEST_YEAR = max(ALL_YEARS)

# ── Loader ──────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def load_compose(table: str) -> pd.DataFrame:
    """Carica un mart dal compose inps_analisi."""
    return load_mart_table("inps_analisi", table, LATEST_YEAR, local_root=LOCAL_ROOT)

@st.cache_data(ttl=300, show_spinner=False)
def load_mart(slug: str, table: str) -> pd.DataFrame:
    """Carica un singolo mart parquet."""
    return load_mart_table(slug, table, LATEST_YEAR, local_root=LOCAL_ROOT)

@st.cache_data(ttl=300, show_spinner=False)
def require_compose(table: str) -> pd.DataFrame:
    """Carica compose con guardia dati."""
    df = load_compose(table)
    require_data(df, f"Compose {table} non disponibile. Esegui make run-compose.")
    return df

@st.cache_data(ttl=300, show_spinner=False)
def require_mart(slug: str, table: str) -> pd.DataFrame:
    """Carica mart con guardia dati."""
    df = load_mart(slug, table)
    require_data(df, f"Mart {slug}/{table} non disponibile. Esegui make run.")
    return df

# ── Costanti ────────────────────────────────────────────────────────────────

REGIONI = [
    "Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna",
    "Friuli Venezia Giulia", "Lazio", "Liguria", "Lombardia", "Marche",
    "Molise", "Piemonte", "Puglia", "Sardegna", "Sicilia",
    "Toscana", "Trentino-Alto Adige", "Umbria", "Valle d'Aosta", "Veneto",
]

METRICHE = {
    "pensioni_vigenti": "Pensioni in pagamento",
    "pensioni_liquidate": "Pensioni liquidate",
    "rapporti_lavoro": "Rapporti di lavoro",
    "lavoratori_privati": "Lavoratori privati",
    "naspi": "Beneficiari NASpI",
    "cig_ore": "Ore CIG",
    "assegno_unico": "Figli assegno unico",
    "enti_pubblici": "Enti pubblici",
}

GEOJSON_URL = "https://raw.githubusercontent.com/openpolis/geojson-italian/master/geojson/limits_IT_regions.geojson"
