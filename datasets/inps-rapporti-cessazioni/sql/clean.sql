-- INPS Rapporti Cessazioni — CLEAN
-- Macro toolkit: cast_int, remove_dot_thousands, normalize_string
-- Legge solo da raw_input. Mantiene tutte le dimensioni come colonna `dimensione`.

SELECT
    cast_int(anno) AS anno,
    normalize_string(dimensione) AS dimensione,
    normalize_string(Sesso) AS sesso,
    normalize_string("Tipologia cessazione") AS tipo_cessazione,
    normalize_string("Motivo cessazione") AS motivo_cessazione,
    normalize_string(Regione) AS regione,
    normalize_string(Provincia) AS provincia,
    remove_dot_thousands("NUM_DENUNCE_SUM") AS n_cessazioni
FROM raw_input
