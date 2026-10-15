"""Sostenibilità — quante contribuzioni, occupati o reddito servono.

Fase A: identità contabile sui dati INPS (baseline, bisogno τ*/N*/y*).
Fase B: proiezione 2025-2050 con indici ISTAT reali (pop 15-64 e 65+).
"""

from __future__ import annotations

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st
from sostenibilita import (
    calcola_bisogno,
    carica_proiezioni_istat,
    estrai_baseline,
    leva_decurtazione_eta,
    leva_floor,
    leva_prelievo_solidale,
    proietta_fase_b,
)
from sources import require_mart

DATA_DIR = Path(__file__).parent.parent / "data"
ISTAT_CSV = DATA_DIR / "istat_proiezioni_it_2025_2050.csv"

st.title("⚖️ Sostenibilità del sistema")
st.markdown(
    "Quanto servono **contribuzioni**, **occupati** o **reddito medio** "
    "per coprire la spesa pensioni INPS. Identità pay-as-you-go: "
    "`S = τ·N·y + G`."
)

# ── Dati ────────────────────────────────────────────────────────────────────
pen = require_mart("inps_pensioni_vigenti", "mart_vigenti_regione")
# il mart regione ha anche righe sesso=Totale: il modello le scarta
lav = require_mart("inps_lavoratori_redditi", "mart_lavoratori_redditi_posizione")
ce = require_mart("inps_bilancio_ce", "mart_ce_aggregati")

anni_pen = sorted(pen["anno"].unique(), reverse=True)
anni_lav = sorted(lav["anno"].unique(), reverse=True)
anni_ce = sorted(ce["anno"].unique(), reverse=True)
anno_base = st.selectbox(
    "Anno di baseline (deve esistere in pensioni · redditi · CE)",
    sorted(set(anni_pen) & set(anni_lav) & set(anni_ce), reverse=True),
    index=0,
    key="sos_anno",
)

try:
    base = estrai_baseline(pen, lav, ce, int(anno_base))
except ValueError as e:
    st.error(str(e))
    st.stop()

# ── Panoramica baseline ──────────────────────────────────────────────────────
st.subheader(f"📋 Misure {base.anno}")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Pensioni INPS vigenti", f"{base.n_pensionati / 1e6:.2f} mln")
    st.metric("Spesa pensioni", f"{base.spesa_pensioni_eur / 1e9:.1f} mld €")
with c2:
    st.metric("Pensione media mensile", f"{base.pensione_media_mensile:,.0f} €".replace(",", "."))
    st.metric("Tasso sostituzione prox", f"{base.tasso_sostituzione_prox:.1%}")
with c3:
    st.metric("Lavoratori (pos. prevalente)", f"{base.n_lavoratori / 1e6:.2f} mln")
    st.metric("Reddito medio lavoro", f"{base.reddito_medio:,.0f} €".replace(",", "."))
with c4:
    st.metric("τ effettivo (CE/redditi)", f"{base.tau_effettivo:.1%}")
    st.metric("Quota fiscalità (prestazioni)", f"{base.quota_fiscalita_prestazioni:.1%}")

with st.expander("🔎 Dettaglio conto economico INPS"):
    d1, d2, d3 = st.columns(3)
    d1.metric("Contributi (aliquote CE)", f"{base.contributi_ce_eur / 1e9:.1f} mld €")
    d2.metric("Trasferimenti dallo Stato", f"{base.trasferimenti_stato_ce_eur / 1e9:.1f} mld €")
    d3.metric("Spese prestazioni (tutte)", f"{base.spesa_prestazioni_ce_eur / 1e9:.1f} mld €")
    st.caption(
        "Il surplus C+Tr − prestazioni è fisiologico: le prestazioni includono "
        "NASpI, RdC e altri benefit non pensionistici; l'Istituto ha altre entrate."
    )

st.divider()

# ── Bisogno: slider ─────────────────────────────────────────────────────────
st.subheader("🧮 Quanto serve per le sole pensioni")
st.markdown(
    "Fissa **quanto copre la fiscalità generale** sulla spesa pensioni "
    "(stima ufficiale ~30–35%) e leggi l'aliquota, gli occupati o il reddito "
    "medio necessari."
)

