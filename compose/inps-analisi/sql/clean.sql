-- INPS Analisi — CLEAN Compose
-- Unifica i 7 dataset INPS in una tabella lunga (anno, metrica, sesso, regione, valore).

WITH

-- === PENSIONI VIGENTI (stock) — raw_input ===
pensioni_vigenti_naz AS (
    SELECT anno, sesso, SUM(n_pensioni) AS valore
    FROM raw_input
    WHERE dimensione = 'anno_sesso_importo'
      AND sesso IN ('Maschi', 'Femmine')
      AND (classe_importo IS NULL OR classe_importo NOT LIKE '%Totale%')
    GROUP BY anno, sesso
),
pensioni_vigenti_reg AS (
    SELECT anno, sesso, regione, SUM(n_pensioni) AS valore
    FROM raw_input
    WHERE dimensione = 'anno_regione'
      AND sesso IN ('Maschi', 'Femmine')
      AND (regione IS NULL OR regione NOT LIKE '%Totale%')
    GROUP BY anno, sesso, regione
),

-- === PENSIONI LIQUIDATE ===
liquidate_naz AS (
    SELECT anno, sesso, SUM(n_pensioni) AS valore
    FROM read_parquet('{support.pensioni_liquidate.clean}')
    WHERE dimensione = 'anno_sesso_importo'
      AND sesso IN ('Maschi', 'Femmine')
      AND (classe_importo IS NULL OR classe_importo NOT LIKE '%Totale%')
    GROUP BY anno, sesso
),
liquidate_reg AS (
    SELECT anno, sesso, regione, SUM(n_pensioni) AS valore
    FROM read_parquet('{support.pensioni_liquidate.clean}')
    WHERE dimensione = 'anno_regione'
      AND sesso IN ('Maschi', 'Femmine')
      AND (regione IS NULL OR regione NOT LIKE '%Totale%')
    GROUP BY anno, sesso, regione
),

-- === RAPPORTI LAVORO ===
rapporti_naz AS (
    SELECT anno, sesso, SUM(n_rapporti) AS valore
    FROM read_parquet('{support.rapporti.clean}')
    WHERE dimensione = 'anno_sesso_regione_tipo'
      AND sesso IN ('Maschi', 'Femmine')
      AND tipo_rapporto != 'Totale'
      AND (regione IS NULL OR regione NOT LIKE '%Totale%')
    GROUP BY anno, sesso
),
rapporti_reg AS (
    SELECT anno, sesso, regione, SUM(n_rapporti) AS valore
    FROM read_parquet('{support.rapporti.clean}')
    WHERE dimensione = 'anno_sesso_regione_tipo'
      AND sesso IN ('Maschi', 'Femmine')
      AND tipo_rapporto != 'Totale'
      AND (regione IS NULL OR regione NOT LIKE '%Totale%')
    GROUP BY anno, sesso, regione
),

-- === RETRIBUTIONI ===
retribuzioni_naz AS (
    SELECT anno, sesso, SUM(n_lavoratori) AS valore
    FROM read_parquet('{support.retribuzioni.clean}')
    WHERE dimensione = 'anno_sesso_regione'
      AND fonte = '492'
      AND sesso IN ('Maschi', 'Femmine')
      AND (regione IS NULL OR regione NOT LIKE '%Totale%')
    GROUP BY anno, sesso
),
retribuzioni_reg AS (
    SELECT anno, sesso, regione, SUM(n_lavoratori) AS valore
    FROM read_parquet('{support.retribuzioni.clean}')
    WHERE dimensione = 'anno_sesso_regione'
      AND fonte = '492'
      AND sesso IN ('Maschi', 'Femmine')
      AND (regione IS NULL OR regione NOT LIKE '%Totale%')
    GROUP BY anno, sesso, regione
),

-- === NASpI ===
naspi_naz AS (
    SELECT anno, sesso, SUM(n_beneficiari) AS valore
    FROM read_parquet('{support.naspi.clean}')
    WHERE dimensione = 'beneficiari_anno_sesso_regione'
      AND fonte = '395'
      AND sesso IN ('Maschi', 'Femmine')
      AND (regione IS NULL OR regione NOT LIKE '%Totale%')
    GROUP BY anno, sesso
),
naspi_reg AS (
    SELECT anno, sesso, regione, SUM(n_beneficiari) AS valore
    FROM read_parquet('{support.naspi.clean}')
    WHERE dimensione = 'beneficiari_anno_sesso_regione'
      AND fonte = '395'
      AND sesso IN ('Maschi', 'Femmine')
      AND (regione IS NULL OR regione NOT LIKE '%Totale%')
    GROUP BY anno, sesso, regione
),

