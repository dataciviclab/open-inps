-- INPS CIG — MART Ramo
-- Ore CIG per anno e ramo economico.

SELECT
    anno,
    ramo,
    oretot
FROM clean_input
WHERE dimensione = 'anno_ramo'
  AND (ramo IS NULL OR ramo NOT LIKE '%Totale%')
