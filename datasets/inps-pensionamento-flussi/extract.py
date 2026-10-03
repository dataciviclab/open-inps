#!/usr/bin/env python3
"""Estrae flussi trimestrali di pensionamento — obs INPS #475.

Copertura: anni decorrenza 2021-2026, per trimestre, sesso, regione,
gestione e categoria. Aggiornamento API: 2026-10-02.

Grane estratte (nazionali, senza provincia — l'osservatorio espone regione):
  anno × trimestre × sesso × regione
  anno × trimestre × sesso × gestione
  anno × trimestre × sesso × categoria

Le regioni qui sono raggruppamenti sede INPS (es. "Piemonte e Valle
d'Aosta"), non le 21 regioni ISTAT.
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))
from common import api_post, flatten_nested

MEASURES = [
    "_FREQ_SUM",
    "Età media alla decorrenza",
    "Importo medio alla decorrenza (in euro)",
]


def _row(fid: str, order: int) -> dict:
    return {
        "id": fid,
        "label": fid,
        "order": order,
        "expand": "",
        "hide": False,
        "aggregate": fid not in ("annodec", "SESSO"),
    }


def payload(last_dim: str) -> dict:
    return {
        "id_osservatorio": "475",
        "language": "",
        "totalRow": False,
        "totalColumn": False,
        "subtotalRow": False,
        "subtotalColumn": False,
        "selections": {
            "rows": [_row("annodec", 1), _row("trimestri", 2), _row("SESSO", 3), _row(last_dim, 4)],
            "cols": [],
            "measures": [
                {"id": m, "label": m, "order": n} for n, m in enumerate(MEASURES, start=1)
            ],
            "filters": [],
        },
    }


def fetch(last_dim: str, dimensione: str) -> list[dict]:
    print(f"  475 {last_dim}...", end=" ", flush=True)
    r = api_post("getDatiOsservatorio", payload(last_dim), timeout=120)
    if isinstance(r, dict) and "error" in r:
        print(f"\n  FALLITO 475/{last_dim}: {r['error'][:100]}", file=sys.stderr)
        sys.exit(1)
    flat = flatten_nested(r)
    for row in flat:
        row["dimensione"] = dimensione
        row["obs"] = "475"
    print(f"{len(flat)} righe")
    return flat


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("raw.csv")
    all_rows: list[dict] = []
    all_rows += fetch("REGIONE", "anno_trimestre_sesso_regione")
    all_rows += fetch("gestio", "anno_trimestre_sesso_gestione")
    all_rows += fetch("categ", "anno_trimestre_sesso_categoria")

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
