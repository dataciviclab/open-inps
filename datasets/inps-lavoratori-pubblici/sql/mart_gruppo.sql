-- INPS Lavoratori Pubblici — MART Gruppo contrattuale
-- Lavoratori, retribuzioni e giornate per anno e comparto PA.

SELECT
    anno,
    gruppo_contrattuale,
    n_lavoratori,
    retribuzioni_totali,
    giornate_lavorate,
    settimane_retribuite,
    unita_lavorative
FROM clean_input
WHERE dimensione = 'anno_gruppo'
  AND gruppo_contrattuale IS NOT NULL
  AND gruppo_contrattuale <> ''
  AND n_lavoratori IS NOT NULL
