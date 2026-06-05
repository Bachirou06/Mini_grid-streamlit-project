# utils/data_loader.py
import pandas as pd
import numpy as np
import streamlit as st
import os


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load Niger VIDA data from Excel file"""

    # ✅ Get absolute path automatically
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filepath = os.path.join(base_dir, "data", "Niger VIDA tool.xlsx")

    # Check if file exists
    if not os.path.exists(filepath):
        st.error(f"❌ File not found at: {filepath}")
        st.stop()

    try:
        # ✅ Try different header rows to find the correct one
        # Read first 10 rows to inspect
        df_preview = pd.read_excel(
            filepath,
            sheet_name=0,
            engine="openpyxl",
            header=None,  # No header, read raw
            nrows=10
        )

        st.write("📋 First 10 rows (raw):")
        st.dataframe(df_preview)

        # ✅ Try header at row index 1 (second row)
        df_row1 = pd.read_excel(
            filepath,
            sheet_name=0,
            engine="openpyxl",
            header=1  # Second row as header
        )
        st.write("📋 Columns with header=1:", df_row1.columns.tolist())

        # ✅ Try header at row index 2 (third row)
        df_row2 = pd.read_excel(
            filepath,
            sheet_name=0,
            engine="openpyxl",
            header=2  # Third row as header
        )
        st.write("📋 Columns with header=2:", df_row2.columns.tolist())

        # ✅ Try header at row index 3 (fourth row)
        df_row3 = pd.read_excel(
            filepath,
            sheet_name=0,
            engine="openpyxl",
            header=3  # Fourth row as header
        )
        st.write("📋 Columns with header=3:", df_row3.columns.tolist())

    except Exception as e:
        st.error(f"❌ Error reading Excel file: {e}")
        st.stop()

    st.stop()  # Stop here to inspect results
    return pd.DataFrame()


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and preprocess data"""

    # Drop rows without coordinates
    df = df.dropna(subset=["Latitude", "Longitude"])

    # Numeric columns
    numeric_cols = [
        "Nombre estimé de connexions",
        "Demande énergétique estimée [kWh/day]",
        "Production PV potentielle [kWh/kWp]",
        "Distance au réseau existant [km]",
        "Éclairage nocturne [%]",
        "Population",
        "Indice de richesse relative",
        "Superficie agricole totale [ha]",
        "Valeur totale des cultures [$/year]"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Viability score
    df["Score_Viabilité"] = calculate_viability_score(df)

    return df


def calculate_viability_score(df: pd.DataFrame) -> pd.Series:
    """Calculate a viability score from 0 to 100"""
    score = pd.Series(0.0, index=df.index)

    if "Nombre estimé de connexions" in df.columns:
        score += normalize(df["Nombre estimé de connexions"]) * 25

    if "Demande énergétique estimée [kWh/day]" in df.columns:
        score += normalize(df["Demande énergétique estimée [kWh/day]"]) * 25

    if "Production PV potentielle [kWh/kWp]" in df.columns:
        score += normalize(df["Production PV potentielle [kWh/kWp]"]) * 25

    if "Indice de richesse relative" in df.columns:
        score += normalize(df["Indice de richesse relative"]) * 25

    return score.round(2)


def normalize(series: pd.Series) -> pd.Series:
    """Normalize a series between 0 and 1"""
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series(0.5, index=series.index)
    return (series - min_val) / (max_val - min_val)


def get_summary_stats(df: pd.DataFrame) -> dict:
    """Get summary statistics"""
    return {
        "total_sites": len(df),
        "total_population": df["Population"].sum()
        if "Population" in df.columns else 0,
        "avg_connections": df["Nombre estimé de connexions"].mean()
        if "Nombre estimé de connexions" in df.columns else 0,
        "avg_demand": df["Demande énergétique estimée [kWh/day]"].mean()
        if "Demande énergétique estimée [kWh/day]" in df.columns else 0,
        "regions": df["Région"].nunique()
        if "Région" in df.columns else 0
    }