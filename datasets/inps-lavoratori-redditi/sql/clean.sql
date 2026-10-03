-- INPS Lavoratori Redditi — CLEAN
-- Obs 465: lavoratori, reddito cumulato e settimane lavorate.
-- Misure: _FREQ_SUM=lavoratori, rr_cumulo_Sum=redditi, ss_cum_total_Sum=settimane.

SELECT
    cast_int(anno) AS anno,
    normalize_string(dimensione) AS dimensione,
    normalize_string(Sesso) AS sesso,
    normalize_string("Posizione prevalente") AS posizione_prevalente,
    normalize_string(Regione) AS regione,
    normalize_string("Classe di età") AS classe_eta,
    normalize_string("Cittadinanza") AS cittadinanza,
    normalize_string("Pensionato di vecchiaia-anzianità") AS stato_pensionato,
    remove_dot_thousands("_FREQ_SUM") AS n_lavoratori,
    remove_dot_thousands("rr_cumulo_Sum") AS reddito_cumulato,
    remove_dot_thousands("ss_cum_total_Sum") AS settimane_lavorate
FROM raw_input
