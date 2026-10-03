-- INPS Pensioni Serie — MART Tipo gestione
-- Vigenti e liquidate per anno, sesso e tipo di gestione.

SELECT
    anno,
    tipo_pensione,
    sesso,
    tipo_gestione,
    n_pensioni,
    importo_medio_mensile_eur
FROM clean_input
WHERE dimensione = 'anno_sesso_tipogest'
  AND sesso IN ('Maschi', 'Femmine')
  AND tipo_gestione IS NOT NULL
  AND tipo_gestione <> ''
  AND n_pensioni IS NOT NULL
