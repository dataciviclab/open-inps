"""Lavoro — Deep dive: rapporti e retribuzioni."""

import altair as alt
import pandas as pd
import streamlit as st

from sources import fmt_num, require_mart

st.title("💼 Lavoro")
st.markdown("Dettaglio sul mercato del lavoro: assunzioni per tipo e retribuzioni.")

# ── Dati ────────────────────────────────────────────────────────────────────

rap = require_mart("inps_rapporti_lavoro", "mart_rapporti_regione")
ret = require_mart("inps_retribuzioni", "mart_retribuzioni_regione")

# ── Tabs ────────────────────────────────────────────────────────────────────

tab1, tab2 = st.tabs(["📊 Rapporti di lavoro", "💰 Retribuzioni"])

with tab1:
    st.subheader("Assunzioni per tipo")

    c1, c2 = st.columns(2)
    with c1:
        anno_rap = st.selectbox("Anno", sorted(rap["anno"].unique(), reverse=True), key="rap_anno")
    with c2:
        sesso_rap = st.selectbox("Sesso", ["Maschi", "Femmine"], key="rap_sesso")

    df_r = rap[(rap["anno"] == anno_rap) & (rap["sesso"] == sesso_rap)]
    df_r = df_r[~df_r["tipo_rapporto"].str.contains("Totale", na=False)]
    df_r = df_r.groupby("tipo_rapporto", as_index=False)["n_rapporti"].sum()
    df_r = df_r.sort_values("n_rapporti", ascending=False)

    chart = alt.Chart(df_r).mark_bar().encode(
        y=alt.Y("tipo_rapporto:N", title="Tipo rapporto", sort="-x"),
        x=alt.X("n_rapporti:Q", title="N. rapporti"),
        tooltip=["tipo_rapporto", alt.Tooltip("n_rapporti", format=",.0f")],
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)

    st.subheader("Trend per tipo di rapporto")
    df_trend = rap[(rap["sesso"] == sesso_rap) & (~rap["tipo_rapporto"].str.contains("Totale", na=False))]
    df_trend = df_trend.groupby(["anno", "tipo_rapporto"], as_index=False)["n_rapporti"].sum()

    chart2 = alt.Chart(df_trend).mark_line(point=True).encode(
        x=alt.X("anno:O", title="Anno"),
        y=alt.Y("n_rapporti:Q", title="N. rapporti"),
        color="tipo_rapporto:N",
        tooltip=["anno", "tipo_rapporto", alt.Tooltip("n_rapporti", format=",.0f")],
    ).properties(height=300)
    st.altair_chart(chart2, use_container_width=True)

with tab2:
    st.subheader("Retribuzioni per regione")
    st.caption("Dati dal settore privato (obs 492, 2019-2023)")

    anno_ret = st.selectbox("Anno", sorted(ret["anno"].unique(), reverse=True), key="ret_anno")

    df_ret = ret[(ret["anno"] == anno_ret) & (ret["fonte"] == "492")]
    df_ret = df_ret[df_ret["regione"].notna() & ~df_ret["regione"].str.contains("Totale", na=False)]
    df_ret = df_ret.sort_values("n_lavoratori", ascending=False).head(10)

    chart3 = alt.Chart(df_ret).mark_bar().encode(
        y=alt.Y("regione:N", title="Regione", sort="-x"),
        x=alt.X("n_lavoratori:Q", title="N. lavoratori"),
        tooltip=["regione", alt.Tooltip("n_lavoratori", format=",.0f")],
    ).properties(height=400)
    st.altair_chart(chart3, use_container_width=True)
