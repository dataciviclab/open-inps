#!/usr/bin/env python3
"""Estrae DIS-COLL — obs INPS #397 (beneficiari) + #398 (trattamenti).

Disoccupazione collab.co.co: complemento a NASpI per parasubordinati.
Copertura 2020-2024.

Limitazione API: i tagli territoriali/per età non sono additivi al
totale nazionale (il backend SAS restituisce aggregati non coerenti
tra grane). Si estrae solo anno × sesso, internamente consistente.
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))
from common import api_post, flatten_nested

MEASURES = ["_FREQ_SUM", "SGGTEORICISUM", "SGG_PAGSUM", "STOT_PAGSUM"]
QUERIES = [
    ("397", "beneficiari"),
    ("398", "trattamenti"),
]


def payload(obs: str) -> dict:
    return {
        "id_osservatorio": obs,
        "language": "",
        "totalRow": False,
        "totalColumn": False,
        "subtotalRow": False,
        "subtotalColumn": False,
        "selections": {
            "rows": [
                {
                    "id": "anno",
                    "label": "anno",
                    "order": 1,
                    "expand": "",
                    "hide": False,
                    "aggregate": False,
                },
                {
                    "id": "sesso",
                    "label": "sesso",
                    "order": 2,
                    "expand": "",
                    "hide": False,
                    "aggregate": False,
                },
            ],
            "cols": [],
            "measures": [{"id": m, "label": m, "order": n} for n, m in enumerate(MEASURES, 1)],
            "filters": [],
        },
    }


def fetch(obs: str, tipo: str) -> list[dict]:
    print(f"  {obs} {tipo}/anno×sesso...", end=" ", flush=True)
    r = api_post("getDatiOsservatorio", payload(obs), timeout=120)
    if isinstance(r, dict) and ("error" in r or r.get("errorCode")):
        err = r.get("error") or r.get("message") or "unknown"
        print(f"\n  FALLITO {obs}: {str(err)[:100]}", file=sys.stderr)
        sys.exit(1)
    flat = flatten_nested(r)
    for row in flat:
        row["dimensione"] = "anno_sesso"
        row["tipo_dato"] = tipo
        row["obs"] = obs
    print(f"{len(flat)} righe")
    return flat


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("raw.csv")
    all_rows: list[dict] = []
    for obs, tipo in QUERIES:
        all_rows += fetch(obs, tipo)

    if not all_rows:
        print("Nessuna riga estratta", file=sys.stderr)
        sys.exit(1)

    fieldnames: list[str] = []
    seen: set[str] = set()
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
