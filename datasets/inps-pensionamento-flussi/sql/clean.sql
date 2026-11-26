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
    -- decimal=',': con all_varchar i valori arrivano come stringhe italiane
    -- ("1.564,70", "64,9"): le macro li normalizzano.
    remove_dot_thousands("_FREQ_SUM") AS n_pensioni,
    normalize_italian_number("Età media alla decorrenza") AS eta_media_decorrenza,
    normalize_italian_number("Importo medio alla decorrenza (in euro)") AS importo_medio_decorrenza_eur,
    -- La fonte include una gerarchia di totali (trimestre, dimensione, sesso).
    -- I mart pubblicano solo il dettaglio: il flag rende esplicito il filtro.
    COALESCE(
        normalize_string(Trimestre) = 'Totale'
        OR normalize_string(Regione) = 'Totale'
        OR normalize_string(Gestione) = 'Totale'
        OR normalize_string(Categoria) = 'Totale'
        OR normalize_string(Sesso) LIKE '%:Totale',
        FALSE
    ) AS is_totale
FROM raw_input
