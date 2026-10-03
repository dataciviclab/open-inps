-- INPS Pensionamento Flussi — CLEAN
-- Il raw_profile rileva decimal=',' → DuckDB ha già parsato i numeri
-- italiani. Contratto toolkit: usare CAST AS DOUBLE, NON
-- normalize_italian_number (altrimenti "65,2" → 652).
-- _FREQ_SUM resta con punti migliaia: remove_dot_thousands.

SELECT
    cast_int(anno) AS anno,
    normalize_string(dimensione) AS dimensione,
    normalize_string(Trimestre) AS trimestre,
    normalize_string(Sesso) AS sesso,
    normalize_string(Regione) AS regione,
    normalize_string(Gestione) AS gestione,
    normalize_string(Categoria) AS categoria,
    -- decimal=',': DuckDB parsà "65,2"→65.2 ma lascia VARCHAR
    -- "1.564,70" e "8.511" (punti migliaia + virgola decimale misti).
    remove_dot_thousands("_FREQ_SUM") AS n_pensioni,
    TRY_CAST("Età media alla decorrenza" AS DOUBLE) AS eta_media_decorrenza,
    normalize_italian_number("Importo medio alla decorrenza (in euro)") AS importo_medio_decorrenza_eur
FROM raw_input
