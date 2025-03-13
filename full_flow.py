import pandas as pd
import sqlite3
import os

# File paths
merged_odds_path = r"C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\Merged_Odds.csv"
season_feed_path = r"C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\daily-cbb-season-team-feed.xlsx"

# Load Merged_Odds first
merged_odds = pd.read_csv(merged_odds_path)

# Fix DATE format to remove timestamps
merged_odds["DATE"] = pd.to_datetime(merged_odds["DATE"], errors='coerce').dt.date

# Now load season_feed (after fixing date issues)
season_feed = pd.read_excel(season_feed_path)

# Convert DATE back to string format (optional, ensures no issues in merging)
merged_odds["DATE"] = merged_odds["DATE"].astype(str)

# Standardize column names (remove spaces and newlines)
merged_odds.columns = merged_odds.columns.str.replace("\n", " ", regex=True).str.strip()
season_feed.columns = season_feed.columns.str.replace("\n", " ", regex=True).str.strip()

# Ensure GAME-ID column consistency
merged_odds["GAME-ID"] = merged_odds["GAME-ID"].astype(str)
season_feed["GAME-ID"] = season_feed["GAME-ID"].astype(str)

# Keep only columns that already exist in Merged_Odds
common_columns = [col for col in merged_odds.columns if col in season_feed.columns]
season_feed_filtered = season_feed[common_columns]

# Identify new GAME-IDs that are not already in Merged_Odds
new_games = season_feed_filtered[~season_feed_filtered["GAME-ID"].isin(merged_odds["GAME-ID"])]

# Append new games to Merged_Odds
if not new_games.empty:
    updated_merged_odds = pd.concat([merged_odds, new_games], ignore_index=True)
    updated_merged_odds.to_csv(merged_odds_path, index=False)
else:
    updated_merged_odds = merged_odds.copy()

# Reload updated Merged_Odds
merged_data = pd.read_csv(merged_odds_path)

# Fix DATE format to remove timestamps
merged_odds["DATE"] = pd.to_datetime(merged_odds["DATE"], errors='coerce').dt.date

# Create a dictionary to map GAME-ID to both team names
game_id_map = merged_data.groupby("GAME-ID")["TEAM"].apply(list).to_dict()

# Create a dictionary to store team stats by GAME-ID and TEAM
team_stats = merged_data.set_index(["GAME-ID", "TEAM"])[["1H", "2H", "OT TOTAL", "F"]].to_dict(orient="index")

# Fill in missing opponent-related fields
for index, row in merged_data.iterrows():
    game_id = row["GAME-ID"]
    team = row["TEAM"]
    
    # Get opponent team name
    teams = game_id_map.get(game_id, [])
    opponent = [t for t in teams if t != team]
    opp_team = opponent[0] if opponent else None
    opp_stats = team_stats.get((game_id, opp_team), {})

    # Only fill in missing values
    if pd.isna(row["Opp"]): merged_data.at[index, "Opp"] = opp_team
    if pd.isna(row["Opp 1H"]): merged_data.at[index, "Opp 1H"] = opp_stats.get("1H", None)
    if pd.isna(row["Opp 2H"]): merged_data.at[index, "Opp 2H"] = opp_stats.get("2H", None)
    if pd.isna(row["Opp OT Total"]): merged_data.at[index, "Opp OT Total"] = opp_stats.get("OT TOTAL", None)
    if pd.isna(row["Opp F"]): merged_data.at[index, "Opp F"] = opp_stats.get("F", None)

# Calculate Covered Spread (Only if missing)
for index, row in merged_data.iterrows():
    if pd.isna(row["Covered Spread"]) and pd.notna(row["F"]) and pd.notna(row["CLOSING SPREAD"]) and pd.notna(row["Opp F"]):
        result = row["F"] + row["CLOSING SPREAD"]
        
        if result > row["Opp F"]:
            merged_data.at[index, "Covered Spread"] = "Y"
        elif result < row["Opp F"]:
            merged_data.at[index, "Covered Spread"] = "N"
        else:
            merged_data.at[index, "Covered Spread"] = "PUSH"