col_a, col_b = st.columns(2)
with col_a:
    # percento interi 0–60: format="%.0f%%" su float 0–0.6 mostrerebbe "0%"
    quota_g_pct = st.slider(
        "Quota spesa pensioni coperta da fiscalità generale",
        min_value=0,
        max_value=60,
        value=33,
        step=1,
        format="%d%%",
        key="sos_qg",
    )
    quota_g = quota_g_pct / 100.0
with col_b:
    tau_mode = st.radio(
        "A quale τ tenere fermo N* / y*",
        ["τ effettivo misurato", "τ nominale dipendenti (33%)"],
        horizontal=True,
        key="sos_taumode",
    )
tau_ref = base.tau_effettivo if tau_mode.startswith("τ effettivo") else 0.33

bn = calcola_bisogno(
    spesa_eur=base.spesa_pensioni_eur,
    massa_salariale_eur=base.reddito_lavoro_eur,
    n_lavoratori=base.n_lavoratori,
    reddito_medio_eur=base.reddito_medio,
    tau_attuale=tau_ref,
    quota_fiscalita=quota_g,
)

r1, r2, r3, r4 = st.columns(4)
r1.metric(
    "τ necessario",
    f"{bn.tau_necessario:.1%}",
    f"{(bn.tau_necessario - base.tau_effettivo) * 100:+.1f} pp vs τ effettivo",
    delta_color="off",
)
r2.metric(
    "Occupati necessari",
    f"{bn.n_necessario / 1e6:.1f} mln",
    f"{(bn.n_necessario - base.n_lavoratori) / 1e6:+.1f} mln vs oggi",
    delta_color="off",
)
r3.metric(
    "Reddito medio necessario",
    f"{bn.reddito_medio_necessario:,.0f} €".replace(",", "."),
    f"{(bn.reddito_medio_necessario - base.reddito_medio) / 1000:+.1f} k€ vs oggi",
    delta_color="off",
)
r4.metric(
    "Gettito contributivo richiesto",
    f"{bn.contributi_necessari_eur / 1e9:.1f} mld €",
    f"{(bn.contributi_necessari_eur - base.contributi_ce_eur) / 1e9:+.1f} mld vs CE",
    delta_color="off",
)

st.caption(
    f"τ* = (S − G)/W con S = {base.spesa_pensioni_eur / 1e9:.0f} mld, "
    f"G = {quota_g:.0%}·S, W = {base.reddito_lavoro_eur / 1e9:.0f} mld. "
    "τ* inferiore al τ effettivo non è un paradosso: i contributi finanziano "
    "anche NASpI, RdC, invalidità e altre prestazioni oltre alle pensioni."
)

# ── Sensitività ─────────────────────────────────────────────────────────────
st.subheader("🎛️ Sensitività: τ* al variare della quota G")
grid = []
for q in [i / 100 for i in range(0, 51, 2)]:  # 0% → 50% ogni 2pp
    b = calcola_bisogno(
        spesa_eur=base.spesa_pensioni_eur,
        massa_salariale_eur=base.reddito_lavoro_eur,
        n_lavoratori=base.n_lavoratori,
        reddito_medio_eur=base.reddito_medio,
        tau_attuale=tau_ref,
        quota_fiscalita=q,
    )
    grid.append({"quota_G": q, "tau_necessario": b.tau_necessario})
df_grid = pd.DataFrame(grid)

chart = (
    alt.Chart(df_grid)
    .mark_line(strokeWidth=2.5)
    .encode(
        x=alt.X("quota_G:Q", title="Quota coperta da fiscalità generale", axis=alt.Axis(format=".0%")),
        y=alt.Y("tau_necessario:Q", title="τ necessario", axis=alt.Axis(format=".0%")),
        tooltip=[
            alt.Tooltip("quota_G", format=".0%"),
            alt.Tooltip("tau_necessario", format=".1%"),
        ],
    )
    .properties(height=320)
)
# punto corrente dello slider
point = (
    alt.Chart(pd.DataFrame({"quota_G": [quota_g], "tau_necessario": [bn.tau_necessario]}))
    .mark_point(filled=True, size=100, color="orange")
    .encode(x="quota_G:Q", y="tau_necessario:Q")
    .properties(height=320)
)
# linea verticale sulla quota G selezionata
vline = (
    alt.Chart(pd.DataFrame({"x": [quota_g]}))
    .mark_rule(color="orange", strokeDash=[3, 3], strokeWidth=1.5)
    .encode(x="x:Q")
    .properties(height=320)
)
rule = (
    alt.Chart(pd.DataFrame({"y": [base.tau_effettivo]}))
    .mark_rule(color="red", strokeDash=[4, 4])
    .encode(y="y:Q")
    .properties(height=320)
)
st.altair_chart(chart + vline + point + rule, use_container_width=True)
st.caption(
    f"Linea rossa = τ effettivo misurato ({base.tau_effettivo:.1%}). "
    f" Pallino arancione = quota G selezionata ({quota_g:.0%}) → τ* = {bn.tau_necessario:.1%}."
)

