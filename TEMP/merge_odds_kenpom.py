import pandas as pd
import sqlite3
import os

# Load the merged data
CSV_FILE = r"C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\merged_basketball_data.csv"
merged_data = pd.read_csv(CSV_FILE)

# Add Opponent and Opponent Final Score columns

# Create a dictionary to map GAME-ID to both team names
game_id_map = merged_data.groupby("GAME-ID")["TeamName"].apply(list).to_dict()

# Add Opponent column
merged_data["Opponent"] = merged_data.apply(lambda row: 
    next((team for team in game_id_map[row["GAME-ID"]] if team != row["TeamName"]), None), axis=1)

# Add Opponent Final Score column
score_map = merged_data.set_index(["GAME-ID", "TeamName"])["F"].to_dict()
merged_data["Opponent Final"] = merged_data.apply(lambda row: 
    score_map.get((row["GAME-ID"], row["Opponent"]), None), axis=1)

# Columns to keep and their new names
columns_to_keep = {
    "Season": "Season",
    "Game Type": "Game Type",
    "GAME-ID": "GAME-ID",
    "DATE": "DATE",
    "TeamName": "TeamName",
    "CONFERENCE": "Conference",
    "VENUE": "Venue",
    "1H": "1H",
    "2H": "2H",
    "OT\nTOTAL": "OT_TOTAL",
    "F": "F",
    "STARTING LINEUPS": "starter 1",
    "Unnamed: 33": "starter 2",
    "Unnamed: 34": "starter 3",
    "Unnamed: 35": "starter 4",
    "Unnamed: 36": "starter 5",
    "OPENING SPREAD": "Opening Spread",
    "OPENING TOTAL": "Opening Total",
    "CLOSING SPREAD": "Closing Spread",
    "CLOSING TOTAL": "Closing Total",
    "MONEYLINE": "ML",
    "Covered Spread (Yes/No)": "Covered Spread (Y/N)",
    "Covered Total (Yes/No)": "Covered Total (Y/N)",
    "FG2Pct": "FG2Pct",
    "RankFG2Pct": "RankFG2Pct",
    "FG3Pct": "FG3Pct",
    "RankFG3Pct": "RankFG3Pct",
    "FTPct": "FTPct",
    "RankFTPct": "RankFTPct",
    "OppFG2Pct": "OppFG2Pct",
    "RankOppFG2Pct": "RankOppFG2Pct",
    "OppFG3Pct": "OppFG3Pct",
    "RankOppFG3Pct": "RankOppFG3Pct",
    "FG3Rate": "FG3Rate",
    "RankFG3Rate": "RankFG3Rate",
    "OppFG3Rate": "OppFG3Rate",
    "RankOppFG3Rate": "RankOppFG3Rate",
    "ARate": "ARate",
    "RankARate": "RankARate",
    "OppARate": "OppARate",
    "RankOppARate": "RankOppARate",
    "StlRate": "StlRate",
    "RankStlRate": "RankStlRate",
    "OppStlRate": "OppStlRate",
    "RankOppStlRate": "RankOppStlRate",
    "DFP": "DFP",
    "NSTRate": "NSTRate",
    "RankNSTRate": "RankNSTRate",
    "OppNSTRate": "OppNSTRate",
    "RankOppNSTRate": "RankOppNSTRate",
    "Tempo": "Tempo",
    "RankTempo": "RankTempo",
    "AdjTempo": "AdjTempo",
    "RankAdjTempo": "RankAdjTempo",
    "OE": "OE",
    "RankOE": "RankOE",
    "AdjOE": "AdjOE",
    "RankAdjOE": "RankAdjOE",
    "DE": "DE",
    "RankDE": "RankDE",
    "AdjDE": "AdjDE",
    "RankAdjDE": "RankAdjDE",
    "AdjEM": "AdjEM",
    "RankAdjEM": "RankAdjEM",
    "seed": "seed"
}



# Select and rename the desired columns


# Select and rename the desired columns
cleaned_data = merged_data[columns_to_keep.keys()].rename(columns=columns_to_keep)

# Save the cleaned data back to a CSV
CLEANED_CSV_FILE = r"C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\cleaned_merged_basketball_data.csv"
cleaned_data.to_csv(CLEANED_CSV_FILE, index=False)

# Display a message
print("Data cleaned and saved to", CLEANED_CSV_FILE)
