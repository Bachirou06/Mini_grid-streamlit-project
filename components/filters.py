# components/filters.py
import streamlit as st
import pandas as pd
from config import COLUMNS


def render_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render sidebar filters and return filtered dataframe"""

    st.sidebar.title("🔍 Filtres")

    filtered_df = df.copy()

    # ---- Region Filter ----
    st.sidebar.subheader("📍 Localisation")

    if "Région" in df.columns:
        regions = ["Toutes"] + sorted(df["Région"].dropna().unique().tolist())
        selected_region = st.sidebar.selectbox("Région", regions)
        if selected_region != "Toutes":
            filtered_df = filtered_df[filtered_df["Région"] == selected_region]

    if "Départment" in df.columns:
        depts = ["Tous"] + sorted(
            filtered_df["Départment"].dropna().unique().tolist()
        )
        selected_dept = st.sidebar.selectbox("Département", depts)
        if selected_dept != "Tous":
            filtered_df = filtered_df[filtered_df["Départment"] == selected_dept]

    # ---- Energy Filter ----
    st.sidebar.subheader("⚡ Énergie")

    if "Nombre estimé de connexions" in df.columns:
        min_conn = int(df["Nombre estimé de connexions"].min())
        max_conn = int(df["Nombre estimé de connexions"].max())
        conn_range = st.sidebar.slider(
            "Connexions estimées",
            min_conn, max_conn,
            (min_conn, max_conn)
        )
        filtered_df = filtered_df[
            (filtered_df["Nombre estimé de connexions"] >= conn_range[0]) &
            (filtered_df["Nombre estimé de connexions"] <= conn_range[1])
        ]

    if "Demande énergétique estimée [kWh/day]" in df.columns:
        min_d = float(df["Demande énergétique estimée [kWh/day]"].min())
        max_d = float(df["Demande énergétique estimée [kWh/day]"].max())
        demand_range = st.sidebar.slider(
            "Demande énergétique (kWh/day)",
            min_d, max_d,
            (min_d, max_d)
        )
        filtered_df = filtered_df[
            (filtered_df["Demande énergétique estimée [kWh/day]"] >= demand_range[0]) &
            (filtered_df["Demande énergétique estimée [kWh/day]"] <= demand_range[1])
        ]

    # ---- Security Filter ----
    st.sidebar.subheader("🛡️ Sécurité")

    if "Risque de sécurité" in df.columns:
        risk_levels = df["Risque de sécurité"].dropna().unique().tolist()
        selected_risks = st.sidebar.multiselect(
            "Niveau de risque",
            risk_levels,
            default=risk_levels
        )
        if selected_risks:
            filtered_df = filtered_df[
                filtered_df["Risque de sécurité"].isin(selected_risks)
            ]

    # ---- Viability Score ----
    st.sidebar.subheader("🏆 Score de Viabilité")

    score_range = st.sidebar.slider(
        "Score minimum",
        0, 100,
        (0, 100)
    )
    filtered_df = filtered_df[
        (filtered_df["Score_Viabilité"] >= score_range[0]) &
        (filtered_df["Score_Viabilité"] <= score_range[1])
    ]

    # ---- Map Options ----
    st.sidebar.subheader("🗺️ Options Carte")

    color_by = st.sidebar.selectbox(
        "Colorier par",
        ["Score_Viabilité", "Risque de sécurité",
         "Éclairage nocturne [%]", "Population"]
    )

    map_style = st.sidebar.selectbox(
        "Style de carte",
        ["OpenStreetMap", "Satellite", "Terrain", "Dark"]
    )

    # Results count
    st.sidebar.markdown("---")
    st.sidebar.metric("Sites affichés", len(filtered_df))

    return filtered_df, color_by, map_style