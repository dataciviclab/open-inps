-- INPS Rapporti Cessazioni — MART Regione
-- Cessazioni per anno, sesso, regione e tipologia.

SELECT
    anno,
    sesso,
    regione,
    tipo_cessazione,
    n_cessazioni
FROM clean_input
WHERE dimensione = 'anno_sesso_regione_tipo'
  AND sesso IN ('Maschi', 'Femmine')
  AND (tipo_cessazione IS NULL OR tipo_cessazione NOT LIKE '%Totale%')
  AND (regione IS NULL OR regione NOT LIKE '%Totale%')
