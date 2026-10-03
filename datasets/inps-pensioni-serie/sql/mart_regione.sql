-- INPS Pensioni Serie — MART Regione
-- Vigenti e liquidate per anno, sesso e regione sede INPS.

SELECT
    anno,
    tipo_pensione,
    sesso,
    regione,
    n_pensioni,
    importo_medio_mensile_eur
FROM clean_input
WHERE dimensione = 'anno_sesso_regione'
  AND sesso IN ('Maschi', 'Femmine')
  AND regione IS NOT NULL
  AND regione <> ''
  AND n_pensioni IS NOT NULL
