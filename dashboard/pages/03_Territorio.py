"""Territorio — Mappa e ranking regionale."""

import altair as alt
import pandas as pd
import plotly.express as px
import streamlit as st

from sources import GEOJSON_URL, METRICHE, REGIONI, fmt_it, load_compose

st.title("🗺️ Territorio")

# ── Dati ────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def load():
    return load_compose("mart_territoriale")

df = load()
if df.empty:
    st.error("Dati non disponibili.")
    st.stop()

# ── Filtri ──────────────────────────────────────────────────────────────────

c1, c2 = st.columns(2)
with c1:
    anno = st.selectbox("Anno", sorted(df["anno"].unique(), reverse=True))
with c2:
    met = st.selectbox("Metrica", list(METRICHE.keys()), format_func=lambda x: METRICHE[x])

# ── Prepara dati ────────────────────────────────────────────────────────────

df_f = df[(df["anno"] == anno) & (df["metrica"] == met)]
if (df_f["sesso"] == "Totale").any():
    df_f = df_f[df_f["sesso"] == "Totale"]
else:
    df_f = df_f[df_f["sesso"].isin(["Maschi", "Femmine"])]

df_reg = df_f.groupby("regione", as_index=False)["valore"].sum()
df_reg = df_reg[df_reg["regione"].isin(REGIONI)]

# ── Mappa ───────────────────────────────────────────────────────────────────

st.subheader(f"{METRICHE[met]} — {anno}")

fig = px.choropleth(
    df_reg, geojson=GEOJSON_URL, locations="regione",
    featureidkey="properties.reg_name", color="valore",
    color_continuous_scale="Blues",
    hover_name="regione", hover_data={"valore": ":,.0f"},
    labels={"valore": METRICHE[met]},
)
fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=500)
st.plotly_chart(fig, use_container_width=True)

# ── Ranking ─────────────────────────────────────────────────────────────────

df_rank = df_reg.sort_values("valore", ascending=False).reset_index(drop=True)
df_rank.index = df_rank.index + 1
df_rank.columns = ["Regione", "Valore"]
df_rank["Valore"] = df_rank["Valore"].apply(fmt_it)
st.dataframe(df_rank, use_container_width=True)