# ── Leve di correzione ──────────────────────────────────────────────────────
st.divider()
st.subheader("🛠️ Leve: cosa cambia i conti")
st.markdown(
    "Scenari contabili **illustrativi**, non proposte di policy. "
    "Quanto si muove la spesa pensioni con tre interventi — e l'effetto su τ*."
)

imp = require_mart("inps_pensioni_vigenti", "mart_vigenti_importo")
eta = require_mart("inps_pensioni_vigenti", "mart_vigenti_eta")
imp_a = imp[imp["anno"] == int(anno_base)]
eta_a = eta[eta["anno"] == int(anno_base)]

# ── Concentrazione età ──
st.caption(
    f"Concentrazione per età ({base.anno}): la pensione media **scende** dopo i 75 "
    "(picco 65-69) — la coda alta di importi è fatta soprattutto da neo-pensionati, "
    "non dagli ultra-ottantenni."
)
df_e = (
    eta_a[eta_a["chiave"].notna() & ~eta_a["chiave"].str.contains("Totale", na=False)]
    .copy()
    .groupby("chiave", as_index=False)
    .agg(n_pensioni=("n_pensioni", "sum"), spesa=("importo_medio_mensile_eur", lambda s: float((s * eta_a.loc[s.index, "n_pensioni"] * 12).sum())))
)
df_e["media_annua"] = df_e["spesa"] / df_e["n_pensioni"]
df_e["spesa_mld"] = df_e["spesa"] / 1e9
ordine = [
    "Fino a 14", "15 - 19", "20 - 29", "30 - 39", "40 - 49", "50 - 54",
    "55 - 59", "60 - 64", "65 - 69", "70 - 74", "75 - 79", "80 - 84",
    "85 - 89", "90 ed oltre",
]
df_e["chiave"] = pd.Categorical(df_e["chiave"], categories=ordine, ordered=True)
df_e = df_e.sort_values("chiave")
c1, c2 = st.columns(2)
with c1:
    st.altair_chart(
        alt.Chart(df_e)
        .mark_bar()
        .encode(
            x=alt.X("chiave:N", title="Classe età", sort=ordine),
            y=alt.Y("spesa_mld:Q", title="Spesa annua (mld €)", axis=alt.Axis(format=",.0f")),
            tooltip=[
                "chiave",
                alt.Tooltip("n_pensioni", format=",.0f", title="N. pensioni"),
                alt.Tooltip("spesa_mld", format=",.1f", title="Spesa mld"),
                alt.Tooltip("media_annua", format=",.0f", title="Media €/anno"),
            ],
        )
        .properties(height=300),
        use_container_width=True,
    )
with c2:
    st.altair_chart(
        alt.Chart(df_e)
        .mark_line(point=True, color="orange")
        .encode(
            x=alt.X("chiave:N", title="Classe età", sort=ordine),
            y=alt.Y("media_annua:Q", title="Pensione media (€/anno)", axis=alt.Axis(format=",.0f")),
            tooltip=["chiave", alt.Tooltip("media_annua", format=",.0f")],
        )
        .properties(height=300),
        use_container_width=True,
    )

# ── Leva 1: prelievo solidale ──
st.subheader("Leva 1 — Prelievo solidale sulla coda alta")
c1, c2 = st.columns(2)
with c1:
    soglia = st.select_slider(
        "Soglia mensile",
        options=[1500, 2000, 2500, 3000, 4000],
        value=2500,
        format_func=lambda x: f"{x:,} €".replace(",", "."),
        key="leva1_soglia",
    )
with c2:
    aliq = st.select_slider(
        "Aliquota di prelievo",
        options=[0.05, 0.10, 0.15, 0.20, 0.30],
        value=0.15,
        format_func=lambda x: f"{x:.0%}",
        key="leva1_aliq",
    )
