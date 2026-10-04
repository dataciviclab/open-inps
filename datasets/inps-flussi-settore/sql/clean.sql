-- INPS Flussi Settore — CLEAN
-- Macro toolkit: cast_int, remove_dot_thousands, normalize_string
--
-- Le etichette NACE del backend non sono una chiave stabile (variano per
-- accenti, spazi, "e"/"ed", e tra Rev.2 e Rev.2.1). Si mappa a un codice
-- sezione + nome breve stabile; l'etichetta lunga resta come riferimento.

WITH raw AS (
    SELECT
        cast_int(anno) AS anno,
        normalize_string(dimensione) AS dimensione,
        normalize_string(flusso) AS flusso,
        normalize_string(nace_class) AS nace_class,
        normalize_string(Sesso) AS sesso,
        normalize_string("Settore di attività economica (NACE Rev. 2)") AS settore_label,
        normalize_string(Regione) AS regione,
        normalize_string(
            COALESCE("Tipologia assunzione", "Tipologia cessazione")
        ) AS tipo_flusso,
        remove_dot_thousands("NUM_DENUNCE_SUM") AS n_rapporti
    FROM raw_input
)

SELECT
    anno,
    dimensione,
    flusso,
    nace_class,
    sesso,
    CASE
        WHEN settore_label ILIKE '%Non ripartibili%' THEN NULL
        WHEN settore_label ILIKE '%Agricoltura%' THEN 'A'
        WHEN settore_label ILIKE '%estrattiv%'
            OR settore_label ILIKE '%manifattur%'
            OR settore_label ILIKE '%energia%' THEN 'B-E'
        WHEN settore_label ILIKE '%Costruzioni%' THEN 'F'
        WHEN settore_label ILIKE '%Commercio all%'
            OR settore_label ILIKE '%trasporto%'
            OR settore_label ILIKE '%alloggio%'
            OR settore_label ILIKE '%ristorazione%' THEN 'G-I'
        WHEN settore_label ILIKE '%informazione e comunicazione%' THEN 'J'
        WHEN settore_label ILIKE '%finanziarie%' THEN 'K'
        WHEN settore_label ILIKE '%immobiliari%' THEN 'L'
        WHEN settore_label ILIKE '%Amministrazione pubblica%'
            OR settore_label ILIKE '%istruzione%'
            OR settore_label ILIKE '%salute umana%'
            OR settore_label ILIKE '%assistenza sociale%' THEN 'O-U'
        WHEN settore_label ILIKE '%professional%'
            OR settore_label ILIKE '%servizi di supporto%' THEN 'M-N'
        ELSE 'Z'
    END AS settore_codice,
    CASE
        WHEN settore_label ILIKE '%Non ripartibili%' THEN NULL
        WHEN settore_label ILIKE '%Agricoltura%' THEN 'Agricoltura, silvicoltura e pesca'
        WHEN settore_label ILIKE '%estrattiv%'
            OR settore_label ILIKE '%manifattur%'
            OR settore_label ILIKE '%energia%' THEN 'Imprese manifatturiere ed energetiche'
        WHEN settore_label ILIKE '%Costruzioni%' THEN 'Costruzioni'
        WHEN settore_label ILIKE '%Commercio all%'
            OR settore_label ILIKE '%trasporto%'
            OR settore_label ILIKE '%alloggio%'
            OR settore_label ILIKE '%ristorazione%' THEN 'Commercio, trasporto, alloggio e ristorazione'
        WHEN settore_label ILIKE '%informazione e comunicazione%' THEN 'Informazione e comunicazione'
        WHEN settore_label ILIKE '%finanziarie%' THEN 'Attivita finanziarie e assicurative'
        WHEN settore_label ILIKE '%immobiliari%' THEN 'Attivita immobiliari'
        WHEN settore_label ILIKE '%Amministrazione pubblica%'
            OR settore_label ILIKE '%istruzione%'
            OR settore_label ILIKE '%salute umana%'
            OR settore_label ILIKE '%assistenza sociale%' THEN 'Pubblica amministrazione, istruzione e salute'
        WHEN settore_label ILIKE '%professional%'
            OR settore_label ILIKE '%servizi di supporto%' THEN 'Attivita professionali, scientifiche e tecniche'
        ELSE 'Altre attivita'
    END AS settore_nace,
    settore_label AS settore_label_api,
    regione,
    tipo_flusso,
    n_rapporti
FROM raw
