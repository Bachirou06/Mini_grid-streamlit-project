# app.py
import streamlit as st
import pandas as pd
from components.map import create_map
from components.filters import render_filters
from components.charts import render_charts
from utils.data_loader import load_data, get_summary_stats
from streamlit_folium import st_folium
from config import APP_TITLE, APP_ICON, APP_LAYOUT

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=APP_LAYOUT,
    initial_sidebar_state="expanded"
)

# ===================== CSS =====================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2c3e50, #3498db);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-card {
        background: #f8f9fa;
        border-left: 4px solid #3498db;
        padding: 15px;
        border-radius: 5px;
    }
    .stMetric {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ===================== HEADER =====================
st.markdown(f"""
<div class="main-header">
    <h1>⚡ {APP_TITLE}</h1>
    <p>Analyse de la viabilité des mini-réseaux électriques</p>
</div>
""", unsafe_allow_html=True)

# ===================== LOAD DATA =====================
try:
    df = load_data()
    st.success("✅ Données chargées avec succès!")
except Exception as e:
    st.error(f"❌ Erreur de chargement: {e}")
    st.stop()

# ===================== SUMMARY STATS =====================
stats = get_summary_stats(df)

# ===================== SIDEBAR FILTERS =====================
filtered_df, color_by, map_style = render_filters(df)

# ===================== KPI METRICS =====================
st.subheader("📊 Indicateurs Clés")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "🏘️ Sites Analysés",
        stats["total_sites"]
    )
with col2:
    st.metric(
        "👥 Population Totale",
        f"{stats['total_population']:,.0f}"
    )
with col3:
    st.metric(
        "⚡ Connexions Moy.",
        f"{stats['avg_connections']:.0f}"
    )
with col4:
    st.metric(
        "🔋 Demande Moy.",
        f"{stats['avg_demand']:.1f} kWh/j"
    )
with col5:
    st.metric(
        "🗺️ Régions",
        stats["regions"]
    )

st.markdown("---")

# ===================== MAP =====================
st.subheader("🗺️ Carte Interactive")

if len(filtered_df) > 0:
    folium_map = create_map(filtered_df, color_by, map_style)
    map_data = st_folium(
        folium_map,
        width=None,
        height=600,
        returned_objects=["last_object_clicked"]
    )

    # Show clicked site details
    if map_data["last_object_clicked"]:
        st.info("📍 Cliquez sur un marqueur pour voir les détails")
else:
    st.warning("⚠️ Aucun site ne correspond aux filtres sélectionnés")

st.markdown("---")

# ===================== CHARTS =====================
st.subheader("📈 Analyses et Statistiques")
render_charts(filtered_df)

st.markdown("---")

# ===================== DATA TABLE =====================
st.subheader("📋 Tableau des Données")

col1, col2 = st.columns([3, 1])
with col2:
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Télécharger CSV",
        csv,
        "vida_filtered.csv",
        "text/csv"
    )

st.dataframe(
    filtered_df,
    use_container_width=True,
    height=400
)