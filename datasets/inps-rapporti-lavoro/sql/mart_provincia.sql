-- INPS Rapporti Lavoro — MART Provincia
-- Assunzioni/cessazioni per anno, sesso, provincia, tipo rapporto.

SELECT
    anno,
    sesso,
    provincia,
    tipo_rapporto,
    n_rapporti
FROM clean_input
WHERE dimensione = 'anno_sesso_provincia'
  AND sesso IN ('Maschi', 'Femmine')
  AND (provincia IS NULL OR provincia NOT LIKE '%Totale%')
