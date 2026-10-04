-- INPS Analisi — MART Benchmark
-- Rapporti strutturali: pensioni/lavoratori, assunzioni/cessazioni,
-- NASpI/assunzioni, DIS-COLL, RdC, gap genere.

WITH

naz AS (
    SELECT anno, metrica, sesso, valore
    FROM clean_input
    WHERE regione IS NULL
),

agg AS (
    SELECT anno, metrica,
        SUM(CASE WHEN sesso IN ('Maschi','Femmine','Totale') THEN valore ELSE 0 END) AS valore_tot,
        SUM(CASE WHEN sesso = 'Maschi' THEN valore ELSE 0 END) AS valore_m,
        SUM(CASE WHEN sesso = 'Femmine' THEN valore ELSE 0 END) AS valore_f
    FROM naz
    GROUP BY anno, metrica
),

piv AS (
    SELECT
        anno,
        MAX(CASE WHEN metrica = 'pensioni_vigenti' THEN valore_tot END) AS pensioni,
        MAX(CASE WHEN metrica = 'pensioni_vigenti' THEN valore_m END) AS pensioni_m,
        MAX(CASE WHEN metrica = 'pensioni_vigenti' THEN valore_f END) AS pensioni_f,
        MAX(CASE WHEN metrica = 'rapporti_lavoro' THEN valore_m END) AS assunzioni_m,
        MAX(CASE WHEN metrica = 'rapporti_lavoro' THEN valore_f END) AS assunzioni_f,
        MAX(CASE WHEN metrica = 'rapporti_lavoro' THEN valore_tot END) AS assunzioni,
        MAX(CASE WHEN metrica = 'cessazioni_lavoro' THEN valore_tot END) AS cessazioni,
        MAX(CASE WHEN metrica = 'cessazioni_lavoro' THEN valore_m END) AS cessazioni_m,
        MAX(CASE WHEN metrica = 'cessazioni_lavoro' THEN valore_f END) AS cessazioni_f,
        MAX(CASE WHEN metrica = 'lavoratori_privati' THEN valore_tot END) AS lavoratori,
        MAX(CASE WHEN metrica = 'lavoratori_pa' THEN valore_tot END) AS lavoratori_pa,
        MAX(CASE WHEN metrica = 'lavoratori_redditi' THEN valore_tot END) AS lavoratori_redditi,
        MAX(CASE WHEN metrica = 'pensionamento_flussi' THEN valore_tot END) AS pensionamento,
        MAX(CASE WHEN metrica = 'naspi' THEN valore_tot END) AS naspi,
        MAX(CASE WHEN metrica = 'naspi' THEN valore_m END) AS naspi_m,
        MAX(CASE WHEN metrica = 'naspi' THEN valore_f END) AS naspi_f,
        MAX(CASE WHEN metrica = 'dis_coll' THEN valore_tot END) AS dis_coll,
        MAX(CASE WHEN metrica = 'rdc_nuclei' THEN valore_tot END) AS rdc,
        MAX(CASE WHEN metrica = 'cig_ore' THEN valore_tot END) AS cig,
        MAX(CASE WHEN metrica = 'pensioni_liquidate' THEN valore_tot END) AS liquidate
    FROM agg
    GROUP BY anno
)

SELECT
    anno,
    CASE WHEN COALESCE(lavoratori, 0) > 0
        THEN ROUND(pensioni * 1.0 / lavoratori, 2) END AS rapporto_pensioni_lavoratori,
    CASE WHEN COALESCE(assunzioni, 0) > 0
        THEN ROUND(cessazioni * 100.0 / assunzioni, 1) END AS rapporto_cessazioni_assunzioni_pct,
    CASE WHEN COALESCE(assunzioni_m + assunzioni_f, 0) > 0
        THEN ROUND(naspi * 100.0 / (assunzioni_m + assunzioni_f), 1) END AS rapporto_naspi_assunzioni_pct,
    CASE WHEN COALESCE(naspi, 0) > 0
        THEN ROUND(dis_coll * 100.0 / naspi, 2) END AS rapporto_dis_coll_naspi_pct,
    CASE WHEN COALESCE(pensioni, 0) > 0
        THEN ROUND(COALESCE(liquidate, 0) * 100.0 / pensioni, 1) END AS turnover_pensionistico_pct,
    CASE WHEN COALESCE(pensioni, 0) > 0
        THEN ROUND(COALESCE(pensionamento, 0) * 100.0 / pensioni, 1) END AS flusso_pensionamento_pct,
    CASE WHEN COALESCE(assunzioni_m, 0) > 0
        THEN ROUND((assunzioni_m - assunzioni_f) * 100.0 / assunzioni_m, 1) END AS gap_genere_assunzioni_pct,
    CASE WHEN COALESCE(cessazioni_m, 0) > 0
        THEN ROUND((cessazioni_m - cessazioni_f) * 100.0 / cessazioni_m, 1) END AS gap_genere_cessazioni_pct,
    CASE WHEN COALESCE(pensioni_m, 0) > 0
        THEN ROUND((pensioni_f - pensioni_m) * 100.0 / pensioni_m, 1) END AS gap_genere_pensioni_pct,
    CASE WHEN COALESCE(naspi_m, 0) > 0
        THEN ROUND((naspi_f - naspi_m) * 100.0 / naspi_m, 1) END AS gap_genere_naspi_pct,
    pensioni, pensioni_m, pensioni_f,
    assunzioni, assunzioni_m, assunzioni_f,
    cessazioni, cessazioni_m, cessazioni_f,
    lavoratori, lavoratori_pa, lavoratori_redditi,
    pensionamento, naspi, dis_coll, rdc, cig, liquidate
FROM piv
ORDER BY anno
