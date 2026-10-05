"""Query SQL — interroga i clean parquet INPS via lab-connectors."""

from pathlib import Path

from lab_connectors.duckdb.sql_page import render_sql_query
from lab_connectors.registry import load_registry

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
registry = load_registry(_REPO_ROOT / "registry" / "registry.json")

render_sql_query(
    registry=registry,
    prefix="open-inps/",
    default_slug="inps_rapporti_lavoro",
    title="🧪 Query SQL",
    description=(
        "Interroga direttamente i dati INPS (clean layer). "
        "Usa ``clean_input`` come tabella virtuale — "
        "la CTE viene risolta sui Parquet del dataset selezionato."
    ),
)
