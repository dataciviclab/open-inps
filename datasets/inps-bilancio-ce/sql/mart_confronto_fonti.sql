-- INPS Conto Economico — MART Confronto generale vs GIAS
-- Per anno e voce: differenza tra CE generale e GIAS (quando presente).

WITH gen AS (
    SELECT anno, voce, importo_eur AS importo_generale_eur
    FROM clean_input
    WHERE fonte = 'generale'
),
gias AS (
    SELECT anno, voce, importo_eur AS importo_gias_eur
    FROM clean_input
    WHERE fonte = 'gias'
)
SELECT
    coalesce(gen.anno, gias.anno) AS anno,
    coalesce(gen.voce, gias.voce) AS voce,
    gen.importo_generale_eur,
    gias.importo_gias_eur
FROM gen
FULL OUTER JOIN gias
  ON gen.anno = gias.anno
 AND gen.voce = gias.voce
ORDER BY anno, abs(coalesce(gen.importo_generale_eur, gias.importo_gias_eur)) DESC
