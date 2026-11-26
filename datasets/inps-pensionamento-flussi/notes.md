# inps-pensionamento-flussi — note

## Fonte

Osservatorio INPS **475** — "Dati trimestrali per regione e gestione".
Copertura anni di decorrenza **2021-2026**, aggiornata al 2026-11-26.

## Lettura dei numeri (importante)

La risposta dell'osservatorio contiene una **gerarchia di totali**, non solo il
dettaglio:

- righe di dettaglio: trimestre I-IV, regione/gestione/categoria valorizzate,
  sesso `Maschi`/`Femmine`;
- totali di trimestre: `Trimestre = 'Totale'` (duplicano la somma dei trimestri);
- totali di dimensione: `Regione = 'Totale'`, `Gestione = 'Totale'`,
  `Categoria = 'Totale'` (duplicano il dettaglio della dimensione);
- totali di sesso: `Sesso = 'Maschi:Totale'` / `'Femmine:Totale'` (totali
  generali, accoppiati ai totali di trimestre/dimensione).

Il clean espone la colonna **`is_totale`**: i mart pubblicano solo
`is_totale = false`. Sommare `n_pensioni` senza questo filtro triplica il dato
(il totale di dettaglio 2021-2026 è 5.343.223 per dimensione; la somma di tutte
le righe clean, totali inclusi, è 16.029.669).

## Formato numerico

`clean.read.all_varchar: true`: le colonne arrivano come stringhe e le macro
lavorano sul formato italiano originale.

- `_FREQ_SUM`: punti migliaia → `remove_dot_thousands`
- età media e importo medio: virgola decimale → `normalize_italian_number`

Senza `all_varchar` lo sniffing tipizza `DOUBLE` alcune colonne e le macro
rifiutano il valore (guardia toolkit): è il motivo del fix del 2026-11-26.

## Etichette di sesso

I totali di sesso arrivano dall'API/flatten come `Maschi:Totale` e
`Femmine:Totale`; il dettaglio come `Maschi`/`Femmine`. Altri osservatori INPS
che usano lo stesso `flatten_nested` possono avere etichette analoghe: da
verificare se si aggiungono nuovi dataset.
