"""Pensioni — Deep dive: importo, eta, regione."""

import altair as alt
import pandas as pd
import streamlit as st

from sources import fmt_it, load_mart

st.title("🏦 Pensioni")
st.markdown("Dettaglio sulle pensioni INPS: distribuzione per importo, eta e regione.")

# ── Dati ────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def load():
    imp = load_mart("inps_pensioni_vigenti", "mart_vigenti_importo")
    eta = load_mart("inps_pensioni_vigenti", "mart_vigenti_eta")
    reg = load_mart("inps_pensioni_vigenti", "mart_vigenti_regione")
    liq = load_mart("inps_pensioni_liquidate", "mart_liquidate_importo")
    return imp, eta, reg, liq

imp, eta, reg, liq = load()

# ── Tabs ────────────────────────────────────────────────────────────────────

tab1, tab2, tab3 = st.tabs(["📊 Distribuzione importo", "👴 Distribuzione eta", "🗺️ Per regione"])

with tab1:
    st.subheader("Pensioni per classe di importo")
    c1, c2 = st.columns(2)
    with c1:
        anno_imp = st.selectbox("Anno", sorted(imp["anno"].unique(), reverse=True), key="imp_anno")
    with c2:
        sesso_imp = st.selectbox("Sesso", ["Maschi", "Femmine"], key="imp_sesso")

    df_imp = imp[(imp["anno"] == anno_imp) & (imp["sesso"] == sesso_imp)]
    df_imp = df_imp[df_imp["chiave"].notna() & (df_imp["chiave"] != "")]

    chart = alt.Chart(df_imp).mark_bar().encode(
        x=alt.X("chiave:N", title="Classe importo (EUR)", sort=None),
        y=alt.Y("n_pensioni:Q", title="N. pensioni"),
        tooltip=["chiave", alt.Tooltip("n_pensioni", format=",.0f"), alt.Tooltip("importo_medio_mensile_eur", format=",.0f")],
    ).properties(height=350)
    st.altair_chart(chart, use_container_width=True)

with tab2:
    st.subheader("Pensioni per classe di eta")
    c1, c2 = st.columns(2)
    with c1:
        anno_eta = st.selectbox("Anno", sorted(eta["anno"].unique(), reverse=True), key="eta_anno")
    with c2:
        sesso_eta = st.selectbox("Sesso", ["Maschi", "Femmine"], key="eta_sesso")

    df_eta = eta[(eta["anno"] == anno_eta) & (eta["sesso"] == sesso_eta)]
    df_eta = df_eta[df_eta["chiave"].notna() & (df_eta["chiave"] != "")]

    chart2 = alt.Chart(df_eta).mark_bar().encode(
        x=alt.X("chiave:N", title="Classe di eta", sort=None),
        y=alt.Y("n_pensioni:Q", title="N. pensioni"),
        tooltip=["chiave", alt.Tooltip("n_pensioni", format=",.0f")],
    ).properties(height=350)
    st.altair_chart(chart2, use_container_width=True)

with tab3:
    st.subheader("Pensioni per regione")
    c1, c2 = st.columns(2)
    with c1:
        anno_reg = st.selectbox("Anno", sorted(reg["anno"].unique(), reverse=True), key="reg_anno")
    with c2:
        sesso_reg = st.selectbox("Sesso", ["Maschi", "Femmine"], key="reg_sesso")

    df_r = reg[(reg["anno"] == anno_reg) & (reg["sesso"] == sesso_reg)]
    df_r = df_r[df_r["chiave"].notna() & ~df_r["chiave"].str.contains("Totale", na=False)]
    df_r = df_r.sort_values("n_pensioni", ascending=False).head(10)

    chart3 = alt.Chart(df_r).mark_bar().encode(
        y=alt.Y("chiave:N", title="Regione", sort="-x"),
        x=alt.X("n_pensioni:Q", title="N. pensioni"),
        tooltip=["chiave", alt.Tooltip("n_pensioni", format=",.0f")],
    ).properties(height=400)
    st.altair_chart(chart3, use_container_width=True)
