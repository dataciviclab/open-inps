-- INPS Flussi Settore — MART Nazionale
-- Assunzioni e cessazioni per anno, sesso, settore NACE e tipologia.
-- Join key stabile: settore_codice (non l'etichetta lunga del backend).

SELECT
    anno,
    flusso,
    nace_class,
    sesso,
    settore_codice,
    settore_nace,
    tipo_flusso,
    n_rapporti
FROM clean_input
WHERE dimensione = 'anno_sesso_settore_tipo'
  AND sesso IN ('Maschi', 'Femmine')
  AND (tipo_flusso IS NULL OR tipo_flusso NOT LIKE '%Totale%')
  AND settore_codice IS NOT NULL
  AND n_rapporti IS NOT NULL
