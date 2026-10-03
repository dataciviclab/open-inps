-- INPS Assegno Unico — MART Regione
-- Figli beneficiari per anno e regione.
-- Grain unico: solo dimensione 'figli_anno_regione'.
-- I nuclei (nuclei_anno_regione) restano nel clean, non in questo mart:
-- la colonna n_figli non è commisurabile tra figli e nuclei.

SELECT
    anno,
    regione,
    n_figli,
    importo_medio_figlio
FROM clean_input
WHERE dimensione = 'figli_anno_regione'
  AND (regione IS NULL OR regione NOT LIKE '%Totale%')
