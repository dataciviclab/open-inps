"""Lifecycle — Il ciclo vita: lavoro → disoccupazione → pensione."""

import altair as alt
import pandas as pd
import streamlit as st

from sources import METRICHE, fmt_it, load_mart

st.title("🔄 Lifecycle")
st.markdown("**Il ciclo**: dal lavoro alla pensione, come si muovono gli indicatori nel tempo.")

# ── Carica dati ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def load_lifecycle() -> pd.DataFrame:
    return load_mart("inps_analisi", "mart_lifecycle", 2026)

df = load_lifecycle()
if df.empty:
    st.error("Dati non disponibili.")
    st.stop()

# ── Filtri ──────────────────────────────────────────────────────────────────

sesso = st.radio("Sesso", ["Maschi", "Femmine"], horizontal=True, key="lc_sesso")

df_sesso = df[df["sesso"] == sesso].copy()
if df_sesso.empty:
    st.warning("Nessun dato per il sesso selezionato.")
    st.stop()

# ── Indici normalizzati (base = primo anno disponibile) ─────────────────────

st.subheader(f"Indici normalizzati — {sesso}")

metriche_disponibili = sorted(df_sesso["metrica"].unique())
metriche_labels = {m: METRICHE.get(m, m) for m in metriche_disponibili}

chart = alt.Chart(df_sesso).mark_line(point=True).encode(
    x=alt.X("anno:O", title="Anno"),
    y=alt.Y("indice:Q", title="Indice (base = primo anno)", scale=alt.Scale(type="linear")),
    color=alt.Color("metrica:N", title="Metrica", scale=alt.Scale(scheme="category10")),
    tooltip=["anno", "metrica", "indice", alt.Tooltip("valore", format=",.0f")],
).properties(height=400)

st.altair_chart(chart, use_container_width=True)

st.info(
    "Indice 100 = valore del primo anno disponibile per ogni metrica. "
    "Valori > 100 = crescita, < 100 = calo."
)

# ── Tabella valori ──────────────────────────────────────────────────────────

st.subheader("📋 Valori assoluti")

df_pivot = df_sesso.pivot_table(index="anno", columns="metrica", values="valore", aggfunc="sum")
df_pivot.columns = [metriche_labels.get(c, c) for c in df_pivot.columns]
st.dataframe(df_pivot.style.format("{:,.0f}"), use_container_width=True)

# ── Analisi: lavoro → pensione ──────────────────────────────────────────────

st.markdown("---")
st.subheader("🔍 Focus: lavoro → pensione")

# Confronto diretto lavoro vs pensioni
if "lavoratori_privati" in metriche_disponibili and "pensioni_vigenti" in metriche_disponibili:
    df_lav = df_sesso[df_sesso["metrica"] == "lavoratori_privati"].set_index("anno")["indice"]
    df_pen = df_sesso[df_sesso["metrica"] == "pensioni_vigenti"].set_index("anno")["indice"]

    df_confronto = pd.DataFrame({"Lavoratori": df_lav, "Pensioni": df_pen}).dropna()
    if not df_confronto.empty:
        df_melt = df_confronto.reset_index().melt("anno", var_name="Indicatore", value_name="Indice")
        chart2 = alt.Chart(df_melt).mark_line(point=True).encode(
            x=alt.X("anno:O", title="Anno"),
            y=alt.Y("Indice:Q", title="Indice"),
            color=alt.Color("Indicatore:N"),
            tooltip=["anno", "Indicatore", "Indice"],
        ).properties(height=300)
        st.altair_chart(chart2, use_container_width=True)
