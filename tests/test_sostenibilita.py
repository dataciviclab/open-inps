"""Test modello sostenibilità — protegge l'identità contabile e le inverse.

Il path di `dashboard/` è aggiunto dal conftest.py di repo.
"""

from __future__ import annotations

import pandas as pd
import pytest
from sostenibilita import (
    Baseline,
    calcola_bisogno,
    carica_proiezioni_istat,
    estrai_baseline,
    leva_decurtazione_eta,
    leva_floor,
    leva_prelievo_solidale,
    proietta_fase_b,
    tau_necessario,
)


@pytest.fixture
def baseline_2024() -> Baseline:
    return Baseline(
        anno=2024,
        n_pensionati=20_913_338,
        spesa_pensioni_eur=313.8e9,
        n_lavoratori=26_988_186,
        reddito_lavoro_eur=703.8e9,
        contributi_ce_eur=282.8e9,
        trasferimenti_stato_ce_eur=180.7e9,
        spesa_prestazioni_ce_eur=417.4e9,
    )


def test_tau_necessario_identity(baseline_2024: Baseline) -> None:
    """τ* × W + G = S per costruzione."""
    qg = 0.33
    g = qg * baseline_2024.spesa_pensioni_eur
    tau = tau_necessario(
        baseline_2024.spesa_pensioni_eur, g, baseline_2024.reddito_lavoro_eur
    )
    ricostruito = tau * baseline_2024.reddito_lavoro_eur + g
    assert ricostruito == pytest.approx(baseline_2024.spesa_pensioni_eur)


def test_calcola_bisogno_inverse(baseline_2024: Baseline) -> None:
    """N* e y* sono le inverse coerenti di τ*."""
    b = calcola_bisogno(
        spesa_eur=baseline_2024.spesa_pensioni_eur,
        massa_salariale_eur=baseline_2024.reddito_lavoro_eur,
        n_lavoratori=baseline_2024.n_lavoratori,
        reddito_medio_eur=baseline_2024.reddito_medio,
        tau_attuale=baseline_2024.tau_effettivo,
        quota_fiscalita=0.33,
    )
    # N* × y_medio × τ_attuale = contributi richiesti
    assert b.n_necessario * baseline_2024.reddito_medio * baseline_2024.tau_effettivo == pytest.approx(
        b.contributi_necessari_eur, rel=1e-9
    )
    # τ* × W = contributi richiesti
    assert b.tau_necessario * baseline_2024.reddito_lavoro_eur == pytest.approx(
        b.contributi_necessari_eur, rel=1e-9
    )


def test_tau_zero_g_è_s_su_w(baseline_2024: Baseline) -> None:
    """Con G=0, τ* = S/W."""
    tau = tau_necessario(baseline_2024.spesa_pensioni_eur, 0.0, baseline_2024.reddito_lavoro_eur)
    assert tau == pytest.approx(baseline_2024.spesa_pensioni_eur / baseline_2024.reddito_lavoro_eur)


def test_estrai_baseline_da_mart_fixture() -> None:
    """estrai_baseline legge gli schema dei mart (senza column fonte/dimensione)."""
    pen = pd.DataFrame(
        {
            "anno": [2024, 2024],
            "sesso": ["Maschi", "Femmine"],
            "chiave": ["LOMBARDIA", "LAZIO"],
            "n_pensioni": [1_000_000.0, 2_000_000.0],
            "importo_medio_mensile_eur": [1000.0, 500.0],
        }
    )
    lav = pd.DataFrame(
        {
            "anno": [2024, 2024],
            "sesso": ["Maschi", "Femmine"],
            "posizione_prevalente": ["Dipendente privato", "Artigiano"],
            "n_lavoratori": [1_000_000.0, 1_000_000.0],
            "reddito_cumulato": [30e9, 20e9],
            "settimane_lavorate": [1e6, 1e6],
        }
    )
    ce = pd.DataFrame(
        {
            "anno": [2024, 2024, 2024, 2024],
            "voce": [
                "Aliquote contributive a carico dei datori di lavoro e/o degli iscritti",
                "Trasferimenti da parte dello Stato",
                "Spese per prestazioni",
                "Spese per prestazioni istituzionali (Ratei passivi finali)",
            ],
            "importo_eur": [25e9, 10e9, -40e9, -1e9],
        }
    )
    b = estrai_baseline(pen, lav, ce, 2024)
    assert b.n_pensionati == 3_000_000
    # spesa = (1000×1e6 + 500×2e6)×12 = 24 mld
    assert b.spesa_pensioni_eur == pytest.approx(24e9)
    assert b.contributi_ce_eur == pytest.approx(25e9)
    assert b.trasferimenti_stato_ce_eur == pytest.approx(10e9)
    # ^ Spese per prestazioni istituzionali NON devono essere catturate
    assert b.spesa_prestazioni_ce_eur == pytest.approx(40e9)


