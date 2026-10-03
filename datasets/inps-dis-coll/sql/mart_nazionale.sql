-- INPS DIS-COLL — MART Nazionale
-- Trattamenti e giorni per anno, tipo dato (397/398) e sesso.
-- Unica grana affidabile di questo osservatorio.

SELECT
    anno,
    tipo_dato,
    sesso,
    n_trattamenti,
    giorni_teorici,
    giorni_pagati,
    importo_fonte
FROM clean_input
WHERE dimensione = 'anno_sesso'
  AND sesso IN ('Maschi', 'Femmine')
  AND n_trattamenti IS NOT NULL
