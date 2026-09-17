-- INPS Analisi — MART Lifecycle
-- Indice normalizzato del ciclo: lavoro → disoccupazione → pensione.
-- Ogni valore e' espresso come indice (100 = valore del primo anno).

WITH base AS (
    SELECT anno, metrica, sesso, valore,
        FIRST_VALUE(valore) OVER (PARTITION BY metrica, sesso ORDER BY anno) AS base_val
    FROM clean_input
    WHERE regione IS NULL
      AND metrica IN ('lavoratori_privati', 'rapporti_lavoro', 'naspi', 'cig_ore', 'pensioni_vigenti')
)
SELECT
    anno,
    metrica,
    sesso,
    valore,
    CASE WHEN base_val > 0 THEN ROUND(valore * 100.0 / base_val, 1) ELSE NULL END AS indice
FROM base
