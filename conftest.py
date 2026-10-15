"""Config pytest per repo dataset (modello multi-dataset, ADR-001)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# I moduli della dashboard (sostenibilita, sources, …) vivono in dashboard/
# che non è un package installabile: lo aggiungiamo al path per i test.
_DASH = Path(__file__).parent / "dashboard"
if str(_DASH) not in sys.path:
    sys.path.insert(0, str(_DASH))


def pytest_configure(config: pytest.Config) -> None:
    """Registra i custom markers a livello di repo (policy test del Lab)."""
    config.addinivalue_line("markers", "pure_unit: pure logic, zero side effects")
    config.addinivalue_line("markers", "contract: public interface, contract API")
    config.addinivalue_line("markers", "smoke: golden path end-to-end")
    config.addinivalue_line("markers", "adapter: external service adapter logic")
    config.addinivalue_line("markers", "regression: bug fix documentato in issue/PR")
    config.addinivalue_line("markers", "policy: regola non ovvia o comportamento cross-component")
