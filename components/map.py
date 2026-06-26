# components/map.py
import numpy as np
import pandas as pd
import folium
from folium import plugins
from config import (
    COL, MAP_CENTER, MAP_ZOOM,
    MAP_TILES, MAP_TILES_ATTR,
    RISK_COLORS
)


# ── Color helpers ─────────────────────────────────────────────────────────────
def _score_color(v) -> str:
    try:
        v = float(v)
    except Exception:
        return "#9e9e9e"
    if v >= 75: return "#1a9850"
    if v >= 50: return "#91cf60"
    if v >= 25: return "#fee08b"
    return "#d73027"


def _get_color(row: pd.Series, color_by: str) -> str:
    if color_by == "Score_Viabilité":
        return _score_color(row.get("Score_Viabilité", np.nan))

    if color_by == COL.get("risk"):
        val = str(row.get(COL["risk"], "")).strip()
        return RISK_COLORS.get(val, "#9e9e9e")

    try:
        v = float(row.get(color_by, np.nan))
        if np.isnan(v):
            return "#9e9e9e"
        return "#3498db"
    except Exception:
        return "#3498db"


def _get_radius(row: pd.Series, size_by: str, vmax: float) -> float:
    if size_by == "Fixed size":
        return 6
    try:
        v = float(row.get(size_by, np.nan))
        if np.isnan(v) or vmax <= 0:
            return 4
        r = 4 + (v / vmax) * 10
        return float(max(3, min(16, r)))
    except Exception:
        return 6


# ── Popup builder ─────────────────────────────────────────────────────────────
def _make_popup(row: pd.Series) -> folium.Popup:
    """Lightweight popup HTML."""

    def _v(key, decimals=None):
        col = COL.get(key)
        if not col:
            return "N/A"
        val = row.get(col, None)
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return "N/A"
        if decimals is not None:
            try:
                return f"{float(val):,.{decimals}f}"
            except Exception:
                pass
        return str(val)

    risk_val = _v("risk")
    risk_color = RISK_COLORS.get(risk_val, "#9e9e9e")
    score = row.get("Score_Viabilité", 0)

    try:
        score_f = float(score)
    except Exception:
        score_f = 0.0

    score_color = _score_color(score_f)

    html = f"""
    <div style="font-family:Arial,sans-serif;
                width:260px;font-size:12px;
                border-radius:6px;overflow:hidden;">

      <!-- Header -->
      <div style="background:{score_color};
                  color:white;padding:7px 10px;">
        <b style="font-size:13px;">{_v('name')}</b>
      </div>

      <!-- Body -->
      <div style="padding:8px 10px;
                  border:1px solid #ddd;
                  border-top:none;">

        <table style="width:100%;border-collapse:collapse;
                      font-size:11px;">
          <tr>
            <td style="color:#555;padding:2px 4px;">Region</td>
            <td style="padding:2px 4px;"><b>{_v('region')}</b></td>
          </tr>
          <tr style="background:#f9f9f9;">
            <td style="color:#555;padding:2px 4px;">Department</td>
            <td style="padding:2px 4px;"><b>{_v('dept')}</b></td>
          </tr>
          <tr>
            <td style="color:#555;padding:2px 4px;">Population</td>
            <td style="padding:2px 4px;"><b>{_v('pop', 0)}</b></td>
          </tr>
          <tr style="background:#f9f9f9;">
            <td style="color:#555;padding:2px 4px;">Connections</td>
            <td style="padding:2px 4px;"><b>{_v('connections', 0)}</b></td>
          </tr>
          <tr>
            <td style="color:#555;padding:2px 4px;">Demand</td>
            <td style="padding:2px 4px;"><b>{_v('demand', 1)} kWh/day</b></td>
          </tr>
          <tr style="background:#f9f9f9;">
            <td style="color:#555;padding:2px 4px;">PV potential</td>
            <td style="padding:2px 4px;"><b>{_v('pv', 1)} kWh/kWp</b></td>
          </tr>
          <tr>
            <td style="color:#555;padding:2px 4px;">Dist. to grid</td>
            <td style="padding:2px 4px;"><b>{_v('dist_grid', 1)} km</b></td>
          </tr>
          <tr style="background:#f9f9f9;">
            <td style="color:#555;padding:2px 4px;">Night-light</td>
            <td style="padding:2px 4px;"><b>{_v('nightlight', 1)}%</b></td>
          </tr>
          <tr>
            <td style="color:#555;padding:2px 4px;">Wealth index</td>
            <td style="padding:2px 4px;"><b>{_v('wealth', 2)}</b></td>
          </tr>
          <tr style="background:#f9f9f9;">
            <td style="color:#555;padding:2px 4px;">Security risk</td>
            <td style="padding:2px 4px;">
              <span style="background:{risk_color};
                           color:white;
                           padding:1px 6px;
                           border-radius:3px;">
                {risk_val}
              </span>
            </td>
          </tr>
        </table>

        <!-- Score bar -->
        <div style="margin-top:7px;
                    background:#eee;
                    border-radius:4px;
                    overflow:hidden;">
          <div style="width:{score_f:.0f}%;
                      background:{score_color};
                      color:white;
                      font-size:11px;
                      padding:3px 6px;
                      white-space:nowrap;">
            Score: {score_f:.1f}/100
          </div>
        </div>

      </div>
    </div>
    """
    return folium.Popup(html, max_width=290)


