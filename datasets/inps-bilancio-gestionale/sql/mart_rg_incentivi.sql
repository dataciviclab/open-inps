-- INPS RG — MART Incentivi
-- Capitoli di uscita del rendiconto classificati per famiglia di agevolazione.
-- La famiglia è derivata dal titolo del capitolo con parole chiave esplicite:
-- è una lettura operativa, non una classificazione giuridica.
--
-- Perimetro: solo le uscite. Le agevolazioni possono anche ridurre le entrate
-- contributive (minori entrate) e in quel caso non compaiono qui; per il valore
-- economico complessivo il riferimento è il focus trimestrale INPS.

SELECT
    anno,
    codice,
    denominazione,
    CASE
        WHEN UPPER(denominazione) LIKE '%PERIODI DI PAGA%' THEN 'Esonero generalizzato'
        WHEN UPPER(denominazione) LIKE '%AREE SVANTAGGIATE%'
          OR UPPER(denominazione) LIKE '%MEZZOGIORNO%'
          OR UPPER(denominazione) LIKE '%ZES%' THEN 'Decontribuzione Sud / ZES'
        WHEN UPPER(denominazione) LIKE '%PRESTAZIONI TEMPORANEE%'
          OR UPPER(denominazione) LIKE '%CASSA INTEGRAZIONE%' THEN 'Sgravi CIG e ammortizzatori'
        WHEN UPPER(denominazione) LIKE '%FONDO DI GARANZIA%' THEN 'Fondo garanzia TFR'
        WHEN UPPER(denominazione) LIKE '%GIOVAN%' THEN 'Esonero giovani'
        WHEN UPPER(denominazione) LIKE '%DONNE%'
          OR UPPER(denominazione) LIKE '%LAVORATRICI%'
          OR UPPER(denominazione) LIKE '%MADRI%'
          OR UPPER(denominazione) LIKE '%PARITA%GENERE%' THEN 'Donne, maternità e parità'
        WHEN UPPER(denominazione) LIKE '%DISABIL%' THEN 'Disabilità'
        WHEN UPPER(denominazione) LIKE '%ESONERO%'
          AND (
              UPPER(denominazione) LIKE '%AUTONOMI%'
              OR UPPER(denominazione) LIKE '%LIBERI PROFESSIONISTI%'
          ) THEN 'Esonero autonomi'
        WHEN UPPER(denominazione) LIKE '%ARMATRICI%'
          OR UPPER(denominazione) LIKE '%REGISTRO INTERNAZIONALE%' THEN 'Marittimo'
        ELSE 'Altre misure'
    END AS famiglia,
    importo_esercizio_eur,
    previsioni_definitive_eur,
    importo_esercizio_eur - previsioni_definitive_eur AS scarto_previsionale_eur
FROM clean_input
WHERE tipo = 'uscita'
  AND importo_esercizio_eur IS NOT NULL
  -- Perimetro: una delle keyword di agevolazione contributiva. Le famiglie
  -- più specifiche (TFR, marittimo, disabilità) si applicano solo a righe
  -- già dentro il perimetro, non lo allargano.
  AND (
      UPPER(denominazione) LIKE '%INCENTIV%'
      OR UPPER(denominazione) LIKE '%ESONERO%'
      OR UPPER(denominazione) LIKE '%SGRAVI%'
      OR UPPER(denominazione) LIKE '%DECONTRIB%'
      OR UPPER(denominazione) LIKE '%AGEVOLAZION%'
  )
  -- Esclude gli "incentivi" che non sono agevolazioni contributive
  -- (progettazione, funzioni tecniche): oggi a importo zero, ma fuori tema.
  AND NOT (
      UPPER(denominazione) LIKE '%INCENTIVI PER LA PROGETTAZIONE%'
      OR UPPER(denominazione) LIKE '%INCENTIVI AL PERSONALE PER LO SVOLGIMENTO DI FUNZIONI TECNICHE%'
  )
ORDER BY anno, importo_esercizio_eur DESC
