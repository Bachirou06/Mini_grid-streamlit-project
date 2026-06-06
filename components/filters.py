import streamlit as st
import pandas as pd
from config import COL


def render_filters(df: pd.DataFrame):
    st.sidebar.title("Filters")

    filtered = df.copy()

    # Location
    with st.sidebar.expander("Location", expanded=True):
        if COL["region"] in filtered.columns:
            regions = ["All"] + sorted(filtered[COL["region"]].dropna().unique().tolist())
            sel_region = st.selectbox("Region", regions)
            if sel_region != "All":
                filtered = filtered[filtered[COL["region"]] == sel_region]

        if COL["dept"] in filtered.columns:
            depts = ["All"] + sorted(filtered[COL["dept"]].dropna().unique().tolist())
            sel_dept = st.selectbox("Department", depts)
            if sel_dept != "All":
                filtered = filtered[filtered[COL["dept"]] == sel_dept]

    # Score
    with st.sidebar.expander("Viability score", expanded=True):
        score_range = st.slider("Score range", 0, 100, (0, 100), step=5)
        filtered = filtered[filtered["Score_Viabilité"].between(score_range[0], score_range[1])]

        if "Viabilité_Classe" in filtered.columns:
            classes = [c for c in filtered["Viabilité_Classe"].dropna().unique().tolist()]
            if classes:
                sel_classes = st.multiselect("Class", classes, default=classes)
                if sel_classes:
                    filtered = filtered[filtered["Viabilité_Classe"].isin(sel_classes)]

    # Energy
    with st.sidebar.expander("Energy", expanded=False):
        if COL["connections"] in filtered.columns:
            s = filtered[COL["connections"]].dropna()
            if not s.empty:
                mn, mx = int(s.min()), int(s.max())
                r = st.slider("Connections", mn, mx, (mn, mx))
                filtered = filtered[filtered[COL["connections"]].between(r[0], r[1])]

        if COL["demand"] in filtered.columns:
            s = filtered[COL["demand"]].dropna()
            if not s.empty:
                mn, mx = float(s.min()), float(s.max())
                r = st.slider("Demand (kWh/day)", mn, mx, (mn, mx))
                filtered = filtered[filtered[COL["demand"]].between(r[0], r[1])]

        if COL["dist_grid"] in filtered.columns:
            s = filtered[COL["dist_grid"]].dropna()
            if not s.empty:
                mn, mx = float(s.min()), float(s.max())
                r = st.slider("Distance to grid (km)", mn, mx, (mn, mx))
                filtered = filtered[filtered[COL["dist_grid"]].between(r[0], r[1])]

    # Security
    with st.sidebar.expander("Security", expanded=False):
        if COL["risk"] in filtered.columns:
            levels = df[COL["risk"]].dropna().unique().tolist()
            sel = st.multiselect("Risk level", levels, default=levels)
            if sel:
                filtered = filtered[filtered[COL["risk"]].isin(sel)]

    # Map options
    st.sidebar.markdown("---")
    with st.sidebar.expander("Map options", expanded=True):
        color_by = st.selectbox(
            "Color by",
            ["Score_Viabilité", COL["risk"], COL["pop"], COL["demand"], COL["nightlight"], COL["wealth"]],
        )
        size_by = st.selectbox(
            "Size by",
            [COL["pop"], COL["connections"], COL["demand"], "Fixed size"],
        )
        map_style = st.selectbox(
            "Basemap",
            ["OpenStreetMap", "Satellite", "Terrain", "Dark"],
        )

    st.sidebar.markdown("---")
    st.sidebar.metric("Sites shown", f"{len(filtered):,} / {len(df):,}")

    return filtered, color_by, size_by, map_style