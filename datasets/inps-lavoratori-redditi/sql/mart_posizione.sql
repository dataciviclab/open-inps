-- INPS Lavoratori Redditi — MART Posizione prevalente
-- Lavoratori, redditi e settimane per anno, sesso e posizione lavorativa.

SELECT
    anno,
    sesso,
    posizione_prevalente,
    n_lavoratori,
    reddito_cumulato,
    settimane_lavorate
FROM clean_input
WHERE dimensione = 'anno_sesso_posizione'
  AND sesso IN ('Maschi', 'Femmine')
  AND posizione_prevalente IS NOT NULL
  AND n_lavoratori IS NOT NULL
