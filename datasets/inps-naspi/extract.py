#!/usr/bin/env python3
"""Estrae NASpI — obs INPS #395 (beneficiari) + #396 (trattamenti), 2020-2024."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))
from common import flatten_nested, get_data

QUERIES_395 = {
    "beneficiari_anno_sesso_regione": {
        "id_osservatorio": "395",
        "language": "",
        "totalRow": True,
        "totalColumn": True,
        "subtotalRow": True,
        "subtotalColumn": True,
        "selections": {
            "rows": [
                {
                    "id": "Anno",
                    "label": "Anno",
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
                {
                    "id": "Regione",
                    "label": "Regione",
                    "order": 3,
                    "expand": "",
                    "hide": False,
                    "aggregate": False,
                },
            ],
            "cols": [],
            "measures": [{"id": "beneficiariSUM", "label": "beneficiariSUM", "order": 1}],
            "filters": [],
        },
    },
    "beneficiari_anno_sesso_eta": {
        "id_osservatorio": "395",
        "language": "",
        "totalRow": True,
        "totalColumn": True,
        "subtotalRow": True,
        "subtotalColumn": True,
        "selections": {
            "rows": [
                {
                    "id": "Anno",
                    "label": "Anno",
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
                    "id": "Classe di età",
                    "label": "Classe di età",
                    "order": 1,
                    "expand": "",
                    "hide": False,
                    "aggregate": True,
                },
            ],
            "measures": [{"id": "beneficiariSUM", "label": "beneficiariSUM", "order": 1}],
            "filters": [],
        },
    },
}

QUERIES_396 = {
    "trattamenti_anno_sesso_durata": {
        "id_osservatorio": "396",
        "language": "",
        "totalRow": True,
        "totalColumn": True,
        "subtotalRow": True,
        "subtotalColumn": True,
        "selections": {
            "rows": [
                {
                    "id": "Anno",
                    "label": "Anno",
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
                    "id": "Durata teorica prestazione",
                    "label": "Durata teorica prestazione",
                    "order": 1,
                    "expand": "",
                    "hide": False,
                    "aggregate": True,
                },
            ],
            "measures": [{"id": "beneficiariSUM", "label": "beneficiariSUM", "order": 1}],
            "filters": [],
        },
    },
}

if __name__ == "__main__":
    import csv

    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("raw.csv")
    all_rows = []

    print("  beneficiari_anno_sesso_regione...", end=" ", flush=True)
    r = get_data(QUERIES_395["beneficiari_anno_sesso_regione"])
    flat = flatten_nested(r)
    for row in flat:
        row["dimensione"] = "beneficiari_anno_sesso_regione"
        row["fonte"] = "395"
    all_rows.extend(flat)
    print(f"{len(flat)} righe")

    print("  beneficiari_anno_sesso_eta...", end=" ", flush=True)
    r = get_data(QUERIES_395["beneficiari_anno_sesso_eta"])
    flat = flatten_nested(r)
    for row in flat:
        row["dimensione"] = "beneficiari_anno_sesso_eta"
        row["fonte"] = "395"
    all_rows.extend(flat)
    print(f"{len(flat)} righe")

    print("  trattamenti_anno_sesso_durata...", end=" ", flush=True)
    r = get_data(QUERIES_396["trattamenti_anno_sesso_durata"])
    flat = flatten_nested(r)
    for row in flat:
        row["dimensione"] = "trattamenti_anno_sesso_durata"
        row["fonte"] = "396"
    all_rows.extend(flat)
    print(f"{len(flat)} righe")

    if all_rows:
        fieldnames = []
        seen = set()
        for row in all_rows:
            for k in row:
                if k not in seen:
                    fieldnames.append(k)
                    seen.add(k)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(all_rows)
        print(f"Totale: {len(all_rows)} righe -> {out}")
