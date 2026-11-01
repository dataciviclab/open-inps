"""Client comune per l'API Osservatori Statistici INPS.

Backend SAS: JSON senza spazi (separators=(',',':')).
Endpoint: https://servizi2.inps.it/servizi/osservatoristatistici/api/
"""

import csv
import gzip
import json
import sys
import time
from http.client import HTTPException, IncompleteRead
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_BASE = "https://servizi2.inps.it/servizi/osservatoristatistici/api"

# Il backend SAS tronca le risposte grandi e ogni tanto chiude la connessione:
# sono guasti transitori, non errori di query. Un secondo tentativo li assorbe.
API_RETRIES = 3
API_BACKOFF_SECONDS = 2.0
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) DataCivicLab/1.0"


def _post_once(url: str, data: bytes, timeout: int) -> tuple[str, object]:
    """Una singola POST. Ritorna ``("ok", dict)`` o ``(esito, messaggio)``.

    ``esito`` vale ``"transient"`` per i guasti che ha senso ritentare
    (troncamento, timeout, connessione, HTTP 5xx) e ``"fatal"`` per quelli
    che non cambierebbero con un altro tentativo (HTTP 4xx).
    """
    req = Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", USER_AGENT)
    try:
        with urlopen(req, timeout=timeout) as resp:
            try:
                raw = resp.read()
            except IncompleteRead as e:
                return (
                    "transient",
                    f"Response incompleta ({len(e.partial)} bytes): IncompleteRead. "
                    "Il backend ha troncato la risposta.",
                )
            try:
                raw = gzip.decompress(raw)
            except Exception:
                pass
            try:
                return "ok", json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError as e:
                return (
                    "transient",
                    f"JSON non valido ({len(raw)} bytes): {e}. "
                    "Probabile response troncata dal backend.",
                )
    except HTTPError as e:
        # 429 è un 4xx ma transitorio: è il rate-limit del backend.
        esito = "transient" if e.code >= 500 or e.code == 429 else "fatal"
        return esito, f"HTTP {e.code}: {e.reason}"
    except (HTTPException, ConnectionResetError) as e:
        # Il backend chiude la connessione durante la request o a metà
        # risposta: RemoteDisconnected è un ConnectionResetError, gli altri
        # guasti del protocollo sono HTTPException. IncompleteRead è già
        # gestito sopra, con il conteggio dei byte ricevuti.
        return "transient", f"Connessione interrotta ({type(e).__name__}): {e}"
    except URLError as e:
        return "transient", str(e)
    except TimeoutError as e:
        return "transient", f"Timeout: {e}"


def api_post(endpoint: str, payload: dict, timeout: int = 60, retries: int = API_RETRIES) -> dict:
    """POST verso l'API osservatori INPS, con retry sui guasti transitori.

    Solo dopo ``retries`` tentativi l'errore torna al chiamante come
    ``{"error": ...}``, che i dataset script traducono in fallimento.
    """
    url = f"{API_BASE}/{endpoint}/"
    data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    messaggio = ""
    for tentativo in range(1, retries + 1):
        esito, valore = _post_once(url, data, timeout)
        if esito == "ok":
            return valore  # type: ignore[return-value]
        messaggio = str(valore)
        if esito == "fatal":
            break
        if tentativo < retries:
            time.sleep(API_BACKOFF_SECONDS * tentativo)
    return {"error": messaggio}


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
