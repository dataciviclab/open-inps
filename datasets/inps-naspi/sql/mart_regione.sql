-- INPS NASpI — MART Regione
-- Beneficiari NASpI per anno, sesso, regione.

SELECT
    anno,
    sesso,
    regione,
    n_beneficiari
FROM clean_input
WHERE dimensione = 'beneficiari_anno_sesso_regione'
  AND fonte = '395'
  AND sesso IN ('Maschi', 'Femmine')
  AND (regione IS NULL OR regione NOT LIKE '%Totale%')
