# Open INPS

Sistema di intelligence sui dati INPS: pensioni, lavoro, CIG, NASpI.

- **Fonte**: [INPS Osservatori Statistici](https://servizi2.inps.it/servizi/osservatoristatistici/)
- **API**: JSON non documentata (backend SAS, body senza spazi)
- **Copertura**: 2014-2026

## Dataset

| Dataset | Obs ID | Cosa | Anni | Mart |
|---|---|---|---|---|
| `inps-pensioni-vigenti` | 378 | Stock pensioni per sesso, importo, eta, regione | 2022-2026 | 3 |
| `inps-pensioni-liquidate` | 370 | Nuove pensioni per sesso, importo, regione | 2021-2025 | 2 |
| `inps-rapporti-lavoro` | 489 | Assunzioni/cessazioni per provincia, sesso, settore | 2014-2026 | 3 |
| `inps-naspi` | 395+396 | Beneficiari e trattamenti NASpI | 2020-2024 | 3 |
| `inps-cig` | 512 | Ore CIG autorizzate per gestione, ramo | 2023-2026 | 3 |

**Totale**: 5 dataset, 14 mart

## Setup

```bash
pip install -r requirements.txt
```

## Uso

```bash
make run           # pipeline toolkit completa
make check         # valida config
make registry      # genera registry.json (dry-run)
make registry-write # scrivi registry.json
make clean         # pulisci output
```

## Struttura

```
├── scripts/common.py              # API client INPS (condiviso)
├── datasets/
│   ├── inps-pensioni-vigenti/
│   ├── inps-pensioni-liquidate/
│   ├── inps-rapporti-lavoro/
│   ├── inps-naspi/
│   └── inps-cig/
├── registry/registry.json         # artifact catalog
├── Makefile
├── NOTE.md                        # documentazione API
├── catalog.json                   # 194 osservatori INPS
└── out/                           # output pipeline
```
