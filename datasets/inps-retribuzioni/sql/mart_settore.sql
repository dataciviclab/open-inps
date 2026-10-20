-- INPS Retribuzioni — MART Settore
-- Lavoratori e retribuzioni per anno e sezione ATECO 2007.

SELECT
    anno,
    fonte,
    settore_codice,
    settore_nace,
    settore_label,
    n_lavoratori,
    retribuzione_totale,
    settimane_retribuite,
    settimane_utili,
    giornate_retribuite,
    CASE WHEN n_lavoratori > 0 THEN retribuzione_totale / n_lavoratori END AS retribuzione_media,
    CASE
        WHEN settimane_retribuite > 0 THEN retribuzione_totale / settimane_retribuite
    END AS retribuzione_media_settimana
FROM clean_input
WHERE dimensione = 'anno_settore'
  AND settore_codice IS NOT NULL
