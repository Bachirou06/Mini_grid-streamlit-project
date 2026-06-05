# components/map.py
import folium
import pandas as pd
import numpy as np
from folium import plugins
from streamlit_folium import st_folium
import streamlit as st
from config import MAP_CENTER, MAP_ZOOM, RISK_COLORS


def create_map(df: pd.DataFrame, color_by: str, map_style: str) -> folium.Map:
    """Create main folium map"""

    # Tile styles
    tiles = {
        "OpenStreetMap": "OpenStreetMap",
        "Satellite": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "Terrain": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        "Dark": "CartoDB dark_matter"
    }

    attr = "Esri" if map_style in ["Satellite", "Terrain"] else None

    m = folium.Map(
        location=MAP_CENTER,
        zoom_start=MAP_ZOOM,
        tiles=tiles[map_style],
        attr=attr
    )

    # Add marker cluster
    marker_cluster = plugins.MarkerCluster(name="Sites VIDA").add_to(m)

    # Add markers
    for _, row in df.iterrows():
        color = get_marker_color(row, color_by)
        popup_html = create_popup(row)
        tooltip = create_tooltip(row)

        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=get_marker_size(row),
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=tooltip
        ).add_to(marker_cluster)

    # Add heatmap layer
    add_heatmap(m, df)

    # Add layer control
    folium.LayerControl().add_to(m)

    # Add fullscreen button
    plugins.Fullscreen().add_to(m)

    # Add minimap
    plugins.MiniMap().add_to(m)

    return m


def get_marker_color(row: pd.Series, color_by: str) -> str:
    """Get marker color based on selected column"""

    if color_by == "Risque de sécurité":
        risk = str(row.get("Risque de sécurité", "Faible"))
        return RISK_COLORS.get(risk, "blue")

    elif color_by == "Score_Viabilité":
        score = row.get("Score_Viabilité", 0)
        if score >= 75:
            return "darkgreen"
        elif score >= 50:
            return "green"
        elif score >= 25:
            return "orange"
        else:
            return "red"

    elif color_by == "Éclairage nocturne [%]":
        val = row.get("Éclairage nocturne [%]", 0)
        if val >= 50:
            return "yellow"
        elif val >= 20:
            return "orange"
        else:
            return "darkblue"

    return "blue"


def get_marker_size(row: pd.Series) -> float:
    """Get marker size based on population"""
    pop = row.get("Population", 100)
    if pd.isna(pop):
        return 5
    return max(5, min(20, pop / 500))


def create_popup(row: pd.Series) -> str:
    """Create HTML popup for marker"""
    html = f"""
    <div style="font-family: Arial; width: 300px;">
        <h4 style="color: #2c3e50; border-bottom: 2px solid #3498db;">
            📍 {row.get('Nom', 'Site inconnu')}
        </h4>

        <b>📍 Localisation</b><br>
        Région: {row.get('Région', 'N/A')}<br>
        Département: {row.get('Départment', 'N/A')}<br>
        <br>

        <b>⚡ Énergie</b><br>
        Connexions estimées: {row.get('Nombre estimé de connexions', 'N/A')}<br>
        Demande: {row.get('Demande énergétique estimée [kWh/day]', 'N/A')} kWh/day<br>
        Production PV: {row.get('Production PV potentielle [kWh/kWp]', 'N/A')} kWh/kWp<br>
        <br>

        <b>👥 Population</b><br>
        Population: {row.get('Population', 'N/A')}<br>
        Bâtiments: {row.get('Nombre de bâtiments', 'N/A')}<br>
        <br>

        <b>💰 Économie</b><br>
        Indice richesse: {row.get('Indice de richesse relative', 'N/A')}<br>
        Valeur cultures: {row.get('Valeur totale des cultures [$/year]', 'N/A')} $/year<br>
        <br>

        <b>🛡️ Sécurité</b><br>
        Risque: <span style="color: red;">{row.get('Risque de sécurité', 'N/A')}</span><br>
        <br>

        <b>🏆 Score Viabilité</b><br>
        <div style="background: #3498db; color: white; padding: 5px; border-radius: 5px; text-align: center;">
            {row.get('Score_Viabilité', 0):.1f} / 100
        </div>
    </div>
    """
    return html


def create_tooltip(row: pd.Series) -> str:
    """Create tooltip for marker"""
    return f"""
    🏘️ {row.get('Nom', 'Site inconnu')} |
    👥 Pop: {row.get('Population', 'N/A')} |
    ⚡ Score: {row.get('Score_Viabilité', 0):.0f}/100
    """


def add_heatmap(m: folium.Map, df: pd.DataFrame):
    """Add heatmap layer"""
    heat_data = [
        [row["Latitude"], row["Longitude"],
         row.get("Demande énergétique estimée [kWh/day]", 1)]
        for _, row in df.iterrows()
        if pd.notna(row["Latitude"]) and pd.notna(row["Longitude"])
    ]

    plugins.HeatMap(
        heat_data,
        name="🔥 Carte de chaleur (Demande)",
        radius=15,
        blur=10,
        min_opacity=0.4
    ).add_to(m)