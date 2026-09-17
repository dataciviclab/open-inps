-- INPS Pensioni Vigenti — MART Importo
-- Distribuzione per classe di importo.

SELECT
    anno,
    sesso,
    classe_importo AS chiave,
    n_pensioni,
    importo_medio_mensile_eur
FROM clean_input
WHERE dimensione = 'anno_sesso_importo'
  AND sesso IN ('Maschi', 'Femmine')
  AND (classe_importo IS NULL OR classe_importo NOT LIKE '%Totale%')
