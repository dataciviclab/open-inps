# INPS Osservatori Statistici — API JSON scoperta

**Data**: 2026-09-17
**Contesto**:ricerca fonti dati pensionistiche per il Lab

## Il problema

Il catalogo open data INPS (`opendata.inps.it`) è datato per le pensioni — i dataset CKAN sono fermi al 2012-2014. Gli Osservatori Statistici (`servizi2.inps.it/servizi/osservatoristatistici/`) contengono dati aggiornati al 2026, ma sono presentati come SPA Angular con download Excel generato lato client.

## La scoperta

 Dietro la SPA c'è un'**API JSON** che funziona, con un backend SAS.

### Endpoint

Base: `https://servizi2.inps.it/servizi/osservatoristatistici/api/`

| Endpoint | Metodo | Funzione |
|---|---|---|
| `getAlberoNavigazione/` | POST | Albero tematico completo (24 aree, 194 osservatori) |
| `getStrutturaOsservatorio/` | POST | Struttura (dimensioni, misure, valori distinti) |
| `getFiltriOsservatorio/` | POST | Filtri disponibili |
| `getDatiOsservatorio/` | POST | **Dati grezzi** |
| `getAllegato/?idAllegato=N` | GET | Download allegati (PDF) |

### Formato body (CRITICO)

Il backend **SAS non accetta spazi nel JSON**. Usare sempre:
```python
json.dumps(payload, separators=(',', ':'))
```

### Formato richiesta getDatiOsservatorio

```json
{
  "id_osservatorio": "378",
  "language": "",
  "totalRow": true,
  "totalColumn": true,
  "subtotalRow": true,
  "subtotalColumn": true,
  "selections": {
    "rows": [
      {"id": "Anno-", "label": "Anno-", "order": 1, "expand": "", "hide": false, "aggregate": false}
    ],
    "cols": [
      {"id": "Classi di importo", "label": "Classi di importo", "order": 1, "expand": "", "hide": false, "aggregate": true}
    ],
    "measures": [
      {"id": "_FREQ_SUM", "label": "_FREQ_SUM", "order": 1}
    ],
    "filters": [
      {"id": "anno", "label": "Anno-", "values": ["2026"]}
    ]
  }
}
```

**Regole per rows/cols:**
- `id` = Hierarchy Name dalla struttura (es. `"Anno-"`, `"Sesso-"`, `"Classi di importo"`, `"Regione"`)
- `label` = stessa cosa di `id`
- `aggregate` = `true` per le colonne, `false` per le righe

**Regole per filters:**
- `id` = field ID (es. `"anno"`, `"SESSO"`, `"regione"`)
- `label` = Hierarchy Name (es. `"Anno-"`, `"Sesso-"`, `"Regione"`)
- `values` = array di stringhe (es. `["2026"]`, `["Maschi"]`)

**Regole per measures:**
- `id` = measure field ID (es. `"_FREQ_SUM"`, `"Età media"`, `"tot_impSUM"`, `"Importo medio mensile"`)

### Headers richiesti

```
Content-Type: application/json
User-Agent: Mozilla/5.0  (o qualsiasi)
```

Non serve autenticazione. Non serve cookie (ma non nuoce).

## Misure disponibili (obs 378)

| ID | Significato |
|---|---|
| `_FREQ_SUM` | Numero di pensioni (conteggio) |
| `tot_impSUM` | Importo totale annuo (migliaia di euro) |
| `Importo medio mensile` | Importo medio mensile (euro) |
| `Età media` | Età media dei pensionati |

## Catalogo osservatori

File: `catalog.json` — 194 osservatori totali, 29 relativi alle pensioni.

### Osservatori chiave per il tema pensioni

| ID | Nome | Anni | Dimensioni |
|---|---|---|---|
| 378 | Complesso pensioni vigenti | 2022-2026 | Anno, Sesso, 16 classi importo, 14 fasce età, 20 regioni, 106 province, 6 tipi gestione, 31 gestioni |
| 370 | Complesso pensioni liquidate | 2022-2026 | Stesse di 378 |
| 475 | Flussi trimestrali per regione e gestione | trimestrale | Anno decorrenza, Regione, Trimestre, Sesso, Gestione, Categoria |
| 388 | Per anno di decorrenza | 2022-2026 | Anno, Anno decorrenza, Sesso, Categoria, Sottocategoria, Tipo gestione |
| 389 | Per regime di liquidazione | 2022-2026 | — |
| 380 | Integrate al trattamento minimo | 2022-2026 | — |
| 504 | Maggiorazioni sociali | 2022-2026 | — |
| 381-384 | Invalidi civili | 2022-2026 | — |
| 410-416 | Beneficiari e prestazioni totali | 2022-2026 | — |

## Script di estrazione

File: `extract.py`

```bash
# Scoprire struttura
python extract.py --observatory 378 --structure

# Estrarre dati (query predefinite per 378)
python extract.py --observatory 378

# Estrarre singola query
python extract.py --observatory 378 --query anno_sesso_importo
```

### Query predefinite per obs 378

- `anno_sesso_importo`: Pensioni per anno, sesso, classe di importo (170 righe)
- `anno_sesso_eta`: Pensioni per anno, sesso, classe di età (150 righe)
- `anno_regione`: Pensioni per anno, regione, sesso (300 righe)

## Formato risposta

Risposta nested:
```
values[] → rows[] → values[] → columns[] → values[] → measures[]
```

Per appiattire in CSV: la funzione `flatten_nested()` in extract.py gestisce la struttura.

## Limiti e rischi

1. **Anni disponibili**:2022-2026 (l'osservatorio 378 non ha dati prima del 2022)
2. **Backend SAS**: fragili — gli spazi nel JSON rompono tutto
3. **Nessuna documentazione ufficiale**: l'API non è documentata, potrebbe cambiare
4. **Rate limiting**: non testato sistematicamente, ma le chiamate in serie funzionano (~7s ciascuna)
5. **Dati aggregati**: non ci sono microdati, solo aggregati per dimensioni

## Cross-reference con altre fonti

- **ISTAT Casellario dei Pensioni** (SDMX): 2012-2022, granularità territoriale simile ma senza la dimensione importo
- **Dataset 6002 DAM INPS**: JSON trimestrale 2017-Q2 2024, dimensioni simili ma URL non verificato
- **DoveVannoINostriSoldi**: ha integrato dati INPS da PDF (obs 388) e ISTAT SDMX — il nostro script automatizza ciò che loro fanno manualmente
