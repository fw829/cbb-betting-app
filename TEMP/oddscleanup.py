# oddscleanup.py

import pandas as pd

# Define file paths
odds_path = r'C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\updated_odds_history.csv'
output_path = r'C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\oddspremerge.csv'

# Load odds data
odds_data = pd.read_csv(odds_path, dtype=str, low_memory=False)

# Print available columns for debugging
print("Available columns in the dataset:")
print(odds_data.columns.tolist())

# Create a dictionary to map GAME-ID to both team names
game_id_map = odds_data.groupby("GAME-ID")["TeamName"].apply(list).to_dict()

# Create a new Opponent column by looking up the other team for each GAME-ID
odds_data["Opponent"] = odds_data.apply(lambda row: 
    next((team for team in game_id_map[row["GAME-ID"]] if team != row["TeamName"]), None), axis=1)

# Load dataset
odds_data = pd.read_csv(odds_path, dtype=str, low_memory=False)

# Create a dictionary mapping GAME-ID to TeamName and F (final score)
game_score_map = odds_data.set_index(["GAME-ID", "TeamName"])["F"].to_dict()

# Function to find opponent's score
def get_opponent_score(row):
    return game_score_map.get((row["GAME-ID"], row["Opponent"]))

# Add new column 'Opponent Score'
odds_data["Opponent Score"] = odds_data.apply(get_opponent_score, axis=1)

# Save the updated dataset
odds_data.to_csv(output_path, index=False)

print(f"Updated odds data saved to {output_path}")


# Rename columns
rename_columns = {
    "STARTING LINEUPS": "Starter1",
    "Unnamed: 33": "Starter2",
    "Unnamed: 34": "Starter3",
    "Unnamed: 35": "Starter4",
    "Unnamed: 36": "Starter5",
    "OPENING SPREAD": "Opening Spread",
    "OPENING TOTAL": "Opening Total",
    "CLOSING SPREAD": "Closing Spread",
    "CLOSING TOTAL": "Closing Total",
    "MONEYLINE": "ML",
    "Covered Spread (Yes/No)": "Covered Spread (Y/N)",
    "Covered Total (Yes/No)": "Hit Over (Y/N)"
}

odds_data = odds_data.rename(columns=rename_columns)

# Specify columns to retain
columns_to_keep = [
    "Season", "Game Type", "GAME-ID", "DATE", "TeamName", "Opponent", "CONFERENCE", 
    "1H", "2H", "OT", "F", "Starter1", "Starter2", "Starter3", "Starter4", "Starter5",
    "Opening Spread", "Opening Total", "Closing Spread", "Closing Total", "ML",
    "Covered Spread (Y/N)", "Hit Over (Y/N)"
]

# Ensure all columns exist before filtering
columns_available = odds_data.columns.tolist()
columns_to_keep = [col for col in columns_to_keep if col in columns_available]

odds_data = odds_data[columns_to_keep]

# Save the cleaned dataset
odds_data.to_csv(output_path, index=False)

print(f"Cleaned odds data saved to {output_path}")