# components/filters.py
import streamlit as st
import pandas as pd
from config import COL


def _safe_minmax(df: pd.DataFrame, col: str):
    if col not in df.columns:
        return None
    s = pd.to_numeric(df[col], errors="coerce").dropna()
    if s.empty:
        return None
    return float(s.min()), float(s.max())


def render_filters(df: pd.DataFrame):
    st.sidebar.title("⚡ Filters")

    with st.sidebar.form("vida_filters_form", clear_on_submit=False):

        # Location
        st.markdown("### 📍 Location")
        regions = ["All"] + sorted(df[COL["region"]].dropna().unique().tolist()) \
            if COL["region"] in df.columns else ["All"]
        sel_region = st.selectbox("Region", regions)

        dept_df = df if sel_region == "All" else df[df[COL["region"]] == sel_region]
        depts = ["All"] + sorted(dept_df[COL["dept"]].dropna().unique().tolist()) \
            if COL["dept"] in dept_df.columns else ["All"]
        sel_dept = st.selectbox("Department", depts)

        # Score
        st.markdown("### 🏆 Viability Score")
        score_range = st.slider("Score range", 0, 100, (0, 100), step=5)

        # Energy
        st.markdown("### ⚡ Energy")
        conn_range = None
        demand_range = None
        dist_grid_range = None

        mm = _safe_minmax(df, COL["connections"])
        if mm:
            mn, mx = int(mm[0]), int(mm[1])
            conn_range = st.slider("Connections", mn, mx, (mn, mx))

        mm = _safe_minmax(df, COL["demand"])
        if mm:
            mn, mx = float(mm[0]), float(mm[1])
            demand_range = st.slider("Demand (kWh/day)", mn, mx, (mn, mx))

        mm = _safe_minmax(df, COL["dist_grid"])
        if mm:
            mn, mx = float(mm[0]), float(mm[1])
            dist_grid_range = st.slider("Distance to grid (km)", mn, mx, (mn, mx))

        # Security
        st.markdown("### 🛡️ Security")
        sel_risk = None
        if COL["risk"] in df.columns:
            order = ["Low", "Medium", "High"]
            all_levels = df[COL["risk"]].dropna().unique().tolist()
            levels = [x for x in order if x in all_levels]
            levels += [x for x in all_levels if x not in levels]
            sel_risk = st.multiselect("Risk level", levels, default=levels)

        # Map options
        st.markdown("### 🗺️ Map Options")
        color_by = st.selectbox(
            "Color by",
            [
                "Score_Viabilité",
                COL["risk"],
                COL["pop"],
                COL["demand"],
                COL["nightlight"],
                COL["wealth"],
            ],
        )
        size_by = st.selectbox(
            "Size by",
            [COL["pop"], COL["connections"], COL["demand"], "Fixed size"],
        )
        map_style = st.selectbox(
            "Basemap",
            ["OpenStreetMap", "Satellite", "Terrain", "Dark"]
        )

        # Performance
        st.markdown("### ⚙️ Performance")
        max_points = st.slider(
            "Max points on map",
            min_value=1000,
            max_value=30000,
            value=10000,
            step=1000,
            help="Higher = more sites visible but slower map"
        )
        show_popups = st.checkbox(
            "Enable popups (click on site)",
            value=True,
            help="Uncheck for faster rendering"
        )

        apply = st.form_submit_button(
            "✅ Apply Filters",
            use_container_width=True
        )

    # store in session_state
    if apply or "f_applied" not in st.session_state:
        st.session_state.f_region = sel_region
        st.session_state.f_dept = sel_dept
        st.session_state.f_score = score_range
        st.session_state.f_conn = conn_range
        st.session_state.f_demand = demand_range
        st.session_state.f_dist_grid = dist_grid_range
        st.session_state.f_risk = sel_risk
        st.session_state.f_color = color_by
        st.session_state.f_size = size_by
        st.session_state.f_style = map_style
        st.session_state.f_max = max_points
        st.session_state.f_popups = show_popups
        st.session_state.f_applied = True

    # apply filters on full df
    filtered = df.copy()

    if COL["region"] in filtered.columns and st.session_state.f_region != "All":
        filtered = filtered[filtered[COL["region"]] == st.session_state.f_region]

    if COL["dept"] in filtered.columns and st.session_state.f_dept != "All":
        filtered = filtered[filtered[COL["dept"]] == st.session_state.f_dept]

    if "Score_Viabilité" in filtered.columns:
        lo, hi = st.session_state.f_score
        filtered = filtered[filtered["Score_Viabilité"].between(lo, hi)]

    if st.session_state.f_conn and COL["connections"] in filtered.columns:
        lo, hi = st.session_state.f_conn
        filtered = filtered[
            pd.to_numeric(filtered[COL["connections"]], errors="coerce").between(lo, hi)
        ]

    if st.session_state.f_demand and COL["demand"] in filtered.columns:
        lo, hi = st.session_state.f_demand
        filtered = filtered[
            pd.to_numeric(filtered[COL["demand"]], errors="coerce").between(lo, hi)
        ]

    if st.session_state.f_dist_grid and COL["dist_grid"] in filtered.columns:
        lo, hi = st.session_state.f_dist_grid
        filtered = filtered[
            pd.to_numeric(filtered[COL["dist_grid"]], errors="coerce").between(lo, hi)
        ]

    if st.session_state.f_risk and COL["risk"] in filtered.columns:
        filtered = filtered[filtered[COL["risk"]].isin(st.session_state.f_risk)]

    st.sidebar.markdown("---")
    st.sidebar.metric(
        "Sites after filters",
        f"{len(filtered):,} / {len(df):,}"
    )

    return (
        filtered,
        st.session_state.f_color,
        st.session_state.f_size,
        st.session_state.f_style,
        st.session_state.f_max,
        st.session_state.f_popups,
    )