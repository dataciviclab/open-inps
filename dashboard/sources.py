"""Fonti dati per la dashboard Open INPS.

Pattern standard (standards/dashboard.md): **GCS via lab-connectors**.
I mart si leggono da ``dataciviclab-mart/open-inps/...`` con il prefix
del registry. Nessun auto-detect locale in produzione.

``OPEN_INPS_LOCAL_DATA`` (opzionale) abilita il fallback su ``out/data/``
per lo sviluppo post-``make run``.
"""

from __future__ import annotations

import os
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st
from lab_connectors.formatters import fmt_num, fmt_pct
from lab_connectors.gcs.paths import https_url
from lab_connectors.registry import load_registry

REPO_ROOT = Path(__file__).parent.parent
LOCAL_ROOT = str(REPO_ROOT / "out" / "data")

# Prefix GCS default del repo (registry: prefix_for_slug → "open-inps/")
DEFAULT_PREFIX = "open-inps/"
COMPOSE_SLUG = "inps_analisi"


def _load_registry():
    """Registry del repo; None se assente (deploy senza cartella registry/)."""
    path = REPO_ROOT / "registry" / "registry.json"
    try:
        return load_registry(path)
    except Exception:
        return None


_registry = _load_registry()


def get_registry():
    return _registry


def _prefix_for(slug: str) -> str:
    """Prefix GCS dal registry, fallback open-inps/."""
    if _registry is not None:
        try:
            p = _registry.prefix_for_slug(slug)
            if p:
                return p
        except Exception:
            pass
    return DEFAULT_PREFIX


def _use_local() -> bool:
    return os.environ.get("OPEN_INPS_LOCAL_DATA", "").lower() in {"1", "true", "yes"}


# ── Formattazione italiana (re-export LC + helper locale) ──────────────────


def fmt_it(n: float | int | None) -> str:
    """1234567 → '1.234.567'"""
    if n is None:
        return "–"
    return f"{n:,.0f}".replace(",", ".")


# ── Loader mart — solo GCS (path contract MART) ────────────────────────────


@st.cache_data(ttl=300, show_spinner=False)
def load_mart(slug: str, table: str, year: int = 2026) -> pd.DataFrame:
    """Carica un mart da GCS (bucket dataciviclab-mart).

    Path: ``{prefix}{slug}/{year}/{table}.parquet``
    con ``prefix`` dal registry (``open-inps/``).
    """
    if _use_local():
        local = Path(LOCAL_ROOT) / "mart" / slug / str(year) / f"{table}.parquet"
        if local.is_file():
            with duckdb.connect() as con:
                return con.sql(f"SELECT * FROM read_parquet('{local}')").df()

    prefix = _prefix_for(slug)
    url = https_url(
        "mart",
        "mart_parquet",
        prefix=prefix,
        slug=slug,
        year=str(year),
        table=table,
    )
    with duckdb.connect() as con:
        return con.sql(f"SELECT * FROM read_parquet('{url}')").df()


def require_mart(slug: str, table: str, year: int = 2026) -> pd.DataFrame:
    """Mart di un dataset singolo. Errore esplicito se assente."""
    try:
        df = load_mart(slug, table, year)
    except Exception as e:
        st.error(f"Errore caricamento mart `{slug}/{table}/{year}`: {e}")
        st.caption(
            "La dashboard legge i mart da GCS "
            f"(`dataciviclab-mart/{_prefix_for(slug)}…`). "
            "Verifica che la pipeline abbia pubblicato l'artefatto."
        )
        st.stop()
    if df is None or df.empty:
        st.error(f"Mart vuoto: `{slug}/{table}/{year}`")
        st.stop()
    return df


def require_compose(table: str, year: int = 2026) -> pd.DataFrame:
    """Mart del compose `inps_analisi`."""
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

METRICHE_DERIVATE = {
    "ratio_cessazioni_assunzioni": "Cessazioni / Assunzioni (%)",
}

GEOJSON_URL = (
    "https://raw.githubusercontent.com/openpolis/geojson-italy/master/"
    "geojson/limits_IT_regions.geojson"
)

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
    "DEFAULT_PREFIX",
    "GEOJSON_URL",
    "GEO_NAME_MAP",
    "METRICHE",
    "METRICHE_DERIVATE",
    "REGIONI",
    "fmt_it",
    "fmt_num",
    "fmt_pct",
    "get_registry",
    "load_mart",
    "require_compose",
    "require_mart",
    "to_geo_name",
]
