# components/charts.py
import streamlit as st
import pandas as pd

try:
    import plotly.express as px
except Exception as e:
    px = None

from config import COL, RISK_COLORS


def render_charts(df: pd.DataFrame):
    st.subheader("📊 Analytics (VIDA)")

    if px is None:
        st.error("Plotly is not installed. Run: pip install plotly")
        return

    tab1, tab2, tab3 = st.tabs(["⚡ Energy", "👥 Population", "🛡️ Security"])

    with tab1:
        if COL["demand"] in df.columns:
            fig = px.histogram(df, x=COL["demand"], nbins=30, title="Demand distribution (kWh/day)")
            st.plotly_chart(fig, width="stretch")
        else:
            st.info(f"Column not found: {COL['demand']}")

    with tab2:
        if COL["pop"] in df.columns and COL["region"] in df.columns:
            agg = df.groupby(COL["region"])[COL["pop"]].sum().reset_index()
            fig = px.bar(agg, x=COL["region"], y=COL["pop"], title="Population by region")
            fig.update_xaxes(tickangle=-30)
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Population/Region columns not found.")

    with tab3:
        if COL["risk"] in df.columns:
            cnt = df[COL["risk"]].value_counts().reset_index()
            cnt.columns = ["Risk", "Count"]
            fig = px.bar(
                cnt, x="Risk", y="Count", color="Risk",
                color_discrete_map=RISK_COLORS,
                title="Sites by risk level"
            )
            st.plotly_chart(fig, width="stretch")
        else:
            st.info(f"Column not found: {COL['risk']}")