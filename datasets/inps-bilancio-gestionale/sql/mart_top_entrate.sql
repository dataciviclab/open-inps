-- INPS RG — MART Top entrate per capitolo
-- Accertato più rilevante, con scarto previsione/importo.

SELECT
    anno,
    codice,
    denominazione,
    previsioni_definitive_eur,
    importo_esercizio_eur,
    importo_esercizio_eur - previsioni_definitive_eur AS scarto_previsionale_eur,
    residui_finali_eur
FROM clean_input
WHERE tipo = 'entrata'
  AND importo_esercizio_eur IS NOT NULL
  AND importo_esercizio_eur > 0
ORDER BY anno, importo_esercizio_eur DESC
