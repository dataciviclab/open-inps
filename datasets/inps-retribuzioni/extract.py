#!/usr/bin/env python3
"""Estrae retribuzioni lavoro privato — obs INPS #347 (2014-2018) + #492 (2019-2023).

Il backend SAS non gestisce la dimensione 'Tipologia contrattuale' come colonna.
L'estrazione usa solo rows (anno, sesso, regione) con le misure dirette.
"""
import sys, csv, time, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))
from common import api_post, flatten_nested

ANNO_SESSO_REGIONE = {
    "id_osservatorio": "{obs}", "language": "",
    "totalRow": True, "totalColumn": True, "subtotalRow": True, "subtotalColumn": True,
    "selections": {
        "rows": [
            {"id": "Anno", "label": "Anno", "order": 1, "expand": "", "hide": False, "aggregate": False},
            {"id": "Sesso", "label": "Sesso", "order": 2, "expand": "", "hide": False, "aggregate": False},
            {"id": "Regione", "label": "Regione", "order": 3, "expand": "", "hide": False, "aggregate": False},
        ],
        "cols": [],
        "measures": [
            {"id": "lav_annoSUM", "label": "lav_annoSUM", "order": 1},
            {"id": "s_retrSUM", "label": "s_retrSUM", "order": 2},
            {"id": "UU_TOTSUM", "label": "UU_TOTSUM", "order": 3},
        ],
        "filters": [],
    },
}

ANNO_SESSO_ETA = {
    "id_osservatorio": "{obs}", "language": "",
    "totalRow": True, "totalColumn": True, "subtotalRow": True, "subtotalColumn": True,
    "selections": {
        "rows": [
            {"id": "Anno", "label": "Anno", "order": 1, "expand": "", "hide": False, "aggregate": False},
            {"id": "Sesso", "label": "Sesso", "order": 2, "expand": "", "hide": False, "aggregate": False},
        ],
        "cols": [
            {"id": "CLASSI DI ETA", "label": "CLASSI DI ETA", "order": 1, "expand": "", "hide": False, "aggregate": True},
        ],
        "measures": [
            {"id": "lav_annoSUM", "label": "lav_annoSUM", "order": 1},
            {"id": "s_retrSUM", "label": "s_retrSUM", "order": 2},
        ],
        "filters": [],
    },
}


def query_with_retry(payload, max_retries=3, timeout=120):
    for attempt in range(max_retries):
        try:
            r = api_post("getDatiOsservatorio", payload, timeout=timeout)
            if "error" in r or "errorCode" in r:
                err = r.get("error") or r.get("message", "unknown")
                print(f"    tentativo {attempt+1}: {str(err)[:60]}", file=sys.stderr)
                time.sleep(2)
                continue
            return r
        except Exception as e:
            print(f"    tentativo {attempt+1}: {type(e).__name__}", file=sys.stderr)
            time.sleep(3)
    return None


def run_split_query(obs_id, base_payload, anno_range, label):
    all_flat = []
    for anno in anno_range:
        payload = json.loads(json.dumps(base_payload).replace("{obs}", str(obs_id)))
        payload["selections"]["filters"] = [{"id": "acomp", "label": "Anno", "values": [str(anno)]}]
        print(f"    {anno}...", end=" ", flush=True)
        r = query_with_retry(payload)
        if r is None:
            print("timeout/errore")
            continue
        flat = flatten_nested(r)
        all_flat.extend(flat)
        print(f"{len(flat)} righe")
        time.sleep(1)
    return all_flat


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("raw.csv")
    all_rows = []

    # #347: 2014-2018
    print("  347 (2014-2018)...")
    flat = run_split_query(347, ANNO_SESSO_REGIONE, range(2014, 2019), "347")
    for row in flat:
        row["dimensione"] = "anno_sesso_regione"
        row["fonte"] = "347"
    all_rows.extend(flat)

    # #492: 2019-2023 — regione
    print("  492 regione (2019-2023)...")
    flat = run_split_query(492, ANNO_SESSO_REGIONE, range(2019, 2024), "492")
    for row in flat:
        row["dimensione"] = "anno_sesso_regione"
        row["fonte"] = "492"
    all_rows.extend(flat)

    # #492: 2019-2023 — eta
    print("  492 eta (2019-2023)...")
    flat = run_split_query(492, ANNO_SESSO_ETA, range(2019, 2024), "492")
    for row in flat:
        row["dimensione"] = "anno_sesso_eta"
        row["fonte"] = "492"
    all_rows.extend(flat)

    if all_rows:
        fieldnames = []
        seen = set()
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