# ── Legend HTML ───────────────────────────────────────────────────────────────
def _legend_html(color_by: str) -> str:
    if color_by == "Score_Viabilité":
        items = [
            ("#1a9850", "Excellent  75–100"),
            ("#91cf60", "Good       50–75"),
            ("#fee08b", "Moderate   25–50"),
            ("#d73027", "Low         0–25"),
        ]
        title = "🏆 Viability Score"

    elif color_by == COL.get("risk"):
        items = [(c, k) for k, c in RISK_COLORS.items()]
        title = "🛡️ Security Risk"

    elif color_by == COL.get("nightlight"):
        items = [
            ("#f9d900", "High  ≥50%"),
            ("#f39c12", "Med  20–50%"),
            ("#2980b9", "Low   <20%"),
        ]
        title = "🌙 Night-light"

    elif color_by == COL.get("pop"):
        items = [
            ("#08306b", "Very high"),
            ("#2171b5", "High"),
            ("#6baed6", "Medium"),
            ("#c6dbef", "Low"),
        ]
        title = "👥 Population"

    elif color_by == COL.get("demand"):
        items = [
            ("#800026", "Very high"),
            ("#e31a1c", "High"),
            ("#fc4e2a", "Medium"),
            ("#fed976", "Low"),
        ]
        title = "⚡ Demand"

    else:
        items = [
            ("#005a32", "Very high"),
            ("#238b45", "High"),
            ("#74c476", "Medium"),
            ("#c7e9c0", "Low"),
        ]
        title = "💰 Wealth Index"

    rows_html = "".join(
        f'<tr>'
        f'<td style="padding:3px 6px;">'
        f'<div style="width:14px;height:14px;border-radius:50%;'
        f'background:{c};"></div></td>'
        f'<td style="padding:3px 6px;font-size:12px;">{label}</td>'
        f'</tr>'
        for c, label in items
    )

    return f"""
    <div style="
        position:fixed;
        bottom:40px;right:12px;
        z-index:9999;
        background:white;
        padding:10px 14px;
        border-radius:8px;
        box-shadow:2px 2px 10px rgba(0,0,0,0.3);
        font-family:Arial,sans-serif;
        min-width:170px;">
      <b style="font-size:13px;">{title}</b>
      <table style="margin-top:6px;border-collapse:collapse;">
        {rows_html}
      </table>
    </div>
    """


# ── Main map function ─────────────────────────────────────────────────────────
def create_folium_map(
    df: pd.DataFrame,
    color_by: str,
    size_by: str,
    map_style: str,
    max_points: int,
    show_popups: bool = True,
) -> tuple[folium.Map, int]:

    # cap only for map rendering (KPIs use full df)
    d = df.copy()
    if len(d) > max_points:
        if "Score_Viabilité" in d.columns:
            d = d.sort_values("Score_Viabilité", ascending=False).head(max_points)
        else:
            d = d.sample(max_points, random_state=42)

    # basemap
    tile = MAP_TILES.get(map_style, "OpenStreetMap")
    attr = MAP_TILES_ATTR.get(map_style, None)

    m = folium.Map(
        location=MAP_CENTER,
        zoom_start=MAP_ZOOM,
        tiles=tile,
        attr=attr,
        control_scale=True,
        prefer_canvas=True,   # ← key for speed with many markers
    )

    # marker cluster
    cluster = plugins.MarkerCluster(
        name="VIDA sites",
        options={
            "spiderfyOnMaxZoom": True,
            "showCoverageOnHover": False,
            "zoomToBoundsOnClick": True,
            "disableClusteringAtZoom": 12,  # show individual at zoom 12+
        }
    ).add_to(m)

    # radius scale
    vmax = 1.0
    if size_by != "Fixed size" and size_by in d.columns:
        vmax = pd.to_numeric(d[size_by], errors="coerce").max()
        vmax = float(vmax) if pd.notna(vmax) else 1.0

    # add markers
    for _, row in d.iterrows():
        lat = row.get(COL["lat"])
        lon = row.get(COL["lon"])
        if pd.isna(lat) or pd.isna(lon):
            continue

        color  = _get_color(row, color_by)
        radius = _get_radius(row, size_by, vmax)

        tooltip = (
            f"{row.get(COL.get('name',''), '')} | "
            f"Score: {row.get('Score_Viabilité', 0):.0f}"
        )

        popup = _make_popup(row) if show_popups else None

        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            weight=1,
            tooltip=tooltip,
            popup=popup,
        ).add_to(cluster)

    # legend
    m.get_root().html.add_child(folium.Element(_legend_html(color_by)))

    # controls
    plugins.Fullscreen().add_to(m)
    plugins.MiniMap(toggle_display=True, position="bottomleft").add_to(m)
    folium.LayerControl(collapsed=True).add_to(m)

    return m, len(d)