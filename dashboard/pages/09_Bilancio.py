"""Bilancio — Missioni COFOG, conto economico e rendiconto gestionale.

Fonte: CKAN open data INPS (2022–2024 missioni/CE; 2023–2024 gestionale).
Lente istituzionale: quanto costa l'INPS e chi lo paga — complementare
alle pagine beneficiari (pensioni, welfare, lavoro).
"""

import altair as alt
import pandas as pd
import streamlit as st
from sources import fmt_num, require_mart

st.title("🧾 Bilancio INPS")
st.markdown(
    "Spesa istituzionale per missioni COFOG, conto economico e rendiconto "
    "gestionale. Fonte: open data INPS (non Osservatori statistici)."
)

SLUG_M = "inps_bilancio_missioni"
SLUG_CE = "inps_bilancio_ce"
SLUG_RG = "inps_bilancio_gestionale"

df_m = require_mart(SLUG_M, "mart_bilancio_missioni")
df_conf = require_mart(SLUG_M, "mart_bilancio_confronto")
df_ce = require_mart(SLUG_CE, "mart_ce_aggregati")
df_rg = require_mart(SLUG_RG, "mart_rg_contributi_lavoratori")

anni = sorted(df_m["anno"].unique(), reverse=True)
anno = st.selectbox("Anno di riferimento", anni, key="bil_anno")

# Etichette leggibili per le missioni COFOG
_MISSIONI_LABEL = {
    "Politiche previdenziali (025)": "Previdenza",
    "Diritti sociali, politiche sociali e famiglia (024)": "Diritti sociali e famiglia",
    "Politiche per il lavoro (026)": "Lavoro",
    "Servizi per conto terzi e partite di giro": "Conto terzi e partite di giro",
    "Servizi istituzionali e generali delle pubbliche amminis": "Servizi istituzionali",
    "Servizi istituzionali e generali delle pubbliche amministrazioni": "Servizi istituzionali",
    "Debiti di finanziamento": "Debiti di finanziamento",
    "Fondi da ripartire": "Fondi da ripartire",
}


def _mld(eur: float | None) -> str:
    if eur is None or pd.isna(eur):
        return "–"
    return f"{eur / 1e9:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ── 1. Missioni COFOG ───────────────────────────────────────────────────────

st.subheader(f"Dove va la spesa {anno}")
m = df_m[df_m["anno"] == anno].copy()
m = m[m["competenza_eur"] > 0]
m["missione_label"] = m["missione"].map(_MISSIONI_LABEL).fillna(m["missione"])
m = m.sort_values("competenza_eur", ascending=False)
tot = float(m["competenza_eur"].sum())
m["pct"] = 100.0 * m["competenza_eur"] / tot

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Spesa competenza totale", f"{_mld(tot)} mld €")
with c2:
    top = m.iloc[0]
    st.metric(f"Missione principale ({top['missione_label']})", f"{_mld(top['competenza_eur'])} mld €")
with c3:
    lavoro = m[m["missione_label"] == "Lavoro"]
    if not lavoro.empty:
        st.metric("Politiche per il lavoro", f"{_mld(float(laboro.iloc[0]['competenza_eur']))} mld €")

chart_m = (
    alt.Chart(m)
    .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
    .encode(
        x=alt.X("competenza_eur:Q", title="Competenza (€)", scale=alt.Scale(type="log")),
        y=alt.Y("missione_label:N", sort="-x", title=None),
        color=alt.Color("missione_label:N", legend=None),
        tooltip=[
            alt.Tooltip("missione_label:N", title="Missione"),
            alt.Tooltip("competenza_eur:Q", title="Competenza €", format=",.0f"),
            alt.Tooltip("pct:Q", title="% spesa", format=".1f"),
        ],
    )
    .properties(height=280)
)
st.altair_chart(chart_m, use_container_width=True)
st.caption("Scala log perché le grandezze variano di 2 ordini. Escluse partite di giro a zero.")

# Trend 2022→2024
st.subheader("Variazione 2022 → 2024")
conf = df_conf[df_conf["variazione_assoluta_eur"].notna()].copy()
conf["missione_label"] = conf["missione"].map(_MISSIONI_LABEL).fillna(conf["missione"])
conf = conf[conf["variazione_pct"].notna()].sort_values("variazione_assoluta_eur", key=abs, ascending=False)

chart_conf = (
    alt.Chart(conf)
    .mark_bar()
    .encode(
        x=alt.X("variazione_pct:Q", title="Variazione % competenza"),
        y=alt.Y("missione_label:N", sort="-x", title=None),
        color=alt.Color(
            "variazione_pct:Q",
            scale=alt.Scale(scheme="redblue", domain=[-50, 50]),
            legend=None,
        ),
        tooltip=[
            alt.Tooltip("missione_label:N", title="Missione"),
            alt.Tooltip("competenza_primo_anno:Q", title="2022 €", format=",.0f"),
            alt.Tooltip("competenza_ultimo_anno:Q", title="2024 €", format=",.0f"),
            alt.Tooltip("variazione_pct:Q", title="%", format=".1f"),
        ],
    )
    .properties(height=260)
)
st.altair_chart(chart_conf, use_container_width=True)

