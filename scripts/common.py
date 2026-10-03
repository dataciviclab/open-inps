"""Client comune per l'API Osservatori Statistici INPS.

Backend SAS: JSON senza spazi (separators=(',',':')).
Endpoint: https://servizi2.inps.it/servizi/osservatoristatistici/api/
"""

import csv
import gzip
import json
import sys
from http.client import IncompleteRead
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

API_BASE = "https://servizi2.inps.it/servizi/osservatoristatistici/api"


def api_post(endpoint: str, payload: dict, timeout: int = 60) -> dict:
    url = f"{API_BASE}/{endpoint}/"
    data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    req = Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) DataCivicLab/1.0")
    try:
        with urlopen(req, timeout=timeout) as resp:
            try:
                raw = resp.read()
            except IncompleteRead as e:
                return {
                    "error": f"Response incompleta ({len(e.partial)} bytes): IncompleteRead. "
                    "Ridurre le dimensioni della query o riprovare."
                }
            try:
                raw = gzip.decompress(raw)
            except Exception:
                pass
            try:
                return json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError as e:
                # Response troppo grande o troncata dal backend SAS
                return {
                    "error": f"JSON non valido ({len(raw)} bytes): {e}. "
                    "Probabile response troncata — ridurre le dimensioni della query."
                }
    except URLError as e:
        return {"error": str(e)}
    except TimeoutError as e:
        return {"error": f"Timeout: {e}"}


def get_structure(observatory_id: int) -> dict:
    return api_post(
        "getStrutturaOsservatorio", {"id_osservatorio": observatory_id, "language": "it"}
    )


def get_data(payload: dict) -> dict:
    return api_post("getDatiOsservatorio", payload)


def flatten_nested(data: dict) -> list[dict]:
    """Appiattisce la struttura nested INPS (1-3 livelli di rows)."""
    rows = []

    def walk_node(node: dict, prefix: dict):
        # Se il nodo ha misure dirette (senza columns), e' un leaf
        direct_measures = node.get("measures", [])
        if direct_measures and not node.get("columns"):
            leaf = dict(prefix)
            for m in direct_measures:
                leaf[m["label"]] = m.get("value", "")
            rows.append(leaf)
        # Scendi nelle columns
        for col_group in node.get("columns", []):
            col_dim = col_group.get("col_id", "")
            for col_item in col_group.get("values", []):
                leaf = {**prefix, col_dim: col_item.get("value", "")}
                for m in col_item.get("measures", []):
                    leaf[m["label"]] = m.get("value", "")
                if any(m.get("label") for m in col_item.get("measures", [])):
                    rows.append(leaf)
        # Scendi nei rows
        for row_group in node.get("rows", []):
            row_dim = row_group.get("row_id", "")
            for row_item in row_group.get("values", []):
                walk_node(row_item, {**prefix, row_dim: row_item.get("value", "")})

    for year_val in data.get("values", []):
        walk_node(year_val, {"anno": year_val.get("value", "")})

    return rows


def run_queries(observatory_id: int, queries: dict, output_path: Path) -> int:
    """Esegue piu' query e scrive un CSV unico con colonna `dimensione`. Restituisce il numero di righe."""
    all_rows = []
    for name, payload in queries.items():
        print(f"  {name}...", end=" ", flush=True)
        structure = get_structure(observatory_id)
        if "error" in structure:
            print(f"errore struttura: {structure['error']}", file=sys.stderr)
            continue
        result = get_data(payload)
        if "error" in result:
            print(f"errore: {result['error']}", file=sys.stderr)
            continue
        flat = flatten_nested(result)
        for row in flat:
            row["dimensione"] = name
        all_rows.extend(flat)
        print(f"{len(flat)} righe")

    if not all_rows:
        return 0

    # Unisci colonne (le query possono avere colonne diverse)
    fieldnames = []
    seen = set()
    for row in all_rows:
        for k in row:
            if k not in seen:
                fieldnames.append(k)
                seen.add(k)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_rows)

    return len(all_rows)
