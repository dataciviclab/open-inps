-- INPS Pensionamento Flussi — MART Gestione
-- Nuove pensioni per anno decorrenza, trimestre, sesso e gestione.

SELECT
    anno,
    trimestre,
    sesso,
    gestione,
    n_pensioni,
    eta_media_decorrenza,
    importo_medio_decorrenza_eur
FROM clean_input
WHERE dimensione = 'anno_trimestre_sesso_gestione'
  AND sesso IN ('Maschi', 'Femmine')
  AND gestione IS NOT NULL
  AND gestione <> ''
  AND n_pensioni IS NOT NULL
