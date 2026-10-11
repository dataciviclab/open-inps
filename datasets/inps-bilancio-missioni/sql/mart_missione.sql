-- INPS Bilancio Missioni — MART Missione
-- Spesa per anno e missione COFOG (competenza e cassa).

SELECT
    anno,
    missione,
    sum(competenza_eur) AS competenza_eur,
    sum(cassa_eur) AS cassa_eur,
    count(*) AS n_voci
FROM clean_input
WHERE missione IS NOT NULL
GROUP BY anno, missione
ORDER BY anno, competenza_eur DESC
