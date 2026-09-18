"""Genere — Il paradosso: donne piu pensioni, meno lavoro."""

import altair as alt
import pandas as pd
import streamlit as st

from sources import METRICHE, require_compose, fmt_num

st.title("⚖️ Genere")
st.markdown("**Il paradosso**: le donne hanno piu pensioni ma meno lavoro.")

# ── Dati ────────────────────────────────────────────────────────────────────

df = require_compose("mart_nazionale")
df_bench = require_compose("mart_benchmark")

# ── Filtri ──────────────────────────────────────────────────────────────────

anno = st.selectbox("Anno", sorted(df["anno"].unique(), reverse=True))

# ── Gap sintetico dal benchmark ─────────────────────────────────────────────

bench_yr = df_bench[df_bench["anno"] == anno]
if not bench_yr.empty:
    b = bench_yr.iloc[0]
    g_ass = b.get("gap_genere_assunzioni_pct")
    g_pen = b.get("gap_genere_pensioni_pct")
    g_nas = b.get("gap_genere_naspi_pct")

    st.subheader("Gap di genere (rapporto F/M)")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Assunzioni", f"+{g_ass:.1f}%" if pd.notna(g_ass) else "–",
                  help="Quanto piu assunzioni maschili")
    with c2:
        st.metric("Pensioni", f"+{g_pen:.1f}%" if pd.notna(g_pen) else "–",
                  help="Quanto piu pensioni femminili")
    with c3:
        st.metric("NASpI", f"+{g_nas:.1f}%" if pd.notna(g_nas) else "–",
                  help="Quanto piu disoccupazione femminile")

    st.info("Assunzioni: + = piu uomini. Pensioni/NASpI: + = piu donne.")

# ── Barre impilatte ─────────────────────────────────────────────────────────

st.subheader(f"Confronto donne/uomini — {anno}")

df_yr = df[(df["anno"] == anno) & (df["sesso"].isin(["Maschi", "Femmine"]))]
df_bar = df_yr[["metrica", "sesso", "valore"]].copy()
df_bar["label"] = df_bar["metrica"].map(METRICHE)

chart = alt.Chart(df_bar).mark_bar().encode(
    x=alt.X("valore:Q", title="Valore", scale=alt.Scale(type="symlog")),
    y=alt.Y("label:N", title="", sort="-x"),
    color=alt.Color("sesso:N", scale=alt.Scale(domain=["Maschi", "Femmine"], range=["#2563eb", "#ec4899"])),
    tooltip=["label", "sesso", alt.Tooltip("valore", format=",.0f")],
).properties(height=300)
st.altair_chart(chart, use_container_width=True)

# ── Tabella gap ─────────────────────────────────────────────────────────────

st.subheader("Dettaglio gap")
pivot = df_yr.pivot_table(index="metrica", columns="sesso", values="valore", aggfunc="sum").reset_index()
pivot["label"] = pivot["metrica"].map(METRICHE)
pivot["gap%"] = ((pivot["Femmine"] - pivot["Maschi"]) / pivot["Maschi"] * 100).round(1)
df_gap = pivot[["label", "Maschi", "Femmine", "gap%"]].copy()
df_gap.columns = ["Metrica", "Maschi", "Femmine", "Gap %"]
st.dataframe(df_gap, use_container_width=True, hide_index=True)

# ── Trend gap ───────────────────────────────────────────────────────────────

st.subheader("Evoluzione del gap nel tempo")
met = st.selectbox("Metrica", list(METRICHE.keys()), format_func=lambda x: METRICHE[x], key="gap_met")
df_t = df[(df["metrica"] == met) & (df["sesso"].isin(["Maschi", "Femmine"]))]
pivot_t = df_t.pivot_table(index="anno", columns="sesso", values="valore", aggfunc="sum").reset_index()
pivot_t = pivot_t.dropna(subset=["Maschi", "Femmine"])
pivot_t["gap%"] = ((pivot_t["Femmine"] - pivot_t["Maschi"]) / pivot_t["Maschi"] * 100).round(1)

chart2 = alt.Chart(pivot_t).mark_line(point=True, color="#d97706").encode(
    x=alt.X("anno:O", title="Anno"),
    y=alt.Y("gap%:Q", title="Gap F/M (%)"),
    tooltip=["anno", alt.Tooltip("gap%", format="+.1f")],
).properties(height=250)
st.altair_chart(chart2, use_container_width=True)
