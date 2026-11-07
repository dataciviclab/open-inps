-- INPS Invalidi civili — MART Categoria
-- Prestazioni per anno, sesso e sottocategoria (ciechi, sordomuti,
-- invalidi totali/parziali). Importo medio ponderato sul numero.

SELECT
    anno,
    categoria,
    sottocategoria,
    sesso,
    SUM(n_prestazioni) AS n_prestazioni,
    ROUND(
        SUM(importo_medio_mensile_eur * n_prestazioni) / NULLIF(SUM(n_prestazioni), 0),
        2
    ) AS importo_medio_mensile_eur
FROM clean_input
WHERE dimensione = 'anno_sesso_categoria'
GROUP BY anno, categoria, sottocategoria, sesso
ORDER BY anno, categoria, sottocategoria, sesso
