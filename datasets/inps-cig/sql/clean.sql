-- INPS CIG — CLEAN
-- Macro toolkit: cast_int, remove_dot_thousands, normalize_string
-- Legge solo da raw_input.

SELECT
    cast_int(anno) AS anno,
    normalize_string(dimensione) AS dimensione,
    normalize_string("Tipo intervento") AS gestione,
    normalize_string("Ramo di attività economica") AS ramo,
    normalize_string(Regione) AS regione,
    normalize_string(Mese) AS mese,
    remove_dot_thousands(oretotSUM) AS oretot
FROM raw_input
