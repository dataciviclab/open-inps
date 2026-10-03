-- INPS Lavoratori Pubblici — MART Tipo contratto
-- Lavoratori e retribuzioni per anno, gruppo e tipologia contrattuale.

SELECT
    anno,
    gruppo_contrattuale,
    tipo_contratto,
    n_lavoratori,
    retribuzioni_totali,
    giornate_lavorate
FROM clean_input
WHERE dimensione = 'anno_gruppo_tipo_contratto'
  AND gruppo_contrattuale IS NOT NULL
  AND tipo_contratto IS NOT NULL
  AND n_lavoratori IS NOT NULL
