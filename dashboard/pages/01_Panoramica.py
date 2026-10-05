"""Panoramica — Il sistema welfare e lavoro italiano in numeri."""

import altair as alt
import pandas as pd
import streamlit as st
from sources import ANNO_PIENO_CONSIGLIATO, METRICHE, fmt_num, require_compose

st.title("🇮🇹 Open INPS")
st.markdown(
    "**Panoramica** — Pensioni, mercato del lavoro e welfare: "
    "il quadro nazionale multi-dataset INPS."
)

# ── Dati ────────────────────────────────────────────────────────────────────

df = require_compose("mart_nazionale")
df_bench = require_compose("mart_benchmark")

# ── Anno default: il più pieno nel compose ──────────────────────────────────

anni_completi = df.groupby("anno")["metrica"].nunique().reset_index()
if ANNO_PIENO_CONSIGLIATO in set(anni_completi["anno"]):
    anno_max = ANNO_PIENO_CONSIGLIATO
else:
    anno_max = int(anni_completi[anni_completi["metrica"] >= 5]["anno"].max())

# ── Filtri ──────────────────────────────────────────────────────────────────

c1, c2 = st.columns(2)
with c1:
    anno = st.selectbox(
        "Anno",
        sorted(df["anno"].unique(), reverse=True),
        index=sorted(df["anno"].unique(), reverse=True).index(anno_max),
    )
with c2:
    sesso = st.radio("Sesso", ["Tutti", "Maschi", "Femmine"], horizontal=True)

n_met = df[df["anno"] == anno]["metrica"].nunique()
n_met_max = int(anni_completi["metrica"].max())
if n_met < n_met_max:
    st.info(
        f"**{anno}**: {n_met}/{n_met_max} metriche disponibili. "
        f"Per un quadro completo usa il **{ANNO_PIENO_CONSIGLIATO}** "
        f"(14 metriche)."
    )


def _val(metrica: str, anno: int) -> float:
    df_m = df[(df["anno"] == anno) & (df["metrica"] == metrica)]
    if sesso == "Tutti":
        if (df_m["sesso"] == "Totale").any():
            return float(df_m[df_m["sesso"] == "Totale"]["valore"].sum())
        return float(df_m[df_m["sesso"].isin(["Maschi", "Femmine"])]["valore"].sum())
    return float(df_m[df_m["sesso"] == sesso]["valore"].sum())


# ── KPI mercato del lavoro ──────────────────────────────────────────────────

st.subheader(f"Mercato del lavoro {anno}")

kpi_lavoro = [
    ("rapporti_lavoro", "Assunzioni"),
    ("cessazioni_lavoro", "Cessazioni"),
    ("lavoratori_privati", "Lav. privati"),
    ("lavoratori_pa", "Lav. pubblici"),
]
cols = st.columns(len(kpi_lavoro) + 1)
for col, (metrica, label) in zip(cols[: len(kpi_lavoro)], kpi_lavoro):
    val = _val(metrica, anno)
    prev = _val(metrica, anno - 1) if anno > df["anno"].min() else 0
    delta = (
        f"{(val - prev) / prev * 100:+.1f}%"
        if prev > 0 and abs((val - prev) / prev) <= 0.5
        else None
    )
    with col:
        st.metric(label, fmt_num(int(val)) if val else "–", delta=delta)

a = _val("rapporti_lavoro", anno)
c = _val("cessazioni_lavoro", anno)
with cols[-1]:
    ratio = f"{c / a * 100:.1f}%" if a else "–"
    st.metric("Cess./Assun.", ratio, help="Rapporto cessazioni su assunzioni")

# ── KPI welfare e pensioni ──────────────────────────────────────────────────

st.subheader(f"Pensioni e welfare {anno}")

kpi_welfare = [
    ("pensioni_vigenti", "Pensioni in pagamento"),
    ("pensionamento_flussi", "Nuove pensioni"),
    ("naspi", "NASpI"),
    ("dis_coll", "DIS-COLL"),
    ("rdc_nuclei", "Nuclei RdC/PdC"),
]
cols_w = st.columns(len(kpi_welfare))
for col, (metrica, label) in zip(cols_w, kpi_welfare):
    val = _val(metrica, anno)
    prev = _val(metrica, anno - 1) if anno > df["anno"].min() else 0
    delta = (
        f"{(val - prev) / prev * 100:+.1f}%"
        if prev > 0 and abs((val - prev) / prev) <= 0.5
        else None
    )
    with col:
        st.metric(label, fmt_num(int(val)) if val else "–", delta=delta)

