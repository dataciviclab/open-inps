-- INPS Bilancio Missioni — MART Confronto anni
-- Variazione di competenza tra l'ultimo e il primo anno disponibili.

WITH anni AS (
    SELECT min(anno) AS a0, max(anno) AS a1 FROM clean_input
),
per_missione AS (
    SELECT
        c.missione,
        max(a.a0) AS anno_primo,
        max(a.a1) AS anno_ultimo,
        sum(CASE WHEN c.anno = a.a0 THEN c.competenza_eur END) AS competenza_primo_anno,
        sum(CASE WHEN c.anno = a.a1 THEN c.competenza_eur END) AS competenza_ultimo_anno
    FROM clean_input c
    CROSS JOIN anni a
    WHERE c.missione IS NOT NULL
    GROUP BY c.missione
)
SELECT
    missione,
    anno_primo,
    anno_ultimo,
    competenza_primo_anno,
    competenza_ultimo_anno,
    competenza_ultimo_anno - competenza_primo_anno AS variazione_assoluta_eur,
    CASE
        WHEN competenza_primo_anno > 0
        THEN round(100.0 * (competenza_ultimo_anno - competenza_primo_anno) / competenza_primo_anno, 2)
    END AS variazione_pct
FROM per_missione
WHERE competenza_primo_anno IS NOT NULL
  AND competenza_ultimo_anno IS NOT NULL
ORDER BY abs(competenza_ultimo_anno - competenza_primo_anno) DESC
