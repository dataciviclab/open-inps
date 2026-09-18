"""Territorio — Mappa e ranking regionale."""

import altair as alt
import pandas as pd
import plotly.express as px
import streamlit as st

from sources import GEOJSON_URL, METRICHE, REGIONI, fmt_num, require_compose

st.title("🗺️ Territorio")

# ── Dati ────────────────────────────────────────────────────────────────────

df = require_compose("mart_territoriale")

# ── Filtri ──────────────────────────────────────────────────────────────────

c1, c2, c3 = st.columns(3)
with c1:
    anno = st.selectbox("Anno", sorted(df["anno"].unique(), reverse=True))
with c2:
    met = st.selectbox("Metrica", list(METRICHE.keys()), format_func=lambda x: METRICHE[x])
with c3:
    sesso = st.selectbox("Sesso", ["Totale", "Maschi", "Femmine"])

# ── Prepara dati ────────────────────────────────────────────────────────────

df_f = df[(df["anno"] == anno) & (df["metrica"] == met) & (df["sesso"] == sesso)]

# Se Sesso="Totale" ma non esiste, aggrega Maschi+Femmine
if df_f.empty and sesso == "Totale":
    df_f = df[(df["anno"] == anno) & (df["metrica"] == met) & df["sesso"].isin(["Maschi", "Femmine"])]
    if not df_f.empty:
        df_f = df_f.groupby("regione", as_index=False).agg({"valore": "sum", "share_pct": "sum", "indice_vs_media": "mean"})
        df_f["sesso"] = "Totale"
    else:
        st.warning("Nessun dato disponibile per questa combinazione.")
        st.stop()

df_f = df_f[df_f["regione"].isin(REGIONI)]

# ── Mappa ───────────────────────────────────────────────────────────────────

st.subheader(f"{METRICHE[met]} — {anno} ({sesso})")

fig = px.choropleth(
    df_f, geojson=GEOJSON_URL, locations="regione",
    featureidkey="properties.reg_name", color="valore",
    color_continuous_scale="Blues",
    hover_name="regione",
    hover_data={"valore": ":,.0f", "share_pct": ":.1f", "indice_vs_media": ":.0f"},
    labels={"valore": "Valore", "share_pct": "Share %", "indice_vs_media": "Indice vs media"},
)
fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=500)
st.plotly_chart(fig, use_container_width=True)

# ── Ranking con analisi ─────────────────────────────────────────────────────

st.subheader("📊 Ranking regioni")

df_rank = df_f.sort_values("valore", ascending=False).reset_index(drop=True)
df_rank.index = df_rank.index + 1
df_rank = df_rank[["regione", "valore", "share_pct", "indice_vs_media"]].copy()
df_rank.columns = ["Regione", "Valore", "Share %", "Indice vs media"]
df_rank["Valore"] = df_rank["Valore"].apply(fmt_num)
st.dataframe(df_rank, use_container_width=True)
