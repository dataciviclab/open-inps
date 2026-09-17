"""Fonti dati per la dashboard Open INPS.

Due livelli:
- Compose: per analisi incrociate (genere, territorio, panoramica)
- Singoli dataset: per deep dive (pensioni, lavoro)
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
    if n is None: return "–"
    return f"{n:,.0f}".replace(",", ".")

# ── Loader compose ──────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def load_compose(table: str) -> pd.DataFrame:
    return load_mart_table("inps_analisi", table, 2026, local_root=LOCAL_ROOT)

# ── Loader singoli dataset ──────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def load_mart(slug: str, table: str) -> pd.DataFrame:
    return load_mart_table(slug, table, 2026, local_root=LOCAL_ROOT)

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
