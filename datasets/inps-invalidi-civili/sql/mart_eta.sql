-- INPS Invalidi civili — MART Età
-- Prestazioni per anno, sesso e classe di età.

SELECT
    anno,
    classe_eta,
    sesso,
    SUM(n_prestazioni) AS n_prestazioni,
    ROUND(
        SUM(importo_medio_mensile_eur * n_prestazioni) / NULLIF(SUM(n_prestazioni), 0),
        2
    ) AS importo_medio_mensile_eur
FROM clean_input
WHERE dimensione = 'anno_sesso_eta'
GROUP BY anno, classe_eta, sesso
ORDER BY anno, classe_eta, sesso
