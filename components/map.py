import folium
import pandas as pd
import numpy as np
from folium import plugins

from config import (
    COL, MAP_CENTER, MAP_ZOOM, MAP_TILES, MAP_TILES_ATTR,
    RISK_COLORS
)


def score_color(v: float) -> str:
    if v >= 75: return "#1a9850"
    if v >= 50: return "#91cf60"
    if v >= 25: return "#fee08b"
    return "#d73027"


def get_color(row: pd.Series, color_by: str, df: pd.DataFrame) -> str:
    val = row.get(color_by, None)
    if pd.isna(val):
        return "#9e9e9e"

    if color_by == "Score_Viabilité":
        try:
            return score_color(float(val))
        except Exception:
            return "#9e9e9e"

    if color_by == COL["risk"]:
        return RISK_COLORS.get(str(val), "#9e9e9e")

    # Numeric gradients (simple quantile-ish scaling)
    try:
        v = float(val)
        vmax = float(pd.to_numeric(df[color_by], errors="coerce").max())
        r = (v / vmax) if vmax and vmax > 0 else 0.0
        if r >= 0.75: return "#08306b"
        if r >= 0.50: return "#2171b5"
        if r >= 0.25: return "#6baed6"
        return "#c6dbef"
    except Exception:
        return "#3498db"


def get_radius(row: pd.Series, size_by: str, df: pd.DataFrame) -> float:
    if size_by == "Fixed size":
        return 7

    try:
        v = row.get(size_by, np.nan)
        if pd.isna(v):
            return 5
        vmax = pd.to_numeric(df[size_by], errors="coerce").max()
        r = float(v) / float(vmax) if vmax and vmax > 0 else 0.0
        return max(4, min(20, 4 + r * 16))
    except Exception:
        return 7


def popup_html(row: pd.Series) -> str:
    name = row.get(COL["name"], "Unknown")
    region = row.get(COL["region"], "N/A")
    dept = row.get(COL["dept"], "N/A")
    score = row.get("Score_Viabilité", 0)

    pop = row.get(COL["pop"], "N/A")
    demand = row.get(COL["demand"], "N/A")
    conn = row.get(COL["connections"], "N/A")
    pv = row.get(COL["pv"], "N/A")
    risk = row.get(COL["risk"], "N/A")

    return f"""
    <div style="font-family:Arial; width:320px;">
      <h4 style="margin:0 0 8px 0;">{name}</h4>
      <b>Location</b><br>
      Region: {region}<br>
      Department: {dept}<br><br>

      <b>Mini-grid viability</b><br>
      Score: <b>{score:.1f}/100</b><br>
      Population: {pop}<br>
      Connections: {conn}<br>
      Demand: {demand} kWh/day<br>
      PV potential: {pv} kWh/kWp<br><br>

      <b>Security</b><br>
      Risk: {risk}<br>
    </div>
    """


def create_map(df: pd.DataFrame, color_by: str, size_by: str, map_style: str) -> folium.Map:
    tile = MAP_TILES.get(map_style, "OpenStreetMap")
    attr = MAP_TILES_ATTR.get(map_style, None)

    m = folium.Map(
        location=MAP_CENTER,
        zoom_start=MAP_ZOOM,
        tiles=tile,
        attr=attr,
    )

    cluster = plugins.MarkerCluster(name="VIDA sites").add_to(m)

    for _, row in df.iterrows():
        lat = row.get(COL["lat"])
        lon = row.get(COL["lon"])
        if pd.isna(lat) or pd.isna(lon):
            continue

        color = get_color(row, color_by, df)
        radius = get_radius(row, size_by, df)

        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            weight=1,
            tooltip=str(row.get(COL["name"], "")),
            popup=folium.Popup(popup_html(row), max_width=360),
        ).add_to(cluster)

    # Optional heatmap based on demand
    if COL["demand"] in df.columns:
        heat = []
        demand_series = pd.to_numeric(df[COL["demand"]], errors="coerce").fillna(0)
        for (lat, lon, w) in zip(df[COL["lat"]], df[COL["lon"]], demand_series):
            if pd.notna(lat) and pd.notna(lon):
                heat.append([lat, lon, float(w)])
        if heat:
            plugins.HeatMap(heat, name="Demand heatmap", radius=18, blur=12, min_opacity=0.3).add_to(m)

    plugins.Fullscreen().add_to(m)
    plugins.MiniMap(toggle_display=True).add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)

    return m