-- INPS Pensioni Serie — MART Categoria
-- Vigenti e liquidate per anno, sesso e categoria previdenziale.

SELECT
    anno,
    tipo_pensione,
    sesso,
    categoria,
    n_pensioni,
    importo_medio_mensile_eur,
    eta_media
FROM clean_input
WHERE dimensione = 'anno_sesso_categoria'
  AND sesso IN ('Maschi', 'Femmine')
  AND categoria IS NOT NULL
  AND categoria <> ''
  AND n_pensioni IS NOT NULL
