import sqlite3
import pandas as pd
import os

# Define file paths
file_paths = [
    r'C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\current_odds_history.csv',
    r'C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\misc23.csv',
    r'C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\misc24.csv',
    r'C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\misc25.csv',
    r'C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\summary23_pt.csv',
    r'C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\summary24_pt.csv',
    r'C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\summary25.csv'
]

# Load all files, ensuring all columns are preserved
dataframes = [pd.read_csv(file, dtype=str, low_memory=False) for file in file_paths]

# Merge while preserving all columns
merged_df = pd.concat(dataframes, ignore_index=True, sort=False)

# Ensure team names are consistent (standardize naming convention)
merged_df['TeamName'] = merged_df['TeamName'].str.strip().str.lower()

# Save the merged dataset
output_path = r'C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\merged_cbb_data.csv'
merged_df.to_csv(output_path, index=False)

# File path to SQLite database
db_path = r"C:\Users\Frank W\OneDrive\Desktop\MCBB Data\Testing\basketball_data.db"

# Connect to the database
conn = sqlite3.connect(db_path)

# Load odds data from the database
odds_data = pd.read_sql("SELECT * FROM odds_data", conn)

# Ensure GAME-ID is the same data type in both dataframes
odds_data["GAME-ID"] = odds_data["GAME-ID"].astype(str)
merged_df["GAME-ID"] = merged_df["GAME-ID"].astype(str)

# Ensure the database table retains all merged columns
odds_data = odds_data.merge(merged_df, on=["GAME-ID", "TeamName"], how="left")

# Create a dictionary to map GAME-ID to both team names
game_id_map = odds_data.groupby("GAME-ID")["TeamName"].apply(list).to_dict()

# Create a new Opponent column by looking up the other team for each GAME-ID
odds_data["Opponent"] = odds_data.apply(lambda row: 
    next((team for team in game_id_map[row["GAME-ID"]] if team != row["TeamName"]), None), axis=1)

# Write the updated table back to the database
odds_data.to_sql("odds_data", conn, if_exists="replace", index=False)

conn.close()

print(merged_data["DATE"].unique())  # Print all unique date values
print(merged_data[merged_data["DATE"] == "03/02/2025"].head())  # Check a few rows from March 2
print(merged_data[merged_data["DATE"] == "03/03/2025"].head())  # Check a few rows from March 3

print("Merged data saved to", output_path)
print("Opponent column successfully added, and all columns retained!")
