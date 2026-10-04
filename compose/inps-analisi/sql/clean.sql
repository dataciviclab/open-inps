-- INPS Analisi — CLEAN Compose
-- Unifica i dataset INPS in tabella lunga (anno, metrica, sesso, regione, valore).
-- Include sia le fonti storiche del compose sia i dataset A1 (cessazioni,
-- pensionamento, PA, redditi, RdC, DIS-COLL, serie pensioni pre-2022).

WITH

-- === PENSIONI VIGENTI (stock, 2022+) — raw_input ===
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

-- === SERIE STORICA pensioni vigenti (pre-2022) — estensione ===
pensioni_serie_hist_naz AS (
    SELECT anno, sesso, SUM(n_pensioni) AS valore
    FROM read_parquet('{support.pensioni_serie.clean}')
    WHERE dimensione = 'anno_sesso_categoria'
      AND tipo_pensione = 'vigente'
      AND anno < 2022
      AND sesso IN ('Maschi', 'Femmine')
      AND categoria IS NOT NULL
      AND categoria <> ''
    GROUP BY anno, sesso
),
pensioni_serie_hist_reg AS (
    SELECT anno, sesso, regione, SUM(n_pensioni) AS valore
    FROM read_parquet('{support.pensioni_serie.clean}')
    WHERE dimensione = 'anno_sesso_regione'
      AND tipo_pensione = 'vigente'
      AND anno < 2022
      AND sesso IN ('Maschi', 'Femmine')
      AND regione IS NOT NULL
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

-- === PENSIONAMENTO FLUSSI (decorrenza trimestrale, somma annua) ===
pensionamento_naz AS (
    SELECT anno, sesso, SUM(n_pensioni) AS valore
    FROM read_parquet('{support.pensionamento.clean}')
    WHERE dimensione = 'anno_trimestre_sesso_regione'
      AND sesso IN ('Maschi', 'Femmine')
      AND regione IS NOT NULL
    GROUP BY anno, sesso
),
pensionamento_reg AS (
    SELECT anno, sesso, regione, SUM(n_pensioni) AS valore
    FROM read_parquet('{support.pensionamento.clean}')
    WHERE dimensione = 'anno_trimestre_sesso_regione'
      AND sesso IN ('Maschi', 'Femmine')
      AND regione IS NOT NULL
    GROUP BY anno, sesso, regione
),

-- === RAPPORTI LAVORO (assunzioni 489) ===
rapporti_naz AS (
    SELECT anno, sesso, SUM(n_rapporti) AS valore
    FROM read_parquet('{support.rapporti.clean}')
    WHERE dimensione = 'anno_sesso_regione_tipo'
      AND sesso IN ('Maschi', 'Femmine')
      AND (tipo_rapporto IS NULL OR tipo_rapporto NOT LIKE '%Totale%')
      AND (regione IS NULL OR regione NOT LIKE '%Totale%')
    GROUP BY anno, sesso
),
rapporti_reg AS (
    SELECT anno, sesso, regione, SUM(n_rapporti) AS valore
    FROM read_parquet('{support.rapporti.clean}')
    WHERE dimensione = 'anno_sesso_regione_tipo'
      AND sesso IN ('Maschi', 'Femmine')
      AND (tipo_rapporto IS NULL OR tipo_rapporto NOT LIKE '%Totale%')
      AND (regione IS NULL OR regione NOT LIKE '%Totale%')
    GROUP BY anno, sesso, regione
),

-- === CESSAZIONI (490) ===
cessazioni_naz AS (
    SELECT anno, sesso, SUM(n_cessazioni) AS valore
    FROM read_parquet('{support.cessazioni.clean}')
    WHERE dimensione = 'anno_sesso_regione_tipo'
      AND sesso IN ('Maschi', 'Femmine')
      AND (tipo_cessazione IS NULL OR tipo_cessazione NOT LIKE '%Totale%')
      AND (regione IS NULL OR regione NOT LIKE '%Totale%')
    GROUP BY anno, sesso
),
cessazioni_reg AS (
    SELECT anno, sesso, regione, SUM(n_cessazioni) AS valore
    FROM read_parquet('{support.cessazioni.clean}')
    WHERE dimensione = 'anno_sesso_regione_tipo'
      AND sesso IN ('Maschi', 'Femmine')
      AND (tipo_cessazione IS NULL OR tipo_cessazione NOT LIKE '%Totale%')
      AND (regione IS NULL OR regione NOT LIKE '%Totale%')
    GROUP BY anno, sesso, regione
),

-- === RETRIBUTIONI (lavoratori privati) ===
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

-- === LAVORATORI PA (435, nessun sesso) ===
lavoratori_pa_naz AS (
    SELECT anno, 'Totale' AS sesso, SUM(n_lavoratori) AS valore
    FROM read_parquet('{support.lavoratori_pa.clean}')
    WHERE dimensione = 'anno_gruppo'
      AND gruppo_contrattuale IS NOT NULL
      AND n_lavoratori IS NOT NULL
    GROUP BY anno
),
lavoratori_pa_reg AS (
    SELECT anno, 'Totale' AS sesso, regione, SUM(n_lavoratori) AS valore
    FROM read_parquet('{support.lavoratori_pa.clean}')
    WHERE dimensione = 'anno_gruppo_regione'
      AND gruppo_contrattuale IS NOT NULL
      AND regione IS NOT NULL
      AND n_lavoratori IS NOT NULL
    GROUP BY anno, regione
),

-- === LAVORATORI REDDITI (465, tutte le posizioni) ===
lavoratori_redditi_naz AS (
    SELECT anno, sesso, SUM(n_lavoratori) AS valore
    FROM read_parquet('{support.lavoratori_redditi.clean}')
    WHERE dimensione = 'anno_sesso_posizione'
      AND sesso IN ('Maschi', 'Femmine')
      AND posizione_prevalente IS NOT NULL
    GROUP BY anno, sesso
),
lavoratori_redditi_reg AS (
    SELECT anno, sesso, regione, SUM(n_lavoratori) AS valore
    FROM read_parquet('{support.lavoratori_redditi.clean}')
    WHERE dimensione = 'anno_sesso_regione'
      AND sesso IN ('Maschi', 'Femmine')
      AND regione IS NOT NULL
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

-- === DIS-COLL (397 beneficiari, nazionale) ===
dis_coll_naz AS (
    SELECT anno, sesso, SUM(n_trattamenti) AS valore
    FROM read_parquet('{support.dis_coll.clean}')
    WHERE dimensione = 'anno_sesso'
      AND tipo_dato = 'beneficiari'
      AND sesso IN ('Maschi', 'Femmine')
    GROUP BY anno, sesso
),

-- === RDC/PDC (452 nuclei, nazionale) ===
rdc_naz AS (
    SELECT anno, 'Totale' AS sesso, SUM(n_nuclei) AS valore
    FROM read_parquet('{support.rdc.clean}')
    WHERE dimensione = 'anno_misura'
      AND misura IS NOT NULL
    GROUP BY anno
),
rdc_reg AS (
    SELECT anno, 'Totale' AS sesso, regione, SUM(n_nuclei) AS valore
    FROM read_parquet('{support.rdc.clean}')
    WHERE dimensione = 'anno_misura_regione'
      AND misura IS NOT NULL
      AND regione IS NOT NULL
    GROUP BY anno, regione
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

-- === DIPENDENTI PUBBLICI (enti 440) ===
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

-- === UNIONE NAZIONALE ===
nazionale AS (
    SELECT anno, sesso, 'pensioni_vigenti' AS metrica, valore FROM pensioni_vigenti_naz
    UNION ALL SELECT anno, sesso, 'pensioni_vigenti', valore FROM pensioni_serie_hist_naz
    UNION ALL SELECT anno, sesso, 'pensioni_liquidate', valore FROM liquidate_naz
    UNION ALL SELECT anno, sesso, 'pensionamento_flussi', valore FROM pensionamento_naz
    UNION ALL SELECT anno, sesso, 'rapporti_lavoro', valore FROM rapporti_naz
    UNION ALL SELECT anno, sesso, 'cessazioni_lavoro', valore FROM cessazioni_naz
    UNION ALL SELECT anno, sesso, 'lavoratori_privati', valore FROM retribuzioni_naz
    UNION ALL SELECT anno, sesso, 'lavoratori_pa', valore FROM lavoratori_pa_naz
    UNION ALL SELECT anno, sesso, 'lavoratori_redditi', valore FROM lavoratori_redditi_naz
    UNION ALL SELECT anno, sesso, 'naspi', valore FROM naspi_naz
    UNION ALL SELECT anno, sesso, 'dis_coll', valore FROM dis_coll_naz
    UNION ALL SELECT anno, sesso, 'rdc_nuclei', valore FROM rdc_naz
    UNION ALL SELECT anno, sesso, 'cig_ore', valore FROM cig_naz
    UNION ALL SELECT anno, sesso, 'assegno_unico', valore FROM assegno_naz
    UNION ALL SELECT anno, sesso, 'enti_pubblici', valore FROM dp_naz
),

-- === UNIONE REGIONALE ===
regionale AS (
    SELECT anno, sesso, regione, 'pensioni_vigenti' AS metrica, valore FROM pensioni_vigenti_reg
    UNION ALL SELECT anno, sesso, regione, 'pensioni_vigenti', valore FROM pensioni_serie_hist_reg
    UNION ALL SELECT anno, sesso, regione, 'pensioni_liquidate', valore FROM liquidate_reg
    UNION ALL SELECT anno, sesso, regione, 'pensionamento_flussi', valore FROM pensionamento_reg
    UNION ALL SELECT anno, sesso, regione, 'rapporti_lavoro', valore FROM rapporti_reg
    UNION ALL SELECT anno, sesso, regione, 'cessazioni_lavoro', valore FROM cessazioni_reg
    UNION ALL SELECT anno, sesso, regione, 'lavoratori_privati', valore FROM retribuzioni_reg
    UNION ALL SELECT anno, sesso, regione, 'lavoratori_pa', valore FROM lavoratori_pa_reg
    UNION ALL SELECT anno, sesso, regione, 'lavoratori_redditi', valore FROM lavoratori_redditi_reg
    UNION ALL SELECT anno, sesso, regione, 'naspi', valore FROM naspi_reg
    UNION ALL SELECT anno, sesso, regione, 'rdc_nuclei', valore FROM rdc_reg
    UNION ALL SELECT anno, sesso, regione, 'cig_ore', valore FROM cig_reg
    UNION ALL SELECT anno, sesso, regione, 'assegno_unico', valore FROM assegno_reg
    UNION ALL SELECT anno, sesso, regione, 'enti_pubblici', valore FROM dp_reg
)

SELECT anno, metrica, sesso, CAST(valore AS BIGINT) AS valore, CAST(NULL AS VARCHAR) AS regione
FROM nazionale
UNION ALL
SELECT anno, metrica, sesso, CAST(valore AS BIGINT) AS valore,
    CASE
        WHEN UPPER(regione) = 'ABRUZZO' THEN 'Abruzzo'
        WHEN UPPER(regione) = 'BASILICATA' THEN 'Basilicata'
        WHEN UPPER(regione) = 'CALABRIA' THEN 'Calabria'
        WHEN UPPER(regione) = 'CAMPANIA' THEN 'Campania'
        WHEN UPPER(regione) LIKE '%EMILIA%' THEN 'Emilia-Romagna'
        WHEN UPPER(regione) LIKE '%FRIULI%' THEN 'Friuli Venezia Giulia'
        WHEN UPPER(regione) = 'LAZIO' THEN 'Lazio'
        WHEN UPPER(regione) = 'LIGURIA' THEN 'Liguria'
        WHEN UPPER(regione) = 'LOMBARDIA' THEN 'Lombardia'
        WHEN UPPER(regione) = 'MARCHE' THEN 'Marche'
        WHEN UPPER(regione) = 'MOLISE' THEN 'Molise'
        WHEN UPPER(regione) = 'PIEMONTE' THEN 'Piemonte'
        WHEN UPPER(regione) LIKE '%PIEMONTE%' THEN 'Piemonte'
        WHEN UPPER(regione) = 'PUGLIA' THEN 'Puglia'
        WHEN UPPER(regione) = 'SARDEGNA' THEN 'Sardegna'
        WHEN UPPER(regione) = 'SICILIA' THEN 'Sicilia'
        WHEN UPPER(regione) = 'TOSCANA' THEN 'Toscana'
        WHEN UPPER(regione) LIKE '%TRENTINO%' THEN 'Trentino-Alto Adige'
        WHEN UPPER(regione) = 'UMBRIA' THEN 'Umbria'
        WHEN UPPER(regione) LIKE '%VALLE D%' THEN 'Valle d''Aosta'
        WHEN UPPER(regione) = 'VENETO' THEN 'Veneto'
        ELSE regione
    END AS regione
FROM regionale
