"""Pensioni — Stock, serie storica, categoria, flussi di pensionamento."""

import altair as alt
import pandas as pd
import streamlit as st
from sources import fmt_num, require_compose, require_mart

st.title("🏦 Pensioni")
st.markdown(
    "Stock vigenti, distribuzione per importo/età, **serie storica 1998–2026** "
    "e flussi di pensionamento."
)

tab1, tab2, tab3, tab4 = st.tabs(["📊 Stock", "📜 Serie storica", "🧬 Categoria", "🚰 Flussi"])

# ── Stock (obs 378) ─────────────────────────────────────────────────────────
with tab1:
    imp = require_mart("inps_pensioni_vigenti", "mart_vigenti_importo")
    eta = require_mart("inps_pensioni_vigenti", "mart_vigenti_eta")
    reg = require_mart("inps_pensioni_vigenti", "mart_vigenti_regione")
    st.caption(
        "Obs 378 — stock in pagamento (2022–2026). Per la serie lunga vedi la tab Serie storica."
    )

    tab_a, tab_b, tab_c = st.tabs(["Importo", "Età", "Regione"])
    with tab_a:
        c1, c2 = st.columns(2)
        with c1:
            anno_imp = st.selectbox(
                "Anno", sorted(imp["anno"].unique(), reverse=True), key="imp_anno"
            )
        with c2:
            sesso_imp = st.selectbox("Sesso", ["Maschi", "Femmine"], key="imp_sesso")
        df_imp = imp[(imp["anno"] == anno_imp) & (imp["sesso"] == sesso_imp)]
        df_imp = df_imp[df_imp["chiave"].notna() & (df_imp["chiave"] != "")]
        st.altair_chart(
            alt.Chart(df_imp)
            .mark_bar()
            .encode(
                x=alt.X("chiave:N", title="Classe importo", sort=None),
                y=alt.Y("n_pensioni:Q", title="N. pensioni"),
                tooltip=[
                    "chiave",
                    alt.Tooltip("n_pensioni", format=",.0f"),
                    alt.Tooltip("importo_medio_mensile_eur", format=",.0f"),
                ],
            )
            .properties(height=340),
            use_container_width=True,
        )
    with tab_b:
        c1, c2 = st.columns(2)
        with c1:
            anno_eta = st.selectbox(
                "Anno", sorted(eta["anno"].unique(), reverse=True), key="eta_anno"
            )
        with c2:
            sesso_eta = st.selectbox("Sesso", ["Maschi", "Femmine"], key="eta_sesso")
        df_eta = eta[(eta["anno"] == anno_eta) & (eta["sesso"] == sesso_eta)]
        df_eta = df_eta[df_eta["chiave"].notna() & (df_eta["chiave"] != "")]
        st.altair_chart(
            alt.Chart(df_eta)
            .mark_bar()
            .encode(
                x=alt.X("chiave:N", title="Classe età", sort=None),
                y=alt.Y("n_pensioni:Q", title="N. pensioni"),
                tooltip=["chiave", alt.Tooltip("n_pensioni", format=",.0f")],
            )
            .properties(height=340),
            use_container_width=True,
        )
    with tab_c:
        c1, c2 = st.columns(2)
        with c1:
            anno_reg = st.selectbox(
                "Anno", sorted(reg["anno"].unique(), reverse=True), key="reg_anno"
            )
        with c2:
            sesso_reg = st.selectbox("Sesso", ["Maschi", "Femmine"], key="reg_sesso")
        df_r = reg[(reg["anno"] == anno_reg) & (reg["sesso"] == sesso_reg)]
        df_r = df_r[df_r["chiave"].notna() & ~df_r["chiave"].str.contains("Totale", na=False)]
        df_r = df_r.sort_values("n_pensioni", ascending=False).head(10)
        st.altair_chart(
            alt.Chart(df_r)
            .mark_bar()
            .encode(
                y=alt.Y("chiave:N", title="Regione", sort="-x"),
                x=alt.X("n_pensioni:Q", title="N. pensioni"),
                tooltip=["chiave", alt.Tooltip("n_pensioni", format=",.0f")],
            )
            .properties(height=400),
            use_container_width=True,
        )

