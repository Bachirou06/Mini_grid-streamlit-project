import streamlit as st
from streamlit_folium import st_folium

from config import APP_TITLE, APP_ICON, APP_LAYOUT, ENABLE_CHARTS
from utils.data_loader import load_data, get_kpis
from components.filters import render_filters
from components.map import create_map
from config import ENABLE_CHARTS
if ENABLE_CHARTS:
    from components.charts import render_charts


st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=APP_LAYOUT,
    initial_sidebar_state="expanded",
)

st.title(f"{APP_ICON} {APP_TITLE}")
st.caption("Plan B: app loads pre-cleaned parquet (no upload).")

# Load data
try:
    df = load_data()
except Exception as e:
    st.error(str(e))
    st.stop()

# Filters
filtered_df, color_by, size_by, map_style = render_filters(df)

# KPIs
kpis = get_kpis(filtered_df)
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Sites", f"{kpis['total_sites']:,}")
c2.metric("Population", f"{kpis['total_pop']:,}")
c3.metric("Avg demand", f"{kpis['avg_demand']:.1f}")
c4.metric("Avg connections", f"{kpis['avg_connections']:.0f}")
c5.metric("Avg score", f"{kpis['avg_score']:.1f}/100")
c6.metric("High risk %", f"{kpis['high_risk_pct']:.1f}%")

st.divider()

# Tabs
if ENABLE_CHARTS:
    tab_map, tab_charts, tab_data = st.tabs(["Map", "Charts", "Data"])
else:
    tab_map, tab_data = st.tabs(["Map", "Data"])

with tab_map:
    if filtered_df.empty:
        st.warning("No sites match your filters.")
    else:
        m = create_map(filtered_df, color_by=color_by, size_by=size_by, map_style=map_style)
        st_folium(m, width=None, height=650)

if ENABLE_CHARTS:
    with tab_charts:
        if filtered_df.empty:
            st.warning("No data to chart (adjust filters).")
        else:
            render_charts(filtered_df)

with tab_data:
    st.dataframe(filtered_df, use_container_width=True, height=520)
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered CSV", csv, "vida_filtered.csv", "text/csv")