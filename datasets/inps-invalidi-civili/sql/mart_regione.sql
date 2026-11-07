-- INPS Invalidi civili — MART Regione
-- Prestazioni per regione di residenza del titolare (obs 383), non per sede.

SELECT
    anno,
    regione,
    sesso,
    SUM(n_prestazioni) AS n_prestazioni,
    ROUND(
        SUM(importo_medio_mensile_eur * n_prestazioni) / NULLIF(SUM(n_prestazioni), 0),
        2
    ) AS importo_medio_mensile_eur
FROM clean_input
WHERE dimensione = 'anno_sesso_regione'
GROUP BY anno, regione, sesso
ORDER BY anno, regione, sesso
