"""Panoramica — Il sistema welfare italiano in numei."""

import altair as alt
import pandas as pd
import streamlit as st

from sources import METRICHE, fmt_it, load_compose

st.title("🇮🇹 Open INPS")
st.markdown("**Panoramica** — Come si muove il sistema pensionistico e del lavoro italiano.")

# ── Dati ────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def load():
    return load_compose("mart_nazionale")

df = load()
if df.empty:
    st.error("Dati non disponibili.")
    st.stop()

# ── Anno con piu copertura ──────────────────────────────────────────────────

anni_completi = df.groupby("anno")["metrica"].nunique().reset_index()
anno_max = int(anni_completi[anni_completi["metrica"] >= 4]["anno"].max())

# ── Filtri ──────────────────────────────────────────────────────────────────

c1, c2 = st.columns(2)
with c1:
    anno = st.selectbox("Anno", sorted(df["anno"].unique(), reverse=True),
                        index=sorted(df["anno"].unique(), reverse=True).index(anno_max))
with c2:
    sesso = st.radio("Sesso", ["Tutti", "Maschi", "Femmine"], horizontal=True)

# ── KPI ─────────────────────────────────────────────────────────────────────

st.subheader(f"Indicatori {anno}")

kpi_items = [
    ("pensioni_vigenti", "Pensioni in pagamento"),
    ("rapporti_lavoro", "Nuove assunzioni"),
    ("naspi", "Beneficiari NASpI"),
    ("cig_ore", "Ore CIG"),
]

cols = st.columns(len(kpi_items))
df_yr = df[df["anno"] == anno]

for col, (metrica, label) in zip(cols, kpi_items):
    df_m = df_yr[df_yr["metrica"] == metrica]
    if sesso == "Tutti":
        if (df_m["sesso"] == "Totale").any():
            val = df_m[df_m["sesso"] == "Totale"]["valore"].sum()
        else:
            val = df_m[df_m["sesso"].isin(["Maschi", "Femmine"])]["valore"].sum()
    else:
        val = df_m[df_m["sesso"] == sesso]["valore"].sum()
    with col:
        st.metric(label, fmt_it(int(val)) if val > 0 else "–")

# ── Trend ───────────────────────────────────────────────────────────────────

st.subheader("📈 Trend")

met = st.selectbox("Metrica", list(METRICHE.keys()), format_func=lambda x: METRICHE[x])
df_t = df[(df["metrica"] == met) & (df["sesso"].isin(["Maschi", "Femmine"]))]

chart = alt.Chart(df_t).mark_line(point=True, strokeWidth=2).encode(
    x=alt.X("anno:O", title="Anno"),
    y=alt.Y("valore:Q", title=METRICHE[met]),
    color=alt.Color("sesso:N", scale=alt.Scale(domain=["Maschi", "Femmine"], range=["#2563eb", "#ec4899"])),
    tooltip=["anno", "sesso", alt.Tooltip("valore", format=",.0f")],
).properties(height=350)
st.altair_chart(chart, use_container_width=True)

# ── Riepilogo ───────────────────────────────────────────────────────────────

st.subheader("📋 Riepilogo")
df_riep = df[df["anno"] == anno].copy()
df_riep["label"] = df_riep["metrica"].map(METRICHE)
pivot = df_riep.pivot_table(index="label", columns="sesso", values="valore", aggfunc="sum").reset_index()
cols_t = ["label"] + [c for c in ["Maschi", "Femmine", "Totale"] if c in pivot.columns]
st.dataframe(pivot[cols_t], use_container_width=True, hide_index=True)
