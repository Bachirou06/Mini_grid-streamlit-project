# config.py
import os
from PIL import Image
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)

APP_TITLE = "SEEC Niger – Mini-grid Webmap"

# Load logo with fallback
LOGO_PATH = os.path.join(BASE_DIR, "assets", "seec_icon.jpeg")
#try:
if os.path.exists(LOGO_PATH):
        #logo_img = Image.open(LOGO_PATH)
    APP_ICON = LOGO_PATH
        # Resize to square (256x256) for browser tab
        # APP_ICON = logo_img.resize((512, 512), Image.Resampling.LANCZOS)
        # APP_ICON = Image.open(LOGO_PATH)
    logger.info(f"✅ Logo loaded: {LOGO_PATH}")
        #else:
        #raise FileNotFoundError(f"Logo not found at {LOGO_PATH}")
        #logger.warning(f"⚠️ Could not load logo: {e}. Using emoji fallback.")
        # except Exception as e:
        #APP_ICON = "⚡"
else:
    logger.warning(f"⚠️ Logo not found at {LOGO_PATH}. Using emoji fallback.")
    APP_ICON = "⚡"

APP_LAYOUT = "wide"
ENABLE_CHARTS = True
DATA_PATH = os.path.join(BASE_DIR, "data", "vida_clean.parquet")
APP_TITLE = " SEEC Niger – Mini-grid Webmap"

# Map defaults (Niger)
MAP_CENTER = [17.6078, 8.0817]
MAP_ZOOM = 6

MAP_TILES = {
    "OpenStreetMap": "OpenStreetMap",
    "Satellite": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    "Terrain": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
    "Dark": "CartoDB dark_matter",
}
MAP_TILES_ATTR = {
    "Satellite": "Esri",
    "Terrain": "Esri",
}

# Column mapping (must match the cleaned parquet column names)
COL = {
    "lat": "Latitude",
    "lon": "Longitude",
    "name": "Nom",
    "region": "Région",
    "dept": "Départment",

    "connections": "Nombre estimé de connexions",
    "demand": "Demande énergétique estimée [kWh/day]",
    "pv": "Production PV potentielle [kWh/kWp]",
    "dist_grid": "Distance au réseau existant [km]",
    "nightlight": "Éclairage nocturne [%]",
    "pop": "Population",
    "wealth": "Indice de richesse relative",
    "risk": "Risque de sécurité",
    "incidents_50": "Incidents dans un rayon de 50 km",
}

RISK_COLORS = {
    "Faible": "#2ecc71",
    "Moyen": "#f39c12",
    "Élevé": "#e74c3c",
    "Très élevé": "#922b21",
}

# Weights for computed viability score (0..100)
VIABILITY_WEIGHTS = {
    "connections": 0.30,
    "demand": 0.25,
    "pv": 0.25,
    "wealth": 0.20,
}

# Optional: enable charts tab
ENABLE_CHARTS = True