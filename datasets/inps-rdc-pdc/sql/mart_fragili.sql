-- INPS RdC/PdC — MART Nuclei fragili
-- Nuclei per anno, misura, presenza disabili e minori.

SELECT
    anno,
    misura,
    con_disabili,
    con_minori,
    n_nuclei,
    n_componenti,
    importo_medio_mensile_eur
FROM clean_input
WHERE dimensione IN ('anno_misura_disabili', 'anno_misura_minori')
  AND misura IS NOT NULL
  AND n_nuclei IS NOT NULL
