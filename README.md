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
| `inps-pensioni-serie` | 390+376 | Serie storica: vigenti 1998-2026, liquidate 1997-2025 | 1997-2026 | 3 |
| `inps-pensionamento-flussi` | 475 | Flussi trimestrali per decorrenza: regione, gestione, categoria | 2021-2026 | 3 |
| `inps-lavoratori-pubblici` | 435 | Lavoratori PA: retribuzioni, giornate per comparto, eta, contratto, regione | 2014-2024 | 4 |
| `inps-lavoratori-redditi` | 465 | Lavoratori, redditi e settimane per posizione, regione, eta, cittadinanza | 2014-2024 | 4 |
| `inps-rdc-pdc` | 452 | Nuclei RdC/PdC: misura, regione, componenti, disabili, minori | 2019-2023 | 4 |
| `inps-rapporti-lavoro` | 489 | Assunzioni per provincia, sesso, tipo | 2014-2026 | 3 |
| `inps-rapporti-cessazioni` | 490 | Cessazioni per provincia, sesso, tipo e motivo | 2014-2026 | 3 |
| `inps-flussi-settore` | 407+406+528+530 | Assunzioni e cessazioni per settore NACE (nazionale) | 2014-2026 | 1 |
| `inps-retribuzioni` | 347+492 | Retribuzioni e lavoratori privato per regione, eta | 2014-2023 | 2 |
| `inps-naspi` | 395+396 | Beneficiari e trattamenti NASpI per eta, durata | 2020-2024 | 3 |
| `inps-cig` | 512 | Ore CIG autorizzate per gestione, ramo, mese | 2023-2026 | 3 |
| `inps-assegno-unico` | 498+499 | Assegno Unico: figli e nuclei per ISEE, regione | 2022-2024 | 2 |
| `inps-dipendenti-pubblici` | 440 | Dipendenti pubblici: enti, retribuzioni, forma giuridica | 2022-2026 | 2 |

**Totale**: 16 dataset, 46 mart

> **Nota definizioni pensioni**: `inps-pensioni-serie` (376) conta le pensioni
> liquidate nell'anno (~1,5M/anno). `inps-pensionamento-flussi` (475) conta i
> flussi con decorrenza nel trimestre (~0,9M/anno, ~58% del totale) — universo
> più ristretto, utile per stagionalità e mix gestione. Non sommare i due.

> **Nota PA**: `inps-dipendenti-pubblici` (440) = enti e giornate per forma
> giuridica. `inps-lavoratori-pubblici` (435) = lavoratori e retribuzioni per
> gruppo contrattuale (complementare, non sovrapponibile). Campo SESSO rotto
> sull'obs 435: nessuna dimensione genere.

> **Nota redditi**: `inps-lavoratori-redditi` (465) è il ponte lavoro→reddito
> (posizione prevalente, settimane, cittadinanza). Dipendente pubblico 465
> (~3,7M) ≈ lavoratori PA 435 — definizioni diverse, non sommare.

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
│   ├── inps-pensioni-serie/
│   ├── inps-pensionamento-flussi/
│   ├── inps-lavoratori-pubblici/
│   ├── inps-lavoratori-redditi/
│   ├── inps-rdc-pdc/
│   ├── inps-rapporti-lavoro/
│   ├── inps-rapporti-cessazioni/
│   ├── inps-flussi-settore/
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
