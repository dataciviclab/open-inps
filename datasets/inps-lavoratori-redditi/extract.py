#!/usr/bin/env python3
"""Estrae lavoratori, redditi da lavoro e settimane — obs INPS #465 (2014-2024).

Ponte lavoro→reddito: numero lavoratori, reddito cumulato e settimane
lavorate per posizione prevalente, regione, età e cittadinanza.

API aggiornata 2026-10-02. Misure in formato italiano (punti migliaia).
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))
from common import api_post, flatten_nested

MEASURES = ["_FREQ_SUM", "rr_cumulo_Sum", "ss_cum_total_Sum"]

QUERIES = [
    (["anno", "sesso", "cod_prevalente"], "anno_sesso_posizione"),
    (["anno", "sesso", "REGIONE"], "anno_sesso_regione"),
    (["anno", "sesso", "cl_eta"], "anno_sesso_eta"),
    (["anno", "sesso", "flag"], "anno_sesso_cittadinanza"),
    (["anno", "sesso", "pensionato"], "anno_sesso_pensionato"),
]


def payload(row_ids: list[str]) -> dict:
    return {
        "id_osservatorio": "465",
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
    print(f"  465 {dimensione}...", end=" ", flush=True)
    r = api_post("getDatiOsservatorio", payload(row_ids), timeout=120)
    if isinstance(r, dict) and ("error" in r or r.get("errorCode")):
        err = r.get("error") or r.get("message") or "unknown"
        print(f"\n  FALLITO 465/{dimensione}: {str(err)[:100]}", file=sys.stderr)
        sys.exit(1)
    flat = flatten_nested(r)
    for row in flat:
        row["dimensione"] = dimensione
        row["obs"] = "465"
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