# ── 2. Conto economico ──────────────────────────────────────────────────────

st.markdown("---")
st.subheader(f"Conto economico {anno} — chi finanzia, quanto si spende")

ce = df_ce[df_ce["anno"] == anno].copy()
# mart_ce_aggregati è già filtrato su fonte=generale (vedi SQL)
ce_gen = ce


def _ce_val(pattern: str) -> float | None:
    row = ce_gen[ce_gen["voce"].str.contains(pattern, case=False, na=False)]
    if row.empty:
        return None
    return float(row.iloc[0]["importo_eur"])


contrib = _ce_val(r"^Aliquote contributive")
trasf = _ce_val(r"^Trasferimenti da parte dello Stato")
spese = _ce_val(r"^Spese per prestazioni$")

k1, k2, k3 = st.columns(3)
with k1:
    st.metric("Entrate contributive", f"{_mld(contrib)} mld €")
with k2:
    st.metric("Trasferimenti dallo Stato", f"{_mld(trasf)} mld €")
with k3:
    st.metric("Spese per prestazioni", f"{_mld(abs(spese) if spese else None)} mld €")

if contrib and trasf:
    quota_stato = 100.0 * trasf / (contrib + trasf)
    st.progress(min(quota_stato / 100.0, 1.0), text=f"Quota Stato sulle entrate correnti principali: **{quota_stato:.0f}%**")
    st.caption(
        "Il bilancio INPS non è autosufficiente: una parte rilevante di "
        "famiglia, assistenza e previdenza è finanziata dalla fiscalità generale."
    )

# ── 3. Rendiconto gestionale — contributi per tipologia ─────────────────────

st.markdown("---")
st.subheader(f"Contributi per tipologia di assicurato {anno}")
st.caption(
    "Capitoli 1E1* del rendiconto gestionale — accertato. "
    "Il dettaglio per categoria di lavoratore non esiste negli Osservatori."
)

rg = df_rg[df_rg["anno"] == anno].copy()
rg = rg.sort_values("importo_esercizio_eur", ascending=False).head(12)

# Etichette corte per i capitoli principali
def _contrib_label(denom: str) -> str:
    d = (denom or "").upper()
    if "DENUNCE" in d and "DIPENDENTI" in d:
        return "Dipendenti privati (denunce)"
    if "INPDAP" in d or "AMMINISTRAZIONE PUBBLICA" in d:
        return "Ex-INPDAP (pubblico)"
    if "COMMERCIAL" in d:
        return "Commercianti"
    if "ARTIGIAN" in d:
        return "Artigiani"
    if "TUTELA PREVIDENZIALE" in d or "GESTIONE SEPARATA" in d or "LAVORO AUTONOMO" in d:
        return "Gestione separata"
    if "OPERAI AGRICOLI" in d:
        return "Operai agricoli"
    if "COLTIVATORI" in d or "MEZZADR" in d:
        return "Coltivatori diretti"
    if "DOMESTIC" in d:
        return "Lavoratori domestici"
    if "ENPALS" in d or "SPETTACOLO" in d:
        return "Spettacolo/sport"
    return (denom or "")[:50] + "…"


rg["voce_label"] = rg["denominazione"].map(_contrib_label)
# Dedup etichette: tieni la riga più grande
rg = rg.sort_values("importo_esercizio_eur", ascending=False).drop_duplicates("voce_label", keep="first")

chart_rg = (
    alt.Chart(rg)
    .mark_bar(cornerRadiusEnd=3)
    .encode(
        x=alt.X("importo_esercizio_eur:Q", title="Accertato (€)"),
        y=alt.Y("voce_label:N", sort="-x", title=None),
        color=alt.Color("importo_esercizio_eur:Q", scale=alt.Scale(scheme="blues"), legend=None),
        tooltip=[
            alt.Tooltip("voce_label:N", title="Capitolo"),
            alt.Tooltip("importo_esercizio_eur:Q", title="Accertato €", format=",.0f"),
        ],
    )
    .properties(height=360)
)
st.altair_chart(chart_rg, use_container_width=True)

with st.expander("Nota metodologica"):
    st.markdown(
        "- **Missioni / CE**: file multi-anno CKAN; il 2022 è comparative nei file 2023/2024.\n"
        "- **Gestionale**: solo 2023–2024 (formato moderno); legacy 2014–18 non estratto.\n"
        "- Valori in **euro assoluti** di competenza (missioni) o accertato (gestionale).\n"
        "- Non sommare CE generale + GIAS senza le eliminazioni di consolidamento.\n"
        "- Dati da API open data INPS non documentata come gli Osservatori: vedi NOTE.md del repo."
    )
