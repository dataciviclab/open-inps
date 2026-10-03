-- INPS Lavoratori Redditi — MART Eta
-- Lavoratori, redditi e settimane per anno, sesso e classe di età.

SELECT
    anno,
    sesso,
    classe_eta,
    n_lavoratori,
    reddito_cumulato,
    settimane_lavorate
FROM clean_input
WHERE dimensione = 'anno_sesso_eta'
  AND sesso IN ('Maschi', 'Femmine')
  AND classe_eta IS NOT NULL
  AND n_lavoratori IS NOT NULL
