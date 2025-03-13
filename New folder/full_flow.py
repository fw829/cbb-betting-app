import pandas as pd
import sqlite3
import os

# Define file paths
base_path = r'C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database'
merged_odds_path = os.path.join(base_path, 'Merged_Odds.csv')
daily_feed_path = os.path.join(base_path, '03-03-2025-cbb-season-team-feed.xlsx')
merged_misc_path = os.path.join(base_path, 'Merged_Misc.csv')
misc_25_path = os.path.join(base_path, 'misc25.csv')
merged_summary_path = os.path.join(base_path, 'Merged_Summary.csv')
summary_25_path = os.path.join(base_path, 'summary25.csv')
db_path = os.path.join(base_path, 'basketball_data.db')

# Step 1: Update Merged_Misc and Merged_Summary with 2025 data
def update_merged_data(merged_path, new_data_path, season):
    merged_df = pd.read_csv(merged_path, dtype=str, low_memory=False)
    new_data_df = pd.read_csv(new_data_path, dtype=str, low_memory=False)
    merged_df = merged_df[merged_df["Season"] != season]  # Keep all past data
    updated_df = pd.concat([merged_df, new_data_df], ignore_index=True, sort=False)
    updated_df.to_csv(merged_path, index=False)
    print(f"{merged_path} updated with new {season} season data.")

update_merged_data(merged_misc_path, misc_25_path, "2025")
update_merged_data(merged_summary_path, summary_25_path, "2025")

# Step 2: Load and Process Merged_Odds

# Load Team Name Mapping
mapping_path = os.path.join(base_path, 'Team_Name_Mapping_-_Summary___Misc.csv')
if os.path.exists(mapping_path):
    team_mapping = pd.read_csv(mapping_path, dtype=str)
    team_name_dict = dict(zip(team_mapping["Original_Team_Name"].str.strip(), team_mapping["Mapped_Team_Name"].str.strip()))
    
else:
    raise FileNotFoundError(f"❌ Team name mapping file not found at: {mapping_path}")
if os.path.exists(merged_odds_path):
    merged_odds_df = pd.read_csv(merged_odds_path, dtype=str, low_memory=False)
else:
    merged_odds_df = pd.DataFrame()

# Load new game data
df_new_games = pd.read_excel(daily_feed_path, sheet_name='2024-25-NCAAB-TEAM', dtype=str)
df_new_games.columns = df_new_games.columns.str.strip()

# Standardize column names
column_name_mappings = {
    "ASSOCIATION \n&\nDIVISION": "ASSOCIATION & DIVISION",
    "ARENA\n& \nSTATE": "ARENA & STATE",
    "OT\nTOTAL": "OT TOTAL",
    "CLOSING\nODDS": "CLOSING ODDS",
    "CLOSING\nMONEYLINE": "MONEYLINE"
}
df_new_games.rename(columns=column_name_mappings, inplace=True)

# Standardize date format
df_new_games["DATE"] = pd.to_datetime(df_new_games["DATE"], errors='coerce').dt.strftime('%Y-%m-%d')

# Connect to database
conn = sqlite3.connect(db_path)

# Get database column names
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(basketball_data);")
db_columns = [row[1] for row in cursor.fetchall()]

# Filter new data to match database columns
new_data_filtered = df_new_games[[col for col in df_new_games.columns if col in db_columns]]


opponent_columns = ["Opponent", "Opponent 1H", "Opponent 2H", "Opponent F", "Covered Spread (Y/N)", "Hit Over (Y/N)"]
for col in opponent_columns:
    if col not in new_data_filtered.columns:
        new_data_filtered[col] = ""  # Initialize with empty values






new_data_filtered = df_new_games[[col for col in df_new_games.columns if col in db_columns]]

# Get existing GAME-IDs to prevent duplicates
existing_games = pd.read_sql("SELECT DISTINCT `GAME-ID` FROM basketball_data", conn)
new_data_filtered = new_data_filtered[~new_data_filtered["GAME-ID"].isin(existing_games["GAME-ID"])]

# Ensure only games with exactly two teams are added

