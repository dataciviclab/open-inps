-- INPS Dipendenti Pubblici — MART Regione
-- Enti, giornate e retribuzioni per anno, regione, tipo ente.

SELECT
    anno,
    regione,
    tipo_ente,
    n_enti,
    giorni_totali,
    retribuzione_totale
FROM clean_input
WHERE dimensione = 'anno_regione'
  AND (regione IS NULL OR regione NOT LIKE '%Totale%')