lv = leva_prelievo_solidale(imp_a, soglia, aliq)
spesa_dopo = base.spesa_pensioni_eur - lv["risparmio_eur"]
b_dopo = calcola_bisogno(
    spesa_eur=spesa_dopo,
    massa_salariale_eur=base.reddito_lavoro_eur,
    n_lavoratori=base.n_lavoratori,
    reddito_medio_eur=base.reddito_medio,
    tau_attuale=tau_ref,
    quota_fiscalita=quota_g,
)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Pensionati coinvolti", f"{lv['n_pensionati'] / 1e6:.2f} mln")
c2.metric("Risparmio annuo", f"{lv['risparmio_eur'] / 1e9:.1f} mld €")
c3.metric("Spesa dopo", f"{spesa_dopo / 1e9:.1f} mld €", f"−{lv['risparmio_eur'] / 1e9:.1f} mld")
c4.metric("τ* dopo", f"{b_dopo.tau_necessario:.1%}", f"{(b_dopo.tau_necessario - bn.tau_necessario) * 100:+.1f} pp", delta_color="off")
st.caption(
    "Approssimazione: aliquota uniforme su tutte le classi sopra soglia "
    "(non tasso marginale sul solo excedente). Effetto indicativo."
)

# ── Leva 2: decurtazione per età ──
st.subheader("Leva 2 — Decurtazione sopra soglia di età")
c1, c2 = st.columns(2)
with c1:
    eta_min = st.select_slider(
        "Età minima",
        options=[75, 80, 85, 90],
        value=85,
        format_func=lambda x: f"{x} anni",
        key="leva2_eta",
    )
with c2:
    dec = st.select_slider(
        "Decurtazione",
        options=[0.05, 0.10, 0.15, 0.20, 0.30],
        value=0.15,
        format_func=lambda x: f"−{x:.0%}",
        key="leva2_dec",
    )
lv2 = leva_decurtazione_eta(eta_a, eta_min, dec)
spesa_dopo2 = base.spesa_pensioni_eur - lv2["risparmio_eur"]
b_dopo2 = calcola_bisogno(
    spesa_eur=spesa_dopo2,
    massa_salariale_eur=base.reddito_lavoro_eur,
    n_lavoratori=base.n_lavoratori,
    reddito_medio_eur=base.reddito_medio,
    tau_attuale=tau_ref,
    quota_fiscalita=quota_g,
)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Pensionati coinvolti", f"{lv2['n_pensionati'] / 1e6:.2f} mln")
c2.metric("Risparmio annuo", f"{lv2['risparmio_eur'] / 1e9:.1f} mld €")
c3.metric("Spesa dopo", f"{spesa_dopo2 / 1e9:.1f} mld €", f"−{lv2['risparmio_eur'] / 1e9:.1f} mld")
c4.metric("τ* dopo", f"{b_dopo2.tau_necessario:.1%}", f"{(b_dopo2.tau_necessario - bn.tau_necessario) * 100:+.1f} pp", delta_color="off")
st.caption(
    "Nota: la pensione media scende con l'età (superstiti, carriere parziali, "
    "coorti vecchie) — il risparmio reale di una decurtazione 85+ è più "
    "modesto di quanto suggerisca l'intuizione."
)

# ── Leva 3: floor ──
st.subheader("Leva 3 — Floor: portare a minima tutte le pensioni sotto soglia")
floor = st.select_slider(
    "Pensione minima mensile",
    options=[300, 400, 500, 600, 800],
    value=500,
    format_func=lambda x: f"{x} €/mese",
    key="leva3_floor",
)
lv3 = leva_floor(imp_a, floor)
c1, c2, c3 = st.columns(3)
c1.metric("Pensionati sotto floor", f"{lv3['n_pensionati'] / 1e6:.2f} mln")
c2.metric("Costo aggiuntivo", f"+{lv3['costo_extra_eur'] / 1e9:.1f} mld €", delta_color="off")
c3.metric(
    "Se coperto da fiscalità (G)",
    f"{(base.spesa_pensioni_eur + lv3['costo_extra_eur']) / base.reddito_lavoro_eur:.1%}",
    "S/W dopo il floor",
    delta_color="off",
)
st.caption(
    "Il floor **aumenta** la spesa: è una scelta di equità, non di risparmio. "
    "Finanziarlo da più fiscalità (G) non muove τ*; da più contributi, sì."
)

