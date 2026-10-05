#!/usr/bin/env python3
"""
Open INPS · Dashboard Streamlit
Intelligence sui dati INPS: pensioni, lavoro, welfare.

Pattern: lab-ops/standards/dashboard.md
"""

import streamlit as st
from lab_connectors.branding import apply_branding

st.set_page_config(
    page_title="Open INPS · Dashboard",
    page_icon="🇮🇹",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_branding(
    repo_name="open-inps",
    repo_url="https://github.com/dataciviclab/open-inps",
)

pages = {
    "": [
        st.Page("pages/01_Panoramica.py", title="Panoramica", icon="📊", default=True),
    ],
    "Analisi": [
        st.Page("pages/02_Genere.py", title="Genere", icon="⚖️"),
        st.Page("pages/03_Territorio.py", title="Territorio", icon="🗺️"),
    ],
    "Deep dive": [
        st.Page("pages/04_Pensioni.py", title="Pensioni", icon="🏦"),
        st.Page("pages/05_Lavoro.py", title="Lavoro", icon="💼"),
        st.Page("pages/07_Welfare.py", title="Welfare", icon="🏛️"),
    ],
    "Strumenti": [
        st.Page("pages/08_SQL.py", title="Query SQL", icon="🧪"),
    ],
}

pg = st.navigation(pages, position="sidebar")
pg.run()
