# app.py
import streamlit as st
from streamlit_folium import st_folium

from config import APP_TITLE, APP_ICON, APP_LAYOUT, COL
from config import APP_TITLE, APP_ICON, APP_LAYOUT
from utils.data_loader import load_data, get_kpis
from components.filters import render_filters
from components.map import create_folium_map

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=APP_LAYOUT,
    initial_sidebar_state="expanded",
)

# CSS
st.markdown("""
<style>
  [data-testid="stMetric"] {
    background:#f8f9fa;
    border-radius:10px;
    padding:10px;
    border-left:4px solid #0f3460;
  }
</style>
""", unsafe_allow_html=True)

st.title(f"{APP_ICON} {APP_TITLE}")
st.caption("Niger – Mini-grid viability webmap ")

# Load data (cached)
df = load_data()

# Filters (Apply button prevents constant rerun)
filtered_df, color_by, size_by, map_style, max_points, show_popups = render_filters(df)

# KPIs on full filtered data
kpis = get_kpis(filtered_df)

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("🏘️ Sites",         f"{kpis['total_sites']:,}")
c2.metric("👥 Population",    f"{kpis['total_pop']:,}")
c3.metric("⚡ Avg demand",    f"{kpis['avg_demand']:.1f} kWh/d")
c4.metric("🔌 Avg conn.",     f"{kpis['avg_connections']:.0f}")
c5.metric("🏆 Avg score",     f"{kpis['avg_score']:.1f}/100")
c6.metric("⚠️ High risk",     f"{kpis['high_risk_pct']:.1f}%")

st.divider()

tab_map, tab_data = st.tabs(["🗺️ Map", "📋 Data"])

# MAP TAB
with tab_map:
    if filtered_df.empty:
        st.warning("⚠️ No sites match your current filters.")
    else:
        m, n_drawn = create_folium_map(
            filtered_df,
            color_by=color_by,
            size_by=size_by,
            map_style=map_style,
            max_points=max_points,
            show_popups=show_popups,
        )

        st.caption(
            f"🗺️ Drawing **{n_drawn:,}** of **{len(filtered_df):,}** filtered sites | "
            f"Colored by **{color_by}** | "
            f"Sized by **{size_by}**"
        )

        st_folium(
            m,
            height=650,
            width=None,
            returned_objects=[],
        )

# DATA TAB
with tab_data:
    st.subheader("Filtered data table")

    key_cols = [
        COL["name"] if COL["name"] in filtered_df.columns else None,
        COL["region"] if COL["region"] in filtered_df.columns else None,
        COL["dept"] if COL["dept"] in filtered_df.columns else None,
        COL["pop"] if COL["pop"] in filtered_df.columns else None,
        COL["connections"] if COL["connections"] in filtered_df.columns else None,
        COL["demand"] if COL["demand"] in filtered_df.columns else None,
        COL["risk"] if COL["risk"] in filtered_df.columns else None,
        "Score_Viabilité",
        "Viabilité_Classe",
    ]
    key_cols = [c for c in key_cols if c and c in filtered_df.columns]

    col_a, col_b = st.columns([4, 1])
    with col_b:
        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download CSV",
            data=csv,
            file_name="vida_niger_filtered.csv",
            mime="text/csv",
        )

    st.dataframe(
        filtered_df[key_cols]
          .sort_values("Score_Viabilité", ascending=False)
          .reset_index(drop=True),
        height=500,
    )