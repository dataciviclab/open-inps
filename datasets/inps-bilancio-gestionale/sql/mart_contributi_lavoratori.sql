-- INPS RG — MART Contributi per tipologia lavoratore
-- Solo i capitoli di entrata che iniziano con 1E1 = contributi
-- obbligatori per categoria di assicurato (il cuore analitico del gestionale).

SELECT
    anno,
    codice,
    denominazione,
    importo_esercizio_eur,
    previsioni_definitive_eur,
    importo_esercizio_eur - previsioni_definitive_eur AS scarto_previsionale_eur
FROM clean_input
WHERE tipo = 'entrata'
  AND codice LIKE '1E1%'
  AND importo_esercizio_eur IS NOT NULL
  AND importo_esercizio_eur > 0
ORDER BY anno, importo_esercizio_eur DESC
