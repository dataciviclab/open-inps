#!/usr/bin/env python3
"""Estrae serie storica pensioni — obs INPS #390 (vigenti) + #376 (liquidate).

- 390 pensioni vigenti: 1998-2026
- 376 pensioni liquidate: 1997-2025

Tre grane nazionali per ciascun osservatorio:
  anno × sesso × categoria
  anno × sesso × tipo gestione
  anno × sesso × regione sede INPS

Le misure sono in formato italiano ("1.018,30"): il clean usa
normalize_italian_number / normalize_italian_integer.
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))
from common import api_post, flatten_nested


def _row(fid: str, order: int) -> dict:
    return {
        "id": fid,
        "label": fid,
        "order": order,
        "expand": "",
        "hide": False,
        "aggregate": False,
    }


def _measures(*ids: str) -> list[dict]:
    return [{"id": i, "label": i, "order": n} for n, i in enumerate(ids, start=1)]


def payload(obs: int, last_dim: str) -> dict:
    return {
        "id_osservatorio": str(obs),
        "language": "",
        "totalRow": False,
        "totalColumn": False,
        "subtotalRow": False,
        "subtotalColumn": False,
        "selections": {
            "rows": [_row("ANNO", 1), _row("SESSO", 2), _row(last_dim, 3)],
            "cols": [],
            "measures": _measures("_FREQ_SUM", "Importo medio mensile", "Età media"),
            "filters": [],
        },
    }


def fetch(obs: int, last_dim: str, dimensione: str, tipo_pensione: str) -> list[dict]:
    print(f"  obs {obs} {last_dim} ({tipo_pensione})...", end=" ", flush=True)
    r = api_post("getDatiOsservatorio", payload(obs, last_dim), timeout=120)
    if isinstance(r, dict) and "error" in r:
        print(f"\n  FALLITO obs {obs}/{last_dim}: {r['error'][:100]}", file=sys.stderr)
        sys.exit(1)
    flat = flatten_nested(r)
    for row in flat:
        row["dimensione"] = dimensione
        row["tipo_pensione"] = tipo_pensione
        row["obs"] = str(obs)
    print(f"{len(flat)} righe")
    return flat


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("raw.csv")
    all_rows: list[dict] = []

    all_rows += fetch(390, "catego", "anno_sesso_categoria", "vigente")
    all_rows += fetch(390, "tipogest", "anno_sesso_tipogest", "vigente")
    all_rows += fetch(390, "regione", "anno_sesso_regione", "vigente")

    all_rows += fetch(376, "catego", "anno_sesso_categoria", "liquidata")
    all_rows += fetch(376, "tipogest", "anno_sesso_tipogest", "liquidata")
    all_rows += fetch(376, "regione", "anno_sesso_regione", "liquidata")

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
