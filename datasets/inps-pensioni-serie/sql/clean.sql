-- INPS Pensioni Serie Storica — CLEAN
-- Macro toolkit: normalize_string, normalize_italian_integer, normalize_italian_number
-- 390 vigenti (1998-2026) + 376 liquidate (1997-2025).
-- Le misure del backend sono in formato italiano ("1.018,30").

SELECT
    cast_int(anno) AS anno,
    normalize_string(dimensione) AS dimensione,
    normalize_string(tipo_pensione) AS tipo_pensione,
    normalize_string(Sesso) AS sesso,
    normalize_string(Categoria) AS categoria,
    normalize_string("Tipo gestione") AS tipo_gestione,
    normalize_string("Regione della sede INPS") AS regione,
    normalize_italian_integer("_FREQ_SUM") AS n_pensioni,
    normalize_italian_number("Importo medio mensile") AS importo_medio_mensile_eur,
    normalize_italian_number("Età media") AS eta_media
FROM raw_input
