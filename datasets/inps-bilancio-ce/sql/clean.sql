-- INPS Conto Economico — CLEAN
-- CKAN open data: CE generale + GIAS, 2022-2024, importi in euro.
-- I file multi-anno si sovrappongono; il Progressivo della fonte non è
-- stabile tra i file — si esclude e si deduplica su (anno, fonte, voce).
-- Colonna fonte iniettata dal toolkit via inject_column sulle raw sources.

SELECT DISTINCT
    cast_int("Anno") AS anno,
    normalize_string(fonte) AS fonte,
    normalize_string("Denominazione Conto") AS voce,
    normalize_italian_number("Importo") AS importo_eur
FROM raw_input
