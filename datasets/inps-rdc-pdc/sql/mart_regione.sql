-- INPS RdC/PdC — MART Regione
-- Nuclei e componenti per anno, misura e regione.

SELECT
    anno,
    misura,
    regione,
    n_nuclei,
    n_componenti,
    importo_medio_mensile_eur
FROM clean_input
WHERE dimensione = 'anno_misura_regione'
  AND misura IS NOT NULL
  AND regione IS NOT NULL
  AND regione <> ''
  AND n_nuclei IS NOT NULL