# ── Serie storica (obs 390/376) ────────────────────────────────────────────
with tab2:
    serie = require_mart("inps_pensioni_serie", "mart_pensioni_serie_categoria")
    st.caption(
        "Obs 390+376 — serie lunga. Vigenti 1998–2026, liquidate 1997–2025. "
        "Il compose unifica già le vigenti <2022 con lo stock 378."
    )

    compose = require_compose("mart_nazionale")
    df_v = compose[
        (compose["metrica"] == "pensioni_vigenti")
        & (compose["sesso"].isin(["Maschi", "Femmine", "Totale"]))
    ]
    # preferisci M+F sommati
    df_v = (
        df_v[df_v["sesso"].isin(["Maschi", "Femmine"])]
        .groupby("anno", as_index=False)["valore"]
        .sum()
    )
    df_v = df_v.assign(tipo="Vigenti (compose)")

    df_l = serie[
        (serie["tipo_pensione"] == "liquidata") & (serie["sesso"].isin(["Maschi", "Femmine"]))
    ]
    df_l = (
        df_l.groupby("anno", as_index=False)["n_pensioni"]
        .sum()
        .rename(columns={"n_pensioni": "valore"})
    )
    df_l = df_l.assign(tipo="Liquidate (376)")

    df_s = pd.concat(
        [
            df_v.rename(columns={"valore": "n"})[["anno", "n", "tipo"]],
            df_l.rename(columns={"valore": "n"})[["anno", "n", "tipo"]],
        ],
        ignore_index=True,
    )

    st.altair_chart(
        alt.Chart(df_s)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            x=alt.X("anno:O", title="Anno"),
            y=alt.Y("n:Q", title="N. pensioni"),
            color="tipo:N",
            tooltip=["anno", "tipo", alt.Tooltip("n", format=",.0f")],
        )
        .properties(height=360),
        use_container_width=True,
    )

    # importo medio e età dalla serie
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Importo medio mensile (vigenti)")
        df_imp_s = serie[
            (serie["tipo_pensione"] == "vigente")
            & (serie["sesso"].isin(["Maschi", "Femmine"]))
            & (serie["importo_medio_mensile_eur"].notna())
        ]
        df_imp_s = df_imp_s.groupby(["anno", "sesso"], as_index=False)[
            "importo_medio_mensile_eur"
        ].mean()
        st.altair_chart(
            alt.Chart(df_imp_s)
            .mark_line(point=True)
            .encode(
                x=alt.X("anno:O", title="Anno"),
                y=alt.Y("importo_medio_mensile_eur:Q", title="€ / mese"),
                color="sesso:N",
                tooltip=["anno", "sesso", alt.Tooltip("importo_medio_mensile_eur", format=",.0f")],
            )
            .properties(height=280),
            use_container_width=True,
        )
    with c2:
        st.subheader("Età media alla pensione (vigenti)")
        df_eta_s = serie[
            (serie["tipo_pensione"] == "vigente")
            & (serie["sesso"].isin(["Maschi", "Femmine"]))
            & (serie["eta_media"].notna())
        ]
        df_eta_s = df_eta_s.groupby(["anno", "sesso"], as_index=False)["eta_media"].mean()
        st.altair_chart(
            alt.Chart(df_eta_s)
            .mark_line(point=True)
            .encode(
                x=alt.X("anno:O", title="Anno"),
                y=alt.Y("eta_media:Q", title="Anni"),
                color="sesso:N",
                tooltip=["anno", "sesso", alt.Tooltip("eta_media", format=",.1f")],
            )
            .properties(height=280),
            use_container_width=True,
        )

