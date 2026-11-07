-- INPS Invalidi civili — MART Serie
-- Serie storica 2002-2026 (obs 384) per anno, sesso e tipo prestazione.

SELECT
    anno,
    tipo_prestazione,
    sesso,
    SUM(n_prestazioni) AS n_prestazioni,
    ROUND(
        SUM(importo_medio_mensile_eur * n_prestazioni) / NULLIF(SUM(n_prestazioni), 0),
        2
    ) AS importo_medio_mensile_eur
FROM clean_input
WHERE dimensione = 'anno_serie'
GROUP BY anno, tipo_prestazione, sesso
ORDER BY anno, tipo_prestazione, sesso
