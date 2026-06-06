import os
import pandas as pd

INPUT_XLSX  = os.path.join("data", "Niger VIDA tool.xlsx")
OUTPUT_FILE = os.path.join("data", "vida_clean.parquet")   # fast
# OUTPUT_FILE = os.path.join("data", "vida_clean.csv")     # alternative

def find_header_row(filepath, keywords=("Latitude", "Longitude"), max_rows=30):
    preview = pd.read_excel(filepath, header=None, nrows=max_rows, engine="openpyxl")
    for i in range(len(preview)):
        row = preview.iloc[i].astype(str).str.strip().str.lower().tolist()
        if all(k.lower() in row for k in keywords):
            return i
    return None

def main():
    if not os.path.exists(INPUT_XLSX):
        raise FileNotFoundError(INPUT_XLSX)

    header_row = find_header_row(INPUT_XLSX)
    if header_row is None:
        raise ValueError("Header row not found (Latitude/Longitude not detected). Open Excel and check the row.")

    df = pd.read_excel(INPUT_XLSX, header=header_row, engine="openpyxl")

    # Clean columns
    df.columns = [str(c).strip() for c in df.columns]
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    df = df.dropna(how="all")

    # Make sure coords exist
    required = ["Latitude", "Longitude"]
    for c in required:
        if c not in df.columns:
            raise ValueError(f"Missing required column: {c}. Columns found: {df.columns.tolist()}")

    # Remove rows without coords
    df = df.dropna(subset=["Latitude", "Longitude"]).copy()

    # Convert common numeric columns (add/remove as needed)
    numeric_cols = [
        "Population",
        "Nombre estimé de connexions",
        "Demande énergétique estimée [kWh/day]",
        "Production PV potentielle [kWh/kWp]",
        "Distance au réseau existant [km]",
        "Distance au réseau planifié [km]",
        "Éclairage nocturne [%]",
        "Indice de richesse relative",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Save
    os.makedirs("data", exist_ok=True)
    if OUTPUT_FILE.endswith(".parquet"):
        df.to_parquet(OUTPUT_FILE, index=False)
    else:
        df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print("✅ Clean file saved:", OUTPUT_FILE)
    print("✅ Shape:", df.shape)
    print("✅ Columns:", df.columns.tolist())

if __name__ == "__main__":
    main()