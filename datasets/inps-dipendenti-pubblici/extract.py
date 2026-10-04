#!/usr/bin/env python3
"""Estrae dipendenti pubblici — obs INPS #440 (2022-2026)."""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))
from common import flatten_nested, get_data

QUERIES = {
    "anno_regione": {
        "id_osservatorio": "440",
        "language": "",
        "totalRow": True,
        "totalColumn": True,
        "subtotalRow": True,
        "subtotalColumn": True,
        "selections": {
            "rows": [
                {
                    "id": "Anno competenza",
                    "label": "Anno competenza",
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
                    "id": "TIPO ENTE",
                    "label": "TIPO ENTE",
                    "order": 1,
                    "expand": "",
                    "hide": False,
                    "aggregate": True,
                },
            ],
            "measures": [
                {"id": "num_entiSUM", "label": "num_entiSUM", "order": 1},
                {"id": "giorni_tot_corrSUM", "label": "giorni_tot_corrSUM", "order": 2},
                {"id": "retrimp_tot_corrSUM", "label": "retrimp_tot_corrSUM", "order": 3},
            ],
            "filters": [],
        },
    },
    "anno_forma_giuridica": {
        "id_osservatorio": "440",
        "language": "",
        "totalRow": True,
        "totalColumn": True,
        "subtotalRow": True,
        "subtotalColumn": True,
        "selections": {
            "rows": [
                {
                    "id": "Anno competenza",
                    "label": "Anno competenza",
                    "order": 1,
                    "expand": "",
                    "hide": False,
                    "aggregate": False,
                },
            ],
            "cols": [
                {
                    "id": "FORMA GIURIDICA",
                    "label": "FORMA GIURIDICA",
                    "order": 1,
                    "expand": "",
                    "hide": False,
                    "aggregate": True,
                },
            ],
            "measures": [
                {"id": "num_entiSUM", "label": "num_entiSUM", "order": 1},
                {"id": "retrimp_tot_corrSUM", "label": "retrimp_tot_corrSUM", "order": 2},
            ],
            "filters": [],
        },
    },
}

if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("raw.csv")
    all_rows = []
    for name, payload in QUERIES.items():
        print(f"  {name}...", end=" ", flush=True)
        r = get_data(payload)
        if "error" in r:
            print(f"errore: {r['error']}")
            continue
        flat = flatten_nested(r)
        for row in flat:
            row["dimensione"] = name
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
