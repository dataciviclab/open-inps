-- INPS Rapporti Cessazioni — MART Motivo
-- Cessazioni per anno, sesso, regione e motivo.

SELECT
    anno,
    sesso,
    regione,
    motivo_cessazione,
    n_cessazioni
FROM clean_input
WHERE dimensione = 'anno_sesso_regione_motivo'
  AND sesso IN ('Maschi', 'Femmine')
  AND (motivo_cessazione IS NULL OR motivo_cessazione NOT LIKE '%Totale%')
  AND (regione IS NULL OR regione NOT LIKE '%Totale%')
