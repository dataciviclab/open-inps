#!/usr/bin/env python3
"""Estrae flussi di lavoro per settore NACE — obs INPS #407/#406 + #528/#530.

- 407 assunzioni NACE Rev.2 (2014-2024)
- 406 cessazioni NACE Rev.2 (2014-2024)
- 528 assunzioni NACE Rev.2.1 (2025-2026)
- 530 cessazioni NACE Rev.2.1 (2025-2026)

Due grane:
1. nazionale: anno × sesso × settore × tipologia (cols = tipo flusso)
2. regione (issue #4): anno × settore × regione, **cols vuote** —
   la grana con tipologia/sesso tronca il backend (IncompleteRead).

Le etichette NACE non sono chiavi stabili: il clean mappa a codici sezione.
"""
import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))
from common import api_post, flatten_nested

OBS = [
    (407, "assunzione", "rev2"),
    (406, "cessazione", "rev2"),
    (528, "assunzione", "rev2_1"),
    (530, "cessazione", "rev2_1"),
]


def _row(fid: str, order: int) -> dict:
    return {
        "id": fid,
        "label": fid,
        "order": order,
        "expand": "",
        "hide": False,
        "aggregate": fid not in ("anno", "sesso", "COD_NACE_REV2", "regione"),
    }


def payload_nazionale(obs: int) -> dict:
    return {
        "id_osservatorio": str(obs),
        "language": "",
        "totalRow": False,
        "totalColumn": False,
        "subtotalRow": False,
        "subtotalColumn": False,
        "selections": {
            "rows": [_row("anno", 1), _row("sesso", 2), _row("COD_NACE_REV2", 3)],
            "cols": [
                {
                    "id": "ass_tipo_ass_cess",
                    "label": "ass_tipo_ass_cess",
                    "order": 1,
                    "expand": "",
                    "hide": False,
                    "aggregate": True,
                },
            ],
            "measures": [{"id": "NUM_DENUNCE_SUM", "label": "NUM_DENUNCE_SUM", "order": 1}],
            "filters": [],
        },
    }


def payload_regione(obs: int) -> dict:
    """Grana leggera: totali per settore×regione, senza tipologia."""
    return {
        "id_osservatorio": str(obs),
        "language": "",
        "totalRow": False,
        "totalColumn": False,
        "subtotalRow": False,
        "subtotalColumn": False,
        "selections": {
            "rows": [_row("anno", 1), _row("COD_NACE_REV2", 2), _row("regione", 3)],
            "cols": [],
            "measures": [{"id": "NUM_DENUNCE_SUM", "label": "NUM_DENUNCE_SUM", "order": 1}],
            "filters": [],
        },
    }


def fetch(obs: int, payload: dict, dimensione: str, flusso: str, nace_class: str) -> list[dict]:
    print(f"  obs {obs} {dimensione} ({flusso}, {nace_class})...", end=" ", flush=True)
    r = None
    for attempt in range(5):
        try:
            r = api_post("getDatiOsservatorio", payload, timeout=120)
        except Exception as e:
            print(f"\n    tentativo {attempt + 1}: {type(e).__name__}", file=sys.stderr)
            time.sleep(2)
            continue
        if isinstance(r, dict) and ("error" in r or r.get("errorCode")):
            err = r.get("error") or r.get("message") or "unknown"
            print(f"\n    tentativo {attempt + 1}: {str(err)[:80]}", file=sys.stderr)
            time.sleep(2)
            continue
        break
    if r is None or (isinstance(r, dict) and ("error" in r or r.get("errorCode"))):
        err = r.get("error") if isinstance(r, dict) else "unknown"
        print(f"\n  FALLITO obs {obs}/{dimensione}: {err}", file=sys.stderr)
        sys.exit(1)
    flat = flatten_nested(r)
    for row in flat:
        row["dimensione"] = dimensione
        row["flusso"] = flusso
        row["nace_class"] = nace_class
        row["obs"] = str(obs)
    print(f"{len(flat)} righe")
    return flat


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("raw.csv")
    all_rows: list[dict] = []
    for obs, flusso, nace in OBS:
        all_rows += fetch(obs, payload_nazionale(obs), "anno_sesso_settore_tipo", flusso, nace)
    for obs, flusso, nace in OBS:
        all_rows += fetch(obs, payload_regione(obs), "anno_settore_regione", flusso, nace)

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
