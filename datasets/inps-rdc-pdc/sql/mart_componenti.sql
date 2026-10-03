-- INPS RdC/PdC — MART Componenti
-- Nuclei per anno, misura e numero di componenti del nucleo.

SELECT
    anno,
    misura,
    componenti_nucleo,
    n_nuclei,
    n_componenti,
    importo_medio_mensile_eur
FROM clean_input
WHERE dimensione = 'anno_misura_componenti'
  AND misura IS NOT NULL
  AND componenti_nucleo IS NOT NULL
  AND n_nuclei IS NOT NULL
