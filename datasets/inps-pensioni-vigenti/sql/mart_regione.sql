-- INPS Pensioni Vigenti — MART Regione
-- Distribuzione per regione.

SELECT
    anno,
    sesso,
    regione AS chiave,
    n_pensioni,
    importo_medio_mensile_eur
FROM clean_input
WHERE dimensione = 'anno_regione'
  AND sesso IN ('Maschi', 'Femmine')
  AND (regione IS NULL OR regione NOT LIKE '%Totale%')
