# Pensioni INPS

Dati sulle pensioni erogate dall'INPS: vigenti e liquidate, per sesso, importo, eta, regione.

- **Fonte**: [INPS Osservatori Statistici](https://servizi2.inps.it/servizi/osservatoristatistici/)
- **API**: JSON non documentata (backend SAS, body senza spazi)
- **Copertura**: 2021-2026

## Dataset

| Dataset | Obs ID | Cosa | Anni |
|---|---|---|---|
| `inps-pensioni-vigenti` | 378 | Stock in pagamento per sesso, importo, eta, regione | 2022-2026 |
| `inps-pensioni-liquidate` | 370 | Nuove pensioni per sesso, importo, regione | 2021-2025 |

## Setup

```bash
pip install -r requirements.txt
```

## Uso

```bash
make run       # pipeline toolkit completa
make check     # valida config
make extract   # estrai dati direttamente
make clean     # pulisci output
```

## Struttura

```
├── scripts/
│   ├── common.py                  # API client INPS (condiviso)
│   ├── extract_vigenti.py         # obs 378
│   └── extract_liquidate.py       # obs 370
├── datasets/
│   ├── inps-pensioni-vigenti/
│   │   ├── dataset.yml
│   │   └── sql/ (clean.sql, mart.sql)
│   └── inps-pensioni-liquidate/
│       ├── dataset.yml
│       └── sql/ (clean.sql, mart.sql)
├── Makefile
├── NOTE.md                        # documentazione API
└── catalog.json                   # 194 osservatori INPS
```
