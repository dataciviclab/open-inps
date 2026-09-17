-- INPS Retribuzioni — CLEAN
-- Macro toolkit: cast_int, remove_dot_thousands, normalize_string
-- Legge solo da raw_input.

SELECT
    cast_int(anno) AS anno,
    normalize_string(fonte) AS fonte,
    normalize_string(dimensione) AS dimensione,
    normalize_string(Sesso) AS sesso,
    normalize_string(Regione) AS regione,
    normalize_string("Classe di età") AS classe_eta,
    remove_dot_thousands(lav_annoSUM) AS n_lavoratori,
    remove_dot_thousands(s_retrSUM) AS somma_retribuzioni,
    remove_dot_thousands(UU_TOTSUM) AS unita_lavorative
FROM raw_input
