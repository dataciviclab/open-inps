#!/usr/bin/env python3
"""Estrae nuclei beneficiari RdC/PdC — obs INPS #452 (2019-2023).

Reddito/Pensione di Cittadinanza: nuclei che hanno percepito almeno
una mensilità nell'anno. Copertura 2019-2023 (dopo: Assegno Unico,
già in inps-assegno-unico). Nessuna dimensione genere sull'osservatorio.
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))
from common import api_post, flatten_nested

MEASURES = ["_FREQ_SUM", "NUM_COMPSUM", "Importo medio mensile"]

QUERIES = [
    (["anno", "cod_misura"], "anno_misura"),
    (["anno", "cod_misura", "regione"], "anno_misura_regione"),
    (["anno", "cod_misura", "cl_numcomp"], "anno_misura_componenti"),
    (["anno", "cod_misura", "f_disa"], "anno_misura_disabili"),
    (["anno", "cod_misura", "f_mino"], "anno_misura_minori"),
]


def payload(row_ids: list[str]) -> dict:
    return {
        "id_osservatorio": "452",
        "language": "",
        "totalRow": False,
        "totalColumn": False,
        "subtotalRow": False,
        "subtotalColumn": False,
        "selections": {
            "rows": [
                {"id": i, "label": i, "order": n, "expand": "", "hide": False, "aggregate": False}
                for n, i in enumerate(row_ids, 1)
            ],
            "cols": [],
            "measures": [{"id": m, "label": m, "order": n} for n, m in enumerate(MEASURES, 1)],
            "filters": [],
        },
    }


def fetch(row_ids: list[str], dimensione: str) -> list[dict]:
    print(f"  452 {dimensione}...", end=" ", flush=True)
    r = api_post("getDatiOsservatorio", payload(row_ids), timeout=120)
    if isinstance(r, dict) and ("error" in r or r.get("errorCode")):
        err = r.get("error") or r.get("message") or "unknown"
        print(f"\n  FALLITO 452/{dimensione}: {str(err)[:100]}", file=sys.stderr)
        sys.exit(1)
    flat = flatten_nested(r)
    for row in flat:
        row["dimensione"] = dimensione
        row["obs"] = "452"
    print(f"{len(flat)} righe")
    return flat


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("raw.csv")
    all_rows: list[dict] = []
    for rows, dim in QUERIES:
        all_rows += fetch(rows, dim)

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
