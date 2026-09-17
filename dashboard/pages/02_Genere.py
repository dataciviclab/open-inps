"""Genere — Il paradosso: donne piu pensioni, meno lavoro."""

import altair as alt
import pandas as pd
import streamlit as st

from sources import METRICHE, fmt_it, load_compose

st.title("⚖️ Genere")
st.markdown("**Il paradosso**: le donne hanno piu pensioni ma meno lavoro. Il ciclo e': meno assunzioni → piu NASpI → piu pensioni.")

# ── Dati ────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def load():
    return load_compose("mart_nazionale")

df = load()
if df.empty:
    st.error("Dati non disponibili.")
    st.stop()

# ── Filtri ──────────────────────────────────────────────────────────────────

anno = st.selectbox("Anno", sorted(df["anno"].unique(), reverse=True))

# ── Prepara dati ────────────────────────────────────────────────────────────

df_yr = df[(df["anno"] == anno) & (df["sesso"].isin(["Maschi", "Femmine"]))]
pivot = df_yr.pivot_table(index="metrica", columns="sesso", values="valore", aggfunc="sum").reset_index()
pivot["label"] = pivot["metrica"].map(METRICHE)
pivot["gap_pct"] = ((pivot["Femmine"] - pivot["Maschi"]) / pivot["Maschi"] * 100).round(1)

# ── Grafico a barre ─────────────────────────────────────────────────────────

st.subheader(f"Confronto donne/uomini — {anno}")

df_bar = df_yr[["metrica", "sesso", "valore"]].copy()
df_bar["label"] = df_bar["metrica"].map(METRICHE)

chart = alt.Chart(df_bar).mark_bar().encode(
    x=alt.X("valore:Q", title="Valore", scale=alt.Scale(type="symlog")),
    y=alt.Y("label:N", title="", sort="-x"),
    color=alt.Color("sesso:N", scale=alt.Scale(domain=["Maschi", "Femmine"], range=["#2563eb", "#ec4899"])),
    tooltip=["label", "sesso", alt.Tooltip("valore", format=",.0f")],
).properties(height=300)
st.altair_chart(chart, use_container_width=True)

# ── Tabella gap ─────────────────────────────────────────────────────────────

st.subheader("Gap di genere")
df_gap = pivot[["label", "Maschi", "Femmine", "gap_pct"]].copy()
df_gap.columns = ["Metrica", "Maschi", "Femmine", "Gap %"]
st.dataframe(df_gap, use_container_width=True, hide_index=True)

# ── Trend gap ───────────────────────────────────────────────────────────────

st.subheader("📉 Evoluzione del gap")

met = st.selectbox("Metrica", list(METRICHE.keys()), format_func=lambda x: METRICHE[x], key="gap_met")
df_t = df[(df["metrica"] == met) & (df["sesso"].isin(["Maschi", "Femmine"]))]
pivot_t = df_t.pivot_table(index="anno", columns="sesso", values="valore", aggfunc="sum").reset_index()
pivot_t = pivot_t.dropna(subset=["Maschi", "Femmine"])
pivot_t["gap_pct"] = ((pivot_t["Femmine"] - pivot_t["Maschi"]) / pivot_t["Maschi"] * 100).round(1)

chart2 = alt.Chart(pivot_t).mark_line(point=True, color="#d97706").encode(
    x=alt.X("anno:O", title="Anno"),
    y=alt.Y("gap_pct:Q", title="Gap F/M (%)"),
    tooltip=["anno", alt.Tooltip("gap_pct", format="+.1f")],
).properties(height=250)
st.altair_chart(chart2, use_container_width=True)
