-- INPS CIG — MART Mensile
-- Ore CIG per anno e mese (trend temporale).

SELECT
    anno,
    mese,
    oretot
FROM clean_input
WHERE dimensione = 'anno_mese'
  AND (mese IS NULL OR mese NOT LIKE '%Totale%')