# ── Confronto leve ──
st.subheader("Confronto leve")
righe = []
for nome, risp in [
    (f"Prelievo {aliq:.0%} >{soglia}€", lv["risparmio_eur"]),
    (f"Decurt. −{dec:.0%} ≥{eta_min}anni", lv2["risparmio_eur"]),
]:
    b2 = calcola_bisogno(
        spesa_eur=base.spesa_pensioni_eur - risp,
        massa_salariale_eur=base.reddito_lavoro_eur,
        n_lavoratori=base.n_lavoratori,
        reddito_medio_eur=base.reddito_medio,
        tau_attuale=tau_ref,
        quota_fiscalita=quota_g,
    )
    righe.append({"leva": nome, "risparmio_mld": risp / 1e9, "tau_dopo": b2.tau_necessario})
righe.append({"leva": "Floor (costo)", "risparmio_mld": -lv3["costo_extra_eur"] / 1e9, "tau_dopo": bn.tau_necessario})
df_leve = pd.DataFrame(righe)
st.dataframe(df_leve, use_container_width=True, hide_index=True)

# ── Fase B: proiezione 2025-2050 con indici ISTAT ───────────────────────────
st.divider()
st.subheader("🔭 Fase B — proiezione al 2050")
st.markdown(
    "Indici ISTAT ufficiali (scenario mediano, base 1/1/2025): "
    "**popolazione 15-64 scende del 19% al 2050**, i **65+ salgono del 30%**. "
    "Il modello proietta τ* tenendo conto di entrambe le curve."
)

if not ISTAT_CSV.exists():
    st.warning(f"CSV ISTAT non trovato: `{ISTAT_CSV}` — Fase B non disponibile.")
