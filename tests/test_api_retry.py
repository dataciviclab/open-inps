"""Adapter API INPS — retry sui guasti transitori del backend SAS.

adapter: il backend tronca le risposte grandi (``IncompleteRead``) e ogni tanto
chiude la connessione. Sono guasti transitori, non errori di query: il 1/11/2026
la pipeline è caduta su ``inps_pensionamento_flussi`` dopo 24.828 byte parziali,
mentre lo stesso payload oggi risponde. ``api_post`` deve ritentare da sola e
restituire ``{"error": ...}`` solo quando i tentativi sono esauriti.
"""
from __future__ import annotations

import sys
from pathlib import Path
from urllib.error import HTTPError

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import common


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    """Il backoff non deve allungare i test."""
    monkeypatch.setattr(common.time, "sleep", lambda _seconds: None)


def test_guasto_transitorio_viene_ritentato(monkeypatch):
    esiti = iter([("transient", "Response incompleta (24828 bytes)"), ("ok", {"row_id": 1})])
    chiamate = []

    def fake(_url, _data, _timeout):
        chiamate.append(1)
        return next(esiti)

    monkeypatch.setattr(common, "_post_once", fake)

    risultato = common.api_post("getDatiOsservatorio", {"id_osservatorio": "475"})

    assert risultato == {"row_id": 1}
    assert len(chiamate) == 2


def test_tentativi_esauriti_riportano_errore(monkeypatch):
    chiamate = []

    def fake(_url, _data, _timeout):
        chiamate.append(1)
        return "transient", "Response incompleta (24828 bytes)"

    monkeypatch.setattr(common, "_post_once", fake)

    risultato = common.api_post("getDatiOsservatorio", {"id_osservatorio": "475"}, retries=3)

    assert "Response incompleta" in risultato["error"]
    assert len(chiamate) == 3


def test_errore_fatale_non_viene_ritentato(monkeypatch):
    chiamate = []

    def fake(_url, _data, _timeout):
        chiamate.append(1)
        return "fatal", "HTTP 400: Bad Request"

    monkeypatch.setattr(common, "_post_once", fake)

    risultato = common.api_post("getDatiOsservatorio", {})

    assert "HTTP 400" in risultato["error"]
    assert len(chiamate) == 1


@pytest.mark.parametrize(("codice", "esito_atteso"), [(503, "transient"), (400, "fatal")])
def test_classificazione_http(monkeypatch, codice, esito_atteso):
    """5xx merita un altro tentativo, 4xx no."""

    def fake_urlopen(*_args, **_kwargs):
        raise HTTPError("https://example.invalid", codice, "reason", {}, None)

    monkeypatch.setattr(common, "urlopen", fake_urlopen)

    esito, _messaggio = common._post_once("https://example.invalid", b"{}", 5)

    assert esito == esito_atteso
