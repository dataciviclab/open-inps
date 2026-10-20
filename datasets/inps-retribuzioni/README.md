# INPS Retribuzioni

Lavoratori dipendenti del settore privato non agricolo: retribuzioni, settimane
retribuite e giornate, per regione, classe di età e sezione ATECO 2007.

- **Fonte**: INPS Osservatori Statistici, obs **347** (2014-2018) + **492** (2019-2023)
- **Copertura**: 2014-2023, Italia
- **Grana**: anno × sesso × regione; anno × sesso × età; anno × sezione ATECO
- **Unità territoriale**: regione (incluso “Estero”)

## Misure

| Colonna | Unità | Descrizione |
|---|---|---|
| `n_lavoratori` | persone | Numero di lavoratori nell'anno (non FTE; include part-time e periodi parziali) |
| `retribuzione_totale` | euro | Retribuzione annua dichiarata all'INPS (misura API `RRSUM`) |
| `settimane_retribuite` | settimane | Numero di settimane retribuite nell'anno (misura API `s_retrSUM`) |
| `settimane_utili` | settimane | Numero di settimane utili nell'anno (misura API `UU_TOTSUM`) |
| `giornate_retribuite` | giornate | Numero di giornate retribuite nell'anno (misura API `GGSUM`) |
| `retribuzione_media` | euro | `retribuzione_totale / n_lavoratori` (media per lavoratore, non per FTE) |
| `retribuzione_media_settimana` | euro | `retribuzione_totale / settimane_retribuite` |

`retribuzione_totale` è una retribuzione annua, **non** il netto in busta paga
e **non** il costo azienda: non include i contributi datoriali.

## Settori

`settore_codice` è la sezione ATECO 2007 (B, C, D, E, F, G, H, I, J, K, L, M,
N, P, Q, R, S, T), `settore_nace` è l'etichetta breve stabile, `settore_label`
è l'etichetta grezza dell'API. Le righe di totale hanno `settore_codice` nullo
e vanno escluse dalle analisi per settore.

## Breaking change (2026-10)

Fino a questa revisione il clean mappava:

- `s_retrSUM` → `somma_retribuzioni` (in realtà **settimane retribuite**)
- `UU_TOTSUM` → `unita_lavorative` (in realtà **settimane utili**)

Le colonne sono state rimosse e sostituite da `retribuzione_totale`,
`settimane_retribuite`, `settimane_utili`, `giornate_retribuite`. Chi leggeva
le vecchie colonne come euro deve migrare: i valori precedenti non erano
retribuzioni.

## Limiti

- **Non è un panel di lavoratori**: `n_lavoratori` conta i lavoratori nell'anno,
  non gli FTE. Per confronti di produttività usare `retribuzione_media_settimana`
  o normalizzare per settimane.
- **Rottura 2019**: obs 347 (2014-2018) e obs 492 (2019-2023) sono due tavole
  distinte; la serie 2014-2023 è utilizzabile con nota, ma non è un'unica
  rilevazione.
- **Settore**: la sezione ATECO è quella dichiarata all'INPS; non coincide
  necessariamente con la classificazione delle imprese in altri registri.
- **2024+**: non incluso in questa versione (obs 525 non è ancora estratto).
