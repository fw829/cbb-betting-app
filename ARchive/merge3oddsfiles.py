import pandas as pd
import os

# File paths
file1 = r"C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\daily-cbb-season-team-feed.xlsx"
file2 = r"C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\2022-2023_CBB_Box_Score_Team-Stats.xlsx"
file3 = r"C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\2023-2024_CBB_Box_Score_Team-Stats.xlsx"
output_file = r"C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\Merged_Odds.csv"

# Load data
df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)
df3 = pd.read_excel(file3)

# Standardizing column names (to avoid inconsistencies due to formatting)
df1.columns = df1.columns.str.strip()
df2.columns = df2.columns.str.strip()
df3.columns = df3.columns.str.strip()

# Define required column order
required_columns = [
    "GAME-ID", "DATE", "TEAM", "CONFERENCE", 
    "VENUE", "1H", "2H", "OT TOTAL", "F", 
    "OPENING SPREAD", "OPENING TOTAL", "CLOSING SPREAD", "CLOSING TOTAL", "CLOSING MONEYLINE"
]

# Keep only the required columns and maintain the order
df1 = df1[[col for col in required_columns if col in df1.columns]]
df2 = df2[[col for col in required_columns if col in df2.columns]]
df3 = df3[[col for col in required_columns if col in df3.columns]]

# Merge data
merged_df = pd.concat([df1, df2, df3], ignore_index=True)

# Ensure final DataFrame follows the exact required column order
merged_df = merged_df.reindex(columns=required_columns)

# Overwrite existing file
if os.path.exists(output_file):
    os.remove(output_file)

# Save to CSV
merged_df.to_csv(output_file, index=False)

print(f"Merged file saved as {output_file}")