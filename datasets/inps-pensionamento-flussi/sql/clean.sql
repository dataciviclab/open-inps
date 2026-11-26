-- INPS Pensionamento Flussi — CLEAN
-- read.all_varchar: true → le colonne restano stringhe e le macro lavorano sul
-- formato originale. Serve perché lo sniffing tipizza DOUBLE i numeri già in
-- formato italiano (guardia toolkit: il valore avrebbe già perso il formato).
-- _FREQ_SUM ha punti migliaia: remove_dot_thousands.
-- Importi con virgola decimale: normalize_italian_number.

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
