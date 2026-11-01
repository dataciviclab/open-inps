"""Adapter API INPS — retry sui guasti transitori del backend SAS.

adapter: il backend tronca le risposte grandi (``IncompleteRead``) e ogni tanto
chiude la connessione. Sono guasti transitori, non errori di query: il 1/11/2026
la pipeline è caduta su ``inps_pensionamento_flussi`` dopo 24.828 byte parziali,
mentre lo stesso payload oggi risponde. ``api_post`` deve ritentare da sola e
restituire ``{"error": ...}`` solo quando i tentativi sono esauriti.
"""
from __future__ import annotations

import sys
from http.client import IncompleteRead, RemoteDisconnected
from pathlib import Path
from typing import Self
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


@pytest.mark.parametrize(
    ("codice", "esito_atteso"),
    [(503, "transient"), (429, "transient"), (400, "fatal"), (404, "fatal")],
)
def test_classificazione_http(monkeypatch, codice, esito_atteso):
    """5xx e 429 meritano un altro tentativo, gli altri 4xx no."""

    def fake_urlopen(*_args, **_kwargs):
        raise HTTPError("https://example.invalid", codice, "reason", {}, None)

    monkeypatch.setattr(common, "urlopen", fake_urlopen)

    esito, _messaggio = common._post_once("https://example.invalid", b"{}", 5)

    assert esito == esito_atteso


class _RispostaCheCade:
    """Risposta HTTP il cui ``read()`` muore a metà, come il backend SAS."""

    def __init__(self, eccezione: BaseException) -> None:
        self._eccezione = eccezione

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_args: object) -> bool:
        return False

    def read(self) -> bytes:
        raise self._eccezione


@pytest.mark.parametrize(
    "eccezione",
    [
        RemoteDisconnected("Remote end closed connection without response"),
        ConnectionResetError(104, "Connection reset by peer"),
        IncompleteRead(b"parziale", 1048576),
    ],
)
def test_connessione_che_cade_e_transitoria(monkeypatch, eccezione):
    """Il backend che chiude la connessione è un guasto ritentabile.

    Prima questi casi risalivano come traceback: ``IncompleteRead`` era
    gestito, i reset a metà lettura no, perché non sono ``URLError``.
    """
    monkeypatch.setattr(
        common, "urlopen", lambda *_a, **_k: _RispostaCheCade(eccezione)
    )

    esito, messaggio = common._post_once("https://example.invalid", b"{}", 5)

    assert esito == "transient"
    assert messaggio


def test_api_post_ritenta_dopo_un_reset(monkeypatch):
    """Fine a fine: il reset consuma un tentativo, il secondo passa."""
    chiamate = []

    class _Ok:
        def __enter__(self) -> Self:
            return self

        def __exit__(self, *_args: object) -> bool:
            return False

        def read(self) -> bytes:
            return b'{"row_id": 7}'

    def fake_urlopen(*_args, **_kwargs):
        chiamate.append(1)
        if len(chiamate) == 1:
            return _RispostaCheCade(
                RemoteDisconnected("Remote end closed connection without response")
            )
        return _Ok()

    monkeypatch.setattr(common, "urlopen", fake_urlopen)

    risultato = common.api_post("getDatiOsservatorio", {"id_osservatorio": "475"})

    assert risultato == {"row_id": 7}
    assert len(chiamate) == 2
