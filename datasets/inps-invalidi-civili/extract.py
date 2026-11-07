#!/usr/bin/env python3
"""Estrae prestazioni agli invalidi civili — obs INPS #381, #383, #384.

Fonti:
- 381: prestazioni per anno, sesso, categoria (ciechi, sordomuti, invalidi
  totali/parziali) e sottocategoria; area/regione/provincia della sede INPS.
- 383: stesse prestazioni per residenza del titolare (regione).
- 384: serie storica 2002-2026 per anno, sesso e tipo prestazione.

Le misure sono numero di prestazioni (`_FREQ_SUM`) e importo medio mensile.
I conteggi arrivano in formato italiano ("1.885.235") e gli importi con la
virgola decimale: la normalizzazione sta nel clean.
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))
from common import api_post, flatten_nested

MEASURES = ["_FREQ_SUM", "Importo medio mensile"]

# (osservatorio, righe, nome dimensione)
QUERIES = [
    (381, ["anno", "SESSO", "prest1", "prest2"], "anno_sesso_categoria"),
    (381, ["anno", "SESSO", "CLETAI"], "anno_sesso_eta"),
    (383, ["ANNO", "SESSO", "regione"], "anno_sesso_regione"),
    (384, ["ANNO", "SESSO", "tipoprest"], "anno_serie"),
]


def payload(observatory_id: int, rows: list[str]) -> dict:
    return {
        "id_osservatorio": str(observatory_id),
        "language": "",
        "totalRow": False,
        "totalColumn": False,
        "subtotalRow": False,
        "subtotalColumn": False,
        "selections": {
            "rows": [
                {
                    "id": r,
                    "label": r,
                    "order": n,
                    "expand": "",
                    "hide": False,
                    "aggregate": False,
                }
                for n, r in enumerate(rows, 1)
            ],
            "cols": [],
            "measures": [
                {"id": m, "label": m, "order": n} for n, m in enumerate(MEASURES, 1)
            ],
            "filters": [],
        },
    }


def fetch(observatory_id: int, rows: list[str], dimensione: str) -> list[dict]:
    print(f"  {observatory_id} {dimensione}...", end=" ", flush=True)
    r = api_post(
        "getDatiOsservatorio", payload(observatory_id, rows), timeout=180
    )
    if isinstance(r, dict) and ("error" in r or r.get("errorCode")):
        err = r.get("error") or r.get("message") or "unknown"
        print(f"\n  FALLITO {observatory_id}/{dimensione}: {str(err)[:100]}", file=sys.stderr)
        sys.exit(1)
    flat = flatten_nested(r)
    # L'API aggiunge una riga di totale con dimensioni vuote: la scartiamo.
    flat = [x for x in flat if str(x.get("anno", "")).strip() not in ("", " ")]
    for row in flat:
        row["dimensione"] = dimensione
        row["obs"] = str(observatory_id)
    print(f"{len(flat)} righe")
    return flat


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("raw.csv")
    all_rows: list[dict] = []
    for obs, rows, dim in QUERIES:
        all_rows += fetch(obs, rows, dim)

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
