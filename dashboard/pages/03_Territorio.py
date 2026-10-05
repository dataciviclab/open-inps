"""Territorio — mappa, ranking e metriche derivate per regione."""

import pandas as pd
import plotly.express as px
import streamlit as st
from sources import (
    ANNO_PIENO_CONSIGLIATO,
    GEOJSON_URL,
    METRICHE,
    METRICHE_DERIVATE,
    REGIONI,
    fmt_num,
    require_compose,
    to_geo_name,
)

st.title("🗺️ Territorio")
st.markdown(
    "Mappa e ranking regionale. Le metriche **derivate** (es. C/A) usano "
    "il compose territoriale. Estero escluso dalle mappe."
)

df = require_compose("mart_territoriale")

anni = sorted(df["anno"].unique(), reverse=True)
default_idx = anni.index(ANNO_PIENO_CONSIGLIATO) if ANNO_PIENO_CONSIGLIATO in anni else 0

c1, c2, c3 = st.columns(3)
with c1:
    anno = st.selectbox("Anno", anni, index=default_idx, key="terr_anno")
with c2:
    opzioni_met = list(METRICHE.keys()) + list(METRICHE_DERIVATE.keys())
    met = st.selectbox(
        "Metrica",
        opzioni_met,
        format_func=lambda x: METRICHE.get(x) or METRICHE_DERIVATE.get(x, x),
        key="terr_met",
    )
with c3:
    sesso = st.selectbox("Sesso", ["Totale", "Maschi", "Femmine"], key="terr_sesso")

n_met_anno = df[df["anno"] == anno]["metrica"].nunique()
if n_met_anno < 8:
    st.warning(
        f"Anno **{anno}** con solo {n_met_anno} metriche nel territoriale: "
        f"copertura parziale. Per un quadro pieno prova il **{ANNO_PIENO_CONSIGLIATO}**."
    )


def _agg_sesso(d: pd.DataFrame) -> pd.DataFrame:
    if d.empty:
        return d
    return (
        d.groupby("regione", as_index=False)
        .agg({"valore": "sum", "share_pct": "sum", "indice_vs_media": "mean"})
        .assign(sesso="Totale")
    )


def _load_metrica(metrica: str) -> pd.DataFrame:
    if metrica == "ratio_cessazioni_assunzioni":
        base = df[
            (df["anno"] == anno) & df["metrica"].isin(["rapporti_lavoro", "cessazioni_lavoro"])
        ]
        if sesso == "Totale":
            base = base[base["sesso"].isin(["Maschi", "Femmine"])]
        else:
            base = base[base["sesso"] == sesso]
        piv = base.pivot_table(index="regione", columns="metrica", values="valore", aggfunc="sum")
        if "rapporti_lavoro" not in piv.columns or "cessazioni_lavoro" not in piv.columns:
            return pd.DataFrame()
        out = pd.DataFrame(
            {
                "regione": piv.index,
                "valore": (piv["cessazioni_lavoro"] / piv["rapporti_lavoro"] * 100).round(1),
            }
        )
        out["share_pct"] = None
        out["indice_vs_media"] = None
        out["sesso"] = sesso
        return out

    d = df[(df["anno"] == anno) & (df["metrica"] == metrica)]
    if sesso == "Totale":
        if (d["sesso"] == "Totale").any():
            d = d[d["sesso"] == "Totale"]
        else:
            d = _agg_sesso(d[d["sesso"].isin(["Maschi", "Femmine"])])
    else:
        d = d[d["sesso"] == sesso]
    return d


df_f = _load_metrica(met)
df_f = df_f[df_f["regione"].isin(REGIONI)] if df_f is not None and not df_f.empty else df_f

if df_f is None or df_f.empty or df_f["valore"].isna().all():
    st.warning("Nessun dato disponibile per questa combinazione anno × metrica × sesso.")
    st.stop()

# Mapping nomi → GeoJSON (come RNA/opencivitas)
df_f = df_f.copy()
df_f["reg_geo"] = df_f["regione"].map(to_geo_name)

titolo_met = METRICHE.get(met) or METRICHE_DERIVATE.get(met, met)
st.subheader(f"{titolo_met} — {anno} ({sesso})")

# Pattern RNA: paper_bgcolor trasparente + width stretch
fig = px.choropleth(
    df_f,
    geojson=GEOJSON_URL,
    locations="reg_geo",
    featureidkey="properties.reg_name",
    color="valore",
    color_continuous_scale=("Blues" if met != "ratio_cessazioni_assunzioni" else "RdYlGn_r"),
    hover_name="regione",
    hover_data={
        "reg_geo": False,
        "valore": ":,.1f" if met == "ratio_cessazioni_assunzioni" else ":,.0f",
    },
    labels={"valore": "%" if met == "ratio_cessazioni_assunzioni" else "Valore"},
)
fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor="rgba(0,0,0,0)",
    height=500,
)
st.plotly_chart(fig, width="stretch")

st.subheader("📊 Ranking regioni")

df_rank = df_f.sort_values("valore", ascending=False).reset_index(drop=True)
df_rank.index = df_rank.index + 1
cols_rank = ["regione", "valore"]
if "share_pct" in df_rank.columns and df_rank["share_pct"].notna().any():
    cols_rank.append("share_pct")
if "indice_vs_media" in df_rank.columns and df_rank["indice_vs_media"].notna().any():
    cols_rank.append("indice_vs_media")
df_rank = df_rank[cols_rank].copy()
df_rank.columns = ["Regione", "Valore"] + [c.replace("_", " ").title() for c in cols_rank[2:]]
if met == "ratio_cessazioni_assunzioni":
    df_rank["Valore"] = df_rank["Valore"].apply(lambda x: f"{x:.1f}%")
else:
    df_rank["Valore"] = df_rank["Valore"].apply(fmt_num)
st.dataframe(df_rank, width="stretch")

if met == "ratio_cessazioni_assunzioni":
    st.caption(
        "C/A alta = più cessazioni che assunzioni. "
        "Valori ~95-100% sono la norma nazionale negli ultimi anni."
    )

st.caption("Dati: compose `inps_analisi` · GeoJSON: openpolis/geojson-italy · CC BY 4.0")
