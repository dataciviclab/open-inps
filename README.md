# Open INPS

Sistema di intelligence sui dati INPS: pensioni, lavoro, CIG, NASpI, welfare.

- **Fonte**: [INPS Osservatori Statistici](https://servizi2.inps.it/servizi/osservatoristatistici/)
- **API**: JSON non documentata (backend SAS, body senza spazi)
- **Copertura**: 2014-2026

## Dataset

| Dataset | Obs ID | Cosa | Anni | Mart |
|---|---|---|---|---|
| `inps-pensioni-vigenti` | 378 | Stock pensioni per sesso, importo, eta, regione | 2022-2026 | 3 |
| `inps-pensioni-liquidate` | 370 | Nuove pensioni per sesso, importo, regione | 2021-2025 | 2 |
| `inps-rapporti-lavoro` | 489 | Assunzioni/cessazioni per provincia, sesso, tipo | 2014-2026 | 3 |
| `inps-retribuzioni` | 347+492 | Retribuzioni e lavoratori privato per regione, eta | 2014-2023 | 2 |
| `inps-naspi` | 395+396 | Beneficiari e trattamenti NASpI per eta, durata | 2020-2024 | 3 |
| `inps-cig` | 512 | Ore CIG autorizzate per gestione, ramo, mese | 2023-2026 | 3 |
| `inps-assegno-unico` | 498+499 | Assegno Unico: figli e nuclei per ISEE, regione | 2022-2024 | 2 |
| `inps-dipendenti-pubblici` | 440 | Dipendenti pubblici: enti, retribuzioni, forma giuridica | 2022-2026 | 2 |

**Totale**: 8 dataset, 20 mart

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
│   ├── inps-retribuzioni/
│   ├── inps-naspi/
│   ├── inps-cig/
│   ├── inps-assegno-unico/
│   └── inps-dipendenti-pubblici/
├── registry/registry.json         # artifact catalog
├── Makefile
├── NOTE.md                        # documentazione API
├── catalog.json                   # 194 osservatori INPS
└── out/                           # output pipeline
```
