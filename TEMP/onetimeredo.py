#onetimeredo of database

import pandas as pd
import sqlite3

# File paths
db_path = "C:/Users/Frank W/OneDrive/Desktop/College Basketball Wagering/Database/basketball_data.db"
csv_path = "C:/Users/Frank W/OneDrive/Desktop/College Basketball Wagering/Database/merged_oddsandkenpom.csv"

# Load full dataset from CSV
df = pd.read_csv(csv_path, low_memory=False)

# Connect to SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop the old table to start fresh (RUN THIS ONLY ONCE)
cursor.execute("DROP TABLE IF EXISTS merged_odds_kenpom")

# Create a new table with the correct structure
df.to_sql("merged_odds_kenpom", conn, if_exists="replace", index=False)

print("Database structure updated with the new dataset.")

conn.commit()
conn.close()