# Calculate Hit Over (Only if missing)
for index, row in merged_data.iterrows():
    if pd.isna(row["Hit Over"]) and pd.notna(row["F"]) and pd.notna(row["Opp F"]) and pd.notna(row["CLOSING TOTAL"]):
        total_score = row["F"] + row["Opp F"]
        
        if total_score > row["CLOSING TOTAL"]:
            merged_data.at[index, "Hit Over"] = "Y"
        elif total_score < row["CLOSING TOTAL"]:
            merged_data.at[index, "Hit Over"] = "N"
        else:
            merged_data.at[index, "Hit Over"] = "PUSH"

# Save final version
merged_data.to_csv(merged_odds_path, index=False)

print(f"✅ Merged_Odds.csv successfully updated with {len(new_games)} new games and opponent details.")

import pandas as pd
import os

# File paths
merged_odds_path = r"C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\Merged_Odds.csv"
season_feed_path = r"C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\daily-cbb-season-team-feed.xlsx"
merged_summary_path = r"C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\Merged_Summary.csv"
merged_misc_path = r"C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\Merged_Misc.csv"
team_mapping_path = r"C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\Team_Name_Mapping.csv"
merged_final_path = r"C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\Merged_Final.csv"

# Load merged odds data
merged_odds = pd.read_csv(merged_odds_path)

# Fix DATE format to remove timestamps
merged_odds["DATE"] = pd.to_datetime(merged_odds["DATE"], errors='coerce').dt.date

#Load remaining
season_feed = pd.read_excel(season_feed_path)
merged_summary = pd.read_csv(merged_summary_path)
merged_misc = pd.read_csv(merged_misc_path)
team_mapping = pd.read_csv(team_mapping_path)

# Ensure DATE is stored without time component before mapping Season
merged_odds["DATE"] = pd.to_datetime(merged_odds["DATE"], errors='coerce').dt.date

# Drop any rows where DATE is missing to prevent errors
merged_odds = merged_odds.dropna(subset=["DATE"])

# Convert DATE back to string format (optional, ensures no issues in merging)
merged_odds["DATE"] = merged_odds["DATE"].astype(str)

# Now apply Season mapping
merged_odds["Season"] = merged_odds["DATE"].apply(lambda x: 2023 if (int(x.split("-")[1]) >= 11 and int(x.split("-")[0]) == 2022) or (int(x.split("-")[1]) <= 3 and int(x.split("-")[0]) == 2023) 
                                                       else 2024 if (int(x.split("-")[1]) >= 11 and int(x.split("-")[0]) == 2023) or (int(x.split("-")[1]) <= 3 and int(x.split("-")[0]) == 2024) 
                                                       else 2025 if (int(x.split("-")[1]) >= 11 and int(x.split("-")[0]) == 2024) or (int(x.split("-")[1]) <= 3 and int(x.split("-")[0]) == 2025) 
                                                       else None)

# Standardize column names (remove spaces and newlines)
merged_odds.columns = merged_odds.columns.str.replace("\n", " ", regex=True).str.strip()
season_feed.columns = season_feed.columns.str.replace("\n", " ", regex=True).str.strip()
merged_summary.columns = merged_summary.columns.str.replace("\n", " ", regex=True).str.strip()
merged_misc.columns = merged_misc.columns.str.replace("\n", " ", regex=True).str.strip()
team_mapping.columns = team_mapping.columns.str.replace("\n", " ", regex=True).str.strip()

# Convert Season to string first to ensure consistency, then convert back to integer
merged_odds["Season"] = pd.to_numeric(merged_odds["Season"], errors='coerce').fillna(0).astype(int)
merged_summary["Season"] = pd.to_numeric(merged_summary["Season"], errors='coerce').fillna(0).astype(int)
merged_misc["Season"] = pd.to_numeric(merged_misc["Season"], errors='coerce').fillna(0).astype(int)

