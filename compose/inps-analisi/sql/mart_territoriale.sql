-- INPS Analisi — MART Territoriale
-- Per regione con analytics: share %, YoY %, indice vs media nazionale.

WITH base AS (
    SELECT anno, metrica, sesso, regione, valore,
        -- Totale nazionale per confronto
        SUM(valore) OVER (PARTITION BY anno, metrica, sesso) AS totale_naz,
        -- Totale per regione (tutte le metriche)
        SUM(valore) OVER (PARTITION BY anno, regione, sesso) AS totale_regione,
        -- YoY
        LAG(valore) OVER (PARTITION BY metrica, sesso, regione ORDER BY anno) AS valore_prec
    FROM clean_input
    WHERE regione IS NOT NULL
)

SELECT
    anno,
    metrica,
    sesso,
    regione,
    valore,
    -- Share %: quanto pesa la regione sul totale nazionale
    CASE WHEN totale_naz > 0
        THEN ROUND(valore * 100.0 / totale_naz, 1)
        ELSE NULL
    END AS share_pct,
    -- Variazione % anno su anno
    CASE WHEN valore_prec IS NOT NULL AND valore_prec > 0
        THEN ROUND((valore - valore_prec) * 100.0 / valore_prec, 1)
        ELSE NULL
    END AS yoy_pct,
    -- Indice vs media nazionale (100 = media)
    CASE WHEN totale_naz > 0 AND totale_naz > 0
        THEN ROUND(valore * 100.0 / (totale_naz / 20.0), 1)
        ELSE NULL
    END AS indice_vs_media
FROM base
