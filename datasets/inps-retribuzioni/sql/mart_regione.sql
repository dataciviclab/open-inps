-- INPS Retribuzioni — MART Regione
-- Lavoratori e retribuzioni per anno, sesso, regione.

SELECT
    anno,
    fonte,
    sesso,
    regione,
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
WHERE dimensione = 'anno_sesso_regione'
  AND sesso IN ('Maschi', 'Femmine')
  AND (regione IS NULL OR regione NOT LIKE '%Totale%')
