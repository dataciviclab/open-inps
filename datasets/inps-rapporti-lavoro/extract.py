#!/usr/bin/env python3
"""Estrae nuovi rapporti di lavoro per provincia — obs INPS #489 (2014-2026)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))
from common import run_queries

OBS_ID = 489
QUERIES = {
    "anno_sesso_regione_tipo": {
        "id_osservatorio": "489", "language": "",
        "totalRow": True, "totalColumn": True, "subtotalRow": True, "subtotalColumn": True,
        "selections": {
            "rows": [
                {"id": "Anno", "label": "Anno", "order": 1, "expand": "", "hide": False, "aggregate": False},
                {"id": "Genere-", "label": "Genere-", "order": 2, "expand": "", "hide": False, "aggregate": False},
                {"id": "Regione", "label": "Regione", "order": 3, "expand": "", "hide": False, "aggregate": False},
            ],
            "cols": [
                {"id": "Tipologia assunzione", "label": "Tipologia assunzione", "order": 1, "expand": "", "hide": False, "aggregate": True},
            ],
            "measures": [
                {"id": "NUM_DENUNCE_SUM", "label": "NUM_DENUNCE_SUM", "order": 1},
            ],
            "filters": [],
        },
    },
    "anno_sesso_provincia": {
        "id_osservatorio": "489", "language": "",
        "totalRow": True, "totalColumn": True, "subtotalRow": True, "subtotalColumn": True,
        "selections": {
            "rows": [
                {"id": "Anno", "label": "Anno", "order": 1, "expand": "", "hide": False, "aggregate": False},
                {"id": "Genere-", "label": "Genere-", "order": 2, "expand": "", "hide": False, "aggregate": False},
                {"id": "Provincia", "label": "Provincia", "order": 3, "expand": "", "hide": False, "aggregate": False},
            ],
            "cols": [],
            "measures": [
                {"id": "NUM_DENUNCE_SUM", "label": "NUM_DENUNCE_SUM", "order": 1},
            ],
            "filters": [{"id": "ass_tipo_ass_cess", "label": "Tipologia assunzione", "values": ["Assunzioni a tempo indeterminato"]}],
        },
    },
    "anno_sesso_eta": {
        "id_osservatorio": "489", "language": "",
        "totalRow": True, "totalColumn": True, "subtotalRow": True, "subtotalColumn": True,
        "selections": {
            "rows": [
                {"id": "Anno", "label": "Anno", "order": 1, "expand": "", "hide": False, "aggregate": False},
                {"id": "Genere-", "label": "Genere-", "order": 2, "expand": "", "hide": False, "aggregate": False},
            ],
            "cols": [
                {"id": "Classe di Età", "label": "Classe di Età", "order": 1, "expand": "", "hide": False, "aggregate": True},
            ],
            "measures": [
                {"id": "NUM_DENUNCE_SUM", "label": "NUM_DENUNCE_SUM", "order": 1},
            ],
            "filters": [],
        },
    },
}

if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("raw.csv")
    n = run_queries(OBS_ID, QUERIES, out)
    print(f"Totale: {n} righe -> {out}")
