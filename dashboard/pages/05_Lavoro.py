"""Lavoro — Deep dive: flussi, settore, retribuzioni, PA."""

import altair as alt
import pandas as pd
import streamlit as st
from sources import require_mart

st.title("💼 Lavoro")
st.markdown("Assunzioni e cessazioni, settore NACE, retribuzioni private e lavoratori pubblici.")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Flussi", "🏭 Settore NACE", "💰 Retribuzioni", "🏛️ Pubblico"])

# ── Flussi assunzioni/cessazioni ────────────────────────────────────────────
with tab1:
    rap = require_mart("inps_rapporti_lavoro", "mart_rapporti_regione")
    ces = require_mart("inps_rapporti_cessazioni", "mart_cessazioni_regione")

    c1, c2 = st.columns(2)
    with c1:
        anno = st.selectbox("Anno", sorted(rap["anno"].unique(), reverse=True), key="fl_anno")
    with c2:
        sesso = st.selectbox("Sesso", ["Maschi", "Femmine"], key="fl_sesso")

    def _by_tipo(df, col_tipo, col_n):
        d = df[(df["anno"] == anno) & (df["sesso"] == sesso)]
        d = d[~d[col_tipo].astype(str).str.contains("Totale", na=False)]
        return d.groupby(col_tipo, as_index=False)[col_n].sum().sort_values(col_n, ascending=False)

    df_a = _by_tipo(rap, "tipo_rapporto", "n_rapporti")
    df_c = _by_tipo(ces, "tipo_cessazione", "n_cessazioni")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Assunzioni per tipo")
        st.altair_chart(
            alt.Chart(df_a)
            .mark_bar()
            .encode(
                y=alt.Y("tipo_rapporto:N", sort="-x", title=""),
                x=alt.X("n_rapporti:Q", title="N. rapporti"),
                tooltip=["tipo_rapporto", alt.Tooltip("n_rapporti", format=",.0f")],
            )
            .properties(height=320),
            use_container_width=True,
        )
    with col2:
        st.subheader("Cessazioni per tipo")
        st.altair_chart(
            alt.Chart(df_c)
            .mark_bar()
            .encode(
                y=alt.Y("tipo_cessazione:N", sort="-x", title=""),
                x=alt.X("n_cessazioni:Q", title="N. cessazioni"),
                tooltip=["tipo_cessazione", alt.Tooltip("n_cessazioni", format=",.0f")],
            )
            .properties(height=320),
            use_container_width=True,
        )

    # Trend confronto nazionale
    st.subheader("Trend nazionale assunzioni vs cessazioni")
    trend_a = (
        rap[~rap["tipo_rapporto"].astype(str).str.contains("Totale", na=False)]
        .groupby("anno", as_index=False)["n_rapporti"]
        .sum()
        .assign(flusso="Assunzioni")
        .rename(columns={"n_rapporti": "valore"})
    )
    trend_c = (
        ces[~ces["tipo_cessazione"].astype(str).str.contains("Totale", na=False)]
        .groupby("anno", as_index=False)["n_cessazioni"]
        .sum()
        .assign(flusso="Cessazioni")
        .rename(columns={"n_cessazioni": "valore"})
    )
    trend = pd.concat([trend_a, trend_c], ignore_index=True)
    st.altair_chart(
        alt.Chart(trend)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            x=alt.X("anno:O", title="Anno"),
            y=alt.Y("valore:Q", title="N. rapporti"),
            color="flusso:N",
            tooltip=["anno", "flusso", alt.Tooltip("valore", format=",.0f")],
        )
        .properties(height=320),
        use_container_width=True,
    )

# ── Settore NACE ────────────────────────────────────────────────────────────
with tab2:
    sett = require_mart("inps_flussi_settore", "mart_flussi_settore")
    c1, c2 = st.columns(2)
    with c1:
        anno_s = st.selectbox("Anno", sorted(sett["anno"].unique(), reverse=True), key="set_anno")
    with c2:
        flusso = st.selectbox("Flusso", ["assunzione", "cessazione"], key="set_flusso")

    df_s = sett[
        (sett["anno"] == anno_s)
        & (sett["flusso"] == flusso)
        & (sett["sesso"].isin(["Maschi", "Femmine"]))
    ]
    df_s = df_s.groupby(["settore_codice", "settore_nace"], as_index=False)["n_rapporti"].sum()
    df_s = df_s.sort_values("n_rapporti", ascending=False)

    st.altair_chart(
        alt.Chart(df_s)
        .mark_bar()
        .encode(
            y=alt.Y("settore_nace:N", sort="-x", title=""),
            x=alt.X("n_rapporti:Q", title="N. rapporti"),
            tooltip=["settore_codice", "settore_nace", alt.Tooltip("n_rapporti", format=",.0f")],
        )
        .properties(height=400),
        use_container_width=True,
    )
    st.caption(
        "Codici sezione NACE (A, B-E, F, G-I, J, K, L, M-N, O-U, Z). "
        "Classificazione Rev.2 fino al 2024, Rev.2.1 dal 2025."
    )

# ── Retribuzioni ────────────────────────────────────────────────────────────
with tab3:
    ret = require_mart("inps_retribuzioni", "mart_retribuzioni_regione")
    st.subheader("Lavoratori privati per regione (obs 492)")
    anno_r = st.selectbox("Anno", sorted(ret["anno"].unique(), reverse=True), key="ret_anno")
    df_ret = ret[(ret["anno"] == anno_r) & (ret["fonte"] == "492")]
    df_ret = df_ret[
        df_ret["regione"].notna() & ~df_ret["regione"].astype(str).str.contains("Totale", na=False)
    ]
    df_ret = df_ret.sort_values("n_lavoratori", ascending=False).head(10)
    st.altair_chart(
        alt.Chart(df_ret)
        .mark_bar()
        .encode(
            y=alt.Y("regione:N", sort="-x", title=""),
            x=alt.X("n_lavoratori:Q", title="N. lavoratori"),
            tooltip=["regione", alt.Tooltip("n_lavoratori", format=",.0f")],
        )
        .properties(height=400),
        use_container_width=True,
    )

# ── Pubblico ────────────────────────────────────────────────────────────────
with tab4:
    pa = require_mart("inps_lavoratori_pubblici", "mart_lavoratori_pa_gruppo")
    st.subheader("Lavoratori pubblici per comparto (obs 435)")
    st.caption("Nessuna dimensione genere: campo SESSO rotto sull'API.")
    anno_pa = st.selectbox("Anno", sorted(pa["anno"].unique(), reverse=True), key="pa_anno")
    df_pa = pa[pa["anno"] == anno_pa].sort_values("n_lavoratori", ascending=False)
    df_pa = df_pa.assign(retr_media=df_pa["retribuzioni_totali"] / df_pa["n_lavoratori"])
    st.altair_chart(
        alt.Chart(df_pa)
        .mark_bar()
        .encode(
            y=alt.Y("gruppo_contrattuale:N", sort="-x", title=""),
            x=alt.X("n_lavoratori:Q", title="N. lavoratori"),
            tooltip=[
                "gruppo_contrattuale",
                alt.Tooltip("n_lavoratori", format=",.0f"),
                alt.Tooltip("retr_media", format=",.0f", title="Retr. media €"),
            ],
        )
        .properties(height=360),
        use_container_width=True,
    )
