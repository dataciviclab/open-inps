-- INPS Assegno Unico — MART Regione
-- Figli e nuclei beneficiari per anno e regione.

SELECT
    anno,
    regione,
    dimensione,
    n_figli,
    COALESCE(importo_medio_figlio, importo_medio_nucleo) AS importo_medio
FROM clean_input
WHERE regione IS NULL OR regione NOT LIKE '%Totale%'
