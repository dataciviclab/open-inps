#!/usr/bin/env python3
"""Estrae CIG ore autorizzate — obs INPS #512 (2023-2026)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))
from common import get_data, flatten_nested

QUERIES = {
    "anno_regione_gestione": {
        "id_osservatorio": "512", "language": "",
        "totalRow": True, "totalColumn": True, "subtotalRow": True, "subtotalColumn": True,
        "selections": {
            "rows": [
                {"id": "Anno-", "label": "Anno-", "order": 1, "expand": "", "hide": False, "aggregate": False},
                {"id": "Regione", "label": "Regione", "order": 2, "expand": "", "hide": False, "aggregate": False},
            ],
            "cols": [
                {"id": "Gestio", "label": "Gestio", "order": 1, "expand": "", "hide": False, "aggregate": True},
            ],
            "measures": [{"id": "oretotSUM", "label": "oretotSUM", "order": 1}],
            "filters": [],
        },
    },
    "anno_ramo": {
        "id_osservatorio": "512", "language": "",
        "totalRow": True, "totalColumn": True, "subtotalRow": True, "subtotalColumn": True,
        "selections": {
            "rows": [
                {"id": "Anno-", "label": "Anno-", "order": 1, "expand": "", "hide": False, "aggregate": False},
            ],
            "cols": [
                {"id": "Ramo", "label": "Ramo", "order": 1, "expand": "", "hide": False, "aggregate": True},
            ],
            "measures": [{"id": "oretotSUM", "label": "oretotSUM", "order": 1}],
            "filters": [],
        },
    },
    "anno_mese": {
        "id_osservatorio": "512", "language": "",
        "totalRow": True, "totalColumn": True, "subtotalRow": True, "subtotalColumn": True,
        "selections": {
            "rows": [
                {"id": "Anno-", "label": "Anno-", "order": 1, "expand": "", "hide": False, "aggregate": False},
                {"id": "Mese-", "label": "Mese-", "order": 2, "expand": "", "hide": False, "aggregate": False},
            ],
            "cols": [],
            "measures": [{"id": "oretotSUM", "label": "oretotSUM", "order": 1}],
            "filters": [],
        },
    },
}

if __name__ == "__main__":
    import csv
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
