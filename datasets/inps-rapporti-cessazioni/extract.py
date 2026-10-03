#!/usr/bin/env python3
"""Estrae cessazioni di rapporti di lavoro per provincia — obs INPS #490 (2014-2026).

Specchio di inps-rapporti-lavoro (#489 assunzioni): stesso patto territoriale,
ma con motivo e tipologia di cessazione.

Nota API: le selections usano i field id della struttura
(anno, sesso, REGIONE2, PROVINCIA2, ass_tipo_ass_cess, ass_tipocessaz).
Le label display ("Sesso", "Regione") non sono stabili su questo osservatorio.

La query provincia × tipo × sesso per tutti gli anni supera il limite di
response del backend (~3.4MB): viene spezzata anno per anno.
"""

import csv
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))
from common import api_post, flatten_nested

OBS_ID = 490
ANNI = list(range(2014, 2027))

QUERIES = {
    "anno_sesso_regione_tipo": {
        "id_osservatorio": "490",
        "language": "",
        "totalRow": True,
        "totalColumn": True,
        "subtotalRow": True,
        "subtotalColumn": True,
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
                    "id": "REGIONE2",
                    "label": "REGIONE2",
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
    },
    "anno_sesso_regione_motivo": {
        "id_osservatorio": "490",
        "language": "",
        "totalRow": True,
        "totalColumn": True,
        "subtotalRow": True,
        "subtotalColumn": True,
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
                    "id": "REGIONE2",
                    "label": "REGIONE2",
                    "order": 3,
                    "expand": "",
                    "hide": False,
                    "aggregate": False,
                },
            ],
            "cols": [
                {
                    "id": "ass_tipocessaz",
                    "label": "ass_tipocessaz",
                    "order": 1,
                    "expand": "",
                    "hide": False,
                    "aggregate": True,
                },
            ],
            "measures": [{"id": "NUM_DENUNCE_SUM", "label": "NUM_DENUNCE_SUM", "order": 1}],
            "filters": [],
        },
    },
}

PROVINCIA_PAYLOAD = {
    "id_osservatorio": "490",
    "language": "",
    "totalRow": True,
    "totalColumn": True,
    "subtotalRow": True,
    "subtotalColumn": True,
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
                "id": "PROVINCIA2",
                "label": "PROVINCIA2",
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
        "filters": [{"id": "anno", "label": "anno", "values": ["{anno}"]}],
    },
}


def query_with_retry(payload: dict, max_retries: int = 3, timeout: int = 120):
    for attempt in range(max_retries):
        r = api_post("getDatiOsservatorio", payload, timeout=timeout)
        if isinstance(r, dict) and ("error" in r or "errorCode" in r):
            err = r.get("error") or r.get("message", "unknown")
            print(f"    tentativo {attempt + 1}: {str(err)[:80]}", file=sys.stderr)
            time.sleep(2)
            continue
        return r
    return None


def run_provincia_per_anno(anni: list[int]) -> list[dict]:
    all_rows: list[dict] = []
    for anno in anni:
        payload = json.loads(json.dumps(PROVINCIA_PAYLOAD).replace("{anno}", str(anno)))
        print(f"    provincia {anno}...", end=" ", flush=True)
        r = query_with_retry(payload)
        if r is None:
            print("timeout/errore")
            continue
        flat = flatten_nested(r)
        for row in flat:
            row["dimensione"] = "anno_sesso_provincia_tipo"
        all_rows.extend(flat)
        print(f"{len(flat)} righe")
        time.sleep(1)
    return all_rows


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("raw.csv")
    all_rows: list[dict] = []

    print("  490 regione × tipo...")
    r = query_with_retry(QUERIES["anno_sesso_regione_tipo"])
    if r is None:
        print("  FALLITO regione×tipo", file=sys.stderr)
        sys.exit(1)
    flat = flatten_nested(r)
    for row in flat:
        row["dimensione"] = "anno_sesso_regione_tipo"
    all_rows.extend(flat)
    print(f"    {len(flat)} righe")

    print("  490 regione × motivo...")
    r = query_with_retry(QUERIES["anno_sesso_regione_motivo"])
    if r is None:
        print("  FALLITO regione×motivo", file=sys.stderr)
        sys.exit(1)
    flat = flatten_nested(r)
    for row in flat:
        row["dimensione"] = "anno_sesso_regione_motivo"
    all_rows.extend(flat)
    print(f"    {len(flat)} righe")

    print("  490 provincia × tipo × sesso (per anno)...")
    all_rows.extend(run_provincia_per_anno(ANNI))

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
