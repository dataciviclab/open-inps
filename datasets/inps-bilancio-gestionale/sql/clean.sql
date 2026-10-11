-- INPS Rendiconto Gestionale — CLEAN
-- CKAN open data: capitoli di entrata (accertato) e uscita (impegnato).
-- Il raw profile applica decimal=',' → i numeri arrivano già DOUBLE:
-- usare cast_double, non normalize_italian_number (lo raddoppierebbe).
-- Le colonne nominano in modo diverso lo stesso concetto:
--   entrate: Somme accertate / Riscossioni
--   uscite:  Somme impegnate / Pagamenti
-- anno e tipo arrivano da inject_column sulle raw sources.

SELECT DISTINCT
    cast_int(anno) AS anno,
    normalize_string(tipo) AS tipo,
    normalize_string("Codice") AS codice,
    normalize_string("Denominazione") AS denominazione,
    cast_double("Previsioni iniziali") AS previsioni_iniziali_eur,
    cast_double("Previsioni definitive") AS previsioni_definitive_eur,
    cast_double(coalesce("Somme accertate", "Somme impegnate")) AS importo_esercizio_eur,
    cast_double("Residui iniziali") AS residui_iniziali_eur,
    cast_double("Residui totali") AS residui_totali_eur,
    cast_double("Previsioni cassa") AS previsioni_cassa_eur,
    cast_double(coalesce("Riscossioni", "Pagamenti")) AS incassi_pagamenti_eur,
    cast_double("Totali residui termine esercizio") AS residui_finali_eur
FROM raw_input