# Ensure GAME-ID column consistency
merged_odds["GAME-ID"] = merged_odds["GAME-ID"].astype(str)
season_feed["GAME-ID"] = season_feed["GAME-ID"].astype(str)
merged_summary["Season"] = merged_summary["Season"].astype(str)
merged_misc["Season"] = merged_misc["Season"].astype(str)

# Standardize team names using team mapping
team_mapping_dict = dict(zip(team_mapping["Original_Team_Name"], team_mapping["Standardized_Team_Name"]))
merged_summary["TEAM"] = merged_summary["TeamName"].replace(team_mapping_dict)
merged_misc["TEAM"] = merged_misc["TeamName"].replace(team_mapping_dict)

# Ensure Season is consistently an integer across all datasets
merged_summary["Season"] = merged_summary["Season"].astype(str).str.strip().astype(int)
merged_misc["Season"] = merged_misc["Season"].astype(str).str.strip().astype(int)

# Double-check that we didn’t accidentally remove dates
missing_dates = merged_odds[merged_odds["DATE"].isna()]
if not missing_dates.empty:
    print("⚠️ Warning: Some DATE values are missing after conversion. Check for errors.")
    print(missing_dates)

# Check for missing Season values before merging with KenPom
missing_seasons = merged_odds[merged_odds["Season"].isna()]
if not missing_seasons.empty:
    print("⚠️ Warning: Some rows are missing Season values. Check the DATE format before merging with KenPom.")
    print(missing_seasons[["GAME-ID", "DATE", "TEAM"]])

# Merge Merged_Odds with Merged_Summary and Merged_Misc on TEAM and Season
merged_final = merged_odds.merge(merged_summary, on=["TEAM", "Season"], how="left")
merged_final = merged_final.merge(merged_misc, on=["TEAM", "Season"], how="left")

# Drop unnecessary columns before inserting into SQL
columns_to_drop = ["TeamName_x", "TeamName_y"]

# Check and drop duplicate TEAM column
if "TEAM" in merged_final.columns and merged_final.columns.duplicated().sum() > 0:
    print("⚠️ Duplicate TEAM column detected. Removing extra 'TEAM' column.")
    merged_final = merged_final.loc[:, ~merged_final.columns.duplicated()]

# Drop specific columns if they exist
for col in columns_to_drop:
    if col in merged_final.columns:
        print(f"🗑️ Removing unnecessary column: {col}")
        merged_final.drop(columns=[col], inplace=True)

# Ensure DATE column is formatted correctly before saving
merged_final["DATE"] = pd.to_datetime(merged_final["DATE"], errors='coerce')

# Explicitly format it for Excel recognition (Excel should auto-detect it as "Short Date")
merged_final["DATE"] = merged_final["DATE"].astype(str)

# Save final version
merged_final.to_csv(merged_final_path, index=False)

print(f"✅ Merged_Final.csv successfully created with merged odds and KenPom statistics.")


# ✅ DATABASE UPLOAD PROCESS ✅

# Connect to SQLite database
db_path = r"C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\basketball_data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop the existing table if it exists
cursor.execute("DROP TABLE IF EXISTS games")

