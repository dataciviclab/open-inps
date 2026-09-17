-- INPS NASpI — MART Durata
-- Trattamenti NASpI per anno, sesso, durata teorica.

SELECT
    anno,
    sesso,
    durata_mesi,
    n_beneficiari
FROM clean_input
WHERE dimensione = 'trattamenti_anno_sesso_durata'
  AND fonte = '396'
  AND sesso IN ('Maschi', 'Femmine')
  AND (durata_mesi IS NULL OR durata_mesi NOT LIKE '%Totale%')
