"""Panoramica — KPI nazionali e trend."""

import altair as alt
import pandas as pd
import streamlit as st

from sources import METRICHE, fmt_it, load_mart

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

# ── Anno disponibile (ultimo con >=4 metriche con dati) ─────────────────────

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
    # Aggrega per ogni metrica: usa Totale se disponibile, altrimenti somma F+M
    rows = []
    for metrica in df_anno["metrica"].unique():
        df_m = df_anno[df_anno["metrica"] == metrica]
        if (df_m["sesso"] == "Totale").any():
            rows.append(df_m[df_m["sesso"] == "Totale"])
        else:
            df_fm = df_m[df_m["sesso"].isin(["Maschi", "Femmine"])]
            if not df_fm.empty:
                rows.append(pd.DataFrame([{
                    "anno": anno, "metrica": metrica, "sesso": "Totale",
                    "valore": df_fm["valore"].sum()
                }]))
    df_anno = pd.concat(rows) if rows else df_anno[df_anno["sesso"] == "Totale"]

# ── KPI (solo metriche con dati) ───────────────────────────────────────────

st.markdown("---")
st.subheader(f"Indicatori {anno}")

kpi_metriche = ["pensioni_vigenti", "lavoratori_privati", "naspi", "cig_ore"]
kpi_cols = st.columns(len(kpi_metriche))

for col, metrica in zip(kpi_cols, kpi_metriche):
    val = df_anno[df_anno["metrica"] == metrica]["valore"].sum()
    label = METRICHE.get(metrica, metrica)
    with col:
        if val > 0:
            st.metric(label, fmt_it(int(val)))
        else:
            st.metric(label, "–", help=f"Dati non disponibili per {anno}")

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
    y=alt.Y("valore:Q", title=METRICHE.get(metrica_sel, metrica_sel)),
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
