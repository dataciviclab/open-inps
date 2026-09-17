-- INPS Rapporti Lavoro — MART Regione
-- Assunzioni/cessazioni per anno, sesso, regione, tipo rapporto.

SELECT
    anno,
    sesso,
    regione,
    tipo_rapporto,
    n_rapporti
FROM clean_input
WHERE dimensione = 'anno_sesso_regione_tipo'
  AND sesso IN ('Maschi', 'Femmine')
  AND (regione IS NULL OR regione NOT LIKE '%Totale%')