else:
    df_istat = carica_proiezioni_istat(str(ISTAT_CSV))

    # indicatori demografici rapidi
    d1, d2, d3 = st.columns(3)
    r50 = df_istat[df_istat.anno == 2050].iloc[0]
    r25 = df_istat[df_istat.anno == 2025].iloc[0]
    d1.metric("Pop. 15-64 al 2050", f"{r50.pop_15_64 / 1e6:.1f} mln", f"{(r50.idx_15_64 - 1) * 100:+.1f}%")
    d2.metric("Pop. 65+ al 2050", f"{r50.pop_65p / 1e6:.1f} mln", f"{(r50.idx_65p - 1) * 100:+.1f}%")
    dep25 = r25.pop_65p / r25.pop_15_64
    dep50 = r50.pop_65p / r50.pop_15_64
    d3.metric(
        "Rapporto 65+/15-64",
        f"{dep25:.2f} → {dep50:.2f}",
        "al 2050",
    )

    # slider proiezione — percentuali intere (format="%.1f%%" su float non moltiplica ×100)
    st.markdown("**Leve dello scenario**")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        g_salari_pct = st.slider(
            "Crescita reale salari",
            0, 20, 7, 1,
            format="%d‰",  # per mille: 7 = 0,7%
            key="fb_gsal",
            help="Crescita reale annua del reddito medio da lavoro (per mille)",
        )
        g_salari = g_salari_pct / 1000.0
    with c2:
        occ_delta_pct = st.slider(
            "Variazione tasso occupazione (×0,1 pp/anno)",
            -20, 80, 0, 5,
            format="%+d",
            key="fb_occ",
            help="Extra crescita occupazionale: 10 = +1,0 pp/anno, 5 = +0,5 pp/anno",
        )
        occ_delta = occ_delta_pct / 1000.0
    with c3:
        g_pens_pct = st.slider(
            "Crescita reale pensioni",
            0, 20, 0, 1,
            format="%d‰",
            key="fb_gpens",
            help="0 = pensione media reale costante; >0 = rivalutazione reale (per mille)",
        )
        g_pens = g_pens_pct / 1000.0
    with c4:
        qg_fb = st.slider(
            "Quota fiscalità (G)",
            0, 60, 33, 1,
            format="%d%%",
            key="fb_qg",
        ) / 100.0

    df_proj = proietta_fase_b(
        base,
        df_istat,
        crescita_reale_salari=g_salari,
        tasso_occupazione_delta=occ_delta,
        quota_fiscalita=qg_fb,
        rivalutazione_reale_pensioni=g_pens,
    )

    # τ*(t) chart
    st.markdown("**τ necessario nel tempo**")
    df_plot = df_proj.copy()
    df_plot["gap"] = df_plot["tau_necessario"] - base.tau_effettivo

    chart_tau = (
        alt.Chart(df_plot)
        .mark_line(point=True, strokeWidth=2.5, color="#1f77b4")
        .encode(
            x=alt.X("anno:O", title="Anno"),
            y=alt.Y("tau_necessario:Q", title="τ necessario", axis=alt.Axis(format=".0%")),
            tooltip=[
                "anno",
                alt.Tooltip("tau_necessario", format=".1%", title="τ*"),
                alt.Tooltip("n_lavoratori", format=",.0f", title="Occupati"),
                alt.Tooltip("n_pensionati", format=",.0f", title="Pensionati"),
                alt.Tooltip("spesa_pensioni_eur", format=",.0f", title="Spesa €"),
            ],
        )
        .properties(height=360)
    )
    rule_tau = (
        alt.Chart(pd.DataFrame({"y": [base.tau_effettivo]}))
        .mark_rule(color="red", strokeDash=[4, 4])
        .encode(y="y:Q")
        .properties(height=360)
    )
    st.altair_chart(chart_tau + rule_tau, use_container_width=True)
    st.caption(
        f"Linea rossa = τ effettivo 2024 ({base.tau_effettivo:.1%}). "
        f"Scenario: salari +{g_salari:.1%}/a, occupazione {occ_delta:+.1%}/a, "
        f"pensioni +{g_pens:.1%}/a reale, G={qg_fb:.0%}."
    )

    # metrica al 2050
    r50p = df_proj[df_proj.anno == 2050].iloc[0]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("τ* al 2050", f"{r50p.tau_necessario:.1%}", f"{(r50p.tau_necessario - base.tau_effettivo) * 100:+.1f} pp vs oggi", delta_color="off")
    m2.metric("Spesa pensioni 2050", f"{r50p.spesa_pensioni_eur / 1e9:.0f} mld €", f"{(r50p.spesa_pensioni_eur / base.spesa_pensioni_eur - 1) * 100:+.0f}%")
    m3.metric("Occupati 2050", f"{r50p.n_lavoratori / 1e6:.1f} mln", f"{(r50p.n_lavoratori / base.n_lavoratori - 1) * 100:+.0f}%")
    m4.metric("Rapporto P/L 2050", f"{r50p.rapporto_pensionati_lavoratori:.2f}", f"da {base.rapporto_pensionati_lavoratori:.2f} nel {base.anno}")

    # pop vs spesa
    st.markdown("**La struttura demografica dietro il numero**")
    df_dem = df_proj[["anno", "pop_15_64_idx", "pop_65p_idx"]].melt(
        id_vars="anno", var_name="serie", value_name="indice"
    )
    df_dem["serie"] = df_dem["serie"].map(
        {"pop_15_64_idx": "Pop 15-64 (indice)", "pop_65p_idx": "Pop 65+ (indice)"}
    )
    chart_dem = (
        alt.Chart(df_dem)
        .mark_line(strokeWidth=2)
        .encode(
            x=alt.X("anno:O", title="Anno"),
            y=alt.Y("indice:Q", title="Indice (2025=1)"),
            color=alt.Color("serie:N", title=""),
            tooltip=["anno", "serie", alt.Tooltip("indice", format=".3f")],
        )
        .properties(height=280)
    )
    st.altair_chart(chart_dem, use_container_width=True)

    # opzione: scenario multipli
    with st.expander("📊 Confronto rapido tra scenari"):
        scenari = []
        for nome, gs, occ, gp in [
            ("Status quo", 0.007, 0.0, 0.0),
            ("Alta produttività", 0.015, 0.0, 0.0),
            ("Alta occupazione", 0.007, 0.01, 0.0),
            ("Riforma mista", 0.010, 0.005, 0.0),
            ("Pensioni più basse (reale)", 0.007, 0.0, -0.005),
        ]:
            dp = proietta_fase_b(base, df_istat, gs, occ, qg_fb, gp)
            r = dp[dp.anno == 2050].iloc[0]
            scenari.append({
                "scenario": nome,
                "τ* 2050": f"{r.tau_necessario:.1%}",
                "Spesa (mld €)": f"{r.spesa_pensioni_eur / 1e9:.0f}",
                "Occupati (mln)": f"{r.n_lavoratori / 1e6:.1f}",
                "_tau": r.tau_necessario,
            })
        df_sc = pd.DataFrame(scenari)
        st.dataframe(
            df_sc[["scenario", "τ* 2050", "Spesa (mld €)", "Occupati (mln)"]],
            use_container_width=True,
            hide_index=True,
        )
