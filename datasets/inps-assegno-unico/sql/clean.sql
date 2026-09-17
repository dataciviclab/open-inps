-- INPS Assegno Unico — CLEAN
-- Macro toolkit: cast_int, remove_dot_thousands, normalize_string

SELECT
    cast_int(anno) AS anno,
    normalize_string(dimensione) AS dimensione,
    normalize_string(Regione) AS regione,
    normalize_string(Isee) AS fascia_isee,
    remove_dot_thousands("_FREQ_SUM") AS n_figli,
    remove_dot_thousands("Importo medio mensile per figlio") AS importo_medio_figlio,
    remove_dot_thousands("Importo medio mensile per nucleo") AS importo_medio_nucleo
FROM raw_input
