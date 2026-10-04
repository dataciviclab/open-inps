#!/usr/bin/env python3
"""Estrae pensioni vigenti — obs INPS #378 (2022-2026)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))
from common import run_queries

OBS_ID = 378
QUERIES = {
    "anno_sesso_importo": {
        "id_osservatorio": "378",
        "language": "",
        "totalRow": True,
        "totalColumn": True,
        "subtotalRow": True,
        "subtotalColumn": True,
        "selections": {
            "rows": [
                {
                    "id": "Anno-",
                    "label": "Anno-",
                    "order": 1,
                    "expand": "",
                    "hide": False,
                    "aggregate": False,
                },
                {
                    "id": "Sesso-",
                    "label": "Sesso-",
                    "order": 2,
                    "expand": "",
                    "hide": False,
                    "aggregate": False,
                },
            ],
            "cols": [
                {
                    "id": "Classi di importo",
                    "label": "Classi di importo",
                    "order": 1,
                    "expand": "",
                    "hide": False,
                    "aggregate": True,
                }
            ],
            "measures": [
                {"id": "_FREQ_SUM", "label": "_FREQ_SUM", "order": 1},
                {"id": "tot_impSUM", "label": "tot_impSUM", "order": 2},
                {"id": "Importo medio mensile", "label": "Importo medio mensile", "order": 3},
            ],
            "filters": [],
        },
    },
    "anno_sesso_eta": {
        "id_osservatorio": "378",
        "language": "",
        "totalRow": True,
        "totalColumn": True,
        "subtotalRow": True,
        "subtotalColumn": True,
        "selections": {
            "rows": [
                {
                    "id": "Anno-",
                    "label": "Anno-",
                    "order": 1,
                    "expand": "",
                    "hide": False,
                    "aggregate": False,
                },
                {
                    "id": "Sesso-",
                    "label": "Sesso-",
                    "order": 2,
                    "expand": "",
                    "hide": False,
                    "aggregate": False,
                },
            ],
            "cols": [
                {
                    "id": "Classi di età",
                    "label": "Classi di età",
                    "order": 1,
                    "expand": "",
                    "hide": False,
                    "aggregate": True,
                }
            ],
            "measures": [
                {"id": "_FREQ_SUM", "label": "_FREQ_SUM", "order": 1},
                {"id": "Importo medio mensile", "label": "Importo medio mensile", "order": 2},
            ],
            "filters": [],
        },
    },
    "anno_regione": {
        "id_osservatorio": "378",
        "language": "",
        "totalRow": True,
        "totalColumn": True,
        "subtotalRow": True,
        "subtotalColumn": True,
        "selections": {
            "rows": [
                {
                    "id": "Anno-",
                    "label": "Anno-",
                    "order": 1,
                    "expand": "",
                    "hide": False,
                    "aggregate": False,
                },
                {
                    "id": "Regione",
                    "label": "Regione",
                    "order": 2,
                    "expand": "",
                    "hide": False,
                    "aggregate": False,
                },
            ],
            "cols": [
                {
                    "id": "Sesso-",
                    "label": "Sesso-",
                    "order": 1,
                    "expand": "",
                    "hide": False,
                    "aggregate": True,
                }
            ],
            "measures": [
                {"id": "_FREQ_SUM", "label": "_FREQ_SUM", "order": 1},
                {"id": "Importo medio mensile", "label": "Importo medio mensile", "order": 2},
            ],
            "filters": [],
        },
    },
}

if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("raw.csv")
    n = run_queries(OBS_ID, QUERIES, out)
    print(f"Totale: {n} righe -> {out}")
