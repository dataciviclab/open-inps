"""Query SQL — Query libera sui dati INPS."""

import duckdb
import streamlit as st
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
MART_DIR = REPO_ROOT / "out" / "data" / "mart"

st.title("🧪 Query SQL")
st.markdown("Esegui query SQL direttamente sui mart parquet.")

# ── Schema disponibile ──────────────────────────────────────────────────────

st.subheader("📋 Tabelle disponibili")

with st.expander("Vedi schema"):
    for ds_dir in sorted(MART_DIR.iterdir()):
        if not ds_dir.is_dir():
            continue
        for year_dir in sorted(ds_dir.iterdir()):
            if not year_dir.is_dir():
                continue
            for pq in sorted(year_dir.glob("*.parquet")):
                table_name = f"{ds_dir.name}/{year_dir.name}/{pq.stem}"
                try:
                    con = duckdb.connect()
                    desc = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{pq}')").fetchall()
                    cols = ", ".join(f"{r[0]} {r[1]}" for r in desc)
                    st.code(f"{table_name}: {cols}", language="sql")
                except Exception:
                    pass

# ── Query editor ────────────────────────────────────────────────────────────

st.subheader("📝 Scrivi la tua query")

default_query = """-- Esempio: pensioni per sesso nel 2026
SELECT anno, sesso, metrica, valore
FROM read_parquet('{MART_DIR}/inps_analisi/2026/mart_nazionale.parquet')
WHERE anno = 2026 AND sesso != 'Totale'
ORDER BY metrica, sesso
"""

query = st.text_area(
    "SQL",
    value=default_query.replace("{MART_DIR}", str(MART_DIR)),
    height=200,
    key="sql_query",
)

if st.button("Esegui", key="sql_run"):
    if not query.strip():
        st.warning("Inserisci una query SQL.")
    else:
        try:
            con = duckdb.connect()
            result = con.execute(query).df()
            st.success(f"{len(result)} righe")
            st.dataframe(result, use_container_width=True)
        except Exception as e:
            st.error(f"Errore: {e}")
