"""Fonti dati per la dashboard Open INPS.

Usa lab-connectors per leggere i mart parquet da out/data/mart/.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from lab_connectors.duckdb.queries import load_mart_table
from lab_connectors.formatters import fmt_eur, fmt_num, fmt_pct

REPO_ROOT = Path(__file__).parent.parent
LOCAL_ROOT = str(REPO_ROOT / "out" / "data")

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

# ── Costanti ────────────────────────────────────────────────────────────────

REGIONI = [
    "Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna",
    "Friuli Venezia Giulia", "Lazio", "Liguria", "Lombardia", "Marche",
    "Molise", "Piemonte", "Puglia", "Sardegna", "Sicilia",
    "Toscana", "Trentino-Alto Adige", "Umbria", "Valle d'Aosta", "Veneto",
]

ANNI = list(range(2014, 2027))

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
