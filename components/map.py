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

def _nightlight_color(v) -> str:
    """Color for HEADER based on night-light (access to electricity)."""
    try:
        v = float(v)
    except Exception:
        return "#9e9e9e"

    if v >= 75:  return "#0f3460"
    if v >= 50:  return "#1a5fb4"
    if v >= 20:  return "#f39c12"
    if v >= 5:   return "#e67e22"
    return "#922b21"


def _score_color(v) -> str:
    """Color for viability score (0–100)."""
    try:
        v = float(v)
    except Exception:
        return "#9e9e9e"
    if v >= 75: return "#1a9850"
    if v >= 50: return "#91cf60"
    if v >= 25: return "#fee08b"
    return "#d73027"


def _demand_color(v) -> str:
    """Color for energy demand based on value."""
    try:
        v = float(v)
    except Exception:
        return "#9e9e9e"

    if v >= 1000: return "#800026"  # Very high - dark red
    if v >= 500:  return "#e31a1c"  # High - red
    if v >= 100:  return "#fc4e2a"  # Medium - orange
    return "#fed976"  # Low - yellow


def _wealth_color(v) -> str:
    """Color for wealth index based on value."""
    try:
        v = float(v)
    except Exception:
        return "#9e9e9e"

    if v >= 0.5:  return "#005a32"  # Very high - dark green
    if v >= 0.0:  return "#238b45"  # High - green
    if v >= -0.5: return "#74c476"  # Medium - light green
    return "#c7e9c0"  # Low - very light green


def _pop_color(v) -> str:
    """Color for population based on value."""
    try:
        v = float(v)
    except Exception:
        return "#9e9e9e"

    if v >= 10000: return "#08306b"  # Very high - dark blue
    if v >= 5000:  return "#2171b5"  # High - blue
    if v >= 1000:  return "#6baed6"  # Medium - light blue
    return "#c6dbef"  # Low - very light blue


