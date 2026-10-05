"""Genere — Gap di genere su lavoro, welfare e pensioni."""

import altair as alt
import pandas as pd
import streamlit as st
from sources import METRICHE, fmt_num, require_compose

st.title("⚖️ Genere")
st.markdown(
    "**Il paradosso**: le donne hanno più pensioni ma meno lavoro. "
    "Gap = (Femmine − Maschi) / Maschi."
)

df = require_compose("mart_nazionale")
df_bench = require_compose("mart_benchmark")

# Solo metriche con split M/F reale (no Totale-only come CIG/AU)
METRICHE_SESSO = [
    "rapporti_lavoro",
    "cessazioni_lavoro",
    "pensioni_vigenti",
    "pensioni_liquidate",
    "pensionamento_flussi",
    "lavoratori_privati",
    "lavoratori_redditi",
    "naspi",
    "dis_coll",
]

c1, c2 = st.columns(2)
with c1:
    anni_ok = sorted(
        df[(df["metrica"].isin(METRICHE_SESSO)) & (df["sesso"].isin(["Maschi", "Femmine"]))][
            "anno"
        ].unique(),
        reverse=True,
    )
    anno = st.selectbox("Anno", anni_ok, key="gen_anno")
with c2:
    st.caption("Finestra utile tipica: **2020–2023** (tutte le metriche M/F).")


def _mf(metrica: str) -> pd.DataFrame:
    d = df[(df["anno"] == anno) & (df["metrica"] == metrica)]
    return d[d["sesso"].isin(["Maschi", "Femmine"])][["sesso", "valore"]]


def _gap(metrica: str) -> float | None:
    d = _mf(metrica)
    if d.empty:
        return None
    m = float(d[d["sesso"] == "Maschi"]["valore"].sum())
    f = float(d[d["sesso"] == "Femmine"]["valore"].sum())
    if m <= 0:
        return None
    return (f - m) / m * 100


# ── Gap sintetico benchmark ─────────────────────────────────────────────────

st.subheader(f"Gap di genere — {anno}")

bench_yr = df_bench[df_bench["anno"] == anno]
if not bench_yr.empty:
    b = bench_yr.iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        val = b.get("gap_genere_assunzioni_pct")
        st.metric("Assunzioni", f"+{val:.1f}%" if pd.notna(val) else "–", help="+ = più uomini")
    with c2:
        val = b.get("gap_genere_cessazioni_pct")
        st.metric("Cessazioni", f"+{val:.1f}%" if pd.notna(val) else "–", help="+ = più uomini")
    with c3:
        val = b.get("gap_genere_pensioni_pct")
        st.metric("Pensioni", f"+{val:.1f}%" if pd.notna(val) else "–", help="+ = più donne")
    with c4:
        val = b.get("gap_genere_naspi_pct")
        st.metric("NASpI", f"+{val:.1f}%" if pd.notna(val) else "–", help="+ = più donne")
    st.info(
        "Assunzioni/Cessazioni: + = più uomini. "
        "Pensioni/NASP I: + = più donne. "
        "DIS-COLL nella pratica è a maggioranza femminile."
    )

# ── Tabella gap tutte le metriche M/F ──────────────────────────────────────

st.subheader("Tutte le metriche con split M/F")

rows = []
for met in METRICHE_SESSO:
    d = _mf(met)
    if d.empty:
        continue
    m = float(d[d["sesso"] == "Maschi"]["valore"].sum())
    f = float(d[d["sesso"] == "Femmine"]["valore"].sum())
    gap = (f - m) / m * 100 if m else None
    rows.append(
        {
            "Metrica": METRICHE.get(met, met),
            "Maschi": m,
            "Femmine": f,
            "Gap %": round(gap, 1) if gap is not None else None,
            "Chi ha di più": "Donne" if (gap or 0) > 0 else "Uomini",
        }
    )

if rows:
    df_gap = pd.DataFrame(rows).sort_values("Gap %")
    df_gap["Maschi"] = df_gap["Maschi"].map(fmt_num)
    df_gap["Femmine"] = df_gap["Femmine"].map(fmt_num)
    st.dataframe(df_gap, use_container_width=True, hide_index=True)

    # Barre gap (valori grezzi non servono più nella tabella formattata)
    df_bar = pd.DataFrame(rows).sort_values("Gap %")
    chart = (
        alt.Chart(df_gap)
        .mark_bar()
        .encode(
            x=alt.X("Gap %:Q", title="Gap F/M (%)"),
            y=alt.Y("Metrica:N", sort="-x", title=""),
            color=alt.Color(
                "Chi ha di più:N",
                scale=alt.Scale(domain=["Donne", "Uomini"], range=["#ec4899", "#2563eb"]),
            ),
            tooltip=["Metrica", "Maschi", "Femmine", "Gap %"],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, use_container_width=True)

# ── Trend gap ───────────────────────────────────────────────────────────────

st.markdown("---")
st.subheader("📈 Evoluzione del gap nel tempo")

met = st.selectbox(
    "Metrica",
    METRICHE_SESSO,
    format_func=lambda x: METRICHE.get(x, x),
    key="gen_trend_met",
)
df_t = df[(df["metrica"] == met) & (df["sesso"].isin(["Maschi", "Femmine"]))]
pivot_t = (
    df_t.pivot_table(index="anno", columns="sesso", values="valore", aggfunc="sum")
    .reset_index()
    .dropna(subset=["Maschi", "Femmine"])
)
if not pivot_t.empty:
    pivot_t["gap%"] = ((pivot_t["Femmine"] - pivot_t["Maschi"]) / pivot_t["Maschi"] * 100).round(1)

    # zero line + serie
    base = alt.Chart(pivot_t).mark_rule(color="#94a3b8", strokeDash=[4, 4]).encode(y=alt.datum(0))
    line = (
        alt.Chart(pivot_t)
        .mark_line(point=True, color="#d97706", strokeWidth=2)
        .encode(
            x=alt.X("anno:O", title="Anno"),
            y=alt.Y("gap%:Q", title="Gap F/M (%)"),
            tooltip=["anno", alt.Tooltip("gap%", format="+.1f")],
        )
    )
    st.altair_chart((base + line).properties(height=280), use_container_width=True)

    if METRICHE.get(met, "").lower().find("cessaz") >= 0 or met == "cessazioni_lavoro":
        st.caption(
            "Sulle cessazioni il gap è tipicamente più contenuto che sulle "
            "assunzioni: le donne entrano meno ma, quando entrano, restano."
        )
    if met.startswith("pensioni"):
        st.caption(
            "Sulle pensioni il gap è positivo (più donne): riflette la maggiore "
            "aspettativa di vita e la minore carriera contributiva media."
        )
