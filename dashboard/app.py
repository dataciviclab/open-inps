#!/usr/bin/env python3
"""Open INPS · Dashboard Streamlit"""

import streamlit as st

st.set_page_config(
    page_title="Open INPS · Dashboard",
    page_icon="🇮🇹",
    layout="wide",
    initial_sidebar_state="expanded",
)

pages = {
    "": [
        st.Page("pages/01_Panoramica.py", title="Panoramica", icon="📊", default=True),
    ],
    "Analisi": [
        st.Page("pages/02_Genere.py", title="Genere", icon="⚖️"),
        st.Page("pages/03_Territorio.py", title="Territorio", icon="🗺️"),
    ],
    "Deep Dive": [
        st.Page("pages/04_Pensioni.py", title="Pensioni", icon="🏦"),
        st.Page("pages/05_Lavoro.py", title="Lavoro", icon="💼"),
    ],
    "Esplora": [
        st.Page("pages/06_Dati.py", title="Tabelle", icon="📋"),
    ],
}

st.sidebar.markdown("---")
st.sidebar.caption("Dati: INPS Osservatori Statistici")
st.sidebar.caption("[dataciviclab/open-inps](https://github.com/dataciviclab/open-inps)")

pg = st.navigation(pages, position="sidebar")
pg.run()