def _normalize_risk(val) -> str:
    """Convert risk values to French standard."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "Moyen"

    v = str(val).strip().lower()
    mapping = {
        "low": "Faible",
        "faible": "Faible",
        "medium": "Moyen",
        "moyen": "Moyen",
        "high": "Élevé",
        "élevé": "Élevé",
        "very high": "Très élevé",
        "très élevé": "Très élevé",
    }
    return mapping.get(v, "Moyen")


def _get_color(row: pd.Series, color_by: str) -> str:
    """Get marker color based on selected metric."""
    if color_by == "Score_Viabilité":
        return _score_color(row.get("Score_Viabilité", np.nan))

    if color_by == COL.get("risk"):
        val = row.get(COL["risk"], "")
        normalized_val = _normalize_risk(val)
        return RISK_COLORS.get(normalized_val, "#9e9e9e")

    if color_by == COL.get("nightlight"):
        return _nightlight_color(row.get(COL["nightlight"], np.nan))

    # ✅ NEW: Add color functions for demand, wealth, and population
    if color_by == COL.get("demand"):
        return _demand_color(row.get(COL["demand"], np.nan))

    if color_by == COL.get("wealth"):
        return _wealth_color(row.get(COL["wealth"], np.nan))

    if color_by == COL.get("pop"):
        return _pop_color(row.get(COL["pop"], np.nan))

    # Default fallback
    return "#9e9e9e"
def _get_radius(row: pd.Series, size_by: str, vmax: float) -> float:
    """Get marker radius based on selected metric."""
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
    """Create popup with night-light header and score bar."""

    def _v(key, decimals=None):
        """Helper to safely extract and format values."""
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

    # Security risk (normalized to French)
    raw_risk = _v("risk")
    risk_val = _normalize_risk(raw_risk)
    risk_color = RISK_COLORS.get(risk_val, "#9e9e9e")

    # Viability score
    score = row.get("Score_Viabilité", 0)
    try:
        score_f = float(score)
    except Exception:
        score_f = 0.0
    score_color = _score_color(score_f)

    # Night-light (for HEADER color) - 🎯 This should be BLUE for 97.2%
    nightlight_col = COL.get("nightlight")
    if nightlight_col:
        nightlight = row.get(nightlight_col, 0)
    else:
        nightlight = 0

    try:
        nightlight_f = float(nightlight)
    except Exception:
        nightlight_f = 0.0

    header_color = _nightlight_color(nightlight_f)

    html = f"""
    <div style="font-family:Arial,sans-serif;
                width:280px;font-size:12px;
                border-radius:6px;overflow:hidden;">

      <!-- Header: Colored by NIGHT-LIGHT (access to electricity) -->
      <div style="background:{header_color};
                  color:white;padding:8px 10px;">
        <b style="font-size:13px;">{_v('name')}</b>
        <div style="font-size:10px;margin-top:2px;opacity:0.9;">
          💡 Access: {nightlight_f:.1f}%
        </div>
      </div>

      <!-- Body -->
      <div style="padding:8px 10px;
                  border:1px solid #ddd;
                  border-top:none;">

        <table style="width:100%;border-collapse:collapse;
                      font-size:11px;">
          <tr>
            <td style="color:#555;padding:3px 4px;">Region</td>
            <td style="padding:3px 4px;"><b>{_v('region')}</b></td>
          </tr>
          <tr style="background:#f9f9f9;">
            <td style="color:#555;padding:3px 4px;">Department</td>
            <td style="padding:3px 4px;"><b>{_v('dept')}</b></td>
          </tr>
          <tr>
            <td style="color:#555;padding:3px 4px;">Population</td>
            <td style="padding:3px 4px;"><b>{_v('pop', 0)}</b></td>
          </tr>
          <tr style="background:#f9f9f9;">
            <td style="color:#555;padding:3px 4px;">Connections</td>
            <td style="padding:3px 4px;"><b>{_v('connections', 0)}</b></td>
          </tr>
          <tr>
            <td style="color:#555;padding:3px 4px;">Demand</td>
            <td style="padding:3px 4px;"><b>{_v('demand', 1)} kWh/day</b></td>
          </tr>
          <tr style="background:#f9f9f9;">
            <td style="color:#555;padding:3px 4px;">PV potential</td>
            <td style="padding:3px 4px;"><b>{_v('pv', 1)} kWh/kWp</b></td>
          </tr>
          <tr>
            <td style="color:#555;padding:3px 4px;">Dist. to grid</td>
            <td style="padding:3px 4px;"><b>{_v('dist_grid', 1)} km</b></td>
          </tr>
          <tr style="background:#f9f9f9;">
            <td style="color:#555;padding:3px 4px;">⚡ Night time light </td>
            <td style="padding:3px 4px;">
              <span style="background:{header_color};
                           color:white;padding:2px 6px;
                           border-radius:3px;font-weight:bold;">
                {nightlight_f:.1f}%
              </span>
            </td>
          </tr>
          <tr>
            <td style="color:#555;padding:3px 4px;">Wealth index</td>
            <td style="padding:3px 4px;"><b>{_v('wealth', 2)}</b></td>
          </tr>
          <tr style="background:#f9f9f9;">
            <td style="color:#555;padding:3px 4px;">Security risk</td>
            <td style="padding:3px 4px;">
              <span style="background:{risk_color};
                           color:white;padding:2px 6px;
                           border-radius:3px;font-weight:bold;">
                {risk_val}
              </span>
            </td>
          </tr>
        </table>

        <!-- Score bar: Colored by viability score -->
        <div style="margin-top:10px;
                    background:#eee;
                    border-radius:4px;
                    overflow:hidden;
                    height:24px;">
          <div style="width:{max(score_f, 3):.0f}%;
                      background:{score_color};
                      color:white;
                      font-size:11px;
                      padding:4px 6px;
                      white-space:nowrap;
                      height:100%;
                      box-sizing:border-box;
                      display:flex;
                      align-items:center;">
            🏆 Score: {score_f:.1f}/100
          </div>
        </div>

      </div>
    </div>
    """
    return folium.Popup(html, max_width=300)


# ── Legend HTML ───────────────────────────────────────────────────────────────
def _legend_html(color_by: str) -> str:
    """Generate legend based on selected color metric."""

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
            ("#0f3460", "Very High  ≥75%"),
            ("#1a5fb4", "High       50–75%"),
            ("#f39c12", "Medium     20–50%"),
            ("#e67e22", "Low         5–20%"),
            ("#922b21", "Very Low    <5%"),
        ]
        title = "💡 Night time light"

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
        f'<td style="padding:4px 6px;">'
        f'<div style="width:16px;height:16px;border-radius:50%;'
        f'background:{c};border:1px solid #999;"></div></td>'
        f'<td style="padding:4px 6px;font-size:12px;">{label}</td>'
        f'</tr>'
        for c, label in items
    )

    return f"""
    <div style="
        position:fixed;
        top:70px;right:12px;
        z-index:9999;
        background:white;
        padding:12px 14px;
        border-radius:8px;
        box-shadow:2px 2px 10px rgba(0,0,0,0.3);
        font-family:Arial,sans-serif;
        min-width:180px;">
      <b style="font-size:13px;display:block;margin-bottom:6px;">{title}</b>
      <table style="border-collapse:collapse;">
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
    """Create folium map with markers colored/sized by selected metrics."""

    d = df.copy()
    if len(d) > max_points:
        if "Score_Viabilité" in d.columns:
            d = d.sort_values("Score_Viabilité", ascending=False).head(max_points)
        else:
            d = d.sample(max_points, random_state=42)

    tile = MAP_TILES.get(map_style, "OpenStreetMap")
    attr = MAP_TILES_ATTR.get(map_style, None)

    m = folium.Map(
        location=MAP_CENTER,
        zoom_start=MAP_ZOOM,
        tiles=tile,
        attr=attr,
        control_scale=True,
        prefer_canvas=True,
    )

    cluster = plugins.MarkerCluster(
        name="VIDA sites",
        options={
            "spiderfyOnMaxZoom": True,
            "showCoverageOnHover": False,
            "zoomToBoundsOnClick": True,
            "disableClusteringAtZoom": 12,
        }
    ).add_to(m)

    vmax = 1.0
    if size_by != "Fixed size" and size_by in d.columns:
        vmax = pd.to_numeric(d[size_by], errors="coerce").max()
        vmax = float(vmax) if pd.notna(vmax) else 1.0

    for _, row in d.iterrows():
        lat = row.get(COL["lat"])
        lon = row.get(COL["lon"])
        if pd.isna(lat) or pd.isna(lon):
            continue

        color = _get_color(row, color_by)
        radius = _get_radius(row, size_by, vmax)

        tooltip = (
            f"{row.get(COL.get('name', ''), '')} | "
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

    m.get_root().html.add_child(folium.Element(_legend_html(color_by)))

    plugins.Fullscreen().add_to(m)
    plugins.MiniMap(toggle_display=True, position="bottomleft").add_to(m)
    folium.LayerControl(collapsed=True).add_to(m)

    return m, len(d)