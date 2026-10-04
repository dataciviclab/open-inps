# Open INPS 🇮🇹 — pensioni, lavoro e welfare, aperti e interrogabili

**17 dataset INPS su mercato del lavoro, pensioni e welfare — da assunzioni e cessazioni a NASpI, RdC/PdC e DIS-COLL — pronti per SQL, dashboard e analisi civiche.**

I cataloghi open data INPS sulle pensioni sono fermi al 2012–2014. Gli Osservatori Statistici contengono serie aggiornate al 2026: qui le raccogliamo, normalizziamo in parquet e componiamo in metriche nazionali e territoriali.

## Perché questi dati

- **Mercato del lavoro**: assunzioni vs cessazioni per provincia, sesso e settore NACE — non solo il lato “ingresso”.
- **Pensioni**: stock recente **e** serie storica 1997–2026, più flussi trimestrali di pensionamento.
- **Welfare**: NASpI, DIS-COLL, Reddito/Pensione di Cittadinanza, Assegno Unico, CIG.
- **Ponte lavoro→redditi**: lavoratori, reddito cumulato e settimane per posizione prevalente e cittadinanza.
- **PA**: lavoratori pubblici per comparto, età e retribuzioni (non solo contare gli enti).

## Cosa contengono

| | |
|---|---|
| **Dataset** | **17** toolkit + 1 compose multi-dataset |
| **Mart analitici** | **47** |
| **Periodo** | 1997 — 2026 (a seconda della serie) |
| **Granularità** | Nazionale, regionale, provinciale, settore NACE |
| **Formato** | Parquet (clean/mart) + registry JSON |
| **Fonte** | [INPS Osservatori Statistici](https://servizi2.inps.it/servizi/osservatoristatistici/) |

### Temi coperti

| Tema | Esempi |
|---|---|
| 💼 Lavoro | Assunzioni, cessazioni, settore NACE, retribuzioni private |
| 🏛️ Pubblico | Comparti PA, retribuzioni, giornate |
| 🏦 Pensioni | Vigenti, liquidate, serie storica, pensionamento trimestrale |
| 🛡️ Disoccupazione | NASpI, DIS-COLL (co.co.co) |
| 🏠 Welfare | RdC/PdC, Assegno Unico, CIG |
| 💰 Redditi | Posizione prevalente, settimane, cittadinanza |

Dettaglio per osservatorio: [NOTE.md](NOTE.md) · Catalogo fonte: [catalog.json](catalog.json) (194 osservatori).

## Esempi di domande

1. Quante **cessazioni** ci sono per ogni assunzione, per regione e per settore?
2. Come è cambiato lo **stock di pensioni** dal 1998, e quanti ne entrano oggi (decorrenza trimestrale)?
3. Chi beneficia di **DIS-COLL** rispetto alla NASpI, e com’è il gap di genere su assunzioni e cessazioni?
4. Quanti sono i **lavoratori pubblici** per comparto, e quanto pagano di retribuzione media?
5. Come si distribuiscono i **nuclei RdC/PdC** per regione e composizione del nucleo?

## Come accedere

### 1. Dashboard locale (più rapida)

```bash
git clone https://github.com/dataciviclab/open-inps.git
cd open-inps
pip install -e ".[dashboard]"
make run && make compose
make dashboard
```

Pagine: Panoramica, Genere, Territorio, Pensioni, Lavoro, Welfare, Tabelle.

### 2. DuckDB / SQL sui parquet

```bash
duckdb -c "
SELECT anno, SUM(valore) AS assunzioni
FROM 'out/data/mart/inps_analisi/2026/mart_nazionale.parquet'
WHERE metrica = 'rapporti_lavoro' AND sesso IN ('Maschi','Femmine')
GROUP BY 1 ORDER BY 1;
"
```

### 3. Pipeline toolkit (rigenerare tutto)

```bash
make run       # 17 dataset
make compose   # inps-analisi (14 metriche)
make test
```

Registry machine-readable: [`registry/registry.json`](registry/registry.json).

## Limiti e definizioni (da leggere)

- **API INPS non documentata** (backend SAS): il catalogo ufficiale open data non basta; l’endpoint Osservatori è stabile al momento ma non è un contratto pubblico. Dettagli in [NOTE.md](NOTE.md).
- **Non sommare metriche con definizioni diverse**: es. pensioni liquidate/anno (376) vs flussi per decorrenza trimestrale (475); lavoratori PA 435 vs enti 440; dipendente pubblico 465 ≈ 435.
- **DIS-COLL**: grana nazionale per sesso; nel 2022 la serie 397 è irregolare nella fonte; `importo_fonte` non validato come euro assoluti.
- **Obs 435 (PA)**: campo SESSO rotto sull’API — nessuna dimensione genere.
- **Anni parziali**: 2025–2026 spesso incompleti sulle serie più lente (welfare, redditi).

## Approfondimenti

- Analisi e discussioni: [dataciviclab/dataciviclab](https://github.com/dataciviclab/dataciviclab/discussions)
- Contesto Lab: [dataciviclab.org](https://dataciviclab.org/)

## Partecipa

- **Discussion**: proponi domande di analisi o segnala serie mancanti
- **Issue**: bug di estrazione, mapping territoriale, nuovi osservatori del catalogo
- **PR**: nuovi dataset dal catalogo `catalog.json` (194 osservatori, ne abbiamo coperti 17+)

Contributi e standard del Lab: [CONTRIBUTING.md](CONTRIBUTING.md).

## Licenza

Codice: [MIT](LICENSE). Dati INPS: termini della fonte (Osservatori Statistici INPS).
