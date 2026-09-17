-- INPS Rapporti Lavoro — MART Eta
-- Assunzioni/cessazioni per anno, sesso, classe di eta.

SELECT
    anno,
    sesso,
    classe_eta,
    n_rapporti
FROM clean_input
WHERE dimensione = 'anno_sesso_eta'
  AND sesso IN ('Maschi', 'Femmine')
  AND (classe_eta IS NULL OR classe_eta NOT LIKE '%Totale%')
