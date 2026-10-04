"""Dati — Tabella interattiva su tutti i mart."""

import streamlit as st
from sources import require_compose, require_mart

st.title("📋 Tabelle")
st.markdown("Esplora i dati grezzi dei singoli mart.")

# ── Selezione dataset ────────────────────────────────────────────────────────

DATASETS = {
    "compose/nazionale": ("inps_analisi", "mart_nazionale"),
    "compose/territoriale": ("inps_analisi", "mart_territoriale"),
    "compose/benchmark": ("inps_analisi", "mart_benchmark"),
    "compose/lifecycle": ("inps_analisi", "mart_lifecycle"),
    "pensioni/importo": ("inps_pensioni_vigenti", "mart_vigenti_importo"),
    "pensioni/eta": ("inps_pensioni_vigenti", "mart_vigenti_eta"),
    "pensioni/regione": ("inps_pensioni_vigenti", "mart_vigenti_regione"),
    "pensioni/liquidate": ("inps_pensioni_liquidate", "mart_liquidate_importo"),
    "pensioni/serie_categoria": ("inps_pensioni_serie", "mart_pensioni_serie_categoria"),
    "pensioni/serie_regione": ("inps_pensioni_serie", "mart_pensioni_serie_regione"),
    "pensioni/flussi_regione": ("inps_pensionamento_flussi", "mart_pensionamento_regione"),
    "rapporti/regione": ("inps_rapporti_lavoro", "mart_rapporti_regione"),
    "cessazioni/regione": ("inps_rapporti_cessazioni", "mart_cessazioni_regione"),
    "cessazioni/motivo": ("inps_rapporti_cessazioni", "mart_cessazioni_motivo"),
    "settore/nazionale": ("inps_flussi_settore", "mart_flussi_settore"),
    "retribuzioni/regione": ("inps_retribuzioni", "mart_retribuzioni_regione"),
    "pa/gruppo": ("inps_lavoratori_pubblici", "mart_lavoratori_pa_gruppo"),
    "pa/regione": ("inps_lavoratori_pubblici", "mart_lavoratori_pa_regione"),
    "redditi/posizione": ("inps_lavoratori_redditi", "mart_lavoratori_redditi_posizione"),
    "redditi/regione": ("inps_lavoratori_redditi", "mart_lavoratori_redditi_regione"),
    "naspi/regione": ("inps_naspi", "mart_naspi_regione"),
    "naspi/eta": ("inps_naspi", "mart_naspi_eta"),
    "dis_coll/nazionale": ("inps_dis_coll", "mart_dis_coll_nazionale"),
    "rdc/nazionale": ("inps_rdc_pdc", "mart_rdc_pdc_nazionale"),
    "rdc/regione": ("inps_rdc_pdc", "mart_rdc_pdc_regione"),
    "cig/regione": ("inps_cig", "mart_cig_regione"),
    "assegno/regione": ("inps_assegno_unico", "mart_au_regione"),
    "dp/regione": ("inps_dipendenti_pubblici", "mart_dp_regione"),
}

sel = st.selectbox("Dataset", list(DATASETS.keys()))
slug, table = DATASETS[sel]

if slug == "inps_analisi":
    df = require_compose(table)
else:
    df = require_mart(slug, table)

if df.empty:
    st.stop()

# ── Filtri ──────────────────────────────────────────────────────────────────

with st.expander("Filtri", expanded=False):
    filters = {}
    for col in df.columns:
        if df[col].dtype == "object" and df[col].nunique() < 50:
            vals = sorted(df[col].dropna().unique())
            chosen = st.multiselect(col, vals, default=vals[:5], key=f"filter_{col}")
            if chosen:
                filters[col] = chosen

    df_f = df.copy()
    for col, vals in filters.items():
        df_f = df_f[df_f[col].isin(vals)]

# ── Tabella ──────────────────────────────────────────────────────────────────

st.subheader(f"{len(df_f)} righe")
st.dataframe(df_f, use_container_width=True, height=400)

# ── Download ────────────────────────────────────────────────────────────────

csv = df_f.to_csv(index=False)
st.download_button("⬇️ Scarica CSV", csv, f"{sel.replace('/', '_')}.csv", "text/csv")
