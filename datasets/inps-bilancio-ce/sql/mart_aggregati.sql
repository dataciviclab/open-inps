-- INPS Conto Economico — MART Aggregate istituzionali
-- Macro-aggregati del CE generale: entrate contributive, trasferimenti,
-- spese prestazioni, funzionamento. Solo fonte 'generale'.

SELECT
    anno,
    voce,
    importo_eur
FROM clean_input
WHERE fonte = 'generale'
  AND (
        voce LIKE 'Aliquote contributive%'
     OR voce LIKE 'Trasferimenti da parte dello Stato%'
     OR voce LIKE 'Spese per prestazioni%'
     OR voce LIKE 'Spese per acquisto di beni%'
     OR voce LIKE 'Oneri per il personale in attivit%'
     OR voce LIKE 'Oneri per il personale in quiescenza%'
     OR voce LIKE 'Entrate derivanti dalla vendita%'
  )
  AND importo_eur IS NOT NULL
ORDER BY anno, abs(importo_eur) DESC
