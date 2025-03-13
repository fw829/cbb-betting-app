import sqlite3
import pandas as pd
import os

# File paths
DATA_FOLDER = r"C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database"
DB_FILE = os.path.join(DATA_FOLDER, "basketball_data.db")
CSV_FILE = os.path.join(DATA_FOLDER, "cleaned_merged_basketball_data.csv")

# Connect to the database
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Ensure merged_data table exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS merged_data (
        "GAME-ID" TEXT,
        "Team" TEXT,
        "Opponent" TEXT,
        "Final" INTEGER,
        "OpponentFinalScore" INTEGER,
        "Opening Spread" REAL,
        "Covered Spread (Y/N)" TEXT,
        "Opening Total" REAL,
        "Covered Total (Y/N)" TEXT,
        "Tempo" REAL,
        "AdjTempo" REAL,
        "OE" REAL,
        "AdjOE" REAL,
        "DE" REAL,
        "AdjDE" REAL,
        "AdjEM" REAL,
        PRIMARY KEY ("GAME-ID", "Team")
    )
''')
conn.commit()

# Load merged data
merged_data = pd.read_csv(CSV_FILE)

# Drop rows where GAME-ID or TeamName is missing
merged_data = merged_data.dropna(subset=["GAME-ID", "TeamName"])

# Standardize Team Names
merged_data["TeamName"] = merged_data["TeamName"].str.strip().str.upper()

# Insert or replace data in the database
merged_data.to_sql("merged_data", conn, if_exists="replace", index=False)
conn.commit()

# Close connection
conn.close()

print("Database updated! Merged data successfully integrated.")