-- === CIG ===
cig_naz AS (
    SELECT anno, 'Totale' AS sesso, SUM(oretot) AS valore
    FROM read_parquet('{support.cig.clean}')
    WHERE dimensione = 'anno_regione_gestione'
      AND gestione != 'Totale'
      AND (regione IS NULL OR regione NOT LIKE '%Totale%')
    GROUP BY anno
),
cig_reg AS (
    SELECT anno, 'Totale' AS sesso, regione, SUM(oretot) AS valore
    FROM read_parquet('{support.cig.clean}')
    WHERE dimensione = 'anno_regione_gestione'
      AND gestione != 'Totale'
      AND (regione IS NULL OR regione NOT LIKE '%Totale%')
    GROUP BY anno, regione
),

-- === ASSEGNO UNICO ===
assegno_naz AS (
    SELECT anno, 'Totale' AS sesso, SUM(n_figli) AS valore
    FROM read_parquet('{support.assegno.clean}')
    WHERE dimensione = 'figli_anno_regione'
      AND (regione IS NULL OR regione NOT LIKE '%Totale%')
    GROUP BY anno
),
assegno_reg AS (
    SELECT anno, 'Totale' AS sesso, regione, SUM(n_figli) AS valore
    FROM read_parquet('{support.assegno.clean}')
    WHERE dimensione = 'figli_anno_regione'
      AND (regione IS NULL OR regione NOT LIKE '%Totale%')
    GROUP BY anno, regione
),

-- === DIPENDENTI PUBBLICI ===
dp_naz AS (
    SELECT anno, 'Totale' AS sesso, SUM(n_enti) AS valore
    FROM read_parquet('{support.dp.clean}')
    WHERE dimensione = 'anno_regione'
      AND (regione IS NULL OR regione NOT LIKE '%Totale%')
    GROUP BY anno
),
dp_reg AS (
    SELECT anno, 'Totale' AS sesso, regione, SUM(n_enti) AS valore
    FROM read_parquet('{support.dp.clean}')
    WHERE dimensione = 'anno_regione'
      AND (regione IS NULL OR regione NOT LIKE '%Totale%')
    GROUP BY anno, regione
),

-- === UNIONE ===
nazionale AS (
    SELECT anno, sesso, 'pensioni_vigenti' AS metrica, valore FROM pensioni_vigenti_naz
    UNION ALL SELECT anno, sesso, 'pensioni_liquidate', valore FROM liquidate_naz
    UNION ALL SELECT anno, sesso, 'rapporti_lavoro', valore FROM rapporti_naz
    UNION ALL SELECT anno, sesso, 'lavoratori_privati', valore FROM retribuzioni_naz
    UNION ALL SELECT anno, sesso, 'naspi', valore FROM naspi_naz
    UNION ALL SELECT anno, sesso, 'cig_ore', valore FROM cig_naz
    UNION ALL SELECT anno, sesso, 'assegno_unico', valore FROM assegno_naz
    UNION ALL SELECT anno, sesso, 'enti_pubblici', valore FROM dp_naz
),
regionale AS (
    SELECT anno, sesso, regione, 'pensioni_vigenti' AS metrica, valore FROM pensioni_vigenti_reg
    UNION ALL SELECT anno, sesso, regione, 'pensioni_liquidate', valore FROM liquidate_reg
    UNION ALL SELECT anno, sesso, regione, 'rapporti_lavoro', valore FROM rapporti_reg
    UNION ALL SELECT anno, sesso, regione, 'lavoratori_privati', valore FROM retribuzioni_reg
    UNION ALL SELECT anno, sesso, regione, 'naspi', valore FROM naspi_reg
    UNION ALL SELECT anno, sesso, regione, 'cig_ore', valore FROM cig_reg
    UNION ALL SELECT anno, sesso, regione, 'assegno_unico', valore FROM assegno_reg
    UNION ALL SELECT anno, sesso, regione, 'enti_pubblici', valore FROM dp_reg
)

SELECT anno, metrica, sesso, CAST(valore AS BIGINT) AS valore, CAST(NULL AS VARCHAR) AS regione
FROM nazionale
UNION ALL
SELECT anno, metrica, sesso, CAST(valore AS BIGINT) AS valore, regione
FROM regionale
