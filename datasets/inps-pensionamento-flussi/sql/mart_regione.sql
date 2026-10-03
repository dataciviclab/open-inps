-- INPS Pensionamento Flussi — MART Regione
-- Nuove pensioni per anno decorrenza, trimestre, sesso e regione sede INPS.

SELECT
    anno,
    trimestre,
    sesso,
    regione,
    n_pensioni,
    eta_media_decorrenza,
    importo_medio_decorrenza_eur
FROM clean_input
WHERE dimensione = 'anno_trimestre_sesso_regione'
  AND sesso IN ('Maschi', 'Femmine')
  AND regione IS NOT NULL
  AND regione <> ''
  AND n_pensioni IS NOT NULL
