"""Query SQL — clean layer INPS via lab-connectors + GCS."""

from pathlib import Path

from lab_connectors.duckdb.sql_page import render_sql_query
from lab_connectors.registry import load_registry

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    registry = load_registry(_REPO_ROOT / "registry" / "registry.json")
except Exception:
    registry = None

# Path GCS clean: dataciviclab-clean/open-inps/{slug}/...
# Il registry usa prefix "open-inps/" — senza, gli URL 404.
render_sql_query(
    registry=registry if registry is not None else [],
    prefix="open-inps/",
    default_slug="inps_rapporti_lavoro",
    title="🧪 Query SQL",
    description=(
        "Interroga i clean parquet INPS su GCS "
        "(`dataciviclab-clean/open-inps/…`). "
        "Usa ``clean_input`` come tabella virtuale."
    ),
)
