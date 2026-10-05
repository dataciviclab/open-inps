"""Query SQL — clean layer INPS via lab-connectors (pattern open-siope)."""

from pathlib import Path

from lab_connectors.duckdb.sql_page import render_sql_query
from lab_connectors.registry import load_registry

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent

registry = load_registry(_REPO_ROOT / "registry" / "registry.json")

# Come open-siope: prefix esplicito per i path GCS del repo
render_sql_query(
    registry=registry,
    prefix="open-inps/",
    default_slug="inps_rapporti_lavoro",
    title="🧪 Query SQL",
    description=(
        "Interroga i clean parquet INPS su GCS "
        "(`dataciviclab-clean/open-inps/…`). "
        "Usa ``clean_input`` come tabella virtuale."
    ),
)
