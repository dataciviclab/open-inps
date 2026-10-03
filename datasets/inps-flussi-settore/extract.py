#!/usr/bin/env python3
"""Estrae flussi di lavoro per settore NACE — obs INPS #407/#406 + #528/#530.

- 407 assunzioni NACE Rev.2 (2014-2024)
- 406 cessazioni NACE Rev.2 (2014-2024)
- 528 assunzioni NACE Rev.2.1 (2025-2026)
- 530 cessazioni NACE Rev.2.1 (2025-2026)

Solo grana nazionale (anno × sesso × settore × tipologia).
Il backend usa etichette display come chiavi di colonna.

Nota: la grana settore × regione non è estratta qui — le response
monolitiche per anno × sesso troncano (IncompleteRead ~3.3MB).
Da aggiungere in un passo dedicato con grana più leggera.
"""

import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))
from common import api_post, flatten_nested


def payload(obs: int) -> dict:
    return {
        "id_osservatorio": str(obs),
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
                {
                    "id": "COD_NACE_REV2",
                    "label": "COD_NACE_REV2",
                    "order": 3,
                    "expand": "",
                    "hide": False,
                    "aggregate": False,
                },
            ],
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


def fetch(obs: int, dimensione: str, flusso: str, nace_class: str) -> list[dict]:
    print(f"  obs {obs} settore nazionale ({flusso}, {nace_class})...", end=" ", flush=True)
    r = None
    for attempt in range(5):
        try:
            r = api_post("getDatiOsservatorio", payload(obs), timeout=120)
        except Exception as e:
            print(f"\n    tentativo {attempt + 1}: {type(e).__name__}", file=sys.stderr)
            time.sleep(2)
            continue
        if isinstance(r, dict) and "error" in r:
            print(f"\n    tentativo {attempt + 1}: {str(r['error'])[:80]}", file=sys.stderr)
            time.sleep(2)
            continue
        break
    if r is None or (isinstance(r, dict) and "error" in r):
        err = r.get("error") if isinstance(r, dict) else "unknown"
        print(f"\n  FALLITO obs {obs}: {err}", file=sys.stderr)
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
    all_rows += fetch(407, "anno_sesso_settore_tipo", "assunzione", "rev2")
    all_rows += fetch(406, "anno_sesso_settore_tipo", "cessazione", "rev2")
    all_rows += fetch(528, "anno_sesso_settore_tipo", "assunzione", "rev2_1")
    all_rows += fetch(530, "anno_sesso_settore_tipo", "cessazione", "rev2_1")

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
