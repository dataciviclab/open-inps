-- INPS Retribuzioni — MART Eta
-- Lavoratori e retribuzioni per anno, sesso, classe di eta.

SELECT
    anno,
    fonte,
    sesso,
    classe_eta,
    n_lavoratori,
    somma_retribuzioni
FROM clean_input
WHERE dimensione = 'anno_sesso_eta'
  AND sesso IN ('Maschi', 'Femmine')
  AND (classe_eta IS NULL OR classe_eta NOT LIKE '%Totale%')
