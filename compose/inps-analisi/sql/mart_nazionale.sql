-- INPS Analisi — MART Nazionale
-- Trend nazionale con analytics: share %, YoY %, indice genere.

WITH base AS (
    SELECT anno, metrica, sesso, valore,
        -- Share: % sul totale della metrica nello stesso anno
        SUM(valore) OVER (PARTITION BY anno, metrica) AS totale_metrica,
        -- YoY: valore anno precedente
        LAG(valore) OVER (PARTITION BY metrica, sesso ORDER BY anno) AS valore_prec
    FROM clean_input
    WHERE regione IS NULL
)

SELECT
    anno,
    metrica,
    sesso,
    valore,
    -- Share % sul totale della metrica (Maschi+Femmine)
    CASE WHEN totale_metrica > 0
        THEN ROUND(valore * 100.0 / totale_metrica, 1)
        ELSE NULL
    END AS share_pct,
    -- Variazione % anno su anno
    CASE WHEN valore_prec IS NOT NULL AND valore_prec > 0
        THEN ROUND((valore - valore_prec) * 100.0 / valore_prec, 1)
        ELSE NULL
    END AS yoy_pct,
    -- Indice genere: rapporto F/M * 100 (calcolato nella query successiva)
    NULL AS indice_genere
FROM base
