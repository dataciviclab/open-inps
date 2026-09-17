-- INPS Dipendenti Pubblici — CLEAN
-- Macro toolkit: cast_int, remove_dot_thousands, normalize_string

SELECT
    cast_int(anno) AS anno,
    normalize_string(dimensione) AS dimensione,
    normalize_string(Regione) AS regione,
    normalize_string("Tipo ente") AS tipo_ente,
    normalize_string("Forma giuridica") AS forma_giuridica,
    remove_dot_thousands(num_entiSUM) AS n_enti,
    remove_dot_thousands(giorni_tot_corrSUM) AS giorni_totali,
    remove_dot_thousands(retrimp_tot_corrSUM) AS retribuzione_totale
FROM raw_input