# ── Categoria (obs 390) ────────────────────────────────────────────────────
with tab3:
    cat = require_mart("inps_pensioni_serie", "mart_pensioni_serie_categoria")
    c1, c2 = st.columns(2)
    with c1:
        tipo_p = st.selectbox("Tipo", ["vigente", "liquidata"], key="cat_tipo")
    with c2:
        anno_c = st.selectbox(
            "Anno",
            sorted(cat[cat["tipo_pensione"] == tipo_p]["anno"].unique(), reverse=True),
            key="cat_anno",
        )
    df_c = cat[
        (cat["tipo_pensione"] == tipo_p)
        & (cat["anno"] == anno_c)
        & (cat["sesso"].isin(["Maschi", "Femmine"]))
    ]
    df_c = df_c.groupby("categoria", as_index=False)["n_pensioni"].sum()
    df_c = df_c.sort_values("n_pensioni", ascending=False)
    st.altair_chart(
        alt.Chart(df_c)
        .mark_bar()
        .encode(
            y=alt.Y("categoria:N", sort="-x", title=""),
            x=alt.X("n_pensioni:Q", title="N. pensioni"),
            tooltip=["categoria", alt.Tooltip("n_pensioni", format=",.0f")],
        )
        .properties(height=340),
        use_container_width=True,
    )

    # gestione
    st.subheader("Per tipo di gestione")
    ges = require_mart("inps_pensioni_serie", "mart_pensioni_serie_tipogest")
    df_g = ges[
        (ges["tipo_pensione"] == tipo_p)
        & (ges["anno"] == anno_c)
        & (ges["sesso"].isin(["Maschi", "Femmine"]))
    ]
    df_g = df_g.groupby("tipo_gestione", as_index=False)["n_pensioni"].sum()
    df_g = df_g.sort_values("n_pensioni", ascending=False).head(10)
    st.altair_chart(
        alt.Chart(df_g)
        .mark_bar()
        .encode(
            y=alt.Y("tipo_gestione:N", sort="-x", title=""),
            x=alt.X("n_pensioni:Q", title="N. pensioni"),
            tooltip=["tipo_gestione", alt.Tooltip("n_pensioni", format=",.0f")],
        )
        .properties(height=360),
        use_container_width=True,
    )

# ── Flussi pensionamento (obs 475) ─────────────────────────────────────────
with tab4:
    fl = require_mart("inps_pensionamento_flussi", "mart_pensionamento_regione")
    st.caption(
        "Obs 475 — nuove pensioni per anno decorrenza (non sommare con liquidate/anno: "
        "definizioni diverse)."
    )
    c1, c2 = st.columns(2)
    with c1:
        anno_f = st.selectbox("Anno", sorted(fl["anno"].unique(), reverse=True), key="fl_pen_anno")
    with c2:
        sesso_f = st.selectbox("Sesso", ["Maschi", "Femmine"], key="fl_pen_sesso")

    df_f = fl[(fl["anno"] == anno_f) & (fl["sesso"] == sesso_f)]
    st.metric(
        "Nuove pensioni (M+F somma sesso)",
        fmt_num(int(fl[(fl["anno"] == anno_f)]["n_pensioni"].sum())),
    )

    # trimestre
    df_t = (
        fl[fl["sesso"] == sesso_f]
        .groupby(["anno", "trimestre"], as_index=False)["n_pensioni"]
        .sum()
    )
    ordine = {"I trimestre": 1, "II trimestre": 2, "III trimestre": 3, "IV trimestre": 4}
    df_t["ord"] = df_t["trimestre"].map(ordine).fillna(9)
    df_t = df_t.sort_values(["anno", "ord"])
    st.altair_chart(
        alt.Chart(df_t)
        .mark_line(point=True)
        .encode(
            x=alt.X("anno:O", title="Anno decorrenza"),
            y=alt.Y("n_pensioni:Q", title="N. nuove pensioni"),
            color="trimestre:N",
            tooltip=["anno", "trimestre", alt.Tooltip("n_pensioni", format=",.0f")],
        )
        .properties(height=300),
        use_container_width=True,
    )

    # regioni
    df_reg = df_f.groupby("regione", as_index=False)["n_pensioni"].sum()
    df_reg = df_reg.sort_values("n_pensioni", ascending=False).head(10)
    st.altair_chart(
        alt.Chart(df_reg)
        .mark_bar()
        .encode(
            y=alt.Y("regione:N", sort="-x", title=""),
            x=alt.X("n_pensioni:Q", title="N. nuove pensioni"),
            tooltip=["regione", alt.Tooltip("n_pensioni", format=",.0f")],
        )
        .properties(height=360),
        use_container_width=True,
    )
