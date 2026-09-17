-- INPS Rapporti Lavoro — CLEAN
-- Macro toolkit: cast_int, cast_bigint, normalize_string
-- Legge solo da raw_input. Solo cast/rinomina.

SELECT
    cast_int(anno) AS anno,
    normalize_string(dimensione) AS dimensione,
    normalize_string(Sesso) AS sesso,
    normalize_string("Tipologia assunzione") AS tipo_rapporto,
    normalize_string("Regione") AS regione,
    normalize_string("Provincia") AS provincia,
    normalize_string("Classe di Età") AS classe_eta,
    remove_dot_thousands("NUM_DENUNCE_SUM") AS n_rapporti
FROM raw_input
