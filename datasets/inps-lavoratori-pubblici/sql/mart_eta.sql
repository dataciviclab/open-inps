-- INPS Lavoratori Pubblici — MART Eta
-- Lavoratori e retribuzioni per anno, gruppo contrattuale e classe di età.

SELECT
    anno,
    gruppo_contrattuale,
    classe_eta,
    n_lavoratori,
    retribuzioni_totali,
    giornate_lavorate
FROM clean_input
WHERE dimensione = 'anno_gruppo_eta'
  AND gruppo_contrattuale IS NOT NULL
  AND classe_eta IS NOT NULL
  AND n_lavoratori IS NOT NULL
