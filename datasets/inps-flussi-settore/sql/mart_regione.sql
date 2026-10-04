-- INPS Flussi Settore — MART Regione (issue #4)
-- Totali assunzioni/cessazioni per anno, settore NACE e regione.
-- Grana leggera senza tipologia (la versione con tipo tronca l'API).

SELECT
    anno,
    flusso,
    nace_class,
    settore_codice,
    settore_nace,
    regione,
    n_rapporti
FROM clean_input
WHERE dimensione = 'anno_settore_regione'
  AND settore_codice IS NOT NULL
  AND regione IS NOT NULL
  AND regione <> ''
  AND n_rapporti IS NOT NULL
