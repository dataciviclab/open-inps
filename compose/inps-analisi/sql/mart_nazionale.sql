-- INPS Analisi — MART Nazionale
-- Trend nazionale per metrica e sesso.

SELECT
    anno,
    metrica,
    sesso,
    valore
FROM clean_input
WHERE regione IS NULL
