-- INPS Retribuzioni — MART Regione
-- Lavoratori e retribuzioni per anno, sesso, regione.

SELECT
    anno,
    fonte,
    sesso,
    regione,
    n_lavoratori,
    somma_retribuzioni,
    unita_lavorative
FROM clean_input
WHERE dimensione = 'anno_sesso_regione'
  AND sesso IN ('Maschi', 'Femmine')
  AND (regione IS NULL OR regione NOT LIKE '%Totale%')
