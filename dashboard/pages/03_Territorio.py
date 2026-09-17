"""Territorio — Mappa regionale e ranking."""

import altair as alt
import pandas as pd
import plotly.express as px
import streamlit as st

from sources import GEOJSON_URL, METRICHE, REGIONI, fmt_it, load_mart

st.title("🗺️ Territorio")
st.markdown("Distribuzione geografica degli indicatori INPS per regione.")

# ── Filtri ──────────────────────────────────────────────────────────────────

col_f1, col_f2 = st.columns(2)
with col_f1:
    anno = st.selectbox("Anno", list(range(2026, 2013, -1)), key="terr_anno")
with col_f2:
    metrica = st.selectbox(
        "Metrica",
        options=list(METRICHE.keys()),
        format_func=lambda x: METRICHE[x],
        key="terr_metrica",
    )

# ── Carica dati ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def load_territorio() -> pd.DataFrame:
    return load_mart("inps_analisi", "mart_territoriale", 2026)

df = load_territorio()
if df.empty:
    st.error("Dati non disponibili.")
    st.stop()

# Filtra
df_f = df[(df["anno"] == anno) & (df["metrica"] == metrica)]
if df_f.empty:
    st.warning("Nessun dato per la combinazione selezionata.")
    st.stop()

# Se ci sono righe "Totale", usa quelle. Altrimenti aggrega Maschi+Femmine.
if (df_f["sesso"] == "Totale").any():
    df_f = df_f[df_f["sesso"] == "Totale"]
else:
    df_f = df_f[df_f["sesso"].isin(["Maschi", "Femmine"])]

# Aggrega per regione
df_reg = df_f.groupby("regione", as_index=False)["valore"].sum()
df_reg = df_reg[df_reg["regione"].isin(REGIONI)]

# ── Mappa ───────────────────────────────────────────────────────────────────

st.subheader(f"Mappa — {METRICHE.get(metrica, metrica)} ({anno})")

fig = px.choropleth(
    df_reg,
    geojson=GEOJSON_URL,
    locations="regione",
    featureidkey="properties.reg_name",
    color="valore",
    color_continuous_scale="Blues",
    hover_name="regione",
    hover_data={"valore": ":,.0f"},
    labels={"valore": METRICHE.get(metrica, metrica)},
)
fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=500)
st.plotly_chart(fig, use_container_width=True)

# ── Ranking ─────────────────────────────────────────────────────────────────

st.subheader("📊 Ranking regioni")

df_rank = df_reg.sort_values("valore", ascending=False).reset_index(drop=True)
df_rank.index = df_rank.index + 1
df_rank.columns = ["Regione", "Valore"]
df_rank["Valore"] = df_rank["Valore"].apply(lambda x: fmt_it(x))

st.dataframe(df_rank, use_container_width=True)
