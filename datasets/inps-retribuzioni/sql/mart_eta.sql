-- INPS Retribuzioni — MART Eta
-- Lavoratori e retribuzioni per anno, sesso, classe di eta.

SELECT
    anno,
    fonte,
    sesso,
    classe_eta,
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
WHERE dimensione = 'anno_sesso_eta'
  AND sesso IN ('Maschi', 'Femmine')
  AND (classe_eta IS NULL OR classe_eta NOT LIKE '%Totale%')
