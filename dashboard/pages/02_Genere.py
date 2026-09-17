"""Genere — Il paradosso di genere nel sistema welfare italiano."""

import altair as alt
import pandas as pd
import streamlit as st

from sources import METRICHE, fmt_it, fmt_pct, load_mart

st.title("⚖️ Genere")
st.markdown("**Il paradosso**: le donne hanno più pensioni ma meno lavoro.")

# ── Carica dati ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def load() -> pd.DataFrame:
    return load_mart("inps_analisi", "mart_nazionale", 2026)

df = load()
if df.empty:
    st.error("Dati non disponibili.")
    st.stop()

# ── Filtri ──────────────────────────────────────────────────────────────────

anno = st.selectbox("Anno", sorted(df["anno"].unique(), reverse=True), key="gen_anno")

# ── Prepara dati ────────────────────────────────────────────────────────────

df_anno = df[(df["anno"] == anno) & (df["sesso"].isin(["Maschi", "Femmine"]))]

if df_anno.empty:
    st.warning("Nessun dato per l'anno selezionato.")
    st.stop()

# Pivot per confronto diretto
pivot = df_anno.pivot_table(index="metrica", columns="sesso", values="valore", aggfunc="sum").reset_index()
pivot["metrica_label"] = pivot["metrica"].map(METRICHE)
pivot["gap_pct"] = ((pivot["Femmine"] - pivot["Maschi"]) / pivot["Maschi"] * 100).round(1)

# ── Grafico a barre impilatte ──────────────────────────────────────────────

st.subheader(f"Confronto donne/uomini — {anno}")

df_bar = df_anno[["metrica", "sesso", "valore"]].copy()
df_bar["metrica_label"] = df_bar["metrica"].map(METRICHE)

chart = alt.Chart(df_bar).mark_bar().encode(
    x=alt.X("valore:Q", title="Valore", scale=alt.Scale(type="symlog")),
    y=alt.Y("metrica_label:N", title="", sort="-x"),
    color=alt.Color("sesso:N", title="Sesso", scale=alt.Scale(domain=["Maschi", "Femmine"], range=["#2563eb", "#ec4899"])),
    tooltip=["metrica_label", "sesso", alt.Tooltip("valore", format=",.0f")],
).properties(height=350)

st.altair_chart(chart, use_container_width=True)

# ── Indice di genere ────────────────────────────────────────────────────────

st.subheader("Indice di genere (rapporto F/M)")

df_indice = pivot[["metrica_label", "Maschi", "Femmine", "gap_pct"]].copy()
df_indice.columns = ["Metrica", "Maschi", "Femmine", "Gap %"]
st.dataframe(df_indice, use_container_width=True, hide_index=True)

st.info(
    "Gap positivo = più donne. Gap negativo = più uomini. "
    "Le donne dominano pensioni e NASpI, gli uomini lavoro e assunzioni."
)

# ── Trend gap di genere ────────────────────────────────────────────────────

st.subheader("📉 Evoluzione del gap di genere")

df_trend = df[df["sesso"].isin(["Maschi", "Femmine"])]
pivot_trend = df_trend.pivot_table(index=["anno", "metrica"], columns="sesso", values="valore", aggfunc="sum").reset_index()
pivot_trend = pivot_trend.dropna(subset=["Maschi", "Femmine"])
pivot_trend["gap_pct"] = ((pivot_trend["Femmine"] - pivot_trend["Maschi"]) / pivot_trend["Maschi"] * 100).round(1)

metrica_trend = st.selectbox(
    "Metrica per trend",
    options=list(METRICHE.keys()),
    format_func=lambda x: METRICHE[x],
    key="gen_trend_metrica",
)

df_trend_f = pivot_trend[pivot_trend["metrica"] == metrica_trend]
if not df_trend_f.empty:
    chart_trend = alt.Chart(df_trend_f).mark_line(point=True).encode(
        x=alt.X("anno:O", title="Anno"),
        y=alt.Y("gap_pct:Q", title="Gap F/M (%)"),
        tooltip=["anno", alt.Tooltip("gap_pct", format="+.1f")],
    ).properties(height=250)
    st.altair_chart(chart_trend, use_container_width=True)
