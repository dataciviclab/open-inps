#!/usr/bin/env python3
"""Open INPS · Dashboard Streamlit"""

import streamlit as st
from lab_connectors.dashboard import DashboardConfig, run_dashboard

config = DashboardConfig(
    title="Open INPS · Dashboard",
    icon="🇮🇹",
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
    "Deep Dive": [
        st.Page("pages/04_Pensioni.py", title="Pensioni", icon="🏦"),
        st.Page("pages/05_Lavoro.py", title="Lavoro", icon="💼"),
    ],
    "Esplora": [
        st.Page("pages/06_Dati.py", title="Tabelle", icon="📋"),
    ],
}

run_dashboard(config, pages)