def _fixture_importo() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "anno": [2024, 2024, 2024],
            "sesso": ["Maschi", "Femmine", "Maschi"],
            "chiave": ["2500 - 2999", "1000 - 1249", "Totale"],
            "n_pensioni": [100_000.0, 500_000.0, 9_999_999.0],
            "importo_medio_mensile_eur": [2700.0, 1100.0, 1500.0],
        }
    )


def _fixture_eta() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "anno": [2024, 2024, 2024],
            "sesso": ["Maschi", "Femmine", "Maschi"],
            "chiave": ["85 - 89", "70 - 74", "Totale"],
            "n_pensioni": [50_000.0, 200_000.0, 9_999_999.0],
            "importo_medio_mensile_eur": [1000.0, 1500.0, 1200.0],
        }
    )


def test_leva_prelievo_esclude_totale_e_sotto_soglia() -> None:
    lv = leva_prelievo_solidale(_fixture_importo(), soglia_mensile=2000, aliquota=0.20)
    # solo la classe 2500-2999: 100k × 2700 × 12 × 20% = 6.48 mld
    assert lv["n_pensionati"] == 100_000
    assert lv["risparmio_eur"] == pytest.approx(100_000 * 2700 * 12 * 0.20)


def test_leva_decurtazione_eta_parse() -> None:
    lv = leva_decurtazione_eta(_fixture_eta(), eta_minima=85, aliquota=0.15)
    # solo 85-89: 50k × 1000 × 12 × 15% = 90 mln
    assert lv["n_pensionati"] == 50_000
    assert lv["risparmio_eur"] == pytest.approx(50_000 * 1000 * 12 * 0.15)


def test_leva_floor_costo_positivo() -> None:
    lv = leva_floor(_fixture_importo(), floor_mensile=2000)
    # sotto 2000: solo 1000-1249 → attuale 1100×500k×12; target 2000×500k×12
    attuale = 1100 * 500_000 * 12
    target = 2000 * 500_000 * 12
    assert lv["costo_extra_eur"] == pytest.approx(target - attuale)


def test_proietta_fase_b_anchors_and_direction(baseline_2024: Baseline) -> None:
    """La proiezione parte dalla baseline e τ* cresce se la base si restringe."""
    istat = pd.DataFrame(
        {
            "anno": [2025, 2030, 2040, 2050],
            "idx_15_64": [1.0, 0.98, 0.88, 0.81],
            "idx_65p": [1.0, 1.10, 1.28, 1.30],
            "idx_tot": [1.0, 1.0, 0.97, 0.93],
        }
    )
    df = proietta_fase_b(
        baseline_2024,
        istat,
        crescita_reale_salari=0.0,
        tasso_occupazione_delta=0.0,
        quota_fiscalita=0.33,
        rivalutazione_reale_pensioni=0.0,
    )
    assert len(df) == 4
    # 2025 ≈ baseline (indice 1.0)
    assert df[df.anno == 2025].iloc[0].tau_necessario == pytest.approx(
        baseline_2024.spesa_pensioni_eur * 0.67 / baseline_2024.reddito_lavoro_eur, rel=1e-3
    )
    # τ* cresce perché N scende e P sale
    t25 = df[df.anno == 2025].iloc[0].tau_necessario
    t50 = df[df.anno == 2050].iloc[0].tau_necessario
    assert t50 > t25
    # rapporto P/L peggiora
    assert df[df.anno == 2050].iloc[0].rapporto_pensionati_lavoratori > df[
        df.anno == 2025
    ].iloc[0].rapporto_pensionati_lavoratori


def test_carica_proiezioni_istat_missing_columns(tmp_path) -> None:
    p = tmp_path / "bad.csv"
    p.write_text("anno,popolazione\n2025,100\n", encoding="utf-8")
    with pytest.raises(ValueError, match="mancante"):
        carica_proiezioni_istat(str(p))
