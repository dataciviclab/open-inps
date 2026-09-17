-- INPS Analisi — MART Benchmark
-- Rapporti strutturali: pensioni/lavoratori, NASpI/assunzioni, gap genere.

WITH

-- Dati nazionali (aggrega Maschi+Femmine quando manca Totale)
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
        MAX(CASE WHEN metrica = 'lavoratori_privati' THEN valore_tot END) AS lavoratori,
        MAX(CASE WHEN metrica = 'naspi' THEN valore_tot END) AS naspi,
        MAX(CASE WHEN metrica = 'naspi' THEN valore_m END) AS naspi_m,
        MAX(CASE WHEN metrica = 'naspi' THEN valore_f END) AS naspi_f,
        MAX(CASE WHEN metrica = 'cig_ore' THEN valore_tot END) AS cig,
        MAX(CASE WHEN metrica = 'pensioni_liquidate' THEN valore_tot END) AS liquidate
    FROM agg
    GROUP BY anno
)

SELECT
    anno,
    CASE WHEN COALESCE(lavoratori, 0) > 0
        THEN ROUND(pensioni * 1.0 / lavoratori, 2) END AS rapporto_pensioni_lavoratori,
    CASE WHEN (COALESCE(assunzioni_m, 0) + COALESCE(assunzioni_f, 0)) > 0
        THEN ROUND(naspi * 100.0 / (assunzioni_m + assunzioni_f), 1) END AS rapporto_naspi_assunzioni_pct,
    CASE WHEN COALESCE(pensioni, 0) > 0
        THEN ROUND(COALESCE(liquidate, 0) * 100.0 / pensioni, 1) END AS turnover_pensionistico_pct,
    CASE WHEN COALESCE(assunzioni_m, 0) > 0
        THEN ROUND((assunzioni_m - assunzioni_f) * 100.0 / assunzioni_m, 1) END AS gap_genere_assunzioni_pct,
    CASE WHEN COALESCE(pensioni_m, 0) > 0
        THEN ROUND((pensioni_f - pensioni_m) * 100.0 / pensioni_m, 1) END AS gap_genere_pensioni_pct,
    CASE WHEN COALESCE(naspi_m, 0) > 0
        THEN ROUND((naspi_f - naspi_m) * 100.0 / naspi_m, 1) END AS gap_genere_naspi_pct,
    pensioni, pensioni_m, pensioni_f, assunzioni_m, assunzioni_f,
    lavoratori, naspi, cig, liquidate
FROM piv
ORDER BY anno
