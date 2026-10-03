-- INPS DIS-COLL — CLEAN
-- Obs 397 beneficiari + 398 trattamenti, grana nazionale anno×sesso.
-- Nota: STOT_PAGSUM è la misura importo della fonte; l'unità non è
-- validata come euro assoluti — usare solo confronti relativi.

SELECT
    cast_int(anno) AS anno,
    normalize_string(dimensione) AS dimensione,
    normalize_string(tipo_dato) AS tipo_dato,
    normalize_string(Sesso) AS sesso,
    remove_dot_thousands("_FREQ_SUM") AS n_trattamenti,
    remove_dot_thousands("SGGTEORICISUM") AS giorni_teorici,
    remove_dot_thousands("SGG_PAGSUM") AS giorni_pagati,
    remove_dot_thousands("STOT_PAGSUM") AS importo_fonte
FROM raw_input
