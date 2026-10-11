-- INPS Bilancio Missioni — CLEAN
-- CKAN open data: Missioni/Programmi/COFOG, competenza e cassa in euro.
-- Fonte cp1252 con ';' e decimale ',' — gestiti da clean.read.

-- I file CKAN 2023 e 2024 si sovrappongono sull'anno 2023 (righe identiche):
-- DISTINCT elimina i doppioni.

SELECT DISTINCT
    cast_int("Anno") AS anno,
    normalize_string("Missione") AS missione,
    normalize_string("Programma") AS programma,
    normalize_string("Gruppo COFOG") AS gruppo_cofog,
    normalize_string("Prestazione") AS prestazione,
    cast_double("Competenza") AS competenza_eur,
    cast_double("Cassa") AS cassa_eur
FROM raw_input
