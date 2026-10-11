-- INPS Bilancio Missioni — MART Prestazione
-- Dettaglio per programma e prestazione (la grana più leggibile).

SELECT
    anno,
    missione,
    programma,
    gruppo_cofog,
    prestazione,
    competenza_eur,
    cassa_eur,
    competenza_eur - cassa_eur AS scarto_competenza_cassa_eur
FROM clean_input
WHERE missione IS NOT NULL
  AND programma IS NOT NULL
ORDER BY anno, missione, competenza_eur DESC
