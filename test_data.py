# test_data.py (create in root folder)
import pandas as pd
from utils.data_loader import load_data, get_summary_stats

df = load_data()
print("✅ Shape:", df.shape)
print("✅ Columns:", df.columns.tolist())
print("✅ Stats:", get_summary_stats(df))