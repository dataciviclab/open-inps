-- INPS Analisi — MART Territoriale
-- Per regione, metrica, sesso.

SELECT
    anno,
    metrica,
    sesso,
    regione,
    valore
FROM clean_input
WHERE regione IS NOT NULL
