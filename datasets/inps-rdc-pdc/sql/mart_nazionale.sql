-- INPS RdC/PdC — MART Nazionale
-- Nuclei e componenti per anno e misura (RdC vs PdC).

SELECT
    anno,
    misura,
    n_nuclei,
    n_componenti,
    importo_medio_mensile_eur
FROM clean_input
WHERE dimensione = 'anno_misura'
  AND misura IS NOT NULL
  AND n_nuclei IS NOT NULL
