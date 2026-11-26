-- INPS Retribuzioni — CLEAN
-- Macro toolkit: cast_int, remove_dot_thousands, normalize_string
-- Legge solo da raw_input.
--
-- Misure API (obs 347/492/525), verificate su getStrutturaOsservatorio:
--   lav_annoSUM = numero lavoratori nell'anno
--   RRSUM      = retribuzione nell'anno (euro)
--   s_retrSUM  = numero settimane retribuite nell'anno
--   UU_TOTSUM  = numero settimane utili nell'anno
--   GGSUM      = numero giornate retribuite nell'anno
--
-- NOTA (2026-10): fino a questa revisione il clean mappava s_retrSUM ->
-- somma_retribuzioni e UU_TOTSUM -> unita_lavorative. Erano settimane, non
-- euro/unità lavorative. Le colonne sono state rinominate; il contratto
-- pubblico del dataset è cambiato.

WITH raw AS (
    SELECT
        cast_int(anno) AS anno,
        normalize_string(fonte) AS fonte,
        normalize_string(dimensione) AS dimensione,
        normalize_string(Sesso) AS sesso,
        normalize_string(Regione) AS regione,
        normalize_string("Classe di età") AS classe_eta,
        normalize_string(COALESCE("Sezione ATECO 2007", "Sezione ATECO 2025")) AS settore_label,
        remove_dot_thousands(lav_annoSUM) AS n_lavoratori,
        remove_dot_thousands(RRSUM) AS retribuzione_totale,
        remove_dot_thousands(s_retrSUM) AS settimane_retribuite,
        remove_dot_thousands(UU_TOTSUM) AS settimane_utili,
        remove_dot_thousands(GGSUM) AS giornate_retribuite
    FROM raw_input
),
mapping(pattern, codice, nome, priorita) AS (
    SELECT * FROM (VALUES
        ('%estrazione di minerali%', 'B', 'Estrazione di minerali', 1),
        ('%manifatturier%', 'C', 'Manifattura', 1),
        ('%fornitura di energia%', 'D', 'Energia', 1),
        ('%fornitura di acqua%', 'E', 'Acqua e rifiuti', 1),
        ('%costruzioni%', 'F', 'Costruzioni', 1),
        ('%commercio all%ingrosso%', 'G', 'Commercio e riparazioni', 1),
        ('%trasporto e magazzinaggio%', 'H', 'Trasporti e magazzinaggio', 1),
        ('%alloggio%', 'I', 'Alloggio e ristorazione', 1),
        ('%informazione e comunicazione%', 'J', 'Informazione e comunicazione', 1),
        ('%finanziarie e assicurative%', 'K', 'Finanza e assicurazioni', 1),
        ('%immobiliari%', 'L', 'Attivita immobiliari', 1),
        ('%professionali%', 'M', 'Attivita professionali e scientifiche', 1),
        ('%noleggio%', 'N', 'Noleggio e servizi di supporto', 1),
        ('%istruzione%', 'P', 'Istruzione', 1),
        ('%salute umana%', 'Q', 'Sanita e assistenza sociale', 1),
        ('%sanita%', 'Q', 'Sanita e assistenza sociale', 1),
        ('%artistiche%', 'R', 'Arte e spettacolo', 1),
        ('%famiglie e convivenze%', 'T', 'Famiglie e convivenze', 1),
        -- etichette ATECO 2025 (sezioni riorganizzate)
        ('%estrattive%', 'B', 'Estrazione di minerali', 1),
        ('%amministrative e di servizi di supporto%', 'N', 'Noleggio e servizi di supporto', 1),
        ('%editoriali%', 'J', 'Informazione e comunicazione', 1),
        ('%telecomunicazioni%', 'J', 'Informazione e comunicazione', 1),
        -- catch-all, ultima priorità: non deve oscurare le etichette specifiche
        ('%altre attivit%', 'S', 'Altri servizi', 99)
    ) AS t(pattern, codice, nome, priorita)
)
SELECT
    r.anno,
    r.fonte,
    r.dimensione,
    r.sesso,
    r.regione,
    r.classe_eta,
    r.settore_label,
    m.codice AS settore_codice,
    m.nome AS settore_nace,
    r.n_lavoratori,
    r.retribuzione_totale,
    r.settimane_retribuite,
    r.settimane_utili,
    r.giornate_retribuite
FROM raw r
LEFT JOIN LATERAL (
    SELECT codice, nome
    FROM mapping
    WHERE r.settore_label ILIKE pattern
    ORDER BY priorita
    LIMIT 1
) m ON TRUE