# ── Benchmark strutturali ───────────────────────────────────────────────────

st.markdown("---")
st.subheader("📊 Benchmark strutturali")

bench_yr = df_bench[df_bench["anno"] == anno]
if not bench_yr.empty:
    b = bench_yr.iloc[0]
    b1, b2, b3, b4 = st.columns(4)

    with b1:
        val = b.get("rapporto_cessazioni_assunzioni_pct")
        st.metric(
            "Cessazioni / Assunzioni",
            f"{val:.1f}%" if pd.notna(val) else "–",
            help="Quante cessazioni per 100 assunzioni",
        )
    with b2:
        val = b.get("rapporto_pensioni_lavoratori")
        st.metric(
            "Pensioni / Lav. privati",
            f"{val:.2f}" if pd.notna(val) else "–",
        )
    with b3:
        val = b.get("rapporto_dis_coll_naspi_pct")
        st.metric(
            "DIS-COLL / NASpI",
            f"{val:.2f}%" if pd.notna(val) else "–",
            help="Nicchia co.co.co rispetto alla NASpI",
        )
    with b4:
        val = b.get("gap_genere_assunzioni_pct")
        st.metric(
            "Gap M/F assunzioni",
            f"+{val:.1f}%" if pd.notna(val) else "–",
        )

# ── Insight sintetici ───────────────────────────────────────────────────────

st.markdown("---")
insights = []
c_a = bench_yr.iloc[0].get("rapporto_cessazioni_assunzioni_pct") if not bench_yr.empty else None
if pd.notna(c_a):
    insights.append(f"Per ogni 100 assunzioni ci sono circa **{c_a:.0f} cessazioni** ({anno}).")
pen_lav = bench_yr.iloc[0].get("rapporto_pensioni_lavoratori") if not bench_yr.empty else None
if pd.notna(pen_lav):
    insights.append(
        f"Ogni lavoratore privato “sostiene” circa **{pen_lav:.2f} pensioni** in pagamento."
    )
g_ass = bench_yr.iloc[0].get("gap_genere_assunzioni_pct") if not bench_yr.empty else None
if pd.notna(g_ass):
    insights.append(f"Le assunzioni restano a **maggioranza maschile** (+{g_ass:.1f}% M vs F).")
if n_met < n_met_max:
    insights.append(
        f"Attenzione: {n_met}/{n_met_max} metriche in {anno} — non confrontare anni parziali senza filtro."
    )

if insights:
    st.markdown("**In sintesi**")
    for line in insights:
        st.markdown(f"- {line}")

# ── Trend ───────────────────────────────────────────────────────────────────

st.markdown("---")
st.subheader("📈 Trend")

met = st.selectbox("Metrica", list(METRICHE.keys()), format_func=lambda x: METRICHE[x])
df_t = df[(df["metrica"] == met) & (df["sesso"].isin(["Maschi", "Femmine", "Totale"]))]

if df_t.empty:
    df_t = df[df["metrica"] == met]

chart = (
    alt.Chart(df_t)
    .mark_line(point=True, strokeWidth=2)
    .encode(
        x=alt.X("anno:O", title="Anno"),
        y=alt.Y("valore:Q", title=METRICHE[met]),
        color=alt.Color(
            "sesso:N",
            scale=alt.Scale(
                domain=["Maschi", "Femmine", "Totale"], range=["#2563eb", "#ec4899", "#64748b"]
            ),
        ),
        tooltip=[
            "anno",
            "sesso",
            alt.Tooltip("valore", format=",.0f"),
            alt.Tooltip("share_pct", format=".1f", title="Share %"),
            alt.Tooltip("yoy_pct", format="+.1f", title="YoY %"),
        ],
    )
    .properties(height=350)
)
st.altair_chart(chart, use_container_width=True)

# ── Riepilogo ───────────────────────────────────────────────────────────────

st.subheader("📋 Riepilogo")
df_riep = df[df["anno"] == anno].copy()
df_riep["label"] = df_riep["metrica"].map(METRICHE)
pivot = df_riep.pivot_table(
    index="label", columns="sesso", values="valore", aggfunc="sum"
).reset_index()
cols_t = ["label"] + [c for c in ["Maschi", "Femmine", "Totale"] if c in pivot.columns]
st.dataframe(pivot[cols_t], use_container_width=True, hide_index=True)
