-- INPS NASpI — MART Eta
-- Beneficiari NASpI per anno, sesso, classe di eta.

SELECT
    anno,
    sesso,
    classe_eta,
    n_beneficiari
FROM clean_input
WHERE dimensione = 'beneficiari_anno_sesso_eta'
  AND fonte = '395'
  AND sesso IN ('Maschi', 'Femmine')
  AND (classe_eta IS NULL OR classe_eta NOT LIKE '%Totale%')
