"""Panoramica — KPI nazionali e trend."""

import altair as alt
import pandas as pd
import streamlit as st

from sources import ANNI, METRICHE, fmt_it, fmt_eur, load_mart

st.title("🇮🇹 Open INPS")
st.markdown("**Panoramica** — Il sistema pensionistico e del lavoro italiano.")

# ── Carica dati nazionali ───────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def load_nazionale() -> pd.DataFrame:
    return load_mart("inps_analisi", "mart_nazionale", 2026)

df = load_nazionale()
if df.empty:
    st.error("Dati non disponibili. Esegui `make run-compose` prima.")
    st.stop()

# ── Anno disponibile per KPI ( ultimo anno con almeno 4 metriche) ──────────

anni_completi = (
    df.groupby("anno")["metrica"]
    .nunique()
    .reset_index()
    .rename(columns={"metrica": "n_metriche"})
)
anno_max = int(anni_completi[anni_completi["n_metriche"] >= 4]["anno"].max())

# ── Filtri ──────────────────────────────────────────────────────────────────

col_f1, col_f2 = st.columns(2)
with col_f1:
    anno = st.selectbox(
        "Anno",
        sorted(df["anno"].unique(), reverse=True),
        index=sorted(df["anno"].unique(), reverse=True).index(anno_max),
        key="pan_anno",
    )
with col_f2:
    sesso_filter = st.radio("Sesso", ["Tutti", "Maschi", "Femmine"], horizontal=True, key="pan_sesso")

# ── Filtra dati ─────────────────────────────────────────────────────────────

df_anno = df[df["anno"] == anno]
if sesso_filter != "Tutti":
    df_anno = df_anno[df_anno["sesso"] == sesso_filter]
else:
    # Se esiste "Totale", usa quello. Altrimenti somma Maschi+Femmine.
    if (df_anno["sesso"] == "Totale").any():
        df_anno = df_anno[df_anno["sesso"] == "Totale"]
    else:
        df_anno = df_anno[df_anno["sesso"].isin(["Maschi", "Femmine"])]

# ── KPI ────────────────────────────────────────────────────────────────────

st.markdown("---")
st.subheader(f"Indicatori {anno}")

k1, k2, k3, k4 = st.columns(4)

pensioni = df_anno[df_anno["metrica"] == "pensioni_vigenti"]["valore"].sum()
lavoratori = df_anno[df_anno["metrica"] == "lavoratori_privati"]["valore"].sum()
naspi = df_anno[df_anno["metrica"] == "naspi"]["valore"].sum()
cig = df_anno[df_anno["metrica"] == "cig_ore"]["valore"].sum()

k1.metric("Pensioni in pagamento", fmt_it(pensioni) if pensioni else "–")
k2.metric("Lavoratori privati", fmt_it(lavoratori) if lavoratori else "–")
k3.metric("Beneficiari NASpI", fmt_it(naspi) if naspi else "–")
k4.metric("Ore CIG", fmt_it(cig) if cig else "–")

# ── Trend ───────────────────────────────────────────────────────────────────

st.markdown("---")
st.subheader("📈 Trend nazionale")

metrica_sel = st.selectbox(
    "Metrica",
    options=list(METRICHE.keys()),
    format_func=lambda x: METRICHE[x],
    key="pan_metrica",
)

df_trend = df[(df["metrica"] == metrica_sel) & (df["sesso"] != "Totale")]
if df_trend.empty:
    df_trend = df[df["metrica"] == metrica_sel]

chart = alt.Chart(df_trend).mark_line(point=True, strokeWidth=2).encode(
    x=alt.X("anno:O", title="Anno"),
    y=alt.Y("valore:Q", title=METRICHE.get(metrica_sel, metrica_sel), scale=alt.Scale(type="linear")),
    color=alt.Color("sesso:N", title="Sesso",
                     scale=alt.Scale(domain=["Maschi", "Femmine"], range=["#2563eb", "#ec4899"])),
    tooltip=["anno", "sesso", alt.Tooltip("valore", format=",.0f")],
).properties(height=400)

st.altair_chart(chart, use_container_width=True)

# ── Tabella riepilogativa ───────────────────────────────────────────────────

st.markdown("---")
st.subheader("📋 Riepilogo per metrica")

df_riepilogo = df[df["anno"] == anno].pivot_table(
    index="metrica", columns="sesso", values="valore", aggfunc="sum"
).reset_index()

df_riepilogo["metrica_label"] = df_riepilogo["metrica"].map(METRICHE)
cols = ["metrica_label"] + [c for c in ["Maschi", "Femmine", "Totale"] if c in df_riepilogo.columns]
st.dataframe(df_riepilogo[cols], use_container_width=True, hide_index=True)
