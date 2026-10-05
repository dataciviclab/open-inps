"""Fonti dati per la dashboard Open INPS.

Pattern standard Lab (standards/dashboard.md): loader su
``lab_connectors.duckdb.queries`` con auto-detect locale/GCS.
``require_*`` sono il contratto delle pagine: falliscono in chiaro
se un mart manca.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
from lab_connectors.duckdb.queries import load_mart_table
from lab_connectors.formatters import fmt_num
from lab_connectors.registry import load_registry

REPO_ROOT = Path(__file__).parent.parent
LOCAL_ROOT = str(REPO_ROOT / "out" / "data")

# Registry del repo (path contract + colonne)
_registry = load_registry(REPO_ROOT / "registry" / "registry.json")

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
    """Carica un mart. Auto-detect: out/data locale o GCS via registry."""
    try:
        return load_mart_table(slug, table, year, local_root=LOCAL_ROOT)
    except Exception:
        # Fallback GCS (pattern standard) se il path locale non risolve
        return load_mart_table(slug, table, year)


def require_mart(slug: str, table: str, year: int = 2026) -> pd.DataFrame:
    """Mart di un dataset singolo. Errore esplicito se assente."""
    df = load_mart(slug, table, year)
    if df is None or df.empty:
        st.error(f"Mart non trovato o vuoto: `{slug}/{table}/{year}`")
        st.stop()
    return df


def require_compose(table: str, year: int = 2026) -> pd.DataFrame:
    """Mart del compose `inps_analisi`."""
    return require_mart(COMPOSE_SLUG, table, year)


def get_registry():
    """Registry del repo (per SQL page e tool LC)."""
    return _registry


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

# Anno con la copertura più completa nel compose
ANNO_PIENO_CONSIGLIATO = 2023

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

# Metriche derivate dal compose (non colonne del mart lungo)
METRICHE_DERIVATE = {
    "ratio_cessazioni_assunzioni": "Cessazioni / Assunzioni (%)",
}

# GeoJSON regioni — openpolis/geojson-italy (stesso di RNA/opencivitas).
# "geojson-italian" è un path errato (404).
GEOJSON_URL = (
    "https://raw.githubusercontent.com/openpolis/geojson-italy/master/"
    "geojson/limits_IT_regions.geojson"
)

# I mart usano nomi brevi; il GeoJSON usa etichette estese.
GEO_NAME_MAP = {
    "Trentino-Alto Adige": "Trentino-Alto Adige/Südtirol",
    "Valle d'Aosta": "Valle d'Aosta/Vallée d'Aoste",
    "Friuli Venezia Giulia": "Friuli-Venezia Giulia",
    "Emilia Romagna": "Emilia-Romagna",
}


def to_geo_name(regione: str) -> str:
    """Mappa il nome regione dei mart sul reg_name del GeoJSON."""
    if not regione:
        return regione
    return GEO_NAME_MAP.get(regione, regione)


__all__ = [
    "ALL_YEARS",
    "ANNO_PIENO_CONSIGLIATO",
    "ANNI",
    "COMPOSE_SLUG",
    "GEOJSON_URL",
    "GEO_NAME_MAP",
    "METRICHE",
    "METRICHE_DERIVATE",
    "REGIONI",
    "fmt_it",
    "fmt_num",
    "get_registry",
    "load_mart",
    "require_compose",
    "require_mart",
    "to_geo_name",
]
