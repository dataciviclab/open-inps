-- INPS Invalidi civili — CLEAN
-- Macro toolkit: cast_int, normalize_string, remove_dot_thousands,
-- normalize_italian_number.
-- Fonti: obs 381 (prestazioni, sede INPS), 383 (residenza), 384 (serie).
-- I conteggi arrivano in formato italiano ("1.885.235"); gli importi con la
-- virgola decimale. Il reader è forzato a VARCHAR in dataset.yml.

SELECT
    cast_int(anno) AS anno,
    normalize_string(dimensione) AS dimensione,
    CASE
        WHEN UPPER(normalize_string(Sesso)) = 'MASCHI' THEN 'Maschi'
        WHEN UPPER(normalize_string(Sesso)) = 'FEMMINE' THEN 'Femmine'
        ELSE normalize_string(Sesso)
    END AS sesso,
    normalize_string(Categoria) AS categoria,
    normalize_string(Sottocategoria) AS sottocategoria,
    normalize_string("Classe di età") AS classe_eta,
    normalize_string("Regione di residenza") AS regione,
    normalize_string("Tipo prestazione") AS tipo_prestazione,
    normalize_italian_integer("_FREQ_SUM") AS n_prestazioni,
    normalize_italian_number("Importo medio mensile") AS importo_medio_mensile_eur
FROM raw_input
WHERE normalize_string(dimensione) IS NOT NULL
