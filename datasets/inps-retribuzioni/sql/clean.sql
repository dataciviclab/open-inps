-- INPS Retribuzioni — CLEAN
-- Macro toolkit: cast_int, remove_dot_thousands, normalize_string
-- Legge solo da raw_input.
--
-- Misure API (obs 347/492), verificate su getStrutturaOsservatorio:
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
        normalize_string("Sezione ATECO 2007") AS settore_label,
        remove_dot_thousands(lav_annoSUM) AS n_lavoratori,
        remove_dot_thousands(RRSUM) AS retribuzione_totale,
        remove_dot_thousands(s_retrSUM) AS settimane_retribuite,
        remove_dot_thousands(UU_TOTSUM) AS settimane_utili,
        remove_dot_thousands(GGSUM) AS giornate_retribuite
    FROM raw_input
),
mapping(pattern, codice, nome) AS (
    SELECT * FROM (VALUES
        ('%estrazione di minerali%', 'B', 'Estrazione di minerali'),
        ('%manifatturier%', 'C', 'Manifattura'),
        ('%fornitura di energia%', 'D', 'Energia'),
        ('%fornitura di acqua%', 'E', 'Acqua e rifiuti'),
        ('%costruzioni%', 'F', 'Costruzioni'),
        ('%commercio all%ingrosso%', 'G', 'Commercio e riparazioni'),
        ('%trasporto e magazzinaggio%', 'H', 'Trasporti e magazzinaggio'),
        ('%alloggio%', 'I', 'Alloggio e ristorazione'),
        ('%informazione e comunicazione%', 'J', 'Informazione e comunicazione'),
        ('%finanziarie e assicurative%', 'K', 'Finanza e assicurazioni'),
        ('%immobiliari%', 'L', 'Attivita immobiliari'),
        ('%professionali%', 'M', 'Attivita professionali e scientifiche'),
        ('%noleggio%', 'N', 'Noleggio e servizi di supporto'),
        ('%istruzione%', 'P', 'Istruzione'),
        ('%sanita%', 'Q', 'Sanita e assistenza sociale'),
        ('%artistiche%', 'R', 'Arte e spettacolo'),
        ('%altre attivita%', 'S', 'Altri servizi'),
        ('%famiglie e convivenze%', 'T', 'Famiglie e convivenze')
    ) AS t(pattern, codice, nome)
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
LEFT JOIN mapping m ON r.settore_label ILIKE m.pattern
