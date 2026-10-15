"""Modello di sostenibilità previdenzaria (pay-as-you-go).

Identità contabile per ogni anno t:
    S(t) = τ(t) × W(t) + G(t)
dove W = N × y (massa salariale), G = copertura da fiscalità generale.

Inverse (tenendo fissi due dei tre fattori):
    τ* = (S − G) / W        aliquota necessaria
    N* = (S − G) / (τ × y)  occupati necessari
    y* = (S − G) / (τ × N)  reddito medio necessario

Funzioni pure: nessuna I/O, pandas in / pandas out. La pagina
carica i mart e chiama queste.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Baseline:
    """Grandezze misurate per un anno di riferimento."""

    anno: int
    n_pensionati: float  # pensioni INPS vigenti (M+F)
    spesa_pensioni_eur: float  # spesa annua pensioni (importo_medio ×12 ×n)
    n_lavoratori: float  # lavoratori con posizione prevalente
    reddito_lavoro_eur: float  # massa redditi da lavoro (imponibile INPS)
    contributi_ce_eur: float  # aliquote contributive CE INPS
    trasferimenti_stato_ce_eur: float  # trasferimenti dallo Stato CE INPS
    spesa_prestazioni_ce_eur: float  # spese per prestazioni CE INPS (tutte le prestazioni)

    @property
    def reddito_medio(self) -> float:
        """Reddito medio da lavoro pro capite."""
        return self.reddito_lavoro_eur / self.n_lavoratori

    @property
    def pensione_media_annua(self) -> float:
        return self.spesa_pensioni_eur / self.n_pensionati

    @property
    def pensione_media_mensile(self) -> float:
        return self.pensione_media_annua / 12

    @property
    def tau_effettivo(self) -> float:
        """Aliquota contributiva effettiva = contributi CE / massa redditi."""
        return self.contributi_ce_eur / self.reddito_lavoro_eur

    @property
    def quota_fiscalita_prestazioni(self) -> float:
        """Quota delle spese per prestazioni (tutte) coperta da trasferimenti Stato."""
        return self.trasferimenti_stato_ce_eur / self.spesa_prestazioni_ce_eur

    @property
    def rapporto_pensionati_lavoratori(self) -> float:
        return self.n_pensionati / self.n_lavoratori

    @property
    def tasso_sostituzione_prox(self) -> float:
        """Tasso di sostituzione prox = pensione media / reddito medio lavoro."""
        return self.pensione_media_annua / self.reddito_medio


@dataclass(frozen=True)
class Bisogno:
    """Quanto serve per coprire S con la quota data da fiscalità generale."""

    tau_necessario: float  # aliquota necessaria sul reddito da lavoro
    n_necessario: float  # occupati necessari (a τ attuale)
    reddito_medio_necessario: float  # reddito medio necessario (a τ attuale)
    contributi_necessari_eur: float  # gettito contributivo richiesto
    fiscalita_necessaria_eur: float  # G richiesto (se τ tenuto attuale)


def tau_necessario(spesa_eur: float, fiscalita_eur: float, massa_salariale_eur: float) -> float:
    return (spesa_eur - fiscalita_eur) / massa_salariale_eur


def n_necessario(spesa_eur: float, fiscalita_eur: float, tau: float, reddito_medio_eur: float) -> float:
    return (spesa_eur - fiscalita_eur) / (tau * reddito_medio_eur)


def reddito_medio_necessario(spesa_eur: float, fiscalita_eur: float, tau: float, n: float) -> float:
    return (spesa_eur - fiscalita_eur) / (tau * n)


def calcola_bisogno(
    spesa_eur: float,
    massa_salariale_eur: float,
    n_lavoratori: float,
    reddito_medio_eur: float,
    tau_attuale: float,
    quota_fiscalita: float,
) -> Bisogno:
    """Bisogno di bilancio a fiscalità generale in quota `quota_fiscalita` di S.

    G = quota_fiscalita × S; residuo a carico dei contributi.
    """
    fiscalita = quota_fiscalita * spesa_eur
    contributi = spesa_eur - fiscalita
    return Bisogno(
        tau_necessario=contributi / massa_salariale_eur,
        n_necessario=contributi / (tau_attuale * reddito_medio_eur),
        reddito_medio_necessario=contributi / (tau_attuale * n_lavoratori),
        contributi_necessari_eur=contributi,
        fiscalita_necessaria_eur=fiscalita,
    )


def proietta_fattori(
    baseline: Baseline,
    anni: list[int],
    pop_lavorativa_idx: dict[int, float],
    tasso_occupazione: float,
    crescita_reale_salari: float,
) -> pd.DataFrame:
    """Proiezione semplificata dei fattori per anno.

    pop_lavorativa_idx: indice (base anno baseline = 1.0) della popolazione
    in età lavorativa per ogni anno di proiezione.
    tasso_occupazione: frazione della popolazione lavorativa occupata (costante).
    crescita_reale_salari: crescita reale annua del reddito medio (es. 0.007).
    """
    rows = []
    for a in anni:
        k = pop_lavorativa_idx.get(a, 1.0)
        n = baseline.n_lavoratori * k * (tasso_occupazione / _tasso_base(baseline))
        y = baseline.reddito_medio * (1 + crescita_reale_salari) ** (a - baseline.anno)
        rows.append(
            {
                "anno": a,
                "n_lavoratori": n,
                "reddito_medio": y,
                "massa_salariale": n * y,
            }
        )
    return pd.DataFrame(rows)


def _tasso_base(baseline: Baseline) -> float:
    """Tasso di occupazione implicito nella baseline (non noto esplicitamente).

    Usato solo come normalizzatore relativo: assumiamo che il rapporto
    n_lavoratori / pop_lavorativa resti scalabile. Per la proiezione
    serve l'indice di popolazione, non il livello assoluto.
    """
    return 1.0


def carica_proiezioni_istat(path_csv: str) -> pd.DataFrame:
    """Legge il CSV snapshot ISTAT (anno, idx_15_64, idx_65p, idx_tot)."""
    df = pd.read_csv(path_csv)
    required = {"anno", "idx_15_64", "idx_65p"}
    if not required.issubset(df.columns):
        raise ValueError(f"CSV ISTAT mancante di colonne: {required - set(df.columns)}")
    return df.sort_values("anno").reset_index(drop=True)


def proietta_fase_b(
    baseline: Baseline,
    df_istat: pd.DataFrame,
    crescita_reale_salari: float = 0.007,
    tasso_occupazione_delta: float = 0.0,
    quota_fiscalita: float = 0.33,
    rivalutazione_reale_pensioni: float = 0.0,
) -> pd.DataFrame:
    """Proiezione 2025-2050 con indici ISTAT reali (pop 15-64 e 65+).

    N(t)  = N₀ × idx_15-64(t) × (1 + delta_occupazione)^(t−2025)
    P(t)  = P₀ × idx_65+(t)                     — pensionati ≈ pop 65+
    y(t)  = y₀ × (1 + g_salari)^(t−2025)
    pen_media(t) = pen_media₀ × (1 + g_rival)^(t−2025)   (0 = costante reale)
    S(t)  = P(t) × pen_media(t)
    G(t)  = qG × S(t)
    τ*(t) = (S(t) − G(t)) / (N(t) × y(t))

    Ancoraggio: baseline 2024 ≈ indici 2025 (continuità anno-su-anno).
    """
    rows = []
    for _, r in df_istat.iterrows():
        a = int(r["anno"])
        t = a - 2025
        occ_f = (1.0 + tasso_occupazione_delta) ** t
        n = baseline.n_lavoratori * float(r["idx_15_64"]) * occ_f
        n_pens = baseline.n_pensionati * float(r["idx_65p"])
        y = baseline.reddito_medio * (1 + crescita_reale_salari) ** t
        pen_media = baseline.pensione_media_annua * (1 + rivalutazione_reale_pensioni) ** t
        spesa = n_pens * pen_media
        g = quota_fiscalita * spesa
        w = n * y
        tau_star = (spesa - g) / w if w > 0 else float("nan")
        rows.append(
            {
                "anno": a,
                "pop_15_64_idx": float(r["idx_15_64"]),
                "pop_65p_idx": float(r["idx_65p"]),
                "n_lavoratori": n,
                "reddito_medio": y,
                "massa_salariale": w,
                "n_pensionati": n_pens,
                "pensione_media_annua": pen_media,
                "spesa_pensioni_eur": spesa,
                "fiscalita_eur": g,
                "contributi_necessari_eur": spesa - g,
                "tau_necessario": tau_star,
                "rapporto_pensionati_lavoratori": n_pens / n if n > 0 else float("nan"),
            }
        )
    df = pd.DataFrame(rows)
    df["tau_effettivo"] = baseline.tau_effettivo
    return df


def estrai_baseline(
    df_pensioni: pd.DataFrame,
    df_lavoratori: pd.DataFrame,
    df_ce: pd.DataFrame,
    anno: int,
) -> Baseline:
    """Costruisce la Baseline dai mart del dashboard.

    df_pensioni: mart_vigenti_regione (anno, sesso M/F, chiave, n_pensioni,
        importo_medio_mensile_eur) — già senza righe Totale.
    df_lavoratori: mart_lavoratori_redditi_posizione (anno, sesso,
        posizione_prevalente, n_lavoratori, reddito_cumulato).
    df_ce: mart_ce_aggregati (anno, voce, importo_eur) — solo fonte generale.
    """
    p = df_pensioni[
        (df_pensioni["anno"] == anno)
        & (df_pensioni["sesso"].isin(["Maschi", "Femmine"]))
    ]
    n_pens = float(p["n_pensioni"].sum())
    spesa = float((p["importo_medio_mensile_eur"] * p["n_pensioni"] * 12).sum())

    lav = df_lavoratori[df_lavoratori["anno"] == anno]
    n_lav = float(lav["n_lavoratori"].sum())
    reddito = float(lav["reddito_cumulato"].sum())

    c = df_ce[df_ce["anno"] == anno]

    def _voce(frag: str) -> float:
        m = c[c["voce"].str.contains(frag, case=False, regex=True, na=False)]
        if m.empty:
            return 0.0
        return float(m["importo_eur"].iloc[0])

    contributi = _voce(r"^Aliquote contributive")
    trasferimenti = _voce(r"^Trasferimenti da parte dello Stato$")
    prestazioni = abs(_voce(r"^Spese per prestazioni$"))

    if min(n_pens, spesa, n_lav, reddito) <= 0:
        raise ValueError(f"Baseline {anno}: grandezze non positive")

    return Baseline(
        anno=anno,
        n_pensionati=n_pens,
        spesa_pensioni_eur=spesa,
        n_lavoratori=n_lav,
        reddito_lavoro_eur=reddito,
        contributi_ce_eur=contributi,
        trasferimenti_stato_ce_eur=trasferimenti,
        spesa_prestazioni_ce_eur=prestazioni,
    )


# ── Leve di correzione (scenari contabili, non proposte di policy) ──────────


def leva_prelievo_solidale(
    df_importo: pd.DataFrame,
    soglia_mensile: float,
    aliquota: float,
) -> dict:
    """Risparmio da aliquota sulle pensioni con importo medio >= soglia.

    df_importo: mart_vigenti_importo (anno, sesso, chiave=classe, n_pensioni,
        importo_medio_mensile_eur). Approssimazione: aliquota uniforme su
        tutte le classi sopra soglia (non tasso marginale sul solo excedente).
    """
    d = df_importo[df_importo["chiave"].notna() & ~df_importo["chiave"].str.contains("Totale", na=False)]
    d = d[d["importo_medio_mensile_eur"] >= soglia_mensile]
    n = float(d["n_pensioni"].sum())
    massa_annua = float((d["importo_medio_mensile_eur"] * d["n_pensioni"] * 12).sum())
    return {
        "soglia_mensile": soglia_mensile,
        "aliquota": aliquota,
        "n_pensionati": n,
        "massa_annua_eur": massa_annua,
        "risparmio_eur": massa_annua * aliquota,
    }


def leva_decurtazione_eta(
    df_eta: pd.DataFrame,
    eta_minima: int,
    aliquota: float,
) -> dict:
    """Risparmio da decurtazione su tutte le pensioni di eta >= eta_minima.

    df_eta: mart_vigenti_eta (anno, sesso, chiave=classe_eta, n_pensioni,
        importo_medio_mensile_eur). classe_eta parse: '85 - 89' → 85,
    '90 ed oltre' → 90.
    """
    d = df_eta[df_eta["chiave"].notna() & ~df_eta["chiave"].str.contains("Totale", na=False)].copy()
    d["eta_min"] = d["chiave"].str.extract(r"(\d+)").astype(float)
    d = d[d["eta_min"] >= eta_minima]
    n = float(d["n_pensioni"].sum())
    massa_annua = float((d["importo_medio_mensile_eur"] * d["n_pensioni"] * 12).sum())
    return {
        "eta_minima": eta_minima,
        "aliquota": aliquota,
        "n_pensionati": n,
        "massa_annua_eur": massa_annua,
        "risparmio_eur": massa_annua * aliquota,
    }


def leva_floor(
    df_importo: pd.DataFrame,
    floor_mensile: float,
) -> dict:
    """Costo di portare tutte le pensioni sotto `floor_mensile` al floor."""
    d = df_importo[df_importo["chiave"].notna() & ~df_importo["chiave"].str.contains("Totale", na=False)]
    sotto = d[d["importo_medio_mensile_eur"] < floor_mensile]
    n = float(sotto["n_pensioni"].sum())
    massa_attuale = float((sotto["importo_medio_mensile_eur"] * sotto["n_pensioni"] * 12).sum())
    massa_target = floor_mensile * 12 * n
    return {
        "floor_mensile": floor_mensile,
        "n_pensionati": n,
        "massa_attuale_eur": massa_attuale,
        "massa_target_eur": massa_target,
        "costo_extra_eur": max(0.0, massa_target - massa_attuale),
    }
