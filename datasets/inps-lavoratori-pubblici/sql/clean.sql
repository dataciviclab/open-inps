-- INPS Lavoratori Pubblici — CLEAN
-- Obs 435: retribuzioni e periodi retribuiti, gruppo contrattuale PA.
-- SESSO è rotto sull'osservatorio (SAS -320): nessuna dimensione genere.
-- Misura _FREQ_SUM = lavoratori; RR = retribuzioni; GG = giornate.

SELECT
    cast_int(anno) AS anno,
    normalize_string(dimensione) AS dimensione,
    normalize_string("Gruppo contrattuale") AS gruppo_contrattuale,
    normalize_string("Classe di età") AS classe_eta,
    normalize_string("Tipologia contrattuale") AS tipo_contratto,
    normalize_string("Presenza tempo parziale nell'anno") AS tempo_parziale,
    normalize_string(Regione) AS regione,
    remove_dot_thousands("_FREQ_SUM") AS n_lavoratori,
    remove_dot_thousands("RR_SumSUM") AS retribuzioni_totali,
    remove_dot_thousands("GG_SumSUM") AS giornate_lavorate,
    remove_dot_thousands("SS_SumSUM") AS settimane_retribuite,
    remove_dot_thousands("UU_TOT_SumSUM") AS unita_lavorative
FROM raw_input
