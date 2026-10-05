"""Welfare — NASpI, DIS-COLL, RdC/PdC, Assegno Unico, CIG."""

import altair as alt
import pandas as pd
import streamlit as st
from sources import ANNO_PIENO_CONSIGLIATO, fmt_num, require_compose, require_mart

st.title("🏛️ Welfare e politiche passive")
st.markdown(
    "NASpI, DIS-COLL, Reddito/Pensione di Cittadinanza, Assegno Unico e Cassa Integrazione."
)

df = require_compose("mart_nazionale")
bench = require_compose("mart_benchmark")

anni = sorted(df["anno"].unique(), reverse=True)
default_idx = anni.index(ANNO_PIENO_CONSIGLIATO) if ANNO_PIENO_CONSIGLIATO in anni else 0
c1, c2 = st.columns(2)
with c1:
    anno = st.selectbox("Anno", anni, index=default_idx, key="wf_anno")
with c2:
    sesso = st.radio("Sesso", ["Tutti", "Maschi", "Femmine"], horizontal=True, key="wf_sesso")


def _series(metrica: str) -> pd.DataFrame:
    d = df[df["metrica"] == metrica]
    if sesso == "Tutti":
        if (d["sesso"] == "Totale").any():
            return d[d["sesso"] == "Totale"][["anno", "valore"]]
        return (
            d[d["sesso"].isin(["Maschi", "Femmine"])]
            .groupby("anno", as_index=False)["valore"]
            .sum()
        )
    return d[d["sesso"] == sesso][["anno", "valore"]]


st.subheader(f"Quadro {anno}")

kpi = [
    ("naspi", "NASpI beneficiari"),
    ("dis_coll", "DIS-COLL beneficiari"),
    ("rdc_nuclei", "Nuclei RdC/PdC"),
    ("assegno_unico", "Figli assegno unico"),
    ("cig_ore", "Ore CIG"),
]
cols = st.columns(len(kpi))
for col, (metrica, label) in zip(cols, kpi):
    d = _series(metrica)
    val = float(d[d["anno"] == anno]["valore"].sum()) if not d[d["anno"] == anno].empty else None
    with col:
        st.metric(label, fmt_num(int(val)) if val else "–")

# ── Trend: scala grande vs DIS-COLL ────────────────────────────────────────

st.markdown("---")
st.subheader("📈 Serie storiche welfare")

BIG = [("naspi", "NASpI"), ("rdc_nuclei", "RdC/PdC"), ("assegno_unico", "Assegno Unico")]
trend_parts = []
for metrica, label in BIG:
    d = _series(metrica)
    if not d.empty:
        trend_parts.append(d.assign(metrica=label))

if trend_parts:
    trend = pd.concat(trend_parts, ignore_index=True)
    st.altair_chart(
        alt.Chart(trend)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            x=alt.X("anno:O", title="Anno"),
            y=alt.Y("valore:Q", title="Beneficiari / nuclei / figli"),
            color="metrica:N",
            tooltip=["anno", "metrica", alt.Tooltip("valore", format=",.0f")],
        )
        .properties(height=320),
        use_container_width=True,
    )
    st.caption("Scala unitaria (milioni). RdC/PdC 2019–2023; Assegno Unico dal 2022.")

st.subheader("DIS-COLL (scala separata)")
df_dc = _series("dis_coll")
if not df_dc.empty:
    st.altair_chart(
        alt.Chart(df_dc)
        .mark_line(point=True, strokeWidth=2, color="#b45309")
        .encode(
            x=alt.X("anno:O", title="Anno"),
            y=alt.Y("valore:Q", title="N. beneficiari"),
            tooltip=["anno", alt.Tooltip("valore", format=",.0f")],
        )
        .properties(height=240),
        use_container_width=True,
    )
    st.caption(
        "DIS-COLL è una nicchia co.co.co (~23k/anno vs ~2M NASpI): "
        "grafico separato per non appiattirlo sulle altre serie."
    )
else:
    st.info(f"Nessun dato DIS-COLL per {sesso}.")

# ── RdC per regione ─────────────────────────────────────────────────────────

st.markdown("---")
st.subheader("🗺️ RdC/PdC per regione")

rdc_reg = require_mart("inps_rdc_pdc", "mart_rdc_pdc_regione")
anni_rdc = sorted(rdc_reg["anno"].unique(), reverse=True)
if anni_rdc:
    anno_rdc = st.selectbox("Anno RdC/PdC", anni_rdc, key="rdc_anno")
    df_rdc = rdc_reg[rdc_reg["anno"] == anno_rdc]
    df_rdc = df_rdc.groupby("regione", as_index=False)["n_nuclei"].sum()
    df_rdc = df_rdc.sort_values("n_nuclei", ascending=False)
    st.altair_chart(
        alt.Chart(df_rdc)
        .mark_bar()
        .encode(
            y=alt.Y("regione:N", sort="-x", title=""),
            x=alt.X("n_nuclei:Q", title="N. nuclei"),
            tooltip=["regione", alt.Tooltip("n_nuclei", format=",.0f")],
        )
        .properties(height=420),
        use_container_width=True,
    )
    st.caption("Osservatorio 452: nuclei con almeno una mensilità RdC/PdC nell'anno.")

# ── Benchmark welfare ───────────────────────────────────────────────────────

st.markdown("---")
st.subheader("📊 Rapporti strutturali")

bench_yr = bench[bench["anno"] == anno]
if not bench_yr.empty:
    b = bench_yr.iloc[0]
    c1, c2, c3 = st.columns(3)
    with c1:
        val = b.get("rapporto_dis_coll_naspi_pct")
        st.metric("DIS-COLL / NASpI", f"{val:.2f}%" if pd.notna(val) else "–")
    with c2:
        val = b.get("rapporto_cessazioni_assunzioni_pct")
        st.metric("Cessazioni / Assunzioni", f"{val:.1f}%" if pd.notna(val) else "–")
    with c3:
        val = b.get("turnover_pensionistico_pct")
        st.metric(
            "Turnover pensioni",
            f"{val:.1f}%" if pd.notna(val) else "–",
            help="Liquidate su vigenti",
        )
