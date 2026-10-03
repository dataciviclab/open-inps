-- INPS Rapporti Cessazioni — MART Provincia
-- Cessazioni per anno, sesso, provincia e tipologia.

SELECT
    anno,
    sesso,
    provincia,
    tipo_cessazione,
    n_cessazioni
FROM clean_input
WHERE dimensione = 'anno_sesso_provincia_tipo'
  AND sesso IN ('Maschi', 'Femmine')
  AND (tipo_cessazione IS NULL OR tipo_cessazione NOT LIKE '%Totale%')
  AND (provincia IS NULL OR provincia NOT LIKE '%Totale%')
