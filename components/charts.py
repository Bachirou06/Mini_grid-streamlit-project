# components/charts.py
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st


def render_charts(df: pd.DataFrame):
    """Render all charts"""

    tab1, tab2, tab3, tab4 = st.tabs([
        "⚡ Énergie",
        "👥 Population",
        "💰 Agriculture",
        "🛡️ Sécurité"
    ])

    with tab1:
        render_energy_charts(df)

    with tab2:
        render_population_charts(df)

    with tab3:
        render_agriculture_charts(df)

    with tab4:
        render_security_charts(df)


def render_energy_charts(df: pd.DataFrame):
    col1, col2 = st.columns(2)

    with col1:
        if "Demande énergétique estimée [kWh/day]" in df.columns:
            fig = px.histogram(
                df,
                x="Demande énergétique estimée [kWh/day]",
                nbins=30,
                title="Distribution de la Demande Énergétique",
                color_discrete_sequence=["#3498db"],
                labels={"Demande énergétique estimée [kWh/day]": "kWh/day"}
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "Score_Viabilité" in df.columns and "Région" in df.columns:
            fig = px.box(
                df,
                x="Région",
                y="Score_Viabilité",
                title="Score de Viabilité par Région",
                color="Région"
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

    if "Distance au réseau existant [km]" in df.columns and \
       "Demande énergétique estimée [kWh/day]" in df.columns:
        fig = px.scatter(
            df,
            x="Distance au réseau existant [km]",
            y="Demande énergétique estimée [kWh/day]",
            size="Nombre estimé de connexions",
            color="Score_Viabilité",
            hover_name="Nom",
            title="Distance au Réseau vs Demande Énergétique",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig, use_container_width=True)


def render_population_charts(df: pd.DataFrame):
    col1, col2 = st.columns(2)

    with col1:
        if "Région" in df.columns and "Population" in df.columns:
            pop_region = df.groupby("Région")["Population"].sum().reset_index()
            fig = px.bar(
                pop_region,
                x="Région",
                y="Population",
                title="Population par Région",
                color="Population",
                color_continuous_scale="Blues"
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        building_cols = [
            "Bâtiments grands",
            "Bâtiments moyens",
            "Bâtiments petits",
            "Structures très petites"
        ]
        existing_cols = [c for c in building_cols if c in df.columns]

        if existing_cols:
            totals = df[existing_cols].sum()
            fig = px.pie(
                values=totals.values,
                names=totals.index,
                title="Répartition des Types de Bâtiments"
            )
            st.plotly_chart(fig, use_container_width=True)


def render_agriculture_charts(df: pd.DataFrame):
    col1, col2 = st.columns(2)

    with col1:
        if "Région" in df.columns and \
           "Valeur totale des cultures [$/year]" in df.columns:
            agr_region = df.groupby("Région")[
                "Valeur totale des cultures [$/year]"
            ].sum().reset_index()
            fig = px.bar(
                agr_region,
                x="Région",
                y="Valeur totale des cultures [$/year]",
                title="Valeur Agricole par Région ($)",
                color="Valeur totale des cultures [$/year]",
                color_continuous_scale="Greens"
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "Rendement total des cultures [kg/ha]" in df.columns and \
           "Superficie agricole totale [ha]" in df.columns:
            fig = px.scatter(
                df,
                x="Superficie agricole totale [ha]",
                y="Rendement total des cultures [kg/ha]",
                color="Région",
                hover_name="Nom",
                title="Superficie vs Rendement Agricole"
            )
            st.plotly_chart(fig, use_container_width=True)


def render_security_charts(df: pd.DataFrame):
    col1, col2 = st.columns(2)

    with col1:
        if "Risque de sécurité" in df.columns:
            risk_count = df["Risque de sécurité"].value_counts().reset_index()
            risk_count.columns = ["Risque", "Nombre"]
            fig = px.bar(
                risk_count,
                x="Risque",
                y="Nombre",
                title="Distribution des Niveaux de Risque",
                color="Risque",
                color_discrete_map={
                    "Faible": "green",
                    "Moyen": "orange",
                    "Élevé": "red",
                    "Très élevé": "darkred"
                }
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "Incidents dans un rayon de 50 km" in df.columns and \
           "Région" in df.columns:
            incidents_region = df.groupby("Région")[
                "Incidents dans un rayon de 50 km"
            ].sum().reset_index()
            fig = px.bar(
                incidents_region,
                x="Région",
                y="Incidents dans un rayon de 50 km",
                title="Incidents par Région (50 km)",
                color="Incidents dans un rayon de 50 km",
                color_continuous_scale="Reds"
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)