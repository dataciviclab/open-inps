-- INPS Pensionamento Flussi — MART Categoria
-- Nuove pensioni per anno decorrenza, trimestre, sesso e categoria.

SELECT
    anno,
    trimestre,
    sesso,
    categoria,
    n_pensioni,
    eta_media_decorrenza,
    importo_medio_decorrenza_eur
FROM clean_input
WHERE dimensione = 'anno_trimestre_sesso_categoria'
  AND sesso IN ('Maschi', 'Femmine')
  AND categoria IS NOT NULL
  AND categoria <> ''
  AND n_pensioni IS NOT NULL
