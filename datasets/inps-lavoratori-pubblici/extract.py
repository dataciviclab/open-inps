#!/usr/bin/env python3
"""Estrae retribuzioni e lavoratori pubblici — obs INPS #435 (2014-2024).

Complemento di inps-dipendenti-pubblici (obs 440: enti/giornate):
qui ci sono lavoratori, retribuzioni totali, giornate e unità per
gruppo contrattuale PA.

Nota API: il campo SESSO di questo osservatorio è rotto (SAS -320).
Le grane non includono il genere. Le misure sono in formato italiano.
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))
from common import api_post, flatten_nested

MEASURES = ["_FREQ_SUM", "RR_SumSUM", "GG_SumSUM", "SS_SumSUM", "UU_TOT_SumSUM"]

# (extra_dim or None, dimensione)
QUERIES = [
    (None, "anno_gruppo"),
    ("cl_eta", "anno_gruppo_eta"),
    ("tipo_contra", "anno_gruppo_tipo_contratto"),
    ("ptime", "anno_gruppo_tempo_parziale"),
    ("regione", "anno_gruppo_regione"),
]


def payload(extra_dim: str | None) -> dict:
    rows = [
        {
            "id": "anno",
            "label": "anno",
            "order": 1,
            "expand": "",
            "hide": False,
            "aggregate": False,
        },
        {
            "id": "cod_contra",
            "label": "cod_contra",
            "order": 2,
            "expand": "",
            "hide": False,
            "aggregate": False,
        },
    ]
    if extra_dim:
        rows.append(
            {
                "id": extra_dim,
                "label": extra_dim,
                "order": 3,
                "expand": "",
                "hide": False,
                "aggregate": False,
            }
        )
    return {
        "id_osservatorio": "435",
        "language": "",
        "totalRow": False,
        "totalColumn": False,
        "subtotalRow": False,
        "subtotalColumn": False,
        "selections": {
            "rows": rows,
            "cols": [],
            "measures": [{"id": m, "label": m, "order": n} for n, m in enumerate(MEASURES, 1)],
            "filters": [],
        },
    }


def fetch(extra_dim: str | None, dimensione: str) -> list[dict]:
    label = extra_dim or "gruppo"
    print(f"  435 {label}...", end=" ", flush=True)
    r = api_post("getDatiOsservatorio", payload(extra_dim), timeout=120)
    if isinstance(r, dict) and ("error" in r or r.get("errorCode")):
        err = r.get("error") or r.get("message") or "unknown"
        print(f"\n  FALLITO 435/{label}: {str(err)[:100]}", file=sys.stderr)
        sys.exit(1)
    flat = flatten_nested(r)
    for row in flat:
        row["dimensione"] = dimensione
        row["obs"] = "435"
    print(f"{len(flat)} righe")
    return flat


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("raw.csv")
    all_rows: list[dict] = []
    for extra, dim in QUERIES:
        all_rows += fetch(extra, dim)

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
