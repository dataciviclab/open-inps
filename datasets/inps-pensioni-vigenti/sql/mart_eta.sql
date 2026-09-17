-- INPS Pensioni Vigenti — MART Eta
-- Distribuzione per classe di eta.

SELECT
    anno,
    sesso,
    classe_eta AS chiave,
    n_pensioni,
    importo_medio_mensile_eur
FROM clean_input
WHERE dimensione = 'anno_sesso_eta'
  AND sesso IN ('Maschi', 'Femmine')
  AND (classe_eta IS NULL OR classe_eta NOT LIKE '%Totale%')
