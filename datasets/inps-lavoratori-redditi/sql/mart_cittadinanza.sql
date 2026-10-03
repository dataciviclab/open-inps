-- INPS Lavoratori Redditi — MART Cittadinanza
-- Lavoratori, redditi e settimane per anno, sesso e cittadinanza.

SELECT
    anno,
    sesso,
    cittadinanza,
    n_lavoratori,
    reddito_cumulato,
    settimane_lavorate
FROM clean_input
WHERE dimensione = 'anno_sesso_cittadinanza'
  AND sesso IN ('Maschi', 'Femmine')
  AND cittadinanza IS NOT NULL
  AND n_lavoratori IS NOT NULL