# Map GAME-ID to team names to create opponent mapping
game_id_map = new_data_filtered.groupby("GAME-ID")['TEAM'].apply(list).to_dict()

# Assign opponent team name
new_data_filtered["Opponent"] = new_data_filtered.apply(lambda row: next((team for team in game_id_map[row["GAME-ID"]] if team != row["TEAM"]), None), axis=1)

# Map opponent scores
score_map = new_data_filtered.set_index(["GAME-ID", "TEAM"])["F"].to_dict()
new_data_filtered["Opponent F"] = new_data_filtered.apply(lambda row: score_map.get((row["GAME-ID"], row["Opponent"]), None), axis=1)

# Copy first-half and second-half scores of opponents
score_map_1h = new_data_filtered.set_index(["GAME-ID", "TEAM"])["1H"].to_dict()
score_map_2h = new_data_filtered.set_index(["GAME-ID", "TEAM"])["2H"].to_dict()
new_data_filtered["Opponent 1H"] = new_data_filtered.apply(lambda row: score_map_1h.get((row["GAME-ID"], row["Opponent"]), None), axis=1)
new_data_filtered["Opponent 2H"] = new_data_filtered.apply(lambda row: score_map_2h.get((row["GAME-ID"], row["Opponent"]), None), axis=1)

# Assign Covered Spread and Hit Over columns (placeholders for now)
new_data_filtered["Covered Spread (Y/N)"] = ""
new_data_filtered["Hit Over (Y/N)"] = ""
game_counts = new_data_filtered["GAME-ID"].value_counts()
valid_games = game_counts[game_counts == 2].index
new_data_filtered = new_data_filtered[new_data_filtered["GAME-ID"].isin(valid_games)]

# Step 3: Merge KenPom Data (Misc & Summary) for New Games
if not new_data_filtered.empty:
    # Load KenPom data
    df_misc = pd.read_csv(merged_misc_path, dtype=str, low_memory=False).rename(columns={"TeamName": "TEAM"})
    df_summary = pd.read_csv(merged_summary_path, dtype=str, low_memory=False).rename(columns={"TeamName": "TEAM"})
    
     # Apply team name mapping
    new_data_filtered["TEAM"] = new_data_filtered["TEAM"].replace(team_name_dict)
    df_misc["TEAM"] = df_misc["TEAM"].replace(team_name_dict)
    df_summary["TEAM"] = df_summary["TEAM"].replace(team_name_dict)
    
    new_data_filtered["TEAM"] = new_data_filtered["TEAM"].str.strip().str.title()
    df_misc["TEAM"] = df_misc["TEAM"].str.strip().str.title()
    df_summary["TEAM"] = df_summary["TEAM"].str.strip().str.title()
    
    # Identify missing teams before merging
    missing_teams = new_data_filtered[~new_data_filtered["TEAM"].isin(df_summary["TEAM"])]["TEAM"].unique()
    if missing_teams.size > 0:
        print("⚠️ Warning: Some teams are not found in KenPom data:", missing_teams)
    
    # Filter KenPom data to only include the current season (2025)
    df_summary = df_summary[df_summary['Season'].astype(str) == '2025']
    df_misc = df_misc[df_misc['Season'].astype(str) == '2025']

    # Merge KenPom data
    new_data_filtered = new_data_filtered.merge(df_summary, on="TEAM", how="left")
    new_data_filtered = new_data_filtered.merge(df_misc, on="TEAM", how="left")
    
      
    
    
    # Save the merged dataset to a CSV for troubleshooting
    debug_merged_output_path = os.path.join(base_path, 'Debug_Merged_Output.csv')
    new_data_filtered.to_csv(debug_merged_output_path, index=False)
    print(f'📂 Merged data saved temporarily to: {debug_merged_output_path}')

    # Insert merged data into the database
    new_data_filtered.to_sql("basketball_data", conn, if_exists="append", index=False, chunksize=1000)
    print(f"✅ Added {len(new_data_filtered)} new games to the database with KenPom data.")
else:
    print("✅ No new games to add. Database is up to date.")

conn.close()
print("🚀 Database update complete!")
