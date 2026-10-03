-- INPS Lavoratori Pubblici — MART Regione
-- Lavoratori e retribuzioni per anno, gruppo contrattuale e regione.

SELECT
    anno,
    gruppo_contrattuale,
    regione,
    n_lavoratori,
    retribuzioni_totali,
    giornate_lavorate
FROM clean_input
WHERE dimensione = 'anno_gruppo_regione'
  AND gruppo_contrattuale IS NOT NULL
  AND regione IS NOT NULL
  AND regione <> ''
  AND n_lavoratori IS NOT NULL
