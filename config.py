# config.py

# App settings
APP_TITLE = "VIDA - Viabilité des Mini-Réseaux"
APP_ICON = "⚡"
APP_LAYOUT = "wide"

# ✅ Add the file path
DATA_PATH = "data/Niger VIDA tool.csv"

# ✅ Update map center to Niger
MAP_CENTER = [17.6078, 8.0817]  # Niger country center
MAP_ZOOM = 6
# Column groups
COLUMNS = {
    "coordinates": {
        "lat": "Latitude",
        "lon": "Longitude"
    },
    "viability": [
        "Nombre estimé de connexions",
        "Demande énergétique estimée [kWh/day]",
        "Demande moyenne par connexion [kWh/day]",
        "Production PV potentielle [kWh/kWp]",
        "Distance au réseau existant [km]",
        "Distance au réseau planifié [km]",
        "Éclairage nocturne [%]",
        "Distance à la lumière nocturne [km]"
    ],
    "settlement": [
        "Nom",
        "Région",
        "Départment",
        "Densité des bâtiments [%]",
        "Superficie du site [km2]",
        "Nombre de bâtiments",
        "Bâtiments grands",
        "Bâtiments moyens",
        "Bâtiments petits",
        "Structures très petites",
        "Population"
    ],
    "socioeconomic": [
        "Distance à la source d'eau [km]",
        "Établissement d'enseignement",
        "Centres de santé",
        "Indice de richesse relative",
        "Accès routier principal?",
        "Distance à la route principale [km]",
        "Distance au centre urbain [km]",
        "Centre urbain le plus proche"
    ],
    "conflict": [
        "Décès dans un rayon de 50 km (batailles:émeutes:violence contre les civils:explosions)",
        "Décès dans un rayon de 25 km (batailles:émeutes:violence contre les civils:explosions)",
        "Incidents dans un rayon de 50 km",
        "Risque de sécurité"
    ],
    "agriculture": [
        "Les cinq cultures dominantes",
        "Superficie agricole totale [ha]",
        "Valeur totale des cultures [$/year]",
        "Rendement total des cultures [kg/ha]",
        "Valeur totale des cultures par hectare [$/ha]"
    ]
}

# Color scales
COLOR_SCALES = {
    "Éclairage nocturne [%]": "YlOrRd",
    "Population": "Blues",
    "Indice de richesse relative": "Greens",
    "Risque de sécurité": "Reds",
    "Demande énergétique estimée [kWh/day]": "Viridis"
}

# Risk colors
RISK_COLORS = {
    "Faible": "green",
    "Moyen": "orange",
    "Élevé": "red",
    "Très élevé": "darkred"
}