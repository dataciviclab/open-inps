-- INPS Conto Economico — MART Voci principali
-- Le voci di conto economico con importo assoluto più rilevanti.

SELECT
    anno,
    fonte,
    voce,
    importo_eur,
    abs(importo_eur) AS importo_assoluto_eur
FROM clean_input
WHERE voce IS NOT NULL
  AND importo_eur IS NOT NULL
ORDER BY anno, fonte, importo_assoluto_eur DESC
