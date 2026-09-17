-- INPS Dipendenti Pubblici — MART Forma Giuridica
-- Enti e retribuzioni per anno e forma giuridica.

SELECT
    anno,
    forma_giuridica,
    n_enti,
    retribuzione_totale
FROM clean_input
WHERE dimensione = 'anno_forma_giuridica'
  AND (forma_giuridica IS NULL OR forma_giuridica NOT LIKE '%Totale%')
