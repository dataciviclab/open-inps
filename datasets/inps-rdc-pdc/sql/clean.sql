-- INPS RdC/PdC — CLEAN
-- Obs 452: nuclei beneficiari RdC/PdC con almeno una mensilità/anno.
-- Misure: _FREQ_SUM=nuclei, NUM_COMPSUM=componenti, Importo medio mensile.

SELECT
    cast_int(anno) AS anno,
    normalize_string(dimensione) AS dimensione,
    normalize_string(Misura) AS misura,
    normalize_string(Regione) AS regione,
    normalize_string("Numero componenti il nucleo") AS componenti_nucleo,
    normalize_string("Presenza disabili nel nucleo") AS con_disabili,
    normalize_string("Presenza minori nel nucleo") AS con_minori,
    remove_dot_thousands("_FREQ_SUM") AS n_nuclei,
    remove_dot_thousands("NUM_COMPSUM") AS n_componenti,
    normalize_italian_number("Importo medio mensile") AS importo_medio_mensile_eur
FROM raw_input
