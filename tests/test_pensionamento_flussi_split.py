"""Contract INPS 475 — la query è spezzata per anno di decorrenza.

pure_unit: la richiesta su tutte le decorrenze produce una risposta che il
backend tronca (~25 KB) quando arriva dalla rete dei runner: 24828 byte
ricevuti su 25850, sempre lo stesso scarto, con o senza retry. Filtrando per
`annodec` ogni risposta scende a ~4 KB.

Il filtro però materializza il subtotale annuale (`annodec` vuoto), che
duplicherebbe il totale una volta per anno: va scartato. La verifica sul dato
reale è che l'unione per anno, senza subtotali, coincide riga per riga con la
risposta non filtrata e i mart escludono già quelle righe (`sesso` vuoto).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATASET = REPO / "datasets" / "inps-pensionamento-flussi"

sys.path.insert(0, str(REPO / "scripts"))


def _load_extract():
    spec = importlib.util.spec_from_file_location("inps_475_extract", DATASET / "extract.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_payload_filtra_su_un_anno():
    modulo = _load_extract()

    corpo = modulo.payload("REGIONE", "2024")

    filtri = corpo["selections"]["filters"]
    assert filtri == [{"id": "annodec", "values": ["2024"]}]


def test_fetch_spezza_per_anno_e_scarta_i_subtotali(monkeypatch):
    modulo = _load_extract()
    richieste: list[str] = []

    def fake_api_post(_endpoint, payload, **_kwargs):
        anno = payload["selections"]["filters"][0]["values"][0]
        richieste.append(anno)
        return {"rows": anno}

    def fake_flatten(_risposta):
        anno = _risposta["rows"]
        return [
            {"anno": anno, "SESSO": "Maschi", "REGIONE": "Lombardia"},
            # subtotale annuale: annodec vuoto, non è un dato osservato
            {"anno": " ", "SESSO": " ", "REGIONE": " "},
        ]

    monkeypatch.setattr(modulo, "api_post", fake_api_post)
    monkeypatch.setattr(modulo, "flatten_nested", fake_flatten)

    righe = modulo.fetch("REGIONE", "anno_trimestre_sesso_regione", ["2023", "2024"])

    assert richieste == ["2023", "2024"]
    assert [r["anno"] for r in righe] == ["2023", "2024"]
    assert all(r["dimensione"] == "anno_trimestre_sesso_regione" for r in righe)
    assert all(r["obs"] == "475" for r in righe)


def test_anni_decorrenza_li_legge_dalla_struttura(monkeypatch):
    modulo = _load_extract()

    def fake_api_post(_endpoint, payload, **_kwargs):
        assert payload["id_osservatorio"] == "475"
        return {
            "definition": {
                "fields": [
                    {"id": "SESSO", "distinctValues": ["Maschi", "Femmine"]},
                    {"id": "annodec", "distinctValues": ["2024", "2025"]},
                ]
            }
        }

    monkeypatch.setattr(modulo, "api_post", fake_api_post)

    assert modulo.anni_decorrenza() == ["2024", "2025"]


def test_anni_decorrenza_senza_campo_annodec(monkeypatch):
    modulo = _load_extract()
    monkeypatch.setattr(modulo, "api_post", lambda *_a, **_k: {"definition": {"fields": []}})

    assert modulo.anni_decorrenza() == []