# Define table schema
create_table_query = """
CREATE TABLE IF NOT EXISTS games (
    GAME_ID TEXT,
    DATE TEXT,
    TEAM TEXT,
    CONFERENCE TEXT,
    VENUE TEXT,
    H1 INTEGER,  -- Renamed from 1H
    H2 INTEGER,  -- Renamed from 2H
    OT_TOTAL REAL,  -- Renamed from OT TOTAL
    F INTEGER,
    OPENING_SPREAD REAL,  -- Renamed from OPENING SPREAD
    OPENING_TOTAL REAL,
    CLOSING_SPREAD REAL,
    CLOSING_TOTAL REAL,
    Opp TEXT,
    Opp_H1 INTEGER,  -- Renamed from Opp 1H
    Opp_H2 INTEGER,  -- Renamed from Opp 2H
    Opp_OT_TOTAL REAL,  -- Renamed from Opp OT Total
    Opp_F INTEGER,
    Covered_Spread TEXT,  -- Renamed from Covered Spread
    Hit_Over TEXT,  -- Renamed from Hit Over
    Season INTEGER,
-- KenPom Statistics
    Tempo REAL,
    RankTempo INTEGER,
    AdjTempo REAL,
    RankAdjTempo INTEGER,
    OE REAL,
    RankOE INTEGER,
    AdjOE REAL,
    RankAdjOE INTEGER,
    DE REAL,
    RankDE INTEGER,
    AdjDE REAL,
    RankAdjDE INTEGER,
    AdjEM REAL,
    RankAdjEM INTEGER,
    seed REAL,
    FG2Pct REAL,
    RankFG2Pct INTEGER,
    FG3Pct REAL,
    RankFG3Pct INTEGER,
    FTPct REAL,
    RankFTPct INTEGER,
    BlockPct REAL,
    RankBlockPct INTEGER,
    OppFG2Pct REAL,
    RankOppFG2Pct INTEGER,
    OppFG3Pct REAL,
    RankOppFG3Pct INTEGER,
    OppFTPct REAL,
    RankOppFTPct INTEGER,
    OppBlockPct REAL,
    RankOppBlockPct INTEGER,
    FG3Rate REAL,
    RankFG3Rate INTEGER,
    OppFG3Rate REAL,
    RankOppFG3Rate INTEGER,
    ARate REAL,
    RankARate INTEGER,
    OppARate REAL,
    RankOppARate INTEGER,
    StlRate REAL,
    RankStlRate INTEGER,
    OppStlRate REAL,
    RankOppStlRate INTEGER,
    DFP REAL,
    NSTRate REAL,
    RankNSTRate INTEGER,
    OppNSTRate REAL,
    RankOppNSTRate INTEGER,
    PRIMARY KEY (GAME_ID, TEAM));
"""
cursor.execute(create_table_query)

# Standardize column names for SQLite
merged_final.rename(columns={
    "GAME-ID":"GAME_ID",
    "1H": "H1",
    "2H": "H2",
    "OT TOTAL": "OT_TOTAL",
    "OPENING SPREAD": "OPENING_SPREAD",
    "OPENING TOTAL": "OPENING_TOTAL",
    "CLOSING SPREAD": "CLOSING_SPREAD",
    "CLOSING TOTAL":"CLOSING_TOTAL",
    "Opp 1H": "Opp_H1",
    "Opp 2H": "Opp_H2",
    "Opp OT Total": "Opp_OT_TOTAL",
    "Opp F":"Opp_F",
    "Covered Spread": "Covered_Spread",
    "Hit Over": "Hit_Over"
}, inplace=True)

# Ensure TEAM column exists and fix auto-renamed columns
if "TeamName_x" in merged_final.columns:
    merged_final.rename(columns={"TeamName_x": "TEAM"}, inplace=True)
if "TeamName_y" in merged_final.columns:
    merged_final.drop(columns=["TeamName_y"], inplace=True, errors="ignore")

# Drop any other unnecessary `_x` or `_y` columns
merged_final.drop(columns=[col for col in merged_final.columns if "_x" in col or "_y" in col], errors="ignore", inplace=True)

#Drop duplicates
merged_final = merged_final.drop_duplicates(subset=["GAME_ID", "TEAM"])

# Final check
print("=== Final Columns Before SQL Insert ===")
print(merged_final.columns)

# Identify and rename duplicate columns
if "TEAM_x" in merged_final.columns and "TEAM_y" in merged_final.columns:
    merged_final.rename(columns={"TEAM_x": "TEAM"}, inplace=True)
    merged_final.drop(columns=["TEAM_y"], inplace=True)

if "Season_x" in merged_final.columns and "Season_y" in merged_final.columns:
    merged_final.rename(columns={"Season_x": "Season"}, inplace=True)
    merged_final.drop(columns=["Season_y"], inplace=True)

# Check final column names
print("✅ Final columns before inserting into database:", merged_final.columns)

# Load data into database
merged_final.to_sql("games", conn, if_exists="replace", index=False)

# Commit and close connection
conn.commit()
conn.close()

print("✅ Database successfully updated with Merged_Final.csv. No duplicate GAME-ID + TEAM entries.")