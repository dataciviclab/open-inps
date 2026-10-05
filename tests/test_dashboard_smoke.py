"""Smoke test dashboard — contratto struttura secondo standards/dashboard.md.

Non importa le pagine Streamlit (eseguono codice UI all'import):
verifica navigazione app, presenza file e export di sources.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DASH = REPO_ROOT / "dashboard"
PAGES_DIR = DASH / "pages"

pytestmark = pytest.mark.smoke


def test_dashboard_layout_files_exist() -> None:
    """app.py, sources.py, requirements.txt e pages/ come da standard."""
    for rel in ("app.py", "sources.py", "requirements.txt", "pages"):
        assert (DASH / rel).exists(), f"Manca dashboard/{rel}"


def test_app_navigation_pages_exist() -> None:
    """Ogni st.Page referenziato in app.py deve esistere su disco."""
    app = (DASH / "app.py").read_text(encoding="utf-8")
    refs = re.findall(r'st\.Page\("([^"]+)"', app)
    assert refs, "app.py non dichiara pagine st.Page"
    for ref in refs:
        assert (DASH / ref).is_file(), f"Pagina mancante: {ref}"


def test_app_uses_lab_branding() -> None:
    """apply_branding obbligatorio (standards/dashboard.md)."""
    app = (DASH / "app.py").read_text(encoding="utf-8")
    assert "apply_branding" in app
    assert "lab_connectors.branding" in app
    assert 'layout="wide"' in app


def test_pages_parse_and_follow_naming() -> None:
    """Ogni pagina è uno script Python valido con naming NN_Nome.py."""
    pages = sorted(PAGES_DIR.glob("*.py"))
    assert pages, "Nessuna pagina in dashboard/pages/"
    for p in pages:
        ast.parse(p.read_text(encoding="utf-8"))
        assert re.match(r"^\d{2}_[A-Za-z0-9_]+\.py$", p.name), (
            f"Naming pagina non standard: {p.name}"
        )


def test_sources_contract() -> None:
    """sources wrappa lab-connectors come da standards/dashboard.md (RNA)."""
    src = (DASH / "sources.py").read_text(encoding="utf-8")
    for needle in (
        "def load_mart",
        "def require_mart",
        "def require_compose",
        "def fmt_it",
        "load_mart_table",
        "load_registry",
        "registry=_registry",
        "@st.cache_data",
        "fmt_num",
        "fmt_pct",
    ):
        assert needle in src, f"sources.py manca: {needle}"
    # Niente loader custom: il path lo risolve lab-connectors
    assert "https_url" not in src


def test_requirements_match_standard() -> None:
    """requirements.txt minimo dello standard dashboard."""
    text = (DASH / "requirements.txt").read_text(encoding="utf-8").lower()
    for needle in ("streamlit", "duckdb", "pandas", "lab-connectors"):
        assert needle in text, f"requirements.txt manca {needle}"
