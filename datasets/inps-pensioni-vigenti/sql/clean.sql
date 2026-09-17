-- INPS Pensioni Vigenti — CLEAN
-- Macro toolkit: cast_int, cast_bigint, cast_double, normalize_string
-- Legge solo da raw_input. Solo cast/rinomina, niente filtri.

SELECT
    cast_int(anno) AS anno,
    normalize_string(dimensione) AS dimensione,
    normalize_string(Sesso) AS sesso,
    normalize_string("Classe d'importo") AS classe_importo,
    normalize_string("Classe di età") AS classe_eta,
    normalize_string("Regione della sede INPS") AS regione,
    cast_bigint("_FREQ_SUM") AS n_pensioni,
    cast_bigint("tot_impSUM") AS importo_totale_migliaia_eur,
    cast_double("Importo medio mensile") AS importo_medio_mensile_eur
FROM raw_input
