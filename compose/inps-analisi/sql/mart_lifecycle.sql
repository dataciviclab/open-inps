-- INPS Analisi — MART Lifecycle
-- Indici normalizzati del ciclo: lavoro → disoccupazione → pensione.
-- Base = primo anno disponibile per ogni metrica.

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
    CASE WHEN base_val > 0 THEN ROUND(valore * 100.0 / base_val, 1) ELSE NULL END AS indice,
    -- Share % sul totale della metrica
    NULL AS share_pct,
    -- YoY
    LAG(valore) OVER (PARTITION BY metrica, sesso ORDER BY anno) AS valore_prec
FROM base
