import streamlit as st
import pandas as pd
import pydeck as pdk

st.title("Map Test")

df = pd.DataFrame({
    "lat": [13.5128, 17.6078, 14.1939],
    "lon": [2.1063, 8.0817, 5.2933],
})

layer = pdk.Layer(
    "ScatterplotLayer",
    df,
    get_position=["lon", "lat"],
    get_radius=10000,
    get_fill_color=[0, 0, 255],
    pickable=True,
)

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=pdk.ViewState(
        latitude=17.6, longitude=8.0, zoom=6
    ),
    map_style="open-street-map",
)

st.pydeck_chart(deck, width="stretch")