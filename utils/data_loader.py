import os
import pandas as pd
import streamlit as st

from config import DATA_PATH, COL, VIABILITY_WEIGHTS


@st.cache_data(show_spinner="Loading VIDA cleaned data…")
def load_data() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"Missing cleaned file: {DATA_PATH}\n\n"
            "Run first: python prepare_vida_data.py"
        )

    df = pd.read_parquet(DATA_PATH)

    # Strip column names (extra safety)
    df.columns = [str(c).strip() for c in df.columns]

    # Ensure coords exist
    if COL["lat"] not in df.columns or COL["lon"] not in df.columns:
        raise KeyError(
            f"Columns {COL['lat']}/{COL['lon']} not found in cleaned parquet.\n"
            f"Found: {df.columns.tolist()}"
        )

    # Cast coords numeric
    df[COL["lat"]] = pd.to_numeric(df[COL["lat"]], errors="coerce")
    df[COL["lon"]] = pd.to_numeric(df[COL["lon"]], errors="coerce")
    df = df.dropna(subset=[COL["lat"], COL["lon"]]).copy()

    # Cast numeric columns used by filters/score (if present)
    numeric_cols = [
        COL.get("connections"),
        COL.get("demand"),
        COL.get("pv"),
        COL.get("dist_grid"),
        COL.get("nightlight"),
        COL.get("pop"),
        COL.get("wealth"),
        COL.get("incidents_50"),
    ]
    for c in numeric_cols:
        if c and c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Compute viability score
    df["Score_Viabilité"] = compute_viability_score(df)

    # Simple class
    df["Viabilité_Classe"] = pd.cut(
        df["Score_Viabilité"],
        bins=[0, 25, 50, 75, 100],
        labels=["Faible", "Modérée", "Bonne", "Excellente"],
        include_lowest=True,
    )

    return df.reset_index(drop=True)


def normalize(series: pd.Series) -> pd.Series:
    series = series.fillna(0)
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(0.5, index=series.index)
    return (series - mn) / (mx - mn)


def compute_viability_score(df: pd.DataFrame) -> pd.Series:
    score = pd.Series(0.0, index=df.index)

    for key, weight in VIABILITY_WEIGHTS.items():
        colname = COL.get(key)
        if colname and colname in df.columns:
            score += normalize(df[colname]) * (weight * 100)

    return score.round(2)


def get_kpis(df: pd.DataFrame) -> dict:
    def safe_sum(col):
        return float(df[col].sum()) if col in df.columns else 0.0

    def safe_mean(col):
        return float(df[col].mean()) if col in df.columns else 0.0

    return {
        "total_sites": int(len(df)),
        "total_pop": int(safe_sum(COL["pop"])) if COL["pop"] in df.columns else 0,
        "avg_connections": safe_mean(COL["connections"]),
        "avg_demand": safe_mean(COL["demand"]),
        "avg_score": float(df["Score_Viabilité"].mean()) if "Score_Viabilité" in df.columns else 0.0,
        "high_risk_pct": float(
            df[COL["risk"]].isin(["Élevé", "Très élevé"]).mean() * 100
        ) if COL["risk"] in df.columns else 0.0,
    }