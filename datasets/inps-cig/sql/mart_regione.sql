-- INPS CIG — MART Regione
-- Ore CIG per anno, regione, gestione.

SELECT
    anno,
    regione,
    gestione,
    oretot
FROM clean_input
WHERE dimensione = 'anno_regione_gestione'
  AND (regione IS NULL OR regione NOT LIKE '%Totale%')
