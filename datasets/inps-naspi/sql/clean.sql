-- INPS NASpI — CLEAN
-- Macro toolkit: cast_int, remove_dot_thousands, normalize_string
-- Legge solo da raw_input.

SELECT
    cast_int(anno) AS anno,
    normalize_string(dimensione) AS dimensione,
    normalize_string(fonte) AS fonte,
    normalize_string(Sesso) AS sesso,
    normalize_string(Regione) AS regione,
    normalize_string("Classe di età") AS classe_eta,
    normalize_string("Durata teorica in mesi della prestazione") AS durata_mesi,
    remove_dot_thousands("beneficiariSUM") AS n_beneficiari
FROM raw_input
