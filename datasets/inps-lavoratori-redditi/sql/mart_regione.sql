-- INPS Lavoratori Redditi — MART Regione
-- Lavoratori, redditi e settimane per anno, sesso e regione.

SELECT
    anno,
    sesso,
    regione,
    n_lavoratori,
    reddito_cumulato,
    settimane_lavorate
FROM clean_input
WHERE dimensione = 'anno_sesso_regione'
  AND sesso IN ('Maschi', 'Femmine')
  AND regione IS NOT NULL
  AND regione <> ''
  AND n_lavoratori IS NOT NULL
