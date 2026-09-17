-- INPS Assegno Unico — MART ISEE
-- Figli beneficiari per anno e fascia ISEE.

SELECT
    anno,
    fascia_isee,
    n_figli,
    importo_medio_figlio
FROM clean_input
WHERE dimensione = 'figli_anno_isee'
  AND (fascia_isee IS NULL OR fascia_isee NOT LIKE '%Totale%')
